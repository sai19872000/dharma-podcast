"""
tts.py — ElevenLabs TTS for each dialogue turn.

Caches rendered turns by sha256(voice_id + phoneme_text + settings_fp) to
avoid re-billing. Cache lives at <repo_root>/cache/turn_<sha>.mp3

v3 changes (Ep001 v3):
  - Phoneme substitution: Sanskrit/Pāli terms wrapped in IPA phoneme tags
    before sending to ElevenLabs (via engine/pronunciation.py).
  - Realism levers applied (2 of 3 selected):
      1. stability lowered to 0.40 (more expressive prosody variance)
      2. style raised to 0.35 (emotional texture; gated behind try/except)
      3. per-turn jittered speed: N(0.92, 0.02²) clipped to [0.90, 0.94]
         — voice_settings passed per-turn rather than module-level constant
    speed=0.92 baseline kept; style lever gated since some models reject it.
  - Cache key now includes phoneme-substituted text (not raw text), so IPA
    tag changes bust cached audio naturally.

Public API:
    render_turns(turns, episode_dir) -> list[Path]
        Returns ordered list of per-turn mp3 paths.
"""

from __future__ import annotations

import hashlib
import os
import random
import time
from pathlib import Path
from typing import Any

from elevenlabs import ElevenLabs

from engine.pronunciation import apply_phoneme_substitution

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CACHE_DIR = _REPO_ROOT / "cache"

# ElevenLabs model — use multilingual v2 for quality; turbo as fallback
_MODEL_ID = "eleven_multilingual_v2"

# Base voice settings (v3 realism levers applied):
#   - stability: 0.40 (down from 0.60) → more expressive prosody variance
#   - style: 0.35 (up from 0.0) → emotional texture; gated in _build_settings()
#   - speed: 0.92 baseline, jittered ±0.02 per-turn in render_turns()
# Realism levers chosen: (1) stability, (2) style, (3) per-turn speed jitter.
# Lever (2) style is gated: some ElevenLabs models reject the field, so we
# try/except on the first call and omit it if the model rejects it.
_BASE_VOICE_SETTINGS: dict[str, Any] = {
    "stability": 0.40,
    "similarity_boost": 0.75,
    "style": 0.35,
    "use_speaker_boost": True,
    "speed": 0.92,  # baseline; jittered per-turn in render_turns()
}

# Speed jitter: N(0.92, 0.02²), clipped to [0.90, 0.94]
_SPEED_MEAN = 0.92
_SPEED_STD = 0.02
_SPEED_MIN = 0.90
_SPEED_MAX = 0.94

_MAX_RETRIES = 3
_RETRY_DELAY = 5  # seconds

# Module-level flag: if ElevenLabs rejects the `style` field, disable it
# after the first failure so subsequent turns don't waste retries.
_style_supported: bool = True


def _jittered_speed() -> float:
    """Sample per-turn speed from N(0.92, 0.02²) clipped to [0.90, 0.94]."""
    return max(_SPEED_MIN, min(_SPEED_MAX, random.gauss(_SPEED_MEAN, _SPEED_STD)))


def _build_settings(speed: float) -> dict[str, Any]:
    """Build per-turn voice settings with jittered speed and optional style."""
    global _style_supported
    settings = dict(_BASE_VOICE_SETTINGS)
    settings["speed"] = round(speed, 3)
    if not _style_supported:
        settings.pop("style", None)
    return settings


def _settings_fingerprint(settings: dict[str, Any]) -> str:
    """Stable short fingerprint of voice settings for cache-key namespacing."""
    items = sorted(settings.items())
    raw = ";".join(f"{k}={v}" for k, v in items)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def _cache_key(voice_id: str, text: str, settings: dict[str, Any]) -> str:
    fp = _settings_fingerprint(settings)
    raw = f"{voice_id}::{fp}::{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _get_voice_id(voice_label: str) -> str:
    if voice_label == "A":
        vid = os.environ.get("ELEVENLABS_VOICE_ID_SAI", "").strip()
        if not vid:
            raise RuntimeError("ELEVENLABS_VOICE_ID_SAI is not set")
        return vid
    else:
        vid = os.environ.get("ELEVENLABS_VOICE_STUDENT", "").strip()
        if not vid:
            raise RuntimeError("ELEVENLABS_VOICE_STUDENT is not set")
        return vid


def render_turns(
    turns: list[dict[str, Any]],
    episode_dir: Path,
) -> list[Path]:
    """
    Render each turn to mp3. Returns ordered list of paths.

    Each turn dict must have: {voice: 'A'|'B', text: str}
    Output filenames: turn_NNN_A.mp3 or turn_NNN_B.mp3 in episode_dir.
    Cache location: <repo>/cache/turn_<sha>.mp3

    v3: applies IPA phoneme substitution before TTS; uses per-turn jittered
    speed; lowers stability and raises style for realism.
    """
    global _style_supported

    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    episode_dir.mkdir(parents=True, exist_ok=True)

    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is not set")

    client = ElevenLabs(api_key=api_key)
    paths: list[Path] = []
    cached_count = 0
    new_count = 0

    for idx, turn in enumerate(turns):
        voice_label = turn["voice"]
        raw_text = turn["text"]
        voice_id = _get_voice_id(voice_label)

        # Apply IPA phoneme substitution — changes input text so cache
        # will naturally miss for v3 (different text → different sha).
        phoneme_text = apply_phoneme_substitution(raw_text)

        # Per-turn jittered speed (realism lever 3)
        speed = _jittered_speed()
        settings = _build_settings(speed)

        out_path = episode_dir / f"turn_{idx:03d}_{voice_label}.mp3"
        sha = _cache_key(voice_id, phoneme_text, settings)
        cache_path = _CACHE_DIR / f"turn_{sha}.mp3"

        if cache_path.exists():
            import shutil
            shutil.copy2(cache_path, out_path)
            cached_count += 1
            paths.append(out_path)
            print(f"  [tts] turn {idx:03d} voice={voice_label} speed={speed:.3f} — cache hit")
            continue

        # Cache miss — call ElevenLabs
        last_err = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                print(
                    f"  [tts] turn {idx:03d} voice={voice_label} speed={speed:.3f}"
                    f" — ElevenLabs call (attempt {attempt})"
                )
                audio_bytes = b"".join(
                    client.text_to_speech.convert(
                        voice_id=voice_id,
                        text=phoneme_text,
                        model_id=_MODEL_ID,
                        voice_settings=dict(settings),
                        output_format="mp3_44100_128",
                    )
                )
                cache_path.write_bytes(audio_bytes)
                out_path.write_bytes(audio_bytes)
                new_count += 1
                last_err = None
                break
            except Exception as e:
                err_str = str(e)
                # If `style` field rejected by model, disable it globally and retry
                if _style_supported and "style" in err_str.lower():
                    _style_supported = False
                    settings = _build_settings(speed)
                    print(f"  [tts] style field rejected by model — disabling for all turns")
                    continue
                last_err = e
                print(f"  [tts] turn {idx:03d} attempt {attempt} failed: {e}")
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_DELAY * attempt)

        if last_err is not None:
            _notify_tg_failure(idx, voice_label, last_err)
            raise RuntimeError(
                f"TTS failed for turn {idx} (voice={voice_label}) after {_MAX_RETRIES} attempts: {last_err}"
            )

        paths.append(out_path)

    print(f"[tts] done — {new_count} new calls, {cached_count} cache hits")
    return paths


def _notify_tg_failure(turn_idx: int, voice_label: str, err: Exception) -> None:
    """Best-effort Telegram alert when a turn fails after all retries."""
    chat_id = os.environ.get("PERSONAL_TG_CHAT_ID", "").strip()
    if not chat_id:
        return
    import subprocess
    tg_send = Path(__file__).resolve().parent.parent.parent / "factory" / "scripts" / "tg_send.sh"
    if not tg_send.exists():
        tg_send = Path.home() / "factory" / "scripts" / "tg_send.sh"
    if tg_send.exists():
        msg = f"dharma-podcast TTS FAILED: turn {turn_idx} voice={voice_label} — {err}"
        subprocess.run([str(tg_send), chat_id, msg], check=False)

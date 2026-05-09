"""
tts.py — ElevenLabs TTS for each dialogue turn.

Caches rendered turns by sha256(voice_id + text) to avoid re-billing.
Cache lives at <repo_root>/cache/turn_<sha>.mp3

Public API:
    render_turns(turns, episode_dir) -> list[Path]
        Returns ordered list of per-turn mp3 paths.
"""

from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path
from typing import Any

from elevenlabs import ElevenLabs

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CACHE_DIR = _REPO_ROOT / "cache"

# ElevenLabs model — use multilingual v2 for quality; turbo as fallback
_MODEL_ID = "eleven_multilingual_v2"

# Voice settings for a contemplative, grounded feel.
# speed=0.92 per soul.md §7.7 — slower than default to match the show's
# unhurried tone. Range supported by ElevenLabs is roughly 0.7–1.2.
_VOICE_SETTINGS = {
    "stability": 0.60,
    "similarity_boost": 0.75,
    "style": 0.0,
    "use_speaker_boost": True,
    "speed": 0.92,
}

_MAX_RETRIES = 3
_RETRY_DELAY = 5  # seconds


def _settings_fingerprint() -> str:
    """Stable short fingerprint of voice settings for cache-key namespacing.

    Including this in the cache key ensures a settings change (e.g. speed
    going from 1.0 → 0.92) busts cached audio so we don't return audio
    rendered at the wrong speed for the same text.
    """
    items = sorted(_VOICE_SETTINGS.items())
    raw = ";".join(f"{k}={v}" for k, v in items)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


_SETTINGS_FP = _settings_fingerprint()


def _cache_key(voice_id: str, text: str) -> str:
    raw = f"{voice_id}::{_SETTINGS_FP}::{text}"
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
    """
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
        text = turn["text"]
        voice_id = _get_voice_id(voice_label)

        out_path = episode_dir / f"turn_{idx:03d}_{voice_label}.mp3"
        sha = _cache_key(voice_id, text)
        cache_path = _CACHE_DIR / f"turn_{sha}.mp3"

        if cache_path.exists():
            # Cache hit — copy to episode dir
            import shutil
            shutil.copy2(cache_path, out_path)
            cached_count += 1
            paths.append(out_path)
            print(f"  [tts] turn {idx:03d} voice={voice_label} — cache hit")
            continue

        # Cache miss — call ElevenLabs
        last_err = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                print(f"  [tts] turn {idx:03d} voice={voice_label} — ElevenLabs call (attempt {attempt})")
                audio_bytes = b"".join(
                    client.text_to_speech.convert(
                        voice_id=voice_id,
                        text=text,
                        model_id=_MODEL_ID,
                        voice_settings=dict(_VOICE_SETTINGS),
                        output_format="mp3_44100_128",
                    )
                )
                cache_path.write_bytes(audio_bytes)
                out_path.write_bytes(audio_bytes)
                new_count += 1
                last_err = None
                break
            except Exception as e:
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

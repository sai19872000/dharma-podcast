"""
stitch.py — concatenate per-turn mp3s into a single raw episode mp3.

Uses ffmpeg concat demuxer (no re-encode) with jittered silence between turns.
Output: episodes/NNN/episode_NNN_raw.mp3

v3 change: fixed-width 250ms inter-turn silence replaced with jittered silence
sampled uniformly from {250, 350, 450, 550, 650} ms per gap.  Realism lever:
natural conversation doesn't have perfectly metronomic gaps.

v4 change: post-Student (Voice B) gaps are fixed at 350ms.  v3 jitter pool was
applied to ALL gaps, making post-Student pauses sometimes 450–650ms — too long
per Sai's v3 listen.  Post-Teacher (Voice A) gaps keep the jitter pool for
natural teacher pacing.  Voice label is inferred from the turn filename suffix
(e.g. "turn_001_B.mp3" → Voice B), so the stitch_episode() API is unchanged.

Public API:
    stitch_episode(turn_paths, output_path) -> Path
"""

from __future__ import annotations

import random
import subprocess
import tempfile
from pathlib import Path

# Pool of silence durations (ms). Used for post-Teacher (Voice A) gaps.
_SILENCE_POOL_MS: list[int] = [250, 350, 450, 550, 650]

# Fixed silence duration for post-Student (Voice B) gaps.
# v3 used the full jitter pool for all gaps; Sai's v3 listen found post-Student
# pauses (up to 650ms) too long. Restored to v2-equivalent ~300-400ms; 350ms
# is the midpoint and already in the pool so no new silence asset is needed.
_POST_STUDENT_GAP_MS: int = 350


def stitch_episode(
    turn_paths: list[Path],
    output_path: Path,
    silence_ms: int = 0,  # kept for API compatibility; ignored (jitter used instead)
) -> Path:
    """
    Concatenate turn mp3s into output_path using ffmpeg concat demuxer.

    Inter-turn silence is jittered: a value is chosen randomly from
    _SILENCE_POOL_MS [250, 350, 450, 550, 650] ms per gap.
    The `silence_ms` parameter is accepted for API compatibility but ignored.

    Returns output_path.
    """
    if not turn_paths:
        raise ValueError("No turn paths provided to stitch_episode")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Pre-generate the silence pool into episode_dir
    silence_dir = turn_paths[0].parent
    silence_paths: dict[int, Path] = {
        ms: _generate_silence(ms, silence_dir) for ms in _SILENCE_POOL_MS
    }

    # Interleave: for each gap between turns, pick silence duration based on
    # the voice of the preceding turn.
    #   - Post-Voice B (Student): fixed _POST_STUDENT_GAP_MS (350ms) — v3 jitter
    #     was too long here per Sai's listen; restored to v2 ~300-400ms timing.
    #   - Post-Voice A (Teacher): jitter pool {250..650} — unchanged from v3.
    # Voice label is read from the filename suffix: "turn_001_B.mp3" → 'B'.
    ordered: list[Path] = []
    for i, p in enumerate(turn_paths):
        ordered.append(p)
        if i < len(turn_paths) - 1:
            # Extract voice label from filename (e.g. turn_001_B.mp3 → 'B')
            voice_label = p.stem.rsplit('_', 1)[-1]
            if voice_label == 'B':
                gap_ms = _POST_STUDENT_GAP_MS
            else:
                gap_ms = random.choice(_SILENCE_POOL_MS)
            ordered.append(silence_paths[gap_ms])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        concat_list = f.name
        for p in ordered:
            f.write(f"file '{p.resolve()}'\n")

    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list,
            "-c", "copy",
            str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg concat failed:\n{result.stderr}")
    finally:
        Path(concat_list).unlink(missing_ok=True)

    print(f"[stitch] written: {output_path} ({len(turn_paths)} turns, post-A jittered / post-B fixed {_POST_STUDENT_GAP_MS}ms)")
    return output_path


def _generate_silence(ms: int, output_dir: Path) -> Path:
    """Generate (or reuse cached) a short silent mp3 segment of `ms` milliseconds."""
    silence_path = output_dir / f"_silence_{ms}ms.mp3"
    if silence_path.exists():
        return silence_path

    duration = ms / 1000.0
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "anullsrc=r=44100:cl=mono",
        "-t", str(duration),
        "-q:a", "9",
        "-acodec", "libmp3lame",
        str(silence_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg silence gen failed:\n{result.stderr}")
    return silence_path

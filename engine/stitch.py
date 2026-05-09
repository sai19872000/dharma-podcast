"""
stitch.py — concatenate per-turn mp3s into a single raw episode mp3.

Uses ffmpeg concat demuxer (no re-encode) with jittered silence between turns.
Output: episodes/NNN/episode_NNN_raw.mp3

v3 change: fixed-width 250ms inter-turn silence replaced with jittered silence
sampled uniformly from {250, 350, 450, 550, 650} ms per gap.  Realism lever:
natural conversation doesn't have perfectly metronomic gaps.

Public API:
    stitch_episode(turn_paths, output_path) -> Path
"""

from __future__ import annotations

import random
import subprocess
import tempfile
from pathlib import Path

# Pool of silence durations (ms). One value is chosen at random per gap.
_SILENCE_POOL_MS: list[int] = [250, 350, 450, 550, 650]


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

    # Interleave: for each gap between turns, pick a random silence duration
    ordered: list[Path] = []
    for i, p in enumerate(turn_paths):
        ordered.append(p)
        if i < len(turn_paths) - 1:
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

    print(f"[stitch] written: {output_path} ({len(turn_paths)} turns, jittered gaps)")
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

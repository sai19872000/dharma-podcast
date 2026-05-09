"""
stitch.py — concatenate per-turn mp3s into a single raw episode mp3.

Uses ffmpeg concat demuxer (no re-encode) with optional 250ms silence between turns.
Output: episodes/NNN/episode_NNN_raw.mp3

Public API:
    stitch_episode(turn_paths, output_path, silence_ms=250) -> Path
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def stitch_episode(
    turn_paths: list[Path],
    output_path: Path,
    silence_ms: int = 250,
) -> Path:
    """
    Concatenate turn mp3s into output_path using ffmpeg concat demuxer.

    silence_ms: milliseconds of silence to insert between turns (0 to disable).
    Returns output_path.
    """
    if not turn_paths:
        raise ValueError("No turn paths provided to stitch_episode")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build the input file list for ffmpeg concat demuxer
    # If silence_ms > 0, generate a silent segment and interleave
    if silence_ms > 0:
        silence_path = _generate_silence(silence_ms, turn_paths[0].parent)
        ordered: list[Path] = []
        for i, p in enumerate(turn_paths):
            ordered.append(p)
            if i < len(turn_paths) - 1:
                ordered.append(silence_path)
    else:
        ordered = list(turn_paths)

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

    print(f"[stitch] written: {output_path} ({len(turn_paths)} turns)")
    return output_path


def _generate_silence(ms: int, output_dir: Path) -> Path:
    """Generate a short silent mp3 segment."""
    silence_path = output_dir / f"_silence_{ms}ms.mp3"
    if silence_path.exists():
        return silence_path

    duration = ms / 1000.0
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"anullsrc=r=44100:cl=mono",
        "-t", str(duration),
        "-q:a", "9",
        "-acodec", "libmp3lame",
        str(silence_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg silence gen failed:\n{result.stderr}")
    return silence_path

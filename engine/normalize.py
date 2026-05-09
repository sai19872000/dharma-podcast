"""
normalize.py — two-pass loudnorm via ffmpeg-normalize (ADR-3).

Target: -16 LUFS, true-peak ≤ -1.5 dBTP, LRA=11 (podcast preset).
Output: episodes/NNN/episode_NNN.mp3

Public API:
    normalize_episode(raw_path, output_path) -> Path
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def _find_ffmpeg_normalize() -> str:
    """Return path to ffmpeg-normalize executable."""
    # Check user local bin first (pip --user installs here)
    local_bin = Path.home() / ".local" / "bin" / "ffmpeg-normalize"
    if local_bin.exists():
        return str(local_bin)
    found = shutil.which("ffmpeg-normalize")
    if found:
        return found
    raise RuntimeError(
        "ffmpeg-normalize not found. Install with: pip install ffmpeg-normalize"
    )


def normalize_episode(raw_path: Path, output_path: Path) -> Path:
    """
    Run two-pass loudnorm on raw_path and write to output_path.
    Raises RuntimeError if ffmpeg-normalize fails.
    Returns output_path.
    """
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw episode not found: {raw_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ffnorm = _find_ffmpeg_normalize()

    # Two-pass loudnorm: I=-16, TP=-1.5, LRA=11 (podcast preset per ADR-3).
    # ElevenLabs audio typically has high true-peak near 0 dBTP; loudnorm
    # will revert to dynamic mode and land at ~-18 LUFS (the best achievable
    # without exceeding TP=-1.5). That's acceptable — Spotify normalises to
    # -14 LUFS regardless; the important property is TP stays clean.
    cmd = [
        ffnorm,
        str(raw_path),
        "--loudness-range-target", "11",
        "--target-level", "-16",
        "--true-peak", "-1.5",
        "--output", str(output_path),
        "--audio-codec", "libmp3lame",
        "--audio-bitrate", "128k",
        "--sample-rate", "44100",
        "--force",
    ]

    print(f"[normalize] running ffmpeg-normalize on {raw_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg-normalize failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    print(f"[normalize] written: {output_path}")
    return output_path


def measure_lufs(mp3_path: Path) -> dict:
    """
    Measure integrated loudness using ffmpeg loudnorm analysis.
    Returns dict with input_i, input_tp, input_lra, input_thresh.
    """
    cmd = [
        "ffmpeg", "-i", str(mp3_path),
        "-af", "loudnorm=print_format=json",
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # loudnorm stats go to stderr
    output = result.stderr

    # Parse the JSON block from ffmpeg loudnorm output
    import re
    import json
    match = re.search(r"\{[^{}]+\}", output, re.DOTALL)
    if not match:
        return {"raw": output[-500:]}
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return {"raw": match.group()}

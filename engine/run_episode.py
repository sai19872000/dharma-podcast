"""
run_episode.py — top-level orchestrator for a single episode run.

Usage:
    python -m engine.run_episode <concept_slug> <episode_no>

Runs: corpus_loader → script_gen → tts → stitch → normalize → artifacts → tg_notify
Does NOT call publish.py for Episode 001 (HALT per ADR-5).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent


def _step(name: str) -> None:
    print(f"\n{'='*60}")
    print(f"  STEP: {name}")
    print(f"{'='*60}")


def run_episode(concept_slug: str, episode_no: int) -> None:
    from engine.corpus_loader import load_corpus
    from engine.concept_queue import mark_drafted
    from engine.script_gen import generate_script, save_script
    from engine.tts import render_turns
    from engine.stitch import stitch_episode
    from engine.normalize import normalize_episode, measure_lufs
    from engine.artifacts import write_artifacts
    from engine.tg_notify import notify

    episode_dir = _REPO_ROOT / "episodes" / f"{episode_no:03d}"
    episode_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Load corpus
    _step("1/7 corpus_loader")
    corpus = load_corpus(concept_slug)
    print(f"  Loaded {len(corpus)} corpus entries for '{concept_slug}'")
    quotes = [e for e in corpus if e["license"] != "PARAPHRASE"]
    paraphrases = [e for e in corpus if e["license"] == "PARAPHRASE"]
    print(f"  {len(quotes)} PD/CC0 quotes + {len(paraphrases)} paraphrase context entries")

    # Build concept dict for script_gen (read from queue for metadata)
    queue_path = _REPO_ROOT / "concept_queue.json"
    with queue_path.open(encoding="utf-8") as fh:
        queue_data = json.load(fh)
    concept = next(
        (c for c in queue_data["concepts"] if c["slug"] == concept_slug),
        {"slug": concept_slug, "scheduled_episode_no": episode_no},
    )
    concept["scheduled_episode_no"] = episode_no

    # Step 2: Generate script
    _step("2/7 script_gen (Claude claude-opus-4-6)")
    script_path = episode_dir / "script.json"
    if script_path.exists():
        print("  script.json already exists — loading cached script")
        with script_path.open(encoding="utf-8") as fh:
            script = json.load(fh)
    else:
        script = generate_script(concept, episode_no, corpus)
        save_script(script, episode_dir)
        print(f"  Generated {len(script['turns'])} turns, {len(script.get('citations', []))} citations")

    # Mark as drafted in concept queue
    try:
        mark_drafted(concept_slug, episode_no)
        print(f"  Marked '{concept_slug}' as drafted in concept_queue.json")
    except Exception as e:
        print(f"  NOTE: mark_drafted skipped ({e})")

    # Step 3: TTS
    _step("3/7 tts (ElevenLabs)")
    turn_paths = render_turns(script["turns"], episode_dir)
    print(f"  Rendered {len(turn_paths)} turn audio files")

    # Step 4: Stitch
    _step("4/7 stitch")
    raw_mp3 = episode_dir / f"episode_{episode_no:03d}_raw.mp3"
    stitch_episode(turn_paths, raw_mp3)

    # Step 5: Normalize
    _step("5/7 normalize (-16 LUFS)")
    final_mp3 = episode_dir / f"episode_{episode_no:03d}.mp3"
    normalize_episode(raw_mp3, final_mp3)
    lufs_data = measure_lufs(final_mp3)
    print(f"  LUFS measurement: {lufs_data}")

    # Step 6: Artifacts
    _step("6/7 artifacts")
    artifact_paths = write_artifacts(script, episode_dir, final_mp3)

    # Compute duration string for Telegram message
    import subprocess
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(final_mp3)],
            capture_output=True, text=True, check=True,
        )
        secs = float(result.stdout.strip())
        m, s = divmod(int(secs), 60)
        duration_str = f"{m}m{s:02d}s"
    except Exception:
        duration_str = "unknown"

    # Step 7: Telegram notification
    _step("7/7 tg_notify")
    notify(episode_no, episode_dir, final_mp3, script, duration_str)

    # Summary
    print(f"\n{'='*60}")
    print(f"  Episode {episode_no:03d} complete!")
    print(f"  Audio:      {final_mp3}")
    print(f"  Duration:   {duration_str}")
    print(f"  LUFS:       {lufs_data.get('input_i', lufs_data.get('output_i', 'N/A'))}")
    print(f"  Show notes: {artifact_paths['show_notes'].name}")
    print(f"  Citations:  {artifact_paths['citations'].name}")
    print(f"  Pacing:     {artifact_paths['pacing'].name}")
    print(f"\n  HALT — awaiting Sai's approval before RSS publish.")
    print(f"  Set DHARMA_EP001_APPROVED=1 and run publish.py to release.")
    print(f"{'='*60}\n")


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: python -m engine.run_episode <concept_slug> <episode_no>")
        sys.exit(1)
    concept_slug = sys.argv[1]
    try:
        episode_no = int(sys.argv[2])
    except ValueError:
        print(f"episode_no must be an integer, got: {sys.argv[2]}")
        sys.exit(1)
    run_episode(concept_slug, episode_no)


if __name__ == "__main__":
    main()

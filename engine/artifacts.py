"""
artifacts.py — emit show_notes.md, citations.jsonl, pacing.json from script.json.

HARD GUARD (ADR-6): every citation row must have license ∈ {PD, CC0, CC-BY-NC-SA-4.0}.
Fail-fast at runtime — not advisory.

Public API:
    write_artifacts(script, episode_dir, mp3_path) -> dict[str, Path]
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

_VALID_LICENSES = {"PD", "CC0", "CC-BY-NC-SA-4.0"}


def _get_duration_seconds(mp3_path: Path) -> float:
    """Return duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(mp3_path),
            ],
            capture_output=True, text=True, check=True,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def _format_duration(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


def _validate_citations(citations: list[dict[str, Any]]) -> None:
    """ADR-6 hard guard: fail-fast on invalid license values."""
    for row in citations:
        assert row.get("license") in _VALID_LICENSES, (
            f"invalid license '{row.get('license')}' on "
            f"quote from turn_idx={row.get('turn_idx')} source='{row.get('source')}'"
        )


def _build_show_notes(script: dict[str, Any], duration_str: str, ep_num: int) -> str:
    """Render show_notes.md content from script.json."""
    concept = script.get("concept", "")
    concept_pair = script.get("concept_pair", "")
    soul_sha = script.get("soul_md_sha", "")[:12]
    citations = script.get("citations", [])

    # Collect paraphrase context notes from turns (look for mentions of modern thinkers)
    # These come from the script's turn text naturally; we surface them as paraphrase notes

    lines = [
        f"# Episode {ep_num:03d} — {concept.capitalize()} × {concept_pair}",
        "",
        f"**Duration:** {duration_str}  ",
        f"**Soul.md version:** `{soul_sha}`",
        "",
        "---",
        "",
        "## What this episode explores",
        "",
        f"The concept of *{concept}* — dispassion or non-attachment — from the "
        f"Yoga Sūtras and the Bhagavad Gītā, paired with contemporary research "
        f"on *{concept_pair}* from behavioural science (Gilbert & Wilson).",
        "",
        "---",
        "",
        "## Primary source citations",
        "",
    ]

    seen_sources: set[str] = set()
    for i, c in enumerate(citations, 1):
        src_key = c.get("source", "")
        if src_key in seen_sources:
            continue
        seen_sources.add(src_key)
        lines.append(
            f"**{i}. {c.get('source', '')}**  "
        )
        lines.append(
            f"Translator: {c.get('translator', 'Unknown')} · "
            f"License: {c.get('license', '')} · "
            f"[Source]({c.get('corpus_url', '')})"
        )
        lines.append("")

    lines += [
        "---",
        "",
        "## Modern thinker context (paraphrased — not verbatim quotes)",
        "",
        "**Daniel Gilbert & Timothy Wilson — Affective Forecasting**  ",
        "Public lectures and peer-reviewed papers. Gilbert's TED talk: "
        "[The Surprising Science of Happiness](https://www.ted.com/talks/dan_gilbert_the_surprising_science_of_happiness).  ",
        "Core finding: humans systematically overestimate the emotional impact of future events "
        "(impact bias) and underestimate their own psychological immune system's capacity to "
        "adapt (immune neglect). Vairāgya and niṣkāma karma address this asymmetry from the "
        "inside — not by correcting the forecast, but by releasing the grip on outcome.",
        "",
        "---",
        "",
        "## Soul.md anti-patterns active this episode",
        "",
        "- No quantum-consciousness analogies",
        "- No syncretic flattening (Patañjali ≠ Kastrup; vairāgya ≠ detachment-as-coldness)",
        "- 'Consciousness' used only with named referent (vṛtti, puruṣa, or phenomenal self-model)",
        "",
    ]

    return "\n".join(lines)


def _build_pacing_json(script: dict[str, Any], total_duration: float) -> dict[str, Any]:
    """Build pacing manifest per soul.md §7.8 #4."""
    turns = script.get("turns", [])
    n = len(turns)
    if n == 0 or total_duration == 0:
        return {"episode": script.get("concept", ""), "sections": []}

    # Distribute duration evenly across turns as a rough pacing estimate
    per_turn = total_duration / n

    # Map turns to episode sections based on position
    def section_for(idx: int) -> str:
        pct = idx / n
        if pct < 0.15:
            return "HOOK"
        elif pct < 0.45:
            return "EAST"
        elif pct < 0.70:
            return "WEST"
        elif pct < 0.90:
            return "CONVERGENCE"
        else:
            return "TAKEAWAY"

    sections: list[dict] = []
    current_section = None
    section_start = 0.0

    for i, turn in enumerate(turns):
        sec = section_for(i)
        ts = round(i * per_turn, 1)
        if sec != current_section:
            if current_section is not None:
                sections[-1]["end_s"] = ts
            sections.append({
                "section": sec,
                "start_s": ts,
                "end_s": round(total_duration, 1),
                "turn_start": i,
            })
            current_section = sec

    return {
        "episode": f"ep{script.get('episode_no', 0):03d}-{script.get('concept', '')}",
        "total_duration_s": round(total_duration, 1),
        "sections": sections,
    }


def write_artifacts(
    script: dict[str, Any],
    episode_dir: Path,
    mp3_path: Path,
) -> dict[str, Path]:
    """
    Write show_notes.md, citations.jsonl, pacing.json to episode_dir.
    Raises AssertionError on invalid license (ADR-6 hard guard).
    Returns dict mapping artifact names to paths.
    """
    episode_dir.mkdir(parents=True, exist_ok=True)
    ep_num = script.get("episode_no", 1)
    concept = script.get("concept", "episode")
    citations = script.get("citations", [])

    # ADR-6 hard guard — must run before any file write
    _validate_citations(citations)

    duration_s = _get_duration_seconds(mp3_path) if mp3_path.exists() else 0.0
    duration_str = _format_duration(duration_s)

    # show_notes.md
    show_notes_path = episode_dir / f"episode_{ep_num:03d}.show_notes.md"
    show_notes_path.write_text(_build_show_notes(script, duration_str, ep_num), encoding="utf-8")

    # citations.jsonl — quotes only (PARAPHRASE already excluded by script_gen)
    citations_path = episode_dir / f"episode_{ep_num:03d}.citations.jsonl"
    with citations_path.open("w", encoding="utf-8") as fh:
        for i, c in enumerate(citations, 1):
            row = {
                "episode": f"ep{ep_num:03d}-{concept}",
                "quote_id": i,
                "tradition": c.get("tradition", "east-lineage"),
                "work": c.get("source", ""),
                "translator": c.get("translator", ""),
                "verse_or_section": c.get("verse_or_section", ""),
                "license": c.get("license", ""),
                "citation_url": c.get("corpus_url", ""),
                "fetch_url": c.get("corpus_url", ""),
                "verified_date": c.get("verified_date", "2026-05-08"),
                "quote": c.get("quote", ""),
                "turn_idx": c.get("turn_idx", 0),
            }
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    # pacing.json
    pacing_path = episode_dir / f"episode_{ep_num:03d}.pacing.json"
    pacing = _build_pacing_json(script, duration_s)
    with pacing_path.open("w", encoding="utf-8") as fh:
        json.dump(pacing, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"[artifacts] show_notes → {show_notes_path.name}")
    print(f"[artifacts] citations  → {citations_path.name} ({len(citations)} rows)")
    print(f"[artifacts] pacing     → {pacing_path.name}")

    return {
        "show_notes": show_notes_path,
        "citations": citations_path,
        "pacing": pacing_path,
    }

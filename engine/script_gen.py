"""
script_gen.py — generate a two-voice dialogue script from soul.md + corpus excerpts.

Calls Claude claude-opus-4-6 with soul.md as the system-prompt prefix (ADR-1 + ADR-7).
Emits script.json per the architect spec API contract.

Public API:
    generate_script(concept_slug, episode_no, corpus_entries) -> dict
    save_script(script, output_dir) -> Path
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import anthropic

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SOUL_MD = _REPO_ROOT / "soul.md"


def _soul_md_text() -> str:
    return _SOUL_MD.read_text(encoding="utf-8")


def _soul_md_sha() -> str:
    return hashlib.sha256(_SOUL_MD.read_bytes()).hexdigest()


def _build_user_prompt(concept: dict[str, Any], corpus_entries: list[dict[str, Any]]) -> str:
    slug = concept["slug"]
    sanskrit = concept.get("sanskrit") or concept.get("pali") or ""
    english = concept.get("english", "")
    paired_concept = concept.get("paired_modern_concept", "")
    paired_thinker = concept.get("paired_thinker", "")
    episode_no = concept.get("scheduled_episode_no", "?")

    # Separate PD/CC0 quotes from paraphrase context
    quotes = [e for e in corpus_entries if e["license"] != "PARAPHRASE"]
    paraphrases = [e for e in corpus_entries if e["license"] == "PARAPHRASE"]

    corpus_block = ""
    for i, q in enumerate(quotes):
        corpus_block += (
            f"\n--- QUOTE {i+1} ---\n"
            f"Source: {q['source']}\n"
            f"Tradition: {q.get('tradition','')}\n"
            f"Translator: {q.get('translator','')}\n"
            f"License: {q['license']}\n"
            f"Corpus URL: {q.get('corpus_url','')}\n"
            f"Verse: {q.get('verse_or_section','')}\n\n"
            f"{q['quote']}\n"
        )

    paraphrase_block = ""
    for p in paraphrases:
        paraphrase_block += (
            f"\n--- MODERN CONTEXT (paraphrase, DO NOT quote verbatim) ---\n"
            f"Work: {p['source']}\n"
            f"URL: {p.get('corpus_url','')}\n\n"
            f"{p['quote']}\n"
        )

    return f"""Episode {episode_no}: {slug} ({sanskrit}) — "{english}"
East concept: {slug} ({sanskrit})
Modern parallel: {paired_concept} — key thinkers: {paired_thinker}

## Corpus excerpts (direct PD/CC0 quotes — cite these verbatim)
{corpus_block}

## Modern-thinker context (paraphrase only — do NOT quote verbatim from copyrighted books)
{paraphrase_block}

---

Write a two-voice dialogue script following the episode structure from soul.md §7:
- COLD OPEN (Voice A solo, ~15–20s) → HOOK (Voice B) → EAST PRIMARY SOURCE → WEST PARALLEL → CONVERGENCE + DIVERGENCE → SINGLE TAKEAWAY → CLOSING (Voice A solo, ~12–18s)
- The FIRST turn MUST be a Voice A cold-open per soul.md §7.0: one sentence naming the show ("This is Dharma — two voices, one careful question per episode."), then one or two sentences naming THIS episode's concept pair. End the cold-open turn with `<break time="2.5s" />`. Then Voice B's hook follows.
- 13–19 dialogue turns PLUS the cold open PLUS the closing turn = 15–21 turns total.
- The LAST turn MUST be a Voice A solo closing (~12–18s): a contemplative bow, a brief thanks for listening, and optionally one line teasing the next episode's question. Mirror the cold-open tone — unhurried, specific, not a summary. End the closing with `<break time="1.5s" />`.
- Voice A = teacher. Voice B = student.
- 5–8 minutes of audio target. Pace assumes TTS speed=0.92 (slower than default).
- Each turn 1–4 sentences. Dialogue, not monologue.
- Embed at least one direct quote from the PD/CC0 corpus (Voice A reads it).
- Modern thinkers paraphrased only — never lifted verbatim from books.
- The penultimate Voice A turn carries the precise takeaway (not a moral lesson, a reframe). The closing is a separate, final Voice A turn.

## Sanskrit / Pāli term density (HARD RULE — soul.md §1.2 binding)
- Each Sanskrit/Pāli concept term is introduced **once** with an inline English gloss using an em-dash, e.g. `vairāgya — non-attachment`, `niṣkāma karma — action without grasping at outcome`, `sthitaprajña — the one of steady insight`.
- After the introduction, **continue in English only**. Do NOT repeat the Sanskrit/Pāli term across the rest of the episode. At most ONE re-anchor of the original term is allowed if a turn truly needs to point back at the lineage.
- Across the whole script, each Sanskrit/Pāli concept term appears at most TWICE total (introduction + at most one re-anchor).
- Proper names of works, figures, and verses are exempt: Bhagavad Gītā, Yoga Sūtras, Mahābhārata, Patañjali, Krishna, Buddha, Soṇa, AN 5.30 — these stay as-is, do NOT count toward the density cap.
- Verbatim quotes from the corpus are exempt — the quote stays exactly as the translator wrote it. The density rule applies only to the dialogue around the quote.

## Pause / pacing directives (encode these inline) — apply to BOTH voices
- Use ElevenLabs inline break syntax in turn text: `<break time="2.5s" />` after a hook question or after the cold open; `<break time="1.5s" />` after a primary-source verbatim quote or at the close of the closing turn; `<break time="1.0s" />` between two sentences within a turn when the second clause is a reframe of the first.
- Voice B turns specifically: add `<break time="1.0s" />` after Voice B's questions land (when the question is directed at the teacher and Voice B is waiting for an answer). Voice B should also use ellipses for within-sentence pauses when trailing off or thinking aloud.
- Use ellipses `…` (a single Unicode ellipsis character, not three periods) for short within-sentence beats where the speaker is leaving room to think — roughly 400 ms. Both voices use this.
- Do NOT use SSML wrappers like `<speak>…</speak>`. Only inline `<break time="X.Xs" />` and `…` are supported by the TTS path.

Respond with ONLY a JSON object — no markdown fences, no preamble:
{{
  "episode_no": {episode_no},
  "concept": "{slug}",
  "concept_pair": "{paired_concept}",
  "turns": [
    {{"voice": "A", "text": "..."}},
    {{"voice": "B", "text": "..."}},
    ...
  ],
  "citations": [
    {{
      "turn_idx": <int>,
      "quote": "<exact verbatim quote used in that turn>",
      "source": "<human-readable title, e.g. Bhagavad Gita 2.47>",
      "translator": "<translator name>",
      "license": "<PD|CC0|CC-BY-NC-SA-4.0>",
      "corpus_url": "<citation surface URL>",
      "verse_or_section": "<verse or section ref>",
      "tradition": "<east-lineage|west-thinker>",
      "verified_date": "2026-05-08"
    }}
  ]
}}

Rules for citations array:
- Include ONLY verbatim quotes from PD/CC0/CC-BY-NC-SA-4.0 sources.
- Do NOT include paraphrases of modern thinkers.
- license MUST be one of: PD, CC0, CC-BY-NC-SA-4.0
- Every quote embedded in a turn must appear in citations with its turn_idx.
"""


def generate_script(
    concept: dict[str, Any],
    episode_no: int,
    corpus_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Call Claude claude-opus-4-6 with soul.md as system prefix to generate script.json content.
    Returns the parsed script dict (not yet saved to disk).
    """
    soul_text = _soul_md_text()
    sha = _soul_md_sha()

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    user_prompt = _build_user_prompt(concept, corpus_entries)

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=soul_text,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown fences if the model added them despite instructions
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

    script = json.loads(raw)
    script["soul_md_sha"] = sha
    script["episode_no"] = episode_no

    return script


def save_script(script: dict[str, Any], output_dir: Path) -> Path:
    """Write script.json to output_dir. Returns the path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "script.json"
    with out.open("w", encoding="utf-8") as fh:
        json.dump(script, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return out

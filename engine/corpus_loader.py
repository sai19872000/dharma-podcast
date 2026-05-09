"""
corpus_loader.py — offline corpus loader for the dharma-podcast engine.

load_corpus(concept_slug) -> list[dict]

Each dict matches the soul.md §5.2 citation schema:
    {
        quote:          str  — full text of the staged excerpt
        source:         str  — human-readable title (e.g. "Bhagavad Gita 2.47–2.71")
        translator:     str | None
        license:        str  — "PD" | "CC0" | "CC-BY-NC-SA-4.0" | "PARAPHRASE"
        corpus_url:     str  — citation surface URL (for show notes)
        fetch_url:      str | None  — engine-fetch URL (archive.org / GitHub raw)
        verse_or_section: str
        tradition:      str  — "east-lineage" | "west-thinker"
        verified_date:  str  — YYYY-MM-DD
    }

Design notes:
- NO live URL fetch at run time. All text is pre-staged into corpus/<slug>/*.txt
  and corpus/<slug>/*.md files. The manifest.json provides license + citation
  metadata. (ADR: offline corpus avoids rate-limits and keeps the engine
  deterministic across runs.)
- PARAPHRASE entries (license="PARAPHRASE") are returned by this function so
  that script_gen.py can use them as modern-thread context. They must NOT be
  written to citations.jsonl by artifacts.py (soul.md §5.2 + ADR-6).
- The corpus directory is resolved relative to this file's location:
  <repo_root>/corpus/<slug>/
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Repo root is one level above this file (engine/).
_REPO_ROOT = Path(__file__).resolve().parent.parent
_CORPUS_ROOT = _REPO_ROOT / "corpus"

VALID_LICENSES = {"PD", "CC0", "CC-BY-NC-SA-4.0", "PARAPHRASE"}


def _read_text(path: Path) -> str:
    """Read a text file, returning its content stripped of leading/trailing whitespace."""
    return path.read_text(encoding="utf-8").strip()


def _load_manifest(concept_slug: str) -> dict[str, Any]:
    """Load and return the manifest.json for a concept slug."""
    manifest_path = _CORPUS_ROOT / concept_slug / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"No manifest found for concept '{concept_slug}' at {manifest_path}"
        )
    with manifest_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_corpus(concept_slug: str) -> list[dict[str, Any]]:
    """
    Load all staged corpus excerpts for a concept slug.

    Returns a list of dicts, one per source in the manifest.  Each dict
    contains the full text of the excerpt (``quote`` key) plus metadata
    from manifest.json.

    PARAPHRASE entries are included so that script_gen.py can use them as
    modern-thread context.  The caller (artifacts.py) must filter them out
    before writing citations.jsonl.

    Raises:
        FileNotFoundError: if the manifest or a referenced text file is missing.
        ValueError: if a manifest entry has an unrecognised license value.
    """
    manifest = _load_manifest(concept_slug)
    concept_dir = _CORPUS_ROOT / concept_slug
    results: list[dict[str, Any]] = []

    for source in manifest.get("sources", []):
        filename: str = source["file"]
        license_val: str = source.get("license", "")

        # Guard: reject unknown license values early so callers get a clear error.
        if license_val not in VALID_LICENSES:
            raise ValueError(
                f"Unknown license '{license_val}' in manifest for {concept_slug}/{filename}. "
                f"Expected one of: {sorted(VALID_LICENSES)}"
            )

        file_path = concept_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(
                f"Corpus file missing: {file_path}  "
                f"(referenced by {concept_slug}/manifest.json)"
            )

        quote = _read_text(file_path)

        results.append(
            {
                "quote": quote,
                "source": source.get("work", filename),
                "translator": source.get("translator"),
                "license": license_val,
                "corpus_url": source.get("citation_url", ""),
                "fetch_url": source.get("fetch_url"),
                "verse_or_section": source.get("verse_or_section", ""),
                "tradition": source.get("tradition", ""),
                "verified_date": source.get(
                    "verified_date", manifest.get("verified_date", "")
                ),
            }
        )

    return results


def load_quotable_corpus(concept_slug: str) -> list[dict[str, Any]]:
    """
    Like load_corpus() but filters out PARAPHRASE entries.

    Use this when building the citation ledger (citations.jsonl) to ensure
    only PD/CC0/CC-BY-NC-SA-4.0 entries are included (soul.md §5.2 + ADR-6).
    """
    return [e for e in load_corpus(concept_slug) if e["license"] != "PARAPHRASE"]


def load_context_corpus(concept_slug: str) -> list[dict[str, Any]]:
    """
    Return only PARAPHRASE entries (modern-thread context for script_gen.py).

    These are notes on copyrighted modern thinkers — not verbatim quotes,
    so they don't belong in citations.jsonl but are valid context for the
    script-generation prompt.
    """
    return [e for e in load_corpus(concept_slug) if e["license"] == "PARAPHRASE"]


_RECOGNIZED_CORPUS_HOSTS = {
    "suttacentral.net",
    "raw.githubusercontent.com",
    "en.wikisource.org",
    "archive.org",
    "sacred-texts.com",
    "gretil.sub.uni-goettingen.de",
}


def is_recognized_host(url: str | None) -> bool:
    """
    Return True if the URL's host is a recognised PD/CC0 corpus host.

    Used by tests to assert that every fetch_url points at a vetted source.
    """
    if not url:
        return False
    from urllib.parse import urlparse
    host = urlparse(url).netloc.lower()
    return any(host == h or host.endswith("." + h) for h in _RECOGNIZED_CORPUS_HOSTS)

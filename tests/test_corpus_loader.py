"""
tests/test_corpus_loader.py

Light corpus-loader tests (pytest).

Run from the repo root:
    pytest tests/test_corpus_loader.py -v

These tests validate the staged vairagya corpus and the corpus_loader contract
without making any network calls.
"""

import pytest
from pathlib import Path
from engine.corpus_loader import (
    load_corpus,
    load_quotable_corpus,
    load_context_corpus,
    is_recognized_host,
    VALID_LICENSES,
)

CONCEPT = "vairagya"
REQUIRED_KEYS = {
    "quote",
    "source",
    "translator",
    "license",
    "corpus_url",
    "fetch_url",
    "verse_or_section",
    "tradition",
    "verified_date",
}
VALID_TRADITIONS = {"east-lineage", "west-thinker"}
QUOTABLE_LICENSES = {"PD", "CC0", "CC-BY-NC-SA-4.0"}


# ---------------------------------------------------------------------------
# Basic load tests
# ---------------------------------------------------------------------------


def test_load_corpus_returns_list():
    entries = load_corpus(CONCEPT)
    assert isinstance(entries, list), "load_corpus must return a list"
    assert len(entries) > 0, "corpus must not be empty"


def test_all_entries_have_required_keys():
    for entry in load_corpus(CONCEPT):
        missing = REQUIRED_KEYS - entry.keys()
        assert not missing, f"Entry missing keys {missing}: {entry.get('source')}"


def test_east_lineage_minimum_three():
    """load_corpus('vairagya') must return ≥3 east-lineage entries."""
    entries = load_corpus(CONCEPT)
    east = [e for e in entries if e["tradition"] == "east-lineage"]
    assert len(east) >= 3, (
        f"Expected ≥3 east-lineage entries, got {len(east)}: "
        f"{[e['source'] for e in east]}"
    )


def test_all_licenses_valid():
    """Every entry's license must be in the allowed set."""
    for entry in load_corpus(CONCEPT):
        assert entry["license"] in VALID_LICENSES, (
            f"Invalid license '{entry['license']}' on entry: {entry['source']}"
        )


def test_quotable_licenses_are_pd_or_cc0():
    """
    Quotable corpus entries must have license ∈ {PD, CC0, CC-BY-NC-SA-4.0}.
    PARAPHRASE entries are excluded from the quotable corpus.
    """
    for entry in load_quotable_corpus(CONCEPT):
        assert entry["license"] in QUOTABLE_LICENSES, (
            f"Unexpected license in quotable corpus: '{entry['license']}' "
            f"for {entry['source']}"
        )


# ---------------------------------------------------------------------------
# Content / non-empty tests
# ---------------------------------------------------------------------------


def test_all_quotes_non_empty():
    for entry in load_corpus(CONCEPT):
        assert entry["quote"].strip(), (
            f"Empty quote for entry: {entry['source']}"
        )


def test_all_sources_non_empty():
    for entry in load_corpus(CONCEPT):
        assert entry["source"].strip(), "Entry has empty source field"


def test_traditions_are_valid():
    for entry in load_corpus(CONCEPT):
        assert entry["tradition"] in VALID_TRADITIONS, (
            f"Invalid tradition '{entry['tradition']}' for {entry['source']}"
        )


# ---------------------------------------------------------------------------
# fetch_url host recognition (for quotable entries only)
# ---------------------------------------------------------------------------


def test_fetch_urls_point_at_recognized_hosts():
    """
    Every quotable entry's fetch_url must point at a recognized PD/CC0 corpus host.
    PARAPHRASE entries may have fetch_url=None (they are not machine-fetched).
    """
    for entry in load_quotable_corpus(CONCEPT):
        url = entry.get("fetch_url")
        assert is_recognized_host(url), (
            f"fetch_url '{url}' is not a recognized corpus host "
            f"for entry: {entry['source']}"
        )


# ---------------------------------------------------------------------------
# load_quotable_corpus / load_context_corpus split
# ---------------------------------------------------------------------------


def test_quotable_excludes_paraphrase():
    for entry in load_quotable_corpus(CONCEPT):
        assert entry["license"] != "PARAPHRASE"


def test_context_corpus_is_paraphrase_only():
    for entry in load_context_corpus(CONCEPT):
        assert entry["license"] == "PARAPHRASE"


def test_full_corpus_is_union_of_quotable_and_context():
    full = load_corpus(CONCEPT)
    quotable = load_quotable_corpus(CONCEPT)
    context = load_context_corpus(CONCEPT)
    assert len(full) == len(quotable) + len(context)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def test_missing_concept_raises():
    with pytest.raises(FileNotFoundError):
        load_corpus("nonexistent_concept_xyz")


# ---------------------------------------------------------------------------
# Specific corpus content checks
# ---------------------------------------------------------------------------


def test_vairagya_has_gita_arnold():
    entries = load_corpus(CONCEPT)
    sources = [e["source"] for e in entries]
    assert any("Bhagavad Gita" in s for s in sources), (
        f"Expected a Bhagavad Gita entry; found: {sources}"
    )


def test_vairagya_has_yoga_sutras():
    entries = load_corpus(CONCEPT)
    sources = [e["source"] for e in entries]
    assert any("Yoga S" in s for s in sources), (
        f"Expected a Yoga Sutras entry; found: {sources}"
    )


def test_vairagya_has_sujato():
    entries = load_corpus(CONCEPT)
    translators = [e.get("translator") or "" for e in entries]
    assert any("Sujato" in t for t in translators), (
        f"Expected a Sujato (CC0) entry; found translators: {translators}"
    )


def test_sujato_entries_are_cc0():
    entries = load_corpus(CONCEPT)
    for e in entries:
        if e.get("translator") and "Sujato" in e["translator"]:
            assert e["license"] == "CC0", (
                f"Sujato entry should be CC0, got: {e['license']}"
            )


def test_arnold_entries_are_pd():
    entries = load_corpus(CONCEPT)
    for e in entries:
        if e.get("translator") and "Arnold" in e["translator"]:
            assert e["license"] == "PD", (
                f"Arnold entry should be PD, got: {e['license']}"
            )


def test_vivekananda_entry_is_pd():
    entries = load_corpus(CONCEPT)
    for e in entries:
        if e.get("translator") and "Vivekananda" in e["translator"]:
            assert e["license"] == "PD", (
                f"Vivekananda entry should be PD, got: {e['license']}"
            )

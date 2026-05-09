"""
test_artifacts_license_guard.py — verify ADR-6 fail-fast on invalid license.

The guard in artifacts.py must raise AssertionError (not a warning, not a log line)
when any citation row has a license value outside {PD, CC0, CC-BY-NC-SA-4.0}.
"""

import pytest
from pathlib import Path
from unittest.mock import patch
import sys

# Ensure repo root is on path
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from engine.artifacts import write_artifacts, _validate_citations


# --- Unit tests for the guard function directly ---

def test_validate_citations_passes_valid_licenses():
    """Valid licenses must not raise."""
    citations = [
        {"license": "PD", "source": "Gita", "turn_idx": 0},
        {"license": "CC0", "source": "Sujato", "turn_idx": 1},
        {"license": "CC-BY-NC-SA-4.0", "source": "Some work", "turn_idx": 2},
    ]
    _validate_citations(citations)  # must not raise


def test_validate_citations_rejects_paraphrase():
    """PARAPHRASE is not a valid citations.jsonl license (soul.md §5.2 + ADR-6)."""
    citations = [
        {"license": "PARAPHRASE", "source": "Kastrup talk", "turn_idx": 3},
    ]
    with pytest.raises(AssertionError, match="invalid license"):
        _validate_citations(citations)


def test_validate_citations_rejects_unknown():
    """Unknown license values must fail-fast."""
    citations = [
        {"license": "UNKNOWN", "source": "Mystery source", "turn_idx": 5},
    ]
    with pytest.raises(AssertionError, match="invalid license"):
        _validate_citations(citations)


def test_validate_citations_rejects_empty_license():
    """Empty string license must fail."""
    citations = [
        {"license": "", "source": "Something", "turn_idx": 2},
    ]
    with pytest.raises(AssertionError, match="invalid license"):
        _validate_citations(citations)


def test_validate_citations_rejects_copyright():
    """Copyright (©) license must fail."""
    citations = [
        {"license": "©", "source": "Copyrighted book", "turn_idx": 0},
    ]
    with pytest.raises(AssertionError, match="invalid license"):
        _validate_citations(citations)


# --- Integration test: write_artifacts raises before writing any files ---

def test_write_artifacts_fails_before_writing_on_bad_license(tmp_path):
    """write_artifacts must raise AssertionError before creating any file."""
    script = {
        "episode_no": 99,
        "concept": "test",
        "concept_pair": "test pair",
        "soul_md_sha": "abc123",
        "turns": [{"voice": "A", "text": "Hello."}],
        "citations": [
            {"license": "PARAPHRASE", "source": "Bad source", "turn_idx": 0,
             "quote": "some text", "translator": "", "corpus_url": "http://x.com",
             "verse_or_section": "1.1", "tradition": "east-lineage", "verified_date": "2026-05-08"}
        ],
    }
    mp3_dummy = tmp_path / "fake.mp3"
    # mp3 doesn't need to exist for the guard to trigger

    with pytest.raises(AssertionError, match="invalid license"):
        write_artifacts(script, tmp_path / "ep099", mp3_dummy)

    # Confirm no files were written
    assert not (tmp_path / "ep099").exists() or not list((tmp_path / "ep099").iterdir())

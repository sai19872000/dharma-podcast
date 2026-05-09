"""
test_publish_halt_guard.py — verify ADR-5 halt guard in publish.py.

Episode 1 must raise RuntimeError when DHARMA_EP001_APPROVED is not set.
Episode 2+ must not be blocked.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from engine.publish import _adr5_guard, publish_episode


# --- Unit tests on the guard function directly ---

def test_adr5_guard_blocks_ep1_without_env(monkeypatch):
    """Episode 1 must raise when DHARMA_EP001_APPROVED is not set."""
    monkeypatch.delenv("DHARMA_EP001_APPROVED", raising=False)
    with pytest.raises(RuntimeError, match="DHARMA_EP001_APPROVED=1"):
        _adr5_guard(1)


def test_adr5_guard_allows_ep1_with_env(monkeypatch):
    """Episode 1 must pass when DHARMA_EP001_APPROVED=1."""
    monkeypatch.setenv("DHARMA_EP001_APPROVED", "1")
    _adr5_guard(1)  # must not raise


def test_adr5_guard_allows_ep2_without_env(monkeypatch):
    """Episode 2 must never be blocked by the guard."""
    monkeypatch.delenv("DHARMA_EP001_APPROVED", raising=False)
    _adr5_guard(2)  # must not raise


def test_adr5_guard_allows_ep99_without_env(monkeypatch):
    """Future episodes must never be blocked."""
    monkeypatch.delenv("DHARMA_EP001_APPROVED", raising=False)
    _adr5_guard(99)  # must not raise


# --- Integration test: publish_episode raises before touching R2 ---

def test_publish_episode_blocks_ep1_without_approval(monkeypatch, tmp_path):
    """publish_episode must raise on ep1 before doing any R2 upload."""
    monkeypatch.delenv("DHARMA_EP001_APPROVED", raising=False)

    fake_mp3 = tmp_path / "episode_001.mp3"
    fake_mp3.write_bytes(b"fake")

    with pytest.raises(RuntimeError, match="DHARMA_EP001_APPROVED=1"):
        publish_episode(1, tmp_path, fake_mp3)


def test_publish_episode_ep2_reaches_r2_check(monkeypatch, tmp_path):
    """Episode 2 must pass the guard and attempt R2 (fail on wrangler missing, not on guard)."""
    monkeypatch.delenv("DHARMA_EP001_APPROVED", raising=False)

    fake_mp3 = tmp_path / "episode_002.mp3"
    fake_mp3.write_bytes(b"fake audio bytes")

    # Guard must not raise; failure must come from wrangler/missing template, not the guard
    with pytest.raises((RuntimeError, FileNotFoundError, Exception)) as exc_info:
        publish_episode(2, tmp_path, fake_mp3)

    # Key assertion: the error is NOT the ADR-5 guard
    assert "DHARMA_EP001_APPROVED" not in str(exc_info.value), (
        "Ep2 must not be blocked by the ADR-5 guard"
    )

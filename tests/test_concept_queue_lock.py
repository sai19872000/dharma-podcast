"""
test_concept_queue_lock.py — verify flock prevents concurrent state corruption (ADR-8).

Tests that:
1. pick_next() returns the first queued concept.
2. mark_drafted() correctly transitions status.
3. Concurrent mark_drafted calls don't corrupt the queue (flock serializes them).
"""

import json
import os
import shutil
import tempfile
import threading
from pathlib import Path
import sys
import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))


@pytest.fixture()
def tmp_queue(tmp_path, monkeypatch):
    """Create a temporary concept_queue.json and patch module to use it."""
    queue_data = {
        "version": 1,
        "concepts": [
            {"slug": "alpha", "english": "first", "status": "queued"},
            {"slug": "beta",  "english": "second", "status": "queued"},
            {"slug": "gamma", "english": "third",  "status": "queued"},
        ],
    }
    queue_file = tmp_path / "concept_queue.json"
    queue_file.write_text(json.dumps(queue_data, indent=2), encoding="utf-8")

    import engine.concept_queue as cq
    monkeypatch.setattr(cq, "_QUEUE_FILE", queue_file)
    monkeypatch.setattr(cq, "_LOCK_PATH", str(tmp_path / "test_cq.lock"))
    return queue_file


def test_pick_next_returns_first_queued(tmp_queue):
    """pick_next() must return the first status=queued concept without mutating."""
    import engine.concept_queue as cq
    concept = cq.pick_next()
    assert concept["slug"] == "alpha"
    assert concept["status"] == "queued"


def test_pick_next_skips_non_queued(tmp_queue):
    """pick_next() must skip drafted/published entries."""
    import engine.concept_queue as cq
    cq.mark_drafted("alpha", 1)
    concept = cq.pick_next()
    assert concept["slug"] == "beta"


def test_mark_drafted_transitions_status(tmp_queue):
    """mark_drafted() must set status=drafted and scheduled_episode_no."""
    import engine.concept_queue as cq
    cq.mark_drafted("alpha", 5)
    data = json.loads(tmp_queue.read_text(encoding="utf-8"))
    alpha = next(c for c in data["concepts"] if c["slug"] == "alpha")
    assert alpha["status"] == "drafted"
    assert alpha["scheduled_episode_no"] == 5


def test_mark_published_transitions_status(tmp_queue):
    """mark_published() must set status=published."""
    import engine.concept_queue as cq
    cq.mark_drafted("beta", 2)
    cq.mark_published("beta")
    data = json.loads(tmp_queue.read_text(encoding="utf-8"))
    beta = next(c for c in data["concepts"] if c["slug"] == "beta")
    assert beta["status"] == "published"


def test_mark_drafted_unknown_slug_raises(tmp_queue):
    """mark_drafted() must raise ValueError for an unknown slug."""
    import engine.concept_queue as cq
    with pytest.raises(ValueError, match="not found"):
        cq.mark_drafted("nonexistent", 1)


def test_concurrent_mark_drafted_no_corruption(tmp_queue):
    """
    Concurrent mark_drafted calls must not corrupt the queue.

    Spawn N threads each calling mark_drafted on a different slug.
    After all threads complete, verify all slugs are drafted and
    the total concept count is unchanged.
    """
    import engine.concept_queue as cq

    errors: list[Exception] = []

    def draft(slug: str, ep: int) -> None:
        try:
            cq.mark_drafted(slug, ep)
        except Exception as e:
            errors.append(e)

    threads = [
        threading.Thread(target=draft, args=("alpha", 1)),
        threading.Thread(target=draft, args=("beta", 2)),
        threading.Thread(target=draft, args=("gamma", 3)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == [], f"Threads raised errors: {errors}"

    data = json.loads(tmp_queue.read_text(encoding="utf-8"))
    assert len(data["concepts"]) == 3, "concept count must not change"
    for concept in data["concepts"]:
        assert concept["status"] == "drafted", f"{concept['slug']} not drafted"

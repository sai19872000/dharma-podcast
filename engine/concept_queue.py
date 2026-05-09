"""
concept_queue.py — concept state machine for the dharma-podcast engine.

Public API:
    pick_next()                     → concept dict (first status=queued)
    mark_drafted(slug, episode_no)  → None
    mark_published(slug)            → None

All mutations are wrapped in flock("/tmp/dharma_concept_queue.lock") per ADR-8
to survive parallel pipeline runs.
"""

from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
_QUEUE_FILE = _REPO_ROOT / "concept_queue.json"
_LOCK_PATH = "/tmp/dharma_concept_queue.lock"


def _load() -> dict[str, Any]:
    with _QUEUE_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


def _save(data: dict[str, Any]) -> None:
    with _QUEUE_FILE.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def pick_next() -> dict[str, Any]:
    """Return the first concept with status='queued'. Does NOT mutate state."""
    data = _load()
    for concept in data["concepts"]:
        if concept.get("status") == "queued":
            return dict(concept)
    raise RuntimeError("No queued concepts remain in concept_queue.json")


def mark_drafted(slug: str, episode_no: int) -> None:
    """Set status=drafted and scheduled_episode_no on the named concept."""
    lock_fd = open(_LOCK_PATH, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        data = _load()
        found = False
        for concept in data["concepts"]:
            if concept["slug"] == slug:
                concept["status"] = "drafted"
                concept["scheduled_episode_no"] = episode_no
                found = True
                break
        if not found:
            raise ValueError(f"Slug '{slug}' not found in concept_queue.json")
        _save(data)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


def mark_published(slug: str) -> None:
    """Set status=published on the named concept."""
    lock_fd = open(_LOCK_PATH, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        data = _load()
        found = False
        for concept in data["concepts"]:
            if concept["slug"] == slug:
                concept["status"] = "published"
                found = True
                break
        if not found:
            raise ValueError(f"Slug '{slug}' not found in concept_queue.json")
        _save(data)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()

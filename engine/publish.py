"""
publish.py — upload episode audio to R2 and regenerate feed.xml.

HARD GUARD (ADR-5): refuses to publish episode 1 unless DHARMA_EP001_APPROVED=1 is set.

Public API:
    publish_episode(episode_no, episode_dir, mp3_path) -> None
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
_EPISODES_INDEX = _REPO_ROOT / "episodes" / "index.json"
_FEED_TEMPLATE = _REPO_ROOT / "web" / "feed.xml.template"


def _adr5_guard(episode_no: int) -> None:
    """ADR-5 hard guard — block Ep001 publish without explicit approval."""
    if episode_no == 1 and not os.environ.get("DHARMA_EP001_APPROVED"):
        raise RuntimeError(
            "Ep001 publish blocked — set DHARMA_EP001_APPROVED=1 after Sai's review"
        )


def _load_index() -> list[dict[str, Any]]:
    if _EPISODES_INDEX.exists():
        with _EPISODES_INDEX.open(encoding="utf-8") as fh:
            return json.load(fh)
    return []


def _save_index(episodes: list[dict[str, Any]]) -> None:
    _EPISODES_INDEX.parent.mkdir(parents=True, exist_ok=True)
    with _EPISODES_INDEX.open("w", encoding="utf-8") as fh:
        json.dump(episodes, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def _build_feed_xml(episodes: list[dict[str, Any]], template: str) -> str:
    """Render RSS feed XML from template + episodes list."""
    items = []
    for ep in sorted(episodes, key=lambda e: e["episode_no"], reverse=True):
        item = f"""    <item>
      <title>{ep['title']}</title>
      <description>{ep.get('description', '')}</description>
      <pubDate>{ep['pub_date']}</pubDate>
      <guid isPermaLink="false">dharma-ep{ep['episode_no']:03d}</guid>
      <link>https://dharma.saiteja.ai/episodes/{ep['episode_no']:03d}</link>
      <enclosure url="https://dharma.saiteja.ai/audio/{ep['episode_no']:03d}.mp3"
                 type="audio/mpeg"
                 length="{ep.get('size_bytes', 0)}"/>
      <itunes:duration>{ep.get('duration', '')}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>"""
        items.append(item)
    return template.replace("{ITEMS}", "\n".join(items))


def _r2_put(local_path: Path, r2_key: str) -> None:
    """Upload a file to R2 via Cloudflare API (wrangler r2 object put)."""
    result = subprocess.run(
        ["wrangler", "r2", "object", "put",
         f"dharma-podcast-audio/{r2_key}",
         "--file", str(local_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"R2 upload failed for {r2_key}:\n{result.stderr}")


def publish_episode(
    episode_no: int,
    episode_dir: Path,
    mp3_path: Path,
) -> None:
    """
    Upload mp3 to R2 and regenerate feed.xml.

    Raises RuntimeError for Ep001 without DHARMA_EP001_APPROVED=1 (ADR-5).
    Requires wrangler CLI configured with Cloudflare credentials.
    """
    _adr5_guard(episode_no)  # ADR-5 — must be first

    if not mp3_path.exists():
        raise FileNotFoundError(f"Episode mp3 not found: {mp3_path}")

    r2_audio_key = f"audio/{episode_no:03d}.mp3"
    print(f"[publish] uploading {mp3_path.name} → R2:{r2_audio_key}")
    _r2_put(mp3_path, r2_audio_key)

    # Update episodes index
    episodes = _load_index()
    size_bytes = mp3_path.stat().st_size

    # Remove existing entry for this episode_no if present
    episodes = [e for e in episodes if e.get("episode_no") != episode_no]

    show_notes = episode_dir / f"episode_{episode_no:03d}.show_notes.md"
    description = ""
    if show_notes.exists():
        lines = show_notes.read_text(encoding="utf-8").split("\n")
        # Use first non-empty non-header line as description
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
                description = stripped[:200]
                break

    from datetime import datetime, timezone
    episodes.append({
        "episode_no": episode_no,
        "title": f"Episode {episode_no:03d}",
        "pub_date": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000"),
        "size_bytes": size_bytes,
        "description": description,
        "duration": "",
    })
    _save_index(episodes)

    # Regenerate feed.xml
    if not _FEED_TEMPLATE.exists():
        print("[publish] feed.xml.template not found — skipping feed regen")
        return

    template = _FEED_TEMPLATE.read_text(encoding="utf-8")
    feed_xml = _build_feed_xml(episodes, template)

    feed_path = episode_dir.parent.parent / "web" / "feed.xml"
    feed_path.parent.mkdir(parents=True, exist_ok=True)
    feed_path.write_text(feed_xml, encoding="utf-8")
    print(f"[publish] feed.xml written to {feed_path}")

    _r2_put(feed_path, "feed.xml")
    print(f"[publish] episode {episode_no:03d} published to R2")

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
import xml.sax.saxutils
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engine.artifacts import _get_duration_seconds

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


def _format_duration_hhmmss(seconds: float) -> str:
    """Format duration seconds as HH:MM:SS for itunes:duration."""
    total_secs = int(seconds)
    h, rem = divmod(total_secs, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _build_feed_xml(episodes: list[dict[str, Any]], template: str) -> str:
    """Render RSS feed XML from template + episodes list."""
    # P0-1: substitute all channel-level placeholders
    SHOW = {
        'SHOW_TITLE': 'Dharma',
        'SHOW_LINK': 'https://dharma.saiteja.ai',
        'SHOW_DESC': 'East contemplative lineages and modern consciousness science, in dialogue.',
        'OWNER_EMAIL': os.environ.get('DHARMA_OWNER_EMAIL', ''),
        'LAST_BUILD_DATE': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000'),
    }

    items = []
    for ep in sorted(episodes, key=lambda e: e["episode_no"], reverse=True):
        ep_no = ep['episode_no']
        permalink = f"https://dharma.saiteja.ai/episodes/{ep_no:03d}"
        # P2-1: escape XML-special chars in free-text fields
        title_esc = xml.sax.saxutils.escape(ep['title'])
        desc_esc = xml.sax.saxutils.escape(ep.get('description', ''))
        item = f"""    <item>
      <title>{title_esc}</title>
      <description>{desc_esc}</description>
      <pubDate>{ep['pub_date']}</pubDate>
      <guid isPermaLink="true">{permalink}</guid>
      <link>{permalink}</link>
      <enclosure url="https://dharma.saiteja.ai/audio/{ep_no:03d}.mp3"
                 type="audio/mpeg"
                 length="{ep.get('size_bytes', 0)}"/>
      <itunes:title>{title_esc}</itunes:title>
      <itunes:author>Sai Ram Labs</itunes:author>
      <itunes:summary>{desc_esc}</itunes:summary>
      <itunes:duration>{ep.get('duration', '')}</itunes:duration>
      <itunes:episode>{ep_no}</itunes:episode>
      <itunes:episodeType>full</itunes:episodeType>
      <itunes:explicit>false</itunes:explicit>
    </item>"""
        items.append(item)

    feed_xml = template
    for k, v in SHOW.items():
        feed_xml = feed_xml.replace(f'{{{k}}}', v)
    feed_xml = feed_xml.replace('{ITEMS}', '\n'.join(items))
    return feed_xml


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
    concept = ""
    if show_notes.exists():
        lines = show_notes.read_text(encoding="utf-8").split("\n")
        # P1-4: extract concept from header line "# Episode 001 — Concept × pair"
        if lines and "—" in lines[0]:
            after_dash = lines[0].split("—", 1)[1].strip()
            concept = after_dash.split("×")[0].strip().lstrip("#").strip()
        # Use first non-empty non-header line as description
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
                description = stripped[:200]
                break

    # P1-4: include concept in title; fall back to plain format if unavailable
    title = f"EP {episode_no:03d}: {concept}" if concept else f"Episode {episode_no:03d}"

    # P1-1: compute actual duration via ffprobe and format as HH:MM:SS
    duration_s = _get_duration_seconds(mp3_path)
    duration_str = _format_duration_hhmmss(duration_s) if duration_s > 0 else ""

    episodes.append({
        "episode_no": episode_no,
        "title": title,
        "pub_date": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000"),
        "size_bytes": size_bytes,
        "description": description,
        "duration": duration_str,
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

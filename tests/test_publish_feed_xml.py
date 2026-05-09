"""
test_publish_feed_xml.py — verify _build_feed_xml substitutes all placeholders.

P2-3 close: no literal { } placeholders may survive in the rendered feed.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from engine.publish import _build_feed_xml


# Minimal fixture template — mirrors the real feed.xml.template shape
_FIXTURE_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>{SHOW_TITLE}</title>
    <link>{SHOW_LINK}</link>
    <description>{SHOW_DESC}</description>
    <lastBuildDate>{LAST_BUILD_DATE}</lastBuildDate>
    <itunes:title>{SHOW_TITLE}</itunes:title>
    <itunes:owner><itunes:email>{OWNER_EMAIL}</itunes:email></itunes:owner>
    <atom:link href="{SHOW_LINK}/feed.xml" rel="self"/>
    <image><url>{SHOW_LINK}/cover.jpg</url><title>{SHOW_TITLE}</title><link>{SHOW_LINK}</link></image>
    {ITEMS}
  </channel>
</rss>
"""


def test_feed_xml_renders_show_metadata():
    """No {PLACEHOLDER} literals must survive; show metadata must be present."""
    episodes = [
        {
            "episode_no": 1,
            "title": "EP 001: Vairāgya",
            "pub_date": "Thu, 08 May 2026 00:00:00 +0000",
            "size_bytes": 12345,
            "description": "A test episode description.",
            "duration": "00:06:42",
        }
    ]

    result = _build_feed_xml(episodes, _FIXTURE_TEMPLATE)

    # Definitive check: no un-substituted placeholder remains
    assert "{" not in result, (
        f"Un-substituted placeholder found in feed XML. Offending text:\n"
        + "\n".join(line for line in result.splitlines() if "{" in line)
    )

    # Show-level metadata appears
    assert "<title>Dharma</title>" in result
    assert "https://dharma.saiteja.ai" in result
    assert "East contemplative lineages" in result

    # Episode item rendered correctly
    assert "EP 001: Vair\u0101gya" in result  # title with concept
    assert 'isPermaLink="true"' in result     # P1-2: permalink guid
    assert "https://dharma.saiteja.ai/episodes/001" in result
    assert "<itunes:duration>00:06:42</itunes:duration>" in result  # P1-1
    assert "<itunes:episode>1</itunes:episode>" in result            # P1-3
    assert "<itunes:episodeType>full</itunes:episodeType>" in result # P1-3
    assert "<itunes:author>Sai Ram Labs</itunes:author>" in result   # P1-3

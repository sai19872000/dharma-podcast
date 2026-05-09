"""
tg_notify.py — deliver episode audio + show notes preview to Sai via Telegram.

Uses ~/factory/scripts/tg_send.sh for the text message.
Uses Telegram Bot API directly for audio file upload (tg_send.sh is text-only).

Public API:
    notify(episode_no, episode_dir, mp3_path, script) -> None
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any


def _find_tg_send() -> Path:
    candidates = [
        Path.home() / "factory" / "scripts" / "tg_send.sh",
        Path(__file__).resolve().parent.parent.parent / "factory" / "scripts" / "tg_send.sh",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("tg_send.sh not found — check ~/factory/scripts/")


def _format_message(
    episode_no: int,
    script: dict[str, Any],
    duration_str: str,
    show_notes_path: Path,
) -> str:
    concept = script.get("concept", "")
    concept_pair = script.get("concept_pair", "")
    citations = script.get("citations", [])
    citation_count = len(citations)

    # Unique works cited
    works = list(dict.fromkeys(c.get("source", "").split(" ")[0] for c in citations if c.get("source")))
    works_str = ", ".join(works[:4]) if works else "primary sources"

    # Show notes preview (first 3 non-empty non-header lines)
    preview_lines: list[str] = []
    if show_notes_path.exists():
        for line in show_notes_path.read_text(encoding="utf-8").split("\n"):
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("---") and not stripped.startswith("**Duration"):
                preview_lines.append(stripped)
            if len(preview_lines) >= 3:
                break

    preview = " / ".join(preview_lines[:3]) if preview_lines else ""

    msg = (
        f"Episode {episode_no:03d} — {concept.capitalize()} × {concept_pair}. "
        f"{duration_str} at -16 LUFS. "
        f"{citation_count} quote{'s' if citation_count != 1 else ''} from {works_str}."
    )
    if preview:
        msg += f"\n\nShow notes: {preview[:280]}"
    msg += "\n\nReply 'approve' to unlock RSS publish."
    return msg


def notify(
    episode_no: int,
    episode_dir: Path,
    mp3_path: Path,
    script: dict[str, Any],
    duration_str: str = "",
) -> None:
    """
    Send audio file + summary message to Sai's Telegram chat.

    Sends audio file + caption via tg_send.sh (sendDocument).
    Falls back to text-only if mp3 is missing.
"""
    chat_id = os.environ.get("PERSONAL_TG_CHAT_ID", "").strip()
    if not chat_id:
        raise RuntimeError("PERSONAL_TG_CHAT_ID is not set")

    tg_send = _find_tg_send()

    show_notes_path = episode_dir / f"episode_{episode_no:03d}.show_notes.md"
    message = _format_message(episode_no, script, duration_str, show_notes_path)

    # tg_send.sh loads the correct bot token from ~/.claude/channels/telegram/.env
    # unless TELEGRAM_BOT_TOKEN is already set in the process env.  The factory
    # process may export a *different* bot token (orchestrator bot), so we strip
    # it here so tg_send.sh falls through to its .env file (the chitti bot).
    clean_env = {k: v for k, v in os.environ.items() if k != "TELEGRAM_BOT_TOKEN"}

    # Send audio file with caption via tg_send.sh (supports sendDocument with file arg)
    if mp3_path.exists():
        print(f"[tg_notify] sending audio file + caption to chat {chat_id}")
        result = subprocess.run(
            [str(tg_send), chat_id, message, str(mp3_path)],
            capture_output=True, text=True, env=clean_env,
        )
        output = result.stdout + result.stderr
        print(f"  tg_send output: {output.strip()}")
        if result.returncode != 0:
            print(f"[tg_notify] WARNING: tg_send.sh audio delivery failed — sending text only")
            result2 = subprocess.run(
                [str(tg_send), chat_id, message],
                capture_output=True, text=True, env=clean_env,
            )
            print(f"  tg_send text fallback: {(result2.stdout + result2.stderr).strip()}")
    else:
        print(f"[tg_notify] mp3 not found at {mp3_path} — sending text only")
        result = subprocess.run(
            [str(tg_send), chat_id, message],
            capture_output=True, text=True, env=clean_env,
        )
        print(f"  tg_send output: {(result.stdout + result.stderr).strip()}")


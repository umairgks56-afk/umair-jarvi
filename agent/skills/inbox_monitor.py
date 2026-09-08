from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class InboxItem:
    source: str
    sender: str
    subject: str
    preview: str
    received_at: str


def normalize_email_message(sender: str, subject: str, body: str, received_at: str = "") -> InboxItem:
    preview = " ".join((body or "").split())[:500]
    return InboxItem(
        source="email",
        sender=sender,
        subject=subject,
        preview=preview,
        received_at=received_at or datetime.now().isoformat(timespec="seconds"),
    )


def summarize_items(items: list[InboxItem]) -> str:
    if not items:
        return "No new messages found."
    lines = [f"{len(items)} new item(s) found."]
    for item in items[:10]:
        label = item.subject or item.preview[:80]
        lines.append(f"• {item.source}: {item.sender} — {label}")
    return "\n".join(lines)


# Account-specific connectors intentionally live behind this interface.
# Credentials/tokens must never be stored in JARVIS memory or source code.
# Gmail/Outlook and WhatsApp adapters can call this normalized interface after
# the user explicitly authenticates the account/session on the PC.

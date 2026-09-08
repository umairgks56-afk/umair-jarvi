"""JARVIS connection hub.

Connectors are capability declarations today; individual providers can later plug in
OAuth/session implementations without changing the core agent. Credentials never
belong in memory.db or the chat prompt.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import List


@dataclass
class Integration:
    id: str
    name: str
    category: str
    description: str
    capabilities: List[str]
    auth: str
    status: str = "available"
    connected: bool = False


INTEGRATIONS = [
    Integration("local_files", "PC Files", "computer", "Search and read documents, PDFs and notes from approved folders.", ["search", "read", "summarize", "save_notes"], "local"),
    Integration("browser", "Browser", "computer", "Research websites, read pages and navigate with a real browser session.", ["search_web", "read_page", "navigate"], "local"),
    Integration("gmail", "Gmail", "communication", "Read/search mail and prepare drafts; sending remains confirmation-gated.", ["read", "search", "draft", "send"], "oauth2"),
    Integration("outlook", "Outlook", "communication", "Microsoft mail integration with scoped Graph permissions.", ["read", "search", "draft", "send"], "oauth2"),
    Integration("whatsapp_web", "WhatsApp Web", "communication", "Use a local persistent browser session for WhatsApp Web.", ["read", "search", "draft", "send"], "browser_session"),
    Integration("google_drive", "Google Drive", "storage", "Find and read connected Drive documents.", ["search", "read"], "oauth2"),
    Integration("calendar", "Calendar", "productivity", "Read events and prepare new events/reminders.", ["read", "create"], "oauth2"),
    Integration("pc_control", "PC Control", "computer", "Open apps, inspect system status and perform approved desktop actions.", ["apps", "system", "vision"], "local"),
]


def list_integrations() -> list[dict]:
    return [asdict(x) for x in INTEGRATIONS]


def get_integration(integration_id: str) -> Integration | None:
    return next((x for x in INTEGRATIONS if x.id == integration_id), None)


def connect(integration_id: str) -> dict:
    item = get_integration(integration_id)
    if not item:
        return {"ok": False, "error": "Unknown integration."}
    if item.auth == "local":
        item.connected = True
        item.status = "connected"
        return {"ok": True, "message": f"{item.name} connected locally.", "integration": asdict(item)}
    return {"ok": True, "requires_setup": True, "message": f"{item.name} needs its {item.auth} authentication flow. No password/token is stored by this registry.", "integration": asdict(item)}


def disconnect(integration_id: str) -> dict:
    item = get_integration(integration_id)
    if not item:
        return {"ok": False, "error": "Unknown integration."}
    item.connected = False
    item.status = "available"
    return {"ok": True, "message": f"{item.name} disconnected.", "integration": asdict(item)}

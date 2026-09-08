"""Local append-only audit trail for JARVIS activity.

This log records intent and outcomes, not secrets. It is useful for debugging,
analytics, and showing the user what JARVIS actually did.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from config import DATA_DIR

AUDIT_FILE = DATA_DIR / "audit.jsonl"
AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)


def record(event: str, status: str = "ok", detail: str = "") -> dict:
    item = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "status": status,
        "detail": detail[:1000],
    }
    with AUDIT_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    return item


def recent(limit: int = 50) -> list[dict]:
    if not AUDIT_FILE.exists():
        return []
    rows = []
    for line in AUDIT_FILE.read_text(encoding="utf-8").splitlines()[-max(1, limit):]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows

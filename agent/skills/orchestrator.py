"""Lightweight deterministic task planner.

This is deliberately not an autonomous executor. It turns a natural-language goal
into inspectable steps and leaves execution to the existing, permission-gated tools.
That gives JARVIS a foundation for multi-agent orchestration without unsafe magic.
"""
from __future__ import annotations


def build_plan(goal: str) -> dict:
    text = goal.strip()
    low = text.lower()
    steps: list[dict] = []

    if any(word in low for word in ("research", "research karo", "research on", "web research")):
        steps += [
            {"id": 1, "action": "search_web", "description": "Search multiple relevant web sources."},
            {"id": 2, "action": "read_sources", "description": "Open and extract readable source content."},
            {"id": 3, "action": "synthesize", "description": "Compare the evidence and identify useful findings."},
            {"id": 4, "action": "save_note", "description": "Save the research trail and source URLs locally."},
        ]
    if any(word in low for word in ("pdf", "file", "document", "documents")):
        steps += [
            {"id": len(steps) + 1, "action": "inspect_files", "description": "Locate relevant local documents in approved folders."},
            {"id": len(steps) + 2, "action": "extract", "description": "Read supported text/PDF content."},
        ]
    if any(word in low for word in ("email", "whatsapp", "message", "send")):
        steps += [
            {"id": len(steps) + 1, "action": "prepare_message", "description": "Prepare the requested communication."},
            {"id": len(steps) + 2, "action": "confirm", "description": "Ask for explicit confirmation before external sending."},
        ]

    if not steps:
        steps = [{"id": 1, "action": "understand", "description": "Understand the goal and select the safest available tool."},
                 {"id": 2, "action": "execute", "description": "Run only approved, non-destructive actions."}]

    return {"goal": text, "steps": steps, "execution": "permission_gated"}

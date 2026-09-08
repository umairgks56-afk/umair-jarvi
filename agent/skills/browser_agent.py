"""Goal-driven browser agent powered by the local Ollama model."""
from __future__ import annotations

import json
import re
from typing import Any

from core.ollama import OllamaClient
from skills.browser_operator import _BROWSER
from skills.audit_log import record

_ACTION_RE = re.compile(r"\{.*\}", re.S)

_SYSTEM = """You are JARVIS Browser Operator. You control a visible browser for the user.
Choose exactly one action as JSON:
{"action":"open","target":"https://..."}
{"action":"search","query":"..."}
{"action":"click","target":"visible text or CSS selector"}
{"action":"fill","selector":"CSS selector","value":"..."}
{"action":"press","selector":"CSS selector","key":"Enter"}
{"action":"scroll","direction":"down"}
{"action":"done","message":"..."}
Rules: inspect the page before acting; use visible text/selectors from the page. Never enter passwords, OTPs, card data, or secrets. Never perform purchases, payments, permanent deletion, or final external submission/sending. If the goal reaches such a step, use done and tell the user to finish it manually. Prefer small, reversible steps."""


class BrowserAgent:
    def __init__(self, ai: OllamaClient | None = None, max_steps: int = 12):
        self.ai = ai or OllamaClient()
        self.max_steps = max_steps

    def _decide(self, goal: str, page: str) -> dict[str, Any]:
        prompt = _SYSTEM + "\n\nUSER GOAL:\n" + goal + "\n\nCURRENT PAGE:\n" + page[:12000]
        raw = self.ai.chat([{"role": "system", "content": _SYSTEM}, {"role": "user", "content": prompt}], temperature=0.1)
        match = _ACTION_RE.search(raw)
        if not match:
            return {"action": "done", "message": raw[:1200]}
        try:
            obj = json.loads(match.group(0))
            return obj if isinstance(obj, dict) else {"action": "done", "message": "Model returned an invalid action."}
        except json.JSONDecodeError:
            return {"action": "done", "message": raw[:1200]}

    def run(self, goal: str) -> dict:
        if not goal.strip():
            return {"ok": False, "error": "Browser goal is empty."}
        page = _BROWSER.start()
        history = []
        for step in range(1, self.max_steps + 1):
            snapshot = _BROWSER.snapshot(12000)
            action = self._decide(goal, snapshot)
            name = action.get("action", "done")
            history.append({"step": step, "action": name})
            record("browser_agent", "planned", f"step={step} action={name} goal={goal[:300]}")
            try:
                if name == "open":
                    result = _BROWSER.open(str(action.get("target", "")))
                elif name == "search":
                    result = _BROWSER.search(str(action.get("query", "")))
                elif name == "click":
                    result = _BROWSER.click(str(action.get("target", "")))
                elif name == "fill":
                    result = _BROWSER.fill(str(action.get("selector", "")), str(action.get("value", "")))
                elif name == "press":
                    result = _BROWSER.press(str(action.get("selector", "")), str(action.get("key", "Enter")))
                elif name == "scroll":
                    result = _BROWSER.scroll(str(action.get("direction", "down")))
                else:
                    return {"ok": True, "message": str(action.get("message", "Task complete.")), "history": history, "url": page.url}
                record("browser_agent", "executed", f"step={step} action={name}")
            except PermissionError as exc:
                record("browser_agent", "blocked", str(exc))
                return {"ok": False, "blocked": True, "message": str(exc), "history": history, "url": page.url}
            except Exception as exc:
                record("browser_agent", "error", f"step={step} {exc}")
                return {"ok": False, "error": str(exc), "history": history, "url": page.url}
        return {"ok": False, "error": "Maximum browser steps reached; stopping safely.", "history": history, "url": page.url}

"""Universal, visible browser operator for JARVIS.

Uses a persistent Chromium profile so the user can authenticate manually once and
JARVIS can reuse that browser session. No passwords or OTPs are captured by JARVIS.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote_plus

from config import DATA_DIR

try:
    from playwright.sync_api import sync_playwright
except Exception:  # pragma: no cover
    sync_playwright = None

PROFILE_DIR = DATA_DIR / "browser-profile"
SCREENSHOT_DIR = DATA_DIR / "browser-screenshots"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

_BLOCKED_TERMS = re.compile(r"\b(pay|payment|purchase|buy now|checkout|submit|delete|remove permanently|send message|send email|confirm order)\b", re.I)


class UniversalBrowser:
    def __init__(self):
        self._pw = None
        self.context = None
        self.page = None

    def start(self):
        if self.page is not None:
            return self.page
        if sync_playwright is None:
            raise RuntimeError("Playwright is not installed. Run: pip install -r requirements.txt && playwright install chromium")
        self._pw = sync_playwright().start()
        self.context = self._pw.chromium.launch_persistent_context(
            str(PROFILE_DIR), headless=False, viewport={"width": 1440, "height": 950}
        )
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        return self.page

    def open(self, target: str) -> str:
        page = self.start()
        url = target.strip()
        if not re.match(r"^https?://", url, re.I):
            url = "https://" + url
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return page.url

    def search(self, query: str) -> str:
        return self.open("https://www.google.com/search?q=" + quote_plus(query))

    def snapshot(self, max_chars: int = 14000) -> str:
        page = self.start()
        title = page.title()
        url = page.url
        body = page.locator("body").inner_text(timeout=8000)
        return f"TITLE: {title}\nURL: {url}\n\n{body[:max_chars]}"

    def links(self, limit: int = 80) -> list[dict]:
        page = self.start()
        return page.locator("a").evaluate_all(
            """els => els.map((a,i)=>({i,text:(a.innerText||a.getAttribute('aria-label')||'').trim(),href:a.href}))
            .filter(x=>x.text||x.href).slice(0, arguments[0])""", limit
        )

    def click(self, target: str) -> str:
        if _BLOCKED_TERMS.search(target):
            raise PermissionError("Sensitive browser action blocked. JARVIS will prepare it, but you must perform/confirm the final action manually.")
        page = self.start()
        loc = page.get_by_text(target, exact=False).first
        if loc.count() == 0:
            loc = page.locator(target).first
        loc.click(timeout=15000)
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        return self.snapshot(6000)

    def fill(self, selector: str, value: str) -> str:
        page = self.start()
        page.locator(selector).first.fill(value)
        return f"Filled {selector}."

    def press(self, selector: str, key: str) -> str:
        if _BLOCKED_TERMS.search(key):
            raise PermissionError("Sensitive browser action blocked.")
        page = self.start()
        page.locator(selector).first.press(key)
        return self.snapshot(6000)

    def scroll(self, direction: str = "down") -> str:
        page = self.start()
        delta = 850 if direction.lower() != "up" else -850
        page.mouse.wheel(0, delta)
        return self.snapshot(5000)

    def screenshot(self) -> str:
        page = self.start()
        path = SCREENSHOT_DIR / "latest.png"
        page.screenshot(path=str(path), full_page=True)
        return str(path)

    def close(self):
        if self.context:
            self.context.close()
        if self._pw:
            self._pw.stop()
        self.context = self.page = self._pw = None


_BROWSER = UniversalBrowser()


def browser_open(target: str) -> str:
    return f"Browser opened: {_BROWSER.open(target)}"


def browser_search(query: str) -> str:
    return f"Search opened: {_BROWSER.search(query)}\n\n{_BROWSER.snapshot(7000)}"


def browser_snapshot() -> str:
    return _BROWSER.snapshot()


def browser_links(limit: int = 50) -> str:
    rows = _BROWSER.links(limit)
    return "\n".join(f"[{x['i']}] {x['text'][:100]} — {x['href']}" for x in rows)


def browser_click(target: str) -> str:
    return _BROWSER.click(target)


def browser_fill(selector: str, value: str) -> str:
    return _BROWSER.fill(selector, value)


def browser_press(selector: str, key: str) -> str:
    return _BROWSER.press(selector, key)


def browser_scroll(direction: str = "down") -> str:
    return _BROWSER.scroll(direction)


def browser_screenshot() -> str:
    return _BROWSER.screenshot()

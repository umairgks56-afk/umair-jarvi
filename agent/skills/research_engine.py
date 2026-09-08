"""Browser research and note-taking tools for JARVIS.

The research tool uses a real Playwright browser when available. It searches the web,
opens result pages, extracts readable text, and saves a compact Markdown research note.
It intentionally does not submit forms, log in, or perform purchases.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus, urlparse

try:
    from playwright.sync_api import sync_playwright
except Exception:  # pragma: no cover
    sync_playwright = None

from config import DATA_DIR

RESEARCH_DIR = DATA_DIR / "research"
RESEARCH_DIR.mkdir(parents=True, exist_ok=True)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:70] or "research"


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "")
    return text.strip()


def research_web(query: str, max_sources: int = 5) -> dict:
    if not query.strip():
        return {"ok": False, "error": "Research topic is empty."}
    if sync_playwright is None:
        return {"ok": False, "error": "Playwright is not installed. Run: pip install -r requirements.txt && playwright install chromium"}

    results = []
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto("https://www.google.com/search?q=" + quote_plus(query), wait_until="domcontentloaded", timeout=30000)
            links = page.locator("a").evaluate_all("els => els.map(a => ({t:a.innerText,h:a.href})).filter(x => x.h)")
            seen = set()
            candidates = []
            for item in links:
                url = item.get("h", "")
                title = _clean(item.get("t", ""))
                host = urlparse(url).netloc.lower()
                if not url.startswith("http") or "google." in host or not title or url in seen:
                    continue
                seen.add(url)
                candidates.append((title, url))
                if len(candidates) >= max_sources * 3:
                    break

            for title, url in candidates:
                if len(results) >= max_sources:
                    break
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    text = page.locator("body").inner_text(timeout=5000)
                    text = _clean(text)
                    if len(text) < 250:
                        continue
                    results.append({"title": title or page.title(), "url": url, "text": text[:5000]})
                except Exception as exc:
                    errors.append(f"{url}: {exc}")
        finally:
            browser.close()

    if not results:
        return {"ok": False, "error": "No readable sources were found.", "errors": errors}

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    filename = RESEARCH_DIR / f"{_slug(query)}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    lines = [f"# JARVIS Research: {query}", "", f"Generated: {timestamp}", "", "## Sources", ""]
    for i, source in enumerate(results, 1):
        lines += [f"### {i}. {source['title']}", source["url"], "", source["text"], ""]
    filename.write_text("\n".join(lines), encoding="utf-8")
    return {"ok": True, "query": query, "sources": results, "note": str(filename)}

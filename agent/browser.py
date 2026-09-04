"""Browser control for JARVIS using Playwright."""
from __future__ import annotations

from urllib.parse import quote_plus


class BrowserController:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self._playwright = None
        self.browser = None
        self.page = None

    def start(self):
        if self.page is not None:
            return self.page
        from playwright.sync_api import sync_playwright
        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch(headless=self.headless)
        context = self.browser.new_context()
        self.page = context.new_page()
        return self.page

    def open(self, url: str):
        page = self.start()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        page.goto(url, wait_until="domcontentloaded")
        return page.url

    def search_google(self, query: str):
        return self.open("https://www.google.com/search?q=" + quote_plus(query))

    def type_text(self, selector: str, text: str):
        self.start().locator(selector).fill(text)

    def click(self, selector: str):
        self.start().locator(selector).click()

    def screenshot(self, path: str = "data/browser.png"):
        self.start().screenshot(path=path, full_page=True)
        return path

    def close(self):
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()
        self.browser = self.page = self._playwright = None

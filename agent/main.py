from core.ai import AIClient
from core.prompt import SYSTEM_PROMPT
from memory.store import MemoryStore
from skills.pc_control import open_app, open_url, system_info, confirmation_required
from skills.file_tools import find_files, read_file
from skills.duplicate_scanner import find_duplicates, format_duplicates
from skills.communications import whatsapp_prepare, email_prepare
from skills.research_engine import research_web
from skills.orchestrator import build_plan
from skills.audit_log import record
from integrations.registry import list_integrations
from skills.browser_operator import browser_open, browser_search, browser_snapshot, browser_links, browser_click, browser_fill, browser_press, browser_scroll, browser_screenshot
from skills.browser_agent import BrowserAgent
from skills.browser_mission import research_mission
from config import MEMORY_DB, USER_NAME


class Jarvis:
    def __init__(self):
        self.ai = AIClient()
        self.memory = MemoryStore(MEMORY_DB)
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.last_target = None
        self.pending_action = None

    def handle(self, text: str):
        text = text.strip()
        if not text:
            return "I'm listening."
        low = text.lower()
        record("user_request", "received", text)

        if low in {"hello", "hi", "hey", "hey jarvis", "salam", "assalam o alaikum", "good morning", "good evening", "good night"}:
            return f"Hello {USER_NAME}. JARVIS online hai. How can I help?"

        if low in {"yes", "confirm", "confirmed", "send it", "go ahead", "haan", "han", "kardo"} and self.pending_action:
            action = self.pending_action
            self.pending_action = None
            result = action()
            record("confirmed_action", "completed", str(result))
            return result

        duplicate_phrases = (
            "duplicate files", "duplicate file", "duplicates", "duplicate check",
            "duplicate scan", "duplicates check", "meri duplicate files",
            "pc mein duplicate", "pc ma duplicate", "mere pc mein duplicate",
            "mere pc ma duplicate", "pc ke duplicate", "pc k duplicate",
        )
        if any(p in low for p in duplicate_phrases):
            groups = find_duplicates()
            record("duplicate_scan", "completed", f"{len(groups)} duplicate groups")
            return format_duplicates(groups)

        if low.startswith(("research mission ", "browser research ", "chatgpt se research ", "chatgpt research ")):
            goal = text.split(" ", 2)[-1].strip()
            result = research_mission(goal)
            if not result.get("ok"):
                return "Research mission failed: " + result.get("error", result.get("message", "unknown error"))
            return f"Research mission complete. PDF saved: {result['pdf']}\nSources/URLs captured: {len(result['sources'])}"

        browser_mission_prefixes = ("browser agent ", "browser mein karo ", "browser me karo ", "browser par karo ", "browser karo ")
        if low.startswith(browser_mission_prefixes):
            goal = text.split(" ", 2)[-1].strip()
            result = BrowserAgent(self.ai).run(goal)
            if result.get("blocked"):
                return "Main sensitive final action tak pohanch gaya hoon. " + result.get("message", "Aap manually finish karein.")
            if not result.get("ok"):
                return "Browser task stopped safely: " + result.get("error", "unknown error")
            return result.get("message", "Browser task complete.")

        play_markers = ("play ", "chalao ", "bajao ", "laga do ", "sunao ")
        if any(m in low for m in play_markers) and "youtube" in low:
            query = low
            for prefix in play_markers:
                if query.startswith(prefix):
                    query = query[len(prefix):]
                    break
            for marker in (" on youtube", " youtube par", " youtube pe", " youtube mein", " youtube ma"):
                query = query.replace(marker, "")
            query = query.replace("youtube", "").strip()
            url = "https://www.youtube.com/results?search_query=" + query.replace(" ", "+")
            browser_open(url)
            result = BrowserAgent(self.ai).run(f"Find and play the best matching YouTube result for: {query}")
            if result.get("blocked"):
                return "YouTube open hai, lekin final action manually complete karna hoga."
            return result.get("message", "YouTube search opened.") if result.get("ok") else "YouTube open ho gaya, lekin result select nahi ho saka."

        if low.startswith(("open ", "khol ", "kholo ", "launch ", "start ")):
            target = text.split(" ", 1)[1].strip()
            if target.lower() in {"chrome", "google chrome"}:
                return open_app("chrome")
            if target.lower() in {"notepad", "calculator", "calc", "explorer", "file explorer"}:
                return open_app(target)
            return browser_open(target)

        if low.startswith(("search ", "google search ", "online search ", "web search ")):
            query = text.split(" ", 1)[1].strip()
            return browser_search(query)

        browser_phrases = ("browser mein ", "browser me ", "browser par ", "browser pe ", "website par ", "website pe ")
        if any(low.startswith(p) for p in browser_phrases):
            goal = text.split(" ", 1)[1].strip()
            result = BrowserAgent(self.ai).run(goal)
            if result.get("ok"):
                return result.get("message", "Browser task complete.")
            return "Browser task stopped safely: " + result.get("error", "unknown error")

        if low in {"system info", "pc info", "computer info", "mere pc ki info"}:
            return str(system_info())

        if low.startswith("find files"):
            query = text[len("find files"):].strip()
            return str(find_files(query))

        if low.startswith("read file"):
            path = text[len("read file"):].strip()
            return read_file(path)

        if low.startswith("plan "):
            return str(build_plan(text[len("plan "):].strip()))

        if low.startswith("connect "):
            name = text[len("connect "):].strip()
            return str(list_integrations()) + f"\nRequested connection: {name}"

        self.messages.append({"role": "user", "content": text})
        reply = self.ai.chat(self.messages)
        self.messages.append({"role": "assistant", "content": reply})
        self.memory.remember("last_user_request", text)
        self.memory.remember("last_jarvis_response", reply)
        record("chat", "completed", reply[:1000])
        return reply

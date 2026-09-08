from core.ollama import OllamaClient
from core.prompt import SYSTEM_PROMPT
from memory.store import MemoryStore
from skills.pc_control import open_app, open_url, system_info, confirmation_required
from skills.file_tools import find_files, read_file
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
        self.ai = OllamaClient()
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

        if low in {"yes", "confirm", "confirmed", "send it", "go ahead", "haan", "han", "kardo"} and self.pending_action:
            action = self.pending_action
            self.pending_action = None
            result = action()
            record("confirmed_action", "completed", str(result))
            return result

        if low.startswith(("research mission ", "browser research ", "chatgpt se research ", "chatgpt research ")):
            goal = text.split(" ", 2)[-1].strip()
            result = research_mission(goal)
            if not result.get("ok"):
                return "Research mission failed: " + result.get("error", result.get("message", "unknown error"))
            return f"Research mission complete. PDF saved: {result['pdf']}\nSources/URLs captured: {len(result['sources'])}"

        if low.startswith(("browser agent ", "browser mein karo ", "browser me karo ", "browser par karo ", "browser karo ")):
            goal = text.split(" ", 2)[-1].strip()
            result = BrowserAgent(self.ai).run(goal)
            if result.get("blocked"):
                return "Main sensitive final action tak pohanch gaya hoon. " + result.get("message", "Aap manually finish karein.")
            if not result.get("ok"):
                return "Browser task stopped safely: " + result.get("error", "unknown error")
            return result.get("message", "Browser task complete.")

        if low.startswith(("browser search ", "search browser for ", "browser mein search ", "google par search ")):
            query = text.split(" ", 2)[-1].strip()
            return browser_search(query)
        if low.startswith(("browser open ", "website kholo ", "browser kholo ", "open website ")):
            target = text.split(" ", 2)[-1].strip()
            return browser_open(target)
        if low in {"browser status", "browser kya dekh raha hai", "browser dekho", "page dekho"}:
            return browser_snapshot()
        if low in {"browser links", "page links", "links dekho"}:
            return browser_links()
        if low.startswith("browser click "):
            return browser_click(text[len("browser click "):].strip())
        if low.startswith("browser fill "):
            payload = text[len("browser fill "):].strip().split("|", 1)
            if len(payload) != 2:
                return "Format: browser fill selector | value"
            return browser_fill(payload[0].strip(), payload[1].strip())
        if low.startswith("browser press "):
            payload = text[len("browser press "):].strip().split("|", 1)
            if len(payload) != 2:
                return "Format: browser press selector | key"
            return browser_press(payload[0].strip(), payload[1].strip())
        if low.startswith("browser scroll"):
            direction = "up" if " up" in low else "down"
            return browser_scroll(direction)
        if low in {"browser screenshot", "take browser screenshot"}:
            return "Screenshot saved: " + browser_screenshot()

        if low.startswith(("plan ", "make a plan ", "plan this ", "iska plan ")):
            goal = text.split(" ", 1)[1].strip()
            plan = build_plan(goal)
            record("plan_created", "ok", goal)
            lines = [f"Plan: {plan['goal']}", "", "Execution is permission-gated:"]
            lines += [f"{step['id']}. {step['description']}" for step in plan["steps"]]
            return "\n".join(lines)

        if low.startswith("remember "):
            item = text[9:].strip()
            if " is " in item.lower():
                key, value = item.split(" is ", 1)
            else:
                key, value = "note", item
            self.memory.remember(key.strip(), value.strip())
            record("memory_write", "ok", key.strip())
            return "Done. Yaad rakh liya."

        if "what do you remember" in low or "kya yaad" in low:
            rows = self.memory.recent()
            return "\n".join(f"• {r['key']}: {r['value']}" for r in rows) or "Abhi meri memory mein kuch nahi hai."

        if low in {"hello", "hi", "hey jarvis", "salam", "assalam o alaikum"}:
            return f"Hello {USER_NAME}. JARVIS online hai. How can I help?"

        research_prefixes = ("research ", "research on ", "search web for ", "web research ", "internet par research ", "is topic par research ")
        if low.startswith(research_prefixes):
            topic = text
            for prefix in research_prefixes:
                if low.startswith(prefix):
                    topic = text[len(prefix):].strip()
                    break
            result = research_web(topic)
            if not result.get("ok"):
                record("research", "failed", result.get("error", "unknown error"))
                return "Research failed: " + result.get("error", "unknown error")
            record("research", "completed", f"{topic} | {len(result['sources'])} sources")
            source_lines = "\n".join(f"• {s['title']} — {s['url']}" for s in result["sources"])
            return f"Research complete. {len(result['sources'])} sources checked.\n\n{source_lines}\n\nNote saved: {result['note']}"

        if "what integrations" in low or "connected services" in low or "connections" == low:
            return "\n".join(f"• {x['name']}: {x['status']} — {', '.join(x['capabilities'])}" for x in list_integrations())

        if low.startswith(("find file ", "search file ", "find my file ", "search my files ")):
            query = text.split(" ", 2)[-1].strip()
            rows = find_files(query)
            if not rows:
                return f"Mujhe '{query}' naam se configured folders mein file nahi mili."
            record("file_search", "ok", query)
            return "\n".join(f"• {r['name']} — {r['path']}" for r in rows)

        if low.startswith(("read file ", "open file ", "read my pdf ", "read pdf ")):
            path = text.split(" ", 2)[-1].strip()
            result = read_file(path)
            record("file_read", "ok", path)
            return result

        if any(x in low for x in ["scan my files", "scan my documents", "meri files dekho", "mera pdf dekho"]):
            rows = find_files("", limit=50)
            if not rows:
                return "Configured folders mein readable documents nahi mile."
            return "Maine ye files locate ki hain:\n" + "\n".join(f"• {r['name']} — {r['path']}" for r in rows)

        if low.startswith("whatsapp ") or low.startswith("send whatsapp "):
            payload = text.split(" ", 2)[-1].strip()
            parts = payload.split("|", 1)
            if len(parts) != 2:
                return "Format: whatsapp +923001234567 | message"
            phone, message = parts
            self.pending_action = lambda p=phone, m=message: whatsapp_prepare(p, m)
            record("whatsapp_prepare", "pending_confirmation", phone)
            return f"WhatsApp message ready for {phone}. Send karne ke liye 'confirm' bolo."

        if low.startswith("email ") or low.startswith("send email "):
            payload = text.split(" ", 1)[1].strip()
            parts = payload.split("|", 2)
            if len(parts) != 3:
                return "Format: email recipient@example.com | subject | message"
            to, subject, body = parts
            self.pending_action = lambda t=to, s=subject, b=body: email_prepare(t, s, b)
            record("email_prepare", "pending_confirmation", to)
            return f"Email ready for {to}. Send/prepare karne ke liye 'confirm' bolo."

        if any(x in low for x in ["chrome kholo", "open chrome", "chrome open"]):
            self.last_target = "chrome"
            return open_app("chrome")[1]
        if any(x in low for x in ["youtube kholo", "open youtube", "youtube open"]):
            self.last_target = "youtube"
            return open_url("https://www.youtube.com")[1]
        if any(x in low for x in ["google kholo", "open google", "google open"]):
            self.last_target = "google"
            return open_url("https://www.google.com")[1]
        if any(x in low for x in ["playlist kholo", "mera playlist kholo", "open my playlist"]):
            if self.last_target == "youtube":
                return open_url("https://www.youtube.com/feed/playlists")[1]
            return "Pehle YouTube kholo ya apni playlist ka link mujhe bata do."
        if low.startswith("open "):
            target = text[5:].strip()
            if target.startswith(("http://", "https://", "www.")) or ".com" in target:
                return open_url(target)[1]
            return open_app(target)[1]
        if "system info" in low or "pc status" in low or "system status" in low:
            info = system_info()
            return f"PC status: CPU {info['cpu_percent']}% | RAM {info['memory_percent']}%"
        if confirmation_required(text):
            record("high_impact_request", "blocked", text)
            return "That action is high-impact. Give me explicit confirmation before I execute it."

        context = self.memory.recent(6)
        memory_text = "\n".join(f"{x['key']}: {x['value']}" for x in context)
        prompt = f"Known memory:\n{memory_text}\n\nUser: {text}"
        self.messages.append({"role": "user", "content": prompt})
        answer = self.ai.chat(self.messages)
        self.messages.append({"role": "assistant", "content": answer})
        record("llm_response", "ok", text)
        return answer


if __name__ == "__main__":
    jarvis = Jarvis()
    print("JARVIS online. Type 'exit' to quit.")
    while True:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() in {"exit", "quit"}:
            break
        try:
            print("JARVIS:", jarvis.handle(text))
        except Exception as exc:
            print("JARVIS: Error:", exc)

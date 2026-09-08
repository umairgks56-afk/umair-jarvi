from core.ollama import OllamaClient
from core.prompt import SYSTEM_PROMPT
from memory.store import MemoryStore
from skills.pc_control import open_app, open_url, system_info, confirmation_required
from skills.file_tools import find_files, read_file
from skills.communications import whatsapp_prepare, email_prepare
from skills.research_engine import research_web
from integrations.registry import list_integrations
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

        if low in {"yes", "confirm", "confirmed", "send it", "go ahead", "haan", "han", "kardo"} and self.pending_action:
            action = self.pending_action
            self.pending_action = None
            return action()

        if low.startswith("remember "):
            item = text[9:].strip()
            if " is " in item.lower():
                key, value = item.split(" is ", 1)
            else:
                key, value = "note", item
            self.memory.remember(key.strip(), value.strip())
            return "Done. Yaad rakh liya."

        if "what do you remember" in low or "kya yaad" in low:
            rows = self.memory.recent()
            return "\n".join(f"• {r['key']}: {r['value']}" for r in rows) or "Abhi meri memory mein kuch nahi hai."

        if low in {"hello", "hi", "hey jarvis", "salam", "assalam o alaikum"}:
            return f"Hello {USER_NAME}. JARVIS online hai. How can I help?"

        # Browser research: searches the web, reads several sources, and saves a Markdown note.
        research_prefixes = ("research ", "research on ", "search web for ", "web research ", "internet par research ", "is topic par research ")
        if low.startswith(research_prefixes):
            topic = text
            for prefix in research_prefixes:
                if low.startswith(prefix):
                    topic = text[len(prefix):].strip()
                    break
            result = research_web(topic)
            if not result.get("ok"):
                return "Research failed: " + result.get("error", "unknown error")
            source_lines = "\n".join(f"• {s['title']} — {s['url']}" for s in result["sources"])
            return f"Research complete. {len(result['sources'])} sources checked.\n\n{source_lines}\n\nNote saved: {result['note']}"

        if "what integrations" in low or "connected services" in low or "connections" == low:
            return "\n".join(f"• {x['name']}: {x['status']} — {', '.join(x['capabilities'])}" for x in list_integrations())

        if low.startswith(("find file ", "search file ", "find my file ", "search my files ")):
            query = text.split(" ", 2)[-1].strip()
            rows = find_files(query)
            if not rows:
                return f"Mujhe '{query}' naam se configured folders mein file nahi mili."
            return "\n".join(f"• {r['name']} — {r['path']}" for r in rows)

        if low.startswith(("read file ", "open file ", "read my pdf ", "read pdf ")):
            path = text.split(" ", 2)[-1].strip()
            return read_file(path)

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
            return f"WhatsApp message ready for {phone}. Send karne ke liye 'confirm' bolo."

        if low.startswith("email ") or low.startswith("send email "):
            payload = text.split(" ", 1)[1].strip()
            parts = payload.split("|", 2)
            if len(parts) != 3:
                return "Format: email recipient@example.com | subject | message"
            to, subject, body = parts
            self.pending_action = lambda t=to, s=subject, b=body: email_prepare(t, s, b)
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
            return "That action is high-impact. Give me explicit confirmation before I execute it."

        context = self.memory.recent(6)
        memory_text = "\n".join(f"{x['key']}: {x['value']}" for x in context)
        prompt = f"Known memory:\n{memory_text}\n\nUser: {text}"
        self.messages.append({"role": "user", "content": prompt})
        answer = self.ai.chat(self.messages)
        self.messages.append({"role": "assistant", "content": answer})
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

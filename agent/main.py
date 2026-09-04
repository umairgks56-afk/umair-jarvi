from core.ollama import OllamaClient
from core.prompt import SYSTEM_PROMPT
from memory.store import MemoryStore
from skills.pc_control import open_app, open_url, system_info, confirmation_required
from config import MEMORY_DB, USER_NAME


class Jarvis:
    def __init__(self):
        self.ai = OllamaClient()
        self.memory = MemoryStore(MEMORY_DB)
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.last_target = None

    def handle(self, text: str):
        low = text.lower().strip()

        if low.startswith("remember "):
            item = text[9:].strip()
            if " is " in item.lower():
                key, value = item.split(" is ", 1)
            else:
                key, value = "note", item
            self.memory.remember(key.strip(), value.strip())
            return "Yaad rakh liya."

        if "what do you remember" in low or "kya yaad" in low:
            rows = self.memory.recent()
            return "\n".join(f"• {r['key']}: {r['value']}" for r in rows) or "Abhi meri memory mein kuch nahi hai."

        if low in {"hello", "hi", "hey jarvis", "salam", "assalam o alaikum"}:
            return f"Hello {USER_NAME}. JARVIS online hai."

        # Natural-language PC/browser commands. Wake word is optional.
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
            return f"CPU {info['cpu_percent']}% | RAM {info['memory_percent']}%"

        if confirmation_required(text):
            return "Ye action high-impact hai. Explicit confirmation ke baghair main execute nahi karunga."

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

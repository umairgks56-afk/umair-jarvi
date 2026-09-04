import requests
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

class OllamaClient:
    def __init__(self, model=OLLAMA_MODEL):
        self.model = model
        self.url = f"{OLLAMA_BASE_URL}/api/chat"

    def chat(self, messages, temperature=0.7):
        response = requests.post(
            self.url,
            json={"model": self.model, "messages": messages, "stream": False,
                  "options": {"temperature": temperature}},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    def health(self):
        try:
            r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            return r.ok
        except requests.RequestException:
            return False

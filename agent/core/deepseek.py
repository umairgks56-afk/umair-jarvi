"""DeepSeek API client with the same interface used by JARVIS/Ollama."""
from __future__ import annotations

import requests

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL


class DeepSeekClient:
    def __init__(self, model: str = DEEPSEEK_MODEL):
        self.model = model
        self.url = f"{DEEPSEEK_BASE_URL}/chat/completions"

    @property
    def configured(self) -> bool:
        return bool(DEEPSEEK_API_KEY)

    def chat(self, messages, temperature=0.7):
        if not DEEPSEEK_API_KEY:
            raise RuntimeError("DEEPSEEK_API_KEY is not configured")
        response = requests.post(
            self.url,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "temperature": temperature,
                "thinking": {"type": "enabled", "reasoning_effort": "high"},
            },
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def chat_with_image(self, prompt, image_b64, model=None, temperature=0.2):
        if not DEEPSEEK_API_KEY:
            raise RuntimeError("DEEPSEEK_API_KEY is not configured")
        response = requests.post(
            self.url,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": model or self.model,
                "messages": [{"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                ]}],
                "stream": False,
                "temperature": temperature,
            },
            timeout=180,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def health(self):
        return bool(DEEPSEEK_API_KEY)

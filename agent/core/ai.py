"""Unified AI provider: DeepSeek first, Ollama fallback."""
from __future__ import annotations

from config import AI_PROVIDER, DEEPSEEK_API_KEY
from core.deepseek import DeepSeekClient
from core.ollama import OllamaClient


class AIClient:
    def __init__(self):
        self.deepseek = DeepSeekClient()
        self.ollama = OllamaClient()
        self.provider = "deepseek" if AI_PROVIDER == "deepseek" and DEEPSEEK_API_KEY else "ollama"
        self.model = self.deepseek.model if self.provider == "deepseek" else self.ollama.model

    def chat(self, messages, temperature=0.7):
        if self.provider == "deepseek":
            try:
                return self.deepseek.chat(messages, temperature=temperature)
            except Exception:
                # Keep JARVIS usable if the API is temporarily unavailable.
                self.provider = "ollama"
                self.model = self.ollama.model
        return self.ollama.chat(messages, temperature=temperature)

    def chat_with_image(self, prompt, image_b64, model=None, temperature=0.2):
        if self.provider == "deepseek":
            try:
                return self.deepseek.chat_with_image(prompt, image_b64, model=model, temperature=temperature)
            except Exception:
                self.provider = "ollama"
                self.model = self.ollama.model
        return self.ollama.chat_with_image(prompt, image_b64, model=model, temperature=temperature)

    def health(self):
        if self.provider == "deepseek":
            return self.deepseek.health()
        return self.ollama.health()

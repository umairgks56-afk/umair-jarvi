"""Screen capture + Ollama vision helper."""
from __future__ import annotations

import base64
import io
import os


class ScreenVision:
    def __init__(self, ollama_client):
        self.ai = ollama_client
        self.model = os.getenv("OLLAMA_VISION_MODEL", "llava")

    def capture(self, path: str = "data/screen.png") -> str:
        import pyautogui
        os.makedirs(os.path.dirname(path), exist_ok=True)
        image = pyautogui.screenshot()
        image.save(path)
        return path

    def describe(self, prompt: str = "Describe what is visible on this screen and identify the main actionable UI elements.") -> str:
        path = self.capture()
        with open(path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("ascii")
        return self.ai.chat_with_image(prompt, image_b64, model=self.model)

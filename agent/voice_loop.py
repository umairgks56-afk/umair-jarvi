"""Hands-free JARVIS loop.

Start after installing the optional voice dependencies. The wake-word fallback
uses short Whisper clips, so it is not as efficient as a dedicated hotword
engine yet, but it is fully local.
"""
from __future__ import annotations

import os
import sys

from main import Jarvis
from voice import VoiceEngine, WakeWord


def run():
    jarvis = Jarvis()
    voice = VoiceEngine(model_size=os.getenv("WHISPER_MODEL", "base"))
    wake = WakeWord(voice)
    voice.speak("JARVIS online. Say Hey JARVIS when you need me.")

    while True:
        try:
            if not wake.wait_for_wake_word():
                continue
            voice.speak("Yes, Umair?")
            command = voice.listen_once(seconds=int(os.getenv("VOICE_COMMAND_SECONDS", "8")))
            if not command:
                continue
            reply = jarvis.handle(command)
            print(f"UMAIR > {command}\nJARVIS > {reply}")
            voice.speak(reply)
        except KeyboardInterrupt:
            voice.speak("Goodbye, Umair.")
            return
        except Exception as exc:
            print(f"Voice loop error: {exc}", file=sys.stderr)


if __name__ == "__main__":
    run()

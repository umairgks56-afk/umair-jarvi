"""Local voice input/output for JARVIS.

Optional dependencies:
  pip install faster-whisper sounddevice numpy pyttsx3

Voice output is intentionally local-first. On Windows, pyttsx3 uses the
installed SAPI voices, so the engine can select a natural-sounding voice
without requiring an internet service or making a phone mandatory.

The wake-word layer is intentionally separated so it can later be replaced by
openWakeWord without changing the rest of JARVIS.
"""
from __future__ import annotations

import os
from typing import Optional


class VoiceEngine:
    def __init__(self, model_size: str = "base", language: Optional[str] = None):
        self.model_size = model_size
        self.language = language
        self._model = None
        self._tts = None

    def _load_stt(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            device = os.getenv("WHISPER_DEVICE", "cpu")
            compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
            self._model = WhisperModel(self.model_size, device=device, compute_type=compute_type)
        return self._model

    def _load_tts(self):
        if self._tts is None:
            import pyttsx3

            self._tts = pyttsx3.init()

            # A slightly slower pace sounds more conversational than the
            # default robotic/announcement style. Every setting remains
            # configurable through .env so the user can tune it locally.
            rate = int(os.getenv("JARVIS_TTS_RATE", "165"))
            volume = float(os.getenv("JARVIS_TTS_VOLUME", "0.95"))
            self._tts.setProperty("rate", max(120, min(rate, 210)))
            self._tts.setProperty("volume", max(0.0, min(volume, 1.0)))

            self._select_voice()
        return self._tts

    def _select_voice(self) -> None:
        """Pick a natural installed voice, preferring configurable voice IDs.

        On Windows this usually finds Microsoft SAPI voices such as David,
        Mark, Guy, or Zira. If none match, the first usable installed voice is
        retained rather than failing startup.
        """
        if self._tts is None:
            return

        requested = os.getenv("JARVIS_TTS_VOICE", "").strip().lower()
        preferred = [
            name.strip().lower()
            for name in os.getenv(
                "JARVIS_TTS_PREFERRED_VOICES",
                "Microsoft David,Microsoft Mark,Microsoft Guy,Microsoft Zira"
            ).split(",")
            if name.strip()
        ]

        voices = self._tts.getProperty("voices") or []
        candidates = [requested] if requested else preferred

        for wanted in candidates:
            for voice in voices:
                voice_id = str(getattr(voice, "id", ""))
                voice_name = str(getattr(voice, "name", ""))
                haystack = f"{voice_id} {voice_name}".lower()
                if wanted and wanted in haystack:
                    self._tts.setProperty("voice", voice.id)
                    return

        # Keep the OS default if no preferred voice is installed.
        # This makes JARVIS portable across Windows machines.

    def speak(self, text: str) -> None:
        if not text:
            return
        engine = self._load_tts()
        engine.say(text.strip())
        engine.runAndWait()

    def transcribe_file(self, audio_path: str) -> str:
        model = self._load_stt()
        segments, _ = model.transcribe(audio_path, language=self.language, vad_filter=True)
        return " ".join(segment.text.strip() for segment in segments).strip()

    def listen_once(self, seconds: int = 6, sample_rate: int = 16000) -> str:
        """Record one short microphone clip and return its transcription."""
        import numpy as np
        import sounddevice as sd
        import tempfile
        import wave

        recording = sd.rec(
            int(seconds * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
        )
        sd.wait()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            path = tmp.name
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(np.asarray(recording).tobytes())
        try:
            return self.transcribe_file(path)
        finally:
            try:
                os.remove(path)
            except OSError:
                pass


class WakeWord:
    """Simple wake-word detector with a low-dependency fallback.

    For V0.1 this listens in short clips and checks the transcript for
    'hey jarvis' / 'jarvis'. A true always-on detector can be plugged in later.
    """
    def __init__(self, voice: VoiceEngine):
        self.voice = voice
        self.phrases = ("hey jarvis", "jarvis")

    def wait_for_wake_word(self, max_attempts: int | None = None) -> bool:
        attempts = 0
        while max_attempts is None or attempts < max_attempts:
            text = self.voice.listen_once(seconds=3).lower()
            if any(phrase in text for phrase in self.phrases):
                return True
            attempts += 1
        return False

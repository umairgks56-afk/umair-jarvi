import os
import tempfile
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
import pyttsx3
from faster_whisper import WhisperModel

from main import Jarvis

SAMPLE_RATE = int(os.getenv("VOICE_SAMPLE_RATE", "16000"))
RECORD_SECONDS = float(os.getenv("VOICE_RECORD_SECONDS", "5"))
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")


def speak(engine, text: str):
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()


def record_wav(path: str):
    frames = int(SAMPLE_RATE * RECORD_SECONDS)
    print("Listening... speak now")
    audio = sd.rec(frames, samplerate=SAMPLE_RATE, channels=1, dtype="float32")
    sd.wait()
    audio = np.clip(audio, -1.0, 1.0)
    import wave
    pcm = (audio[:, 0] * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm.tobytes())


def main():
    print("Loading JARVIS voice engine...")
    model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    engine = pyttsx3.init()
    jarvis = Jarvis()
    speak(engine, "JARVIS online. Direct voice commands are enabled.")
    print("No wake word is required. Say a command directly. Press Ctrl+C to stop.")

    while True:
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                wav_path = tmp.name
            try:
                record_wav(wav_path)
                segments, _ = model.transcribe(wav_path, beam_size=3, vad_filter=True)
                text = " ".join(segment.text.strip() for segment in segments).strip()
                if not text:
                    continue
                print(f"YOU: {text}")
                if text.lower() in {"exit", "quit", "stop listening"}:
                    speak(engine, "Voice mode stopped.")
                    break
                reply = jarvis.handle(text)
                speak(engine, reply)
            finally:
                Path(wav_path).unlink(missing_ok=True)
        except KeyboardInterrupt:
            print("\nVoice mode stopped.")
            break
        except Exception as exc:
            print(f"Voice error: {exc}")
            time.sleep(1)


if __name__ == "__main__":
    main()

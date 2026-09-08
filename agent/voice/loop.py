import os
import tempfile
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
import pyttsx3
from faster_whisper import WhisperModel

AGENT_DIR = Path(__file__).resolve().parents[1]
if str(AGENT_DIR) not in os.sys.path:
    os.sys.path.insert(0, str(AGENT_DIR))

from main import Jarvis

SAMPLE_RATE = int(os.getenv("VOICE_SAMPLE_RATE", "16000"))
RECORD_SECONDS = float(os.getenv("VOICE_RECORD_SECONDS", "5"))
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")
SILENCE_RMS = float(os.getenv("VOICE_SILENCE_RMS", "0.001"))
SILENCE_PEAK = float(os.getenv("VOICE_SILENCE_PEAK", "0.01"))


def speak(engine, text: str):
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()


def record_wav(path: str) -> tuple[bool, float, float]:
    frames = int(SAMPLE_RATE * RECORD_SECONDS)
    print("Listening... speak now")
    audio = sd.rec(frames, samplerate=SAMPLE_RATE, channels=1, dtype="float32")
    sd.wait()
    audio = np.clip(audio, -1.0, 1.0)
    rms = float(np.sqrt(np.mean(np.square(audio))))
    peak = float(np.max(np.abs(audio)))

    import wave
    pcm = (audio[:, 0] * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm.tobytes())
    return (rms >= SILENCE_RMS or peak >= SILENCE_PEAK), rms, peak


def transcribe(model, wav_path: str) -> str:
    segments, _ = model.transcribe(
        wav_path,
        beam_size=1,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 350},
        language=None,
        condition_on_previous_text=False,
        temperature=0,
    )
    return " ".join(segment.text.strip() for segment in segments).strip()


def main():
    print("Loading JARVIS voice engine...")
    print(f"Microphone: {sd.query_devices(kind='input')['name']}")
    model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    engine = pyttsx3.init()
    jarvis = Jarvis()
    speak(engine, "JARVIS online. Direct voice commands are enabled.")
    print("No wake word is required. Say a command directly. Press Ctrl+C to stop.")

    quiet_cycles = 0
    while True:
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                wav_path = tmp.name
            try:
                heard, rms, peak = record_wav(wav_path)
                if not heard:
                    quiet_cycles += 1
                    # Silence is not treated as a command, but JARVIS stays socially present.
                    if quiet_cycles >= 3:
                        speak(engine, "Umair? I'm here. Kya hua? Kuch kehna tha?")
                        quiet_cycles = 0
                    continue

                quiet_cycles = 0
                text = transcribe(model, wav_path)
                if not text:
                    # Do not silently discard unclear audible speech.
                    speak(engine, "Mujhe awaaz mili, lekin baat clear nahi hui. Kya hua? Dobara batao.")
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

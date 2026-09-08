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
RECORD_SECONDS = float(os.getenv("VOICE_RECORD_SECONDS", "4"))
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")
SILENCE_RMS = float(os.getenv("VOICE_SILENCE_RMS", "0.0008"))
SILENCE_PEAK = float(os.getenv("VOICE_SILENCE_PEAK", "0.006"))
LOG_PATH = AGENT_DIR / "data" / "voice.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def log(message: str):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line)
    try:
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def speak(engine, text: str):
    log(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()


def record_wav(path: str) -> tuple[bool, float, float]:
    frames = int(SAMPLE_RATE * RECORD_SECONDS)
    log("Listening... speak now")
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
        vad_parameters={"min_silence_duration_ms": 250, "speech_pad_ms": 250},
        language=None,
        condition_on_previous_text=False,
        temperature=0,
    )
    return " ".join(segment.text.strip() for segment in segments).strip()


def main():
    log("Loading JARVIS voice engine...")
    try:
        devices = sd.query_devices()
        input_device = sd.query_devices(kind="input")
        log(f"Microphone: {input_device['name']}")
        log(f"Input devices available: {len(devices)}")
        model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        engine = pyttsx3.init()
        voices = engine.getProperty("voices") or []
        log(f"TTS voices available: {len(voices)}")
        jarvis = Jarvis()
        speak(engine, "JARVIS online. Direct voice commands are enabled.")
        log("No wake word is required. Say a command directly. Press Ctrl+C to stop.")
    except Exception as exc:
        log(f"VOICE STARTUP ERROR: {type(exc).__name__}: {exc}")
        raise

    quiet_cycles = 0
    while True:
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                wav_path = tmp.name
            try:
                heard, rms, peak = record_wav(wav_path)
                log(f"Audio level rms={rms:.6f} peak={peak:.6f}")
                if not heard:
                    quiet_cycles += 1
                    if quiet_cycles >= 4:
                        speak(engine, "Umair? I'm here. Kya hua? Kuch kehna tha?")
                        quiet_cycles = 0
                    continue

                quiet_cycles = 0
                text = transcribe(model, wav_path)
                if not text:
                    speak(engine, "Mujhe awaaz mili, lekin baat clear nahi hui. Kya hua? Dobara batao.")
                    continue

                log(f"YOU: {text}")
                if text.lower() in {"exit", "quit", "stop listening"}:
                    speak(engine, "Voice mode stopped.")
                    break

                reply = jarvis.handle(text)
                speak(engine, reply)
            finally:
                Path(wav_path).unlink(missing_ok=True)
        except KeyboardInterrupt:
            log("Voice mode stopped.")
            break
        except Exception as exc:
            log(f"VOICE RUNTIME ERROR: {type(exc).__name__}: {exc}")
            time.sleep(1)


if __name__ == "__main__":
    main()

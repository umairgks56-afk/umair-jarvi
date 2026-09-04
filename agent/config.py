import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

JARVIS_NAME = os.getenv("JARVIS_NAME", "JARVIS")
USER_NAME = os.getenv("USER_NAME", "Umair")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
MEMORY_DB = os.getenv("MEMORY_DB", str(DATA_DIR / "jarvis.db"))
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8765"))

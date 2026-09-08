from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import API_HOST, API_PORT, JARVIS_API_KEY
from main import Jarvis

app = FastAPI(title="JARVIS Local Agent", version="0.3.0")
jarvis = Jarvis()
DASHBOARD = Path(__file__).parent / "dashboard" / "index.html"


class ChatRequest(BaseModel):
    message: str


def authorize(x_jarvis_key: str | None):
    # Authentication is required whenever a key is configured.
    if JARVIS_API_KEY and x_jarvis_key != JARVIS_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid JARVIS API key")


@app.get("/")
def dashboard():
    return FileResponse(DASHBOARD)


@app.get("/health")
def health(x_jarvis_key: str | None = Header(default=None)):
    authorize(x_jarvis_key)
    return {"status": "online", "ollama": jarvis.ai.health()}


@app.post("/chat")
def chat(request: ChatRequest, x_jarvis_key: str | None = Header(default=None)):
    authorize(x_jarvis_key)
    return {"reply": jarvis.handle(request.message)}


@app.get("/vision")
def vision(x_jarvis_key: str | None = Header(default=None)):
    authorize(x_jarvis_key)
    from vision import ScreenVision
    return {"description": ScreenVision(jarvis.ai).describe()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)

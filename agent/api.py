from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from main import Jarvis

app = FastAPI(title="JARVIS Local Agent", version="0.2.0")
jarvis = Jarvis()
DASHBOARD = Path(__file__).parent / "dashboard" / "index.html"


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def dashboard():
    return FileResponse(DASHBOARD)


@app.get("/health")
def health():
    return {"status": "online", "ollama": jarvis.ai.health()}


@app.post("/chat")
def chat(request: ChatRequest):
    return {"reply": jarvis.handle(request.message)}


@app.get("/vision")
def vision():
    from vision import ScreenVision
    return {"description": ScreenVision(jarvis.ai).describe()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765)

from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import API_HOST, API_PORT, JARVIS_API_KEY
from integrations.registry import connect, disconnect, list_integrations
from main import Jarvis
from skills.audit_log import recent as recent_audit
from skills.behavior_rules import list_rules
from skills.orchestrator import build_plan
from skills.research_engine import research_web

app = FastAPI(title="JARVIS Local Agent", version="0.5.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
jarvis = Jarvis()
DASHBOARD = Path(__file__).parent / "dashboard" / "index.html"


class ChatRequest(BaseModel):
    message: str


class ResearchRequest(BaseModel):
    query: str
    max_sources: int = 5


class PlanRequest(BaseModel):
    goal: str


def authorize(x_jarvis_key: str | None):
    if JARVIS_API_KEY and x_jarvis_key != JARVIS_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid JARVIS API key")


@app.get("/")
def dashboard():
    return FileResponse(DASHBOARD)


@app.get("/health")
def health(x_jarvis_key: str | None = Header(default=None)):
    authorize(x_jarvis_key)
    return {"status": "online", "ollama": jarvis.ai.health(), "version": "0.5.0"}


@app.post("/chat")
def chat(request: ChatRequest, x_jarvis_key: str | None = Header(default=None)):
    authorize(x_jarvis_key)
    return {"reply": jarvis.handle(request.message)}


@app.post("/research")
def research(request: ResearchRequest, x_jarvis_key: str | None = Header(default=None)):
    authorize(x_jarvis_key)
    return research_web(request.query, max(1, min(request.max_sources, 10)))


@app.post("/plan")
def plan(request: PlanRequest, x_jarvis_key: str | None = Header(default=None)):
    authorize(x_jarvis_key)
    return build_plan(request.goal)


@app.get("/behavior-rules")
def behavior_rules(x_jarvis_key: str | None = Header(default=None)):
    authorize(x_jarvis_key)
    return {"rules": list_rules()}


@app.get("/audit")
def audit(limit: int = 50, x_jarvis_key: str | None = Header(default=None)):
    authorize(x_jarvis_key)
    return {"events": recent_audit(max(1, min(limit, 200)))}


@app.get("/integrations")
def integrations(x_jarvis_key: str | None = Header(default=None)):
    authorize(x_jarvis_key)
    return {"integrations": list_integrations()}


@app.post("/integrations/{integration_id}/connect")
def integration_connect(integration_id: str, x_jarvis_key: str | None = Header(default=None)):
    authorize(x_jarvis_key)
    return connect(integration_id)


@app.post("/integrations/{integration_id}/disconnect")
def integration_disconnect(integration_id: str, x_jarvis_key: str | None = Header(default=None)):
    authorize(x_jarvis_key)
    return disconnect(integration_id)


@app.get("/vision")
def vision(x_jarvis_key: str | None = Header(default=None)):
    authorize(x_jarvis_key)
    from vision import ScreenVision
    return {"description": ScreenVision(jarvis.ai).describe()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)

from fastapi import FastAPI
from pydantic import BaseModel
from main import Jarvis

app = FastAPI(title="JARVIS Local Agent", version="0.1.0")
jarvis = Jarvis()

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status":"online", "ollama": jarvis.ai.health()}

@app.post("/chat")
def chat(request: ChatRequest):
    return {"reply": jarvis.handle(request.message)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765)

# JARVIS Windows Agent

The local Python process that can talk to Ollama and perform approved Windows actions.

## Run

```powershell
cd agent
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

For the dashboard API:

```powershell
python api.py
```

The API listens only on `127.0.0.1` by default so it is not exposed to the public internet.

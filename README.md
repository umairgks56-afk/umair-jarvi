# JARVIS

Personal, local-first AI assistant for Umair.

JARVIS is designed around a Windows local agent, Ollama-powered intelligence, modular skills, memory, voice, browser automation, and an optional Vercel dashboard.

## Architecture

```text
Voice / Text -> JARVIS Core -> Planner + Memory + Safety -> Skills -> Windows / Browser / Web
                                  |
                                  +-> Ollama (local AI)

Optional: Next.js dashboard on Vercel <-> local JARVIS agent
```

## Foundation

- Local Ollama AI with no per-request API billing
- English, Urdu, Pashto, Roman Urdu, Roman Pashto and mixed-language instructions
- Persistent local SQLite memory
- Confirmation gates for high-impact actions
- Windows app/file/system tools
- Browser opening foundation
- Modular skill registry
- FastAPI bridge for the future web dashboard
- Optional voice, vision and browser dependencies

## Quick start

1. Install Python 3.11+.
2. Install Ollama and pull a model, for example `ollama pull llama3.2`.
3. Open PowerShell in `agent/`.
4. Run `python -m venv .venv` and `.venv\\Scripts\\activate`.
5. Run `pip install -r requirements.txt`.
6. Copy `.env.example` to `.env`.
7. Run `python main.py`.

Try `hello`, `Chrome kholo`, `open calculator`, or `what do you remember about me?`.

## Security

JARVIS does not treat an LLM response as permission to perform dangerous actions. Shutdown, restart, deletion, arbitrary shell commands and other high-impact operations are confirmation-gated.

## Roadmap

V0.1 brain -> V0.2 voice -> V0.3 PC control -> V0.4 browser -> V0.5 files -> V0.6 web -> V0.7 vision -> V0.8 automation -> V0.9 memory -> V1.0 dashboard -> V1.1 permissions -> V1.2 skills/plugins.

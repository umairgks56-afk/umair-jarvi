# JARVIS Windows Agent

The local Python process that talks to Ollama and performs approved Windows actions.

JARVIS is focused on personal assistance, university support, PC/browser control, voice, vision, memory, web research, local documents, notes, and a connection hub. It is not tied to eBay or e-commerce workflows.

## Run on PC

```bash
cd agent
pip install -r requirements.txt
playwright install chromium
python api.py
```

By default the API listens only on `127.0.0.1`, so JARVIS works fully on the PC without a phone.

## Web Research

The Command Center now includes a **Research Lab**. Ask JARVIS things like:

- `research BS Aesthetic Skin Care Technology career scope Pakistan 2026`
- `research latest AI agent architectures`
- `is topic par research karo: ...`

JARVIS opens a real browser, searches the web, reads several public pages, records their URLs and saves the collected research under `agent/data/research/` as Markdown. It does not log in, submit forms, purchase anything, or send messages as part of research.

## Connection Hub

The dashboard has a **Connect** style integration hub for:

- PC Files
- Browser
- Gmail
- Outlook
- WhatsApp Web
- Google Drive
- Calendar
- PC Control

Local capabilities can be enabled immediately. OAuth/browser-session services are represented by the same connector interface so their authentication can be added without changing the JARVIS core. Passwords and access tokens must never be placed in memory.db or prompts.

High-impact actions such as sending, deleting, purchasing, or submitting remain confirmation-gated.

## Optional phone remote

The phone is **not required**. It is only a remote interface to the JARVIS agent running on the PC.

1. Put the PC and phone on the same Wi-Fi/LAN.
2. In `.env`, set `API_HOST=0.0.0.0`.
3. Set a strong random `JARVIS_API_KEY`.
4. Start `python api.py`.
5. Find the PC's LAN IP (for example `192.168.1.20`).
6. On the phone browser open `http://192.168.1.20:8765`.
7. Enter the same API key in the dashboard.

Do **not** expose port 8765 directly to the public internet. For remote access outside your home/network, use a VPN such as Tailscale or another properly secured tunnel.

The same dashboard is responsive for desktop and mobile screens.

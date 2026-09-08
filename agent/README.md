# JARVIS Windows Agent

The local Python process that talks to Ollama and performs approved Windows actions.

JARVIS is focused on personal assistance, university support, PC/browser control, voice, vision, memory, and general AI help. It is not tied to eBay or e-commerce workflows.

## Run on PC

```bash
cd agent
pip install -r requirements.txt
python api.py
```

By default the API listens only on `127.0.0.1`, so JARVIS works fully on the PC without a phone.

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

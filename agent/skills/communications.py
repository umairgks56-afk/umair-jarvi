from __future__ import annotations

import urllib.parse
import webbrowser


def whatsapp_prepare(phone: str, message: str) -> str:
    clean = "".join(ch for ch in phone if ch.isdigit())
    if clean.startswith("00"):
        clean = clean[2:]
    if not clean:
        return "I need the recipient's phone number with country code."
    url = "https://web.whatsapp.com/send?phone=" + clean + "&text=" + urllib.parse.quote(message)
    webbrowser.open(url)
    return "WhatsApp chat opened with the message prepared. I will not press Send without your confirmation."


def email_prepare(to: str, subject: str, body: str) -> str:
    query = urllib.parse.urlencode({"subject": subject, "body": body})
    url = f"mailto:{urllib.parse.quote(to)}?{query}"
    webbrowser.open(url)
    return "Your email client was opened with the email prepared. I will not send it without your confirmation."

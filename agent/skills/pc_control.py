import os
import subprocess
import webbrowser
from pathlib import Path

SAFE_APPS = {
    "chrome": r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "calculator": "calc.exe",
    "notepad": "notepad.exe",
    "explorer": "explorer.exe",
}

DANGEROUS_WORDS = {"shutdown", "restart", "delete", "format"}

def open_app(name: str):
    key = name.lower().strip()
    target = SAFE_APPS.get(key)
    if not target:
        return False, f"I don't have a safe app mapping for '{name}'."
    try:
        subprocess.Popen(target, shell=False)
        return True, f"Opened {name}."
    except Exception as e:
        return False, str(e)

def open_url(url: str):
    if not url.startswith(("https://", "http://")):
        url = "https://" + url
    webbrowser.open(url)
    return True, f"Opened {url}."

def system_info():
    import psutil
    return {"cpu_percent": psutil.cpu_percent(), "memory_percent": psutil.virtual_memory().percent}

def confirmation_required(command: str):
    text = command.lower()
    return any(word in text for word in DANGEROUS_WORDS)

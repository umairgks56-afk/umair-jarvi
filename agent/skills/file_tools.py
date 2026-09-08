from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

try:
    from pypdf import PdfReader
except ImportError:  # optional until dependency is installed
    PdfReader = None

DEFAULT_EXTENSIONS = {
    ".pdf", ".txt", ".md", ".csv", ".json", ".docx", ".xlsx", ".pptx"
}


def allowed_roots() -> list[Path]:
    raw = os.getenv("JARVIS_DATA_ROOTS", "")
    if not raw:
        return [Path.home() / "Documents", Path.home() / "Downloads", Path.home() / "Desktop"]
    return [Path(p).expanduser().resolve() for p in raw.split(";") if p.strip()]


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def find_files(query: str, limit: int = 30) -> list[dict]:
    q = query.lower().strip()
    results = []
    for root in allowed_roots():
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in DEFAULT_EXTENSIONS:
                continue
            if q in path.name.lower():
                results.append({"name": path.name, "path": str(path), "size": path.stat().st_size})
                if len(results) >= limit:
                    return results
    return results


def _read_pdf(path: Path) -> str:
    if PdfReader is None:
        return "PDF reader dependency is not installed yet. Run: pip install -r agent/requirements.txt"
    reader = PdfReader(str(path))
    chunks = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")
    return "\n".join(chunks).strip()


def read_file(path_text: str, max_chars: int = 12000) -> str:
    path = Path(path_text).expanduser().resolve()
    if not any(_inside(path, root) for root in allowed_roots()):
        return "I can only read files inside my configured JARVIS data folders."
    if not path.is_file():
        return "File not found."
    if path.suffix.lower() == ".pdf":
        text = _read_pdf(path)
    elif path.suffix.lower() in {".txt", ".md", ".csv", ".json"}:
        text = path.read_text(encoding="utf-8", errors="replace")
    else:
        return f"I can locate {path.name}, but this file type needs a dedicated parser before I can explain its contents."
    return text[:max_chars]


def summarize_file(path_text: str) -> str:
    content = read_file(path_text, max_chars=18000)
    if content.startswith("File not found") or content.startswith("I can only") or content.startswith("I can locate") or content.startswith("PDF reader"):
        return content
    return content

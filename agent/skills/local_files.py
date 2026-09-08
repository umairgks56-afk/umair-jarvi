from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from config import JARVIS_DATA_ROOTS

TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".log", ".py", ".html", ".css", ".js"}
PDF_EXTENSION = ".pdf"
MAX_RESULTS = 50
MAX_READ_BYTES = 5_000_000


def allowed_roots() -> list[Path]:
    roots = []
    for raw in JARVIS_DATA_ROOTS.split(";"):
        raw = raw.strip()
        if raw:
            path = Path(os.path.expandvars(os.path.expanduser(raw))).resolve()
            if path.exists():
                roots.append(path)
    return roots


def _inside_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def search_files(query: str, limit: int = MAX_RESULTS) -> list[dict]:
    query = query.lower().strip()
    results = []
    for root in allowed_roots():
        for base, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in {"AppData", "node_modules", ".git"}]
            for name in files:
                if query in name.lower():
                    path = Path(base) / name
                    results.append({"name": name, "path": str(path), "size": path.stat().st_size})
                    if len(results) >= limit:
                        return results
    return results


def read_text_file(path_string: str) -> str:
    path = Path(path_string).resolve()
    if not any(_inside_root(path, root) for root in allowed_roots()):
        raise PermissionError("This file is outside JARVIS's configured local data folders.")
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        raise ValueError("This is not a supported text file.")
    if path.stat().st_size > MAX_READ_BYTES:
        raise ValueError("File is too large for a direct read.")
    return path.read_text(encoding="utf-8", errors="replace")


def read_pdf(path_string: str) -> str:
    path = Path(path_string).resolve()
    if not any(_inside_root(path, root) for root in allowed_roots()):
        raise PermissionError("This file is outside JARVIS's configured local data folders.")
    if path.suffix.lower() != PDF_EXTENSION:
        raise ValueError("Not a PDF file.")
    if path.stat().st_size > MAX_READ_BYTES * 4:
        raise ValueError("PDF is too large for a direct read.")
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Install pypdf to enable PDF reading: pip install pypdf") from exc
    reader = PdfReader(str(path))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)

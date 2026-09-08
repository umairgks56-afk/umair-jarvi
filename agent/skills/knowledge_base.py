"""Local knowledge-base facade for safe document discovery and reading."""
from __future__ import annotations

from skills.file_tools import find_files, read_file

SUPPORTED = {".pdf", ".txt", ".md", ".csv", ".json"}


def search(query: str = "", limit: int = 30) -> list[dict]:
    return find_files(query, max(1, min(limit, 100)))


def get_document(path: str, max_chars: int = 18000) -> dict:
    text = read_file(path, max_chars=max_chars)
    return {"path": path, "content": text, "characters": len(text)}


def status() -> dict:
    files = find_files("", limit=100)
    return {"documents": len(files), "supported_extensions": sorted(SUPPORTED)}

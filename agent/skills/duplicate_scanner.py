"""Fast, truthful duplicate-file scanner for JARVIS.

Duplicates are detected by file size + SHA-256 content hash, never by filename alone.
Only configured JARVIS data roots are scanned.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from skills.file_tools import DEFAULT_EXTENSIONS, allowed_roots


def _iter_files(roots: Iterable[Path]):
    for root in roots:
        if not root.exists():
            continue
        try:
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in DEFAULT_EXTENSIONS:
                    yield path
        except (OSError, PermissionError):
            continue


def _hash(path: Path, chunk_size: int = 1024 * 1024) -> str | None:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as fh:
            while True:
                chunk = fh.read(chunk_size)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()
    except (OSError, PermissionError):
        return None


def find_duplicates(limit_groups: int = 100) -> list[dict]:
    by_size: dict[int, list[Path]] = defaultdict(list)
    for path in _iter_files(allowed_roots()):
        try:
            by_size[path.stat().st_size].append(path)
        except (OSError, PermissionError):
            pass

    groups: dict[tuple[int, str], list[str]] = defaultdict(list)
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        for path in paths:
            digest = _hash(path)
            if digest:
                groups[(size, digest)].append(str(path))

    output = []
    for (size, digest), paths in groups.items():
        if len(paths) < 2:
            continue
        output.append({
            "size": size,
            "sha256": digest,
            "count": len(paths),
            "files": paths,
        })
        if len(output) >= limit_groups:
            break
    return output


def format_duplicates(groups: list[dict]) -> str:
    if not groups:
        return "I scanned the configured JARVIS folders and found no exact duplicate files."
    total = sum(g["count"] for g in groups)
    lines = [f"I found {len(groups)} exact duplicate group(s), covering {total} files.", ""]
    for i, group in enumerate(groups, 1):
        lines.append(f"Group {i} — {group['count']} identical files ({group['size']:,} bytes)")
        lines.extend(f"  • {p}" for p in group["files"])
    lines.append("")
    lines.append("I only report exact content matches; I have not deleted anything.")
    return "\n".join(lines)

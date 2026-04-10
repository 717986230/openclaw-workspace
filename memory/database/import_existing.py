#!/usr/bin/env python3
"""Import existing workspace memory files into SQLite."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Tuple

from init_db import DB_PATH, add_memory, init_database
from runtime_config import get_workspace_root


WORKSPACE = get_workspace_root()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def _import_files(file_specs: Iterable[Tuple[Path, str, str, int]]) -> int:
    imported = 0
    for path, type_name, category, importance in file_specs:
        if not path.exists() or path.suffix.lower() != ".md":
            continue
        content = _read_text(path)
        if not content:
            continue
        add_memory(
            type_=type_name,
            title=path.stem,
            content=content,
            category=category,
            tags=[type_name, category, path.stem],
            importance=importance,
            metadata={"source_file": str(path.relative_to(WORKSPACE))},
        )
        imported += 1
    return imported


def build_import_list() -> List[Tuple[Path, str, str, int]]:
    items: List[Tuple[Path, str, str, int]] = []
    items.append((WORKSPACE / "MEMORY.md", "memory", "core", 10))
    items.append((WORKSPACE / "memory" / "improvements.md", "improvement", "improvements", 8))
    for path in sorted((WORKSPACE / "memory" / "events").glob("*.md")):
        items.append((path, "event", "events", 8))
    for path in sorted((WORKSPACE / "memory" / "learnings").glob("*.md")):
        items.append((path, "learning", "learnings", 7))
    for path in sorted((WORKSPACE / "memory" / "preferences").glob("*.md")):
        items.append((path, "preference", "preferences", 9))
    return items


def import_existing() -> int:
    init_database()
    return _import_files(build_import_list())


if __name__ == "__main__":
    count = import_existing()
    print(f"[OK] Imported {count} files into {DB_PATH}")

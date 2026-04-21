#!/usr/bin/env python3
"""Fast API for reading the workspace memory database."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Dict, List


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "memory" / "database"))
from runtime_config import get_sqlite_db_path


DB_PATH = str(get_sqlite_db_path())


class ErbingBrain:
    """Thin wrapper around the memory SQLite database."""

    def __init__(self):
        self.db_path = DB_PATH

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def get_by_type(self, mem_type: str, limit: int = 10) -> List[Dict]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM memories WHERE type = ? ORDER BY importance DESC, created_at DESC LIMIT ?",
            (mem_type, limit),
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_important(self, min_importance: int = 8, limit: int = 20) -> List[Dict]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM memories WHERE importance >= ? ORDER BY importance DESC, created_at DESC LIMIT ?",
            (min_importance, limit),
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT m.* FROM memories m
                JOIN memory_index mi ON m.id = mi.rowid
                WHERE memory_index MATCH ?
                ORDER BY importance DESC, created_at DESC LIMIT ?
                """,
                (query, limit),
            )
            results = [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            cursor.execute(
                """
                SELECT * FROM memories
                WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
                ORDER BY importance DESC, created_at DESC LIMIT ?
                """,
                (f"%{query}%", f"%{query}%", f"%{query}%", limit),
            )
            results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results


_brain = None


def get_brain() -> ErbingBrain:
    global _brain
    if _brain is None:
        _brain = ErbingBrain()
    return _brain


if __name__ == "__main__":
    brain = get_brain()
    print(brain.get_important(limit=5))

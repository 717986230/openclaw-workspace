#!/usr/bin/env python3
"""Hybrid memory access for SQLite plus local LanceDB."""

from __future__ import annotations

import json
import sqlite3
from typing import Dict, List, Optional

from init_db import init_database
from runtime_config import ensure_directories, get_lancedb_dir, get_sqlite_db_path

try:
    import lancedb

    LANCEDB_AVAILABLE = True
except ImportError:
    lancedb = None
    LANCEDB_AVAILABLE = False


SQLITE_DB = get_sqlite_db_path()
LANCEDB_PATH = get_lancedb_dir()


class HybridMemory:
    def __init__(self):
        ensure_directories()
        init_database()
        self.sqlite_conn = sqlite3.connect(SQLITE_DB)
        self.sqlite_conn.row_factory = sqlite3.Row
        self.lancedb_conn = None
        if LANCEDB_AVAILABLE:
            self.lancedb_conn = lancedb.connect(str(LANCEDB_PATH))

    def search(
        self,
        query: str,
        type_: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict]:
        cursor = self.sqlite_conn.cursor()
        where_clauses = []
        params = []
        if type_:
            where_clauses.append("type = ?")
            params.append(type_)
        if category:
            where_clauses.append("category = ?")
            params.append(category)
        sql = """
            SELECT id, type, title, content, category, tags, importance, created_at
            FROM memories
        """
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        sql += " ORDER BY importance DESC, created_at DESC LIMIT ?"
        params.append(limit)
        cursor.execute(sql, params)
        results = [dict(row) for row in cursor.fetchall()]
        for row in results:
            if row["tags"]:
                row["tags"] = json.loads(row["tags"])
        return results

    def get_stats(self) -> Dict:
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        total = cursor.fetchone()[0]
        cursor.execute(
            """
            SELECT type, COUNT(*) as cnt
            FROM memories
            GROUP BY type
            ORDER BY cnt DESC
            """
        )
        return {
            "total": total,
            "by_type": {row[0]: row[1] for row in cursor.fetchall()},
            "lancedb_available": self.lancedb_conn is not None,
            "lancedb_path": str(LANCEDB_PATH),
        }


_hybrid_memory: Optional[HybridMemory] = None


def get_memory() -> HybridMemory:
    global _hybrid_memory
    if _hybrid_memory is None:
        _hybrid_memory = HybridMemory()
    return _hybrid_memory


if __name__ == "__main__":
    mem = get_memory()
    print(mem.get_stats())

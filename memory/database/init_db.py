#!/usr/bin/env python3
"""Initialize the workspace SQLite memory database."""

from __future__ import annotations

import json
import sqlite3
from typing import Iterable, Optional

from runtime_config import ensure_directories, get_sqlite_db_path


DB_PATH = get_sqlite_db_path()


def init_database() -> None:
    ensure_directories()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            category TEXT,
            tags TEXT,
            importance INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS memory_index USING FTS5(
            title,
            content,
            tags,
            category,
            content='memories',
            content_rowid='id'
        )
        """
    )
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
            INSERT INTO memory_index(rowid, title, content, tags, category)
            VALUES (new.id, new.title, new.content, new.tags, new.category);
        END
        """
    )
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
            INSERT INTO memory_index(memory_index, rowid, title, content, tags, category)
            VALUES('delete', old.id, old.title, old.content, old.tags, old.category);
        END
        """
    )
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
            INSERT INTO memory_index(memory_index, rowid, title, content, tags, category)
            VALUES('delete', old.id, old.title, old.content, old.tags, old.category);
            INSERT INTO memory_index(rowid, title, content, tags, category)
            VALUES (new.id, new.title, new.content, new.tags, new.category);
        END
        """
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)")
    cursor.execute(
        """
        INSERT INTO memory_index(rowid, title, content, tags, category)
        SELECT id, title, content, tags, category FROM memories
        WHERE id NOT IN (SELECT rowid FROM memory_index)
        """
    )
    conn.commit()
    conn.close()


def add_memory(
    type_: str,
    title: str,
    content: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[Iterable[str]] = None,
    importance: int = 5,
    metadata: Optional[dict] = None,
) -> int:
    init_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO memories (type, title, content, category, tags, importance, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            type_,
            title,
            content,
            category,
            json.dumps(list(tags)) if tags else None,
            importance,
            json.dumps(metadata) if metadata else None,
        ),
    )
    memory_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return memory_id


def search_memories(query: str, limit: int = 10):
    init_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT m.id, m.type, m.title, m.content, m.category, m.importance, m.created_at
        FROM memory_index idx
        JOIN memories m ON idx.rowid = m.id
        WHERE memory_index MATCH ?
        ORDER BY m.importance DESC, m.created_at DESC
        LIMIT ?
        """,
        (query, limit),
    )
    results = cursor.fetchall()
    conn.close()
    return results


def get_memories_by_type(type_: str, limit: int = 50):
    init_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, type, title, content, category, importance, created_at
        FROM memories
        WHERE type = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (type_, limit),
    )
    results = cursor.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    init_database()
    print(f"[OK] Database initialized: {DB_PATH}")

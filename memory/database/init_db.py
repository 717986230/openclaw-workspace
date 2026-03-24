#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化小智的记忆数据库
SQLite + FTS5 全文搜索
"""

import sqlite3
import json
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent / "xiaozhi_memory.db"


def init_database():
    """初始化数据库表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 创建 memories 表
    cursor.execute("""
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
    """)

    # 创建 FTS5 全文搜索索引
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS memory_index USING FTS5(
            title,
            content,
            tags,
            content=memories,
            content_rowid=id
        )
    """)

    # 创建索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)
    """)

    conn.commit()
    conn.close()
    print(f"[OK] Database initialized: {DB_PATH}")


def add_memory(type_, title, content=None, category=None, tags=None, importance=5, metadata=None):
    """添加一条记忆"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tags_json = json.dumps(tags) if tags else None
    metadata_json = json.dumps(metadata) if metadata else None

    cursor.execute("""
        INSERT INTO memories (type, title, content, category, tags, importance, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (type_, title, content, category, tags_json, importance, metadata_json))

    memory_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(f"[OK] Added memory: {title} (ID: {memory_id})")
    return memory_id


def search_memories(query, limit=10):
    """全文搜索记忆"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.id, m.type, m.title, m.content, m.category, m.importance, m.created_at
        FROM memory_index idx
        JOIN memories m ON idx.rowid = m.id
        WHERE memory_index MATCH ?
        ORDER BY m.importance DESC, m.created_at DESC
        LIMIT ?
    """, (query, limit))

    results = cursor.fetchall()
    conn.close()

    print(f"[SEARCH] '{query}': {len(results)} results")
    return results


def get_memories_by_type(type_, limit=50):
    """按类型获取记忆"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, type, title, content, category, importance, created_at
        FROM memories
        WHERE type = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (type_, limit))

    results = cursor.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    init_database()

    # 测试添加一些记忆
    print("\n[ADD] Adding test memories...")
    add_memory(
        type_="event",
        title="2026-03-02 - Database Init",
        content="Xiaozhi's memory system migrated from files to SQLite database",
        category="system",
        tags=["database", "sqlite", "init"],
        importance=10
    )

    add_memory(
        type_="learning",
        title="SQLite FTS5 Full-Text Search",
        content="Using SQLite FTS5 extension for efficient full-text search",
        category="tech",
        tags=["sqlite", "fts5", "search"],
        importance=8
    )

    add_memory(
        type_="preference",
        title="Owner Security Requirements",
        content="Lock the house, check ports, prevent hacker attacks",
        category="security",
        tags=["security", "owner", "important"],
        importance=10
    )

    print("\n[DONE] Database initialization complete!")

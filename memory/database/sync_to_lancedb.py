#!/usr/bin/env python3
"""Sync SQLite memories to LanceDB for semantic search."""

import json
import sqlite3
from pathlib import Path

try:
    import lancedb
    import pyarrow as pa
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False

DB_PATH = Path(__file__).parent / "xiaozhi_memory.db"
LANCEDB_PATH = Path(__file__).parent / "lancedb"

def embed_text(text: str) -> list:
    """Simple embedding using word frequency (placeholder for real embeddings)."""
    # This is a placeholder - in production, use sentence-transformers or OpenAI embeddings
    # For now, we'll use a simple TF-IDF-like approach
    words = text.lower().split()
    vocab = {}
    for word in words:
        vocab[word] = vocab.get(word, 0) + 1

    # Create a simple 128-dim vector (hash-based)
    import hashlib
    vector = [0.0] * 128
    for word, freq in vocab.items():
        h = int(hashlib.md5(word.encode()).hexdigest(), 16)
        idx = h % 128
        vector[idx] += freq / len(words)

    # Normalize
    magnitude = sum(v * v for v in vector) ** 0.5
    if magnitude > 0:
        vector = [v / magnitude for v in vector]

    return vector

def main():
    if not LANCEDB_AVAILABLE:
        print("LanceDB not available, skipping sync")
        return

    # Connect to SQLite
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all memories
    cursor.execute("""
        SELECT id, type, title, content, category, tags, importance, created_at
        FROM memories
    """)
    rows = cursor.fetchall()

    if not rows:
        print("No memories to sync")
        return

    print(f"Syncing {len(rows)} memories to LanceDB...")

    # Prepare data for LanceDB
    data = {
        "id": [],
        "type": [],
        "title": [],
        "content": [],
        "category": [],
        "tags": [],
        "importance": [],
        "created_at": [],
        "vector": []
    }

    for row in rows:
        text = f"{row['title']} {row['content'] or ''}"
        vector = embed_text(text)

        data["id"].append(row["id"])
        data["type"].append(row["type"])
        data["title"].append(row["title"])
        data["content"].append(row["content"] or "")
        data["category"].append(row["category"] or "")
        data["tags"].append(row["tags"] or "[]")
        data["importance"].append(row["importance"])
        data["created_at"].append(row["created_at"] or "")
        data["vector"].append(vector)

    # Create Arrow table
    schema = pa.schema([
        ("id", pa.int64()),
        ("type", pa.string()),
        ("title", pa.string()),
        ("content", pa.string()),
        ("category", pa.string()),
        ("tags", pa.string()),
        ("importance", pa.int64()),
        ("created_at", pa.string()),
        ("vector", pa.list_(pa.float32(), 128))
    ])

    table = pa.table(data, schema=schema)

    # Connect to LanceDB and create table
    db = lancedb.connect(str(LANCEDB_PATH))

    # Drop existing table if exists
    if "memories" in db.table_names():
        db.drop_table("memories")

    # Create new table
    tbl = db.create_table("memories", table)
    print(f"Created LanceDB table with {len(rows)} memories")

    # Verify
    print(f"Tables: {db.table_names()}")
    print(f"Rows in LanceDB: {len(tbl)}")

    conn.close()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Query today's memories from database."""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "xiaozhi_memory.db"

def main():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Query today's memories
    c.execute("""
        SELECT type, title, importance, created_at
        FROM memories
        WHERE date(created_at) = date('now')
        ORDER BY importance DESC
    """)

    print("=== Today's Memories (from database) ===")
    rows = c.fetchall()
    if rows:
        for row in rows:
            print(f"[{row['importance']}] {row['type']}: {row['title']}")
    else:
        print("No memories from today")

    # Query all improvements
    c.execute("""
        SELECT title, importance
        FROM memories
        WHERE type = 'improvement'
        ORDER BY importance DESC
    """)

    print("\n=== All Improvements (from database) ===")
    for row in c.fetchall():
        print(f"[{row['importance']}] {row['title']}")

    # Query all skills
    c.execute("""
        SELECT title, importance
        FROM memories
        WHERE type = 'skill'
        ORDER BY importance DESC
    """)

    print("\n=== All Skills (from database) ===")
    for row in c.fetchall():
        print(f"[{row['importance']}] {row['title']}")

    conn.close()

if __name__ == "__main__":
    main()

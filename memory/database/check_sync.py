#!/usr/bin/env python3
"""Check left-right brain sync status."""

import sqlite3
import lancedb
from pathlib import Path

DB_PATH = Path(__file__).parent / "xiaozhi_memory.db"
LANCEDB_PATH = Path(__file__).parent / "lancedb"

def main():
    # SQLite (Left Brain)
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM memories")
    sqlite_count = c.fetchone()[0]
    conn.close()

    # LanceDB (Right Brain)
    db = lancedb.connect(str(LANCEDB_PATH))
    tables = db.table_names()
    lancedb_count = 0
    if "memories" in tables:
        tbl = db.open_table("memories")
        lancedb_count = len(tbl)

    print("=== Left-Right Brain Database Status ===")
    print(f"Left Brain (SQLite):  {sqlite_count} memories")
    print(f"Right Brain (LanceDB): {lancedb_count} vectors")
    status = "SYNCED" if sqlite_count == lancedb_count else "NOT SYNCED"
    print(f"Sync Status: {status}")

    print("\n=== By Type (Left Brain) ===")
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("SELECT type, COUNT(*) FROM memories GROUP BY type ORDER BY COUNT(*) DESC")
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]}")
    conn.close()

if __name__ == "__main__":
    main()

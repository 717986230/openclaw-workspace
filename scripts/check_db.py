#!/usr/bin/env python3
"""Inspect the workspace SQLite database schema."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "memory" / "database"))
from runtime_config import get_sqlite_db_path


DB_PATH = get_sqlite_db_path()


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print("Tables:", tables)
    if tables:
        cursor.execute(f"PRAGMA table_info({tables[0][0]})")
        columns = cursor.fetchall()
        print("\nColumns:")
        for col in columns:
            print(f"  {col}")
    conn.close()


if __name__ == "__main__":
    main()

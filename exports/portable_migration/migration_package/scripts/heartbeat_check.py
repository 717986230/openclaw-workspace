#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Heartbeat check for memory database health"""

import sqlite3
import os

# Check SQLite database
db_path = 'memory/database/xiaozhi_memory.db'
print(f"SQLite DB exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check agent_prompts table
        cursor.execute('SELECT COUNT(*) FROM agent_prompts')
        agent_count = cursor.fetchone()[0]
        print(f"Agent prompts: {agent_count}")

        # Check memories table
        cursor.execute('SELECT COUNT(*) FROM memories')
        memory_count = cursor.fetchone()[0]
        print(f"Memories: {memory_count}")

        conn.close()
        print("SQLite DB: OK")
    except Exception as e:
        print(f"SQLite DB: ERROR - {e}")
else:
    print("SQLite DB: NOT FOUND")

# Check LanceDB
lancedb_path = 'memory/database/lancedb'
print(f"LanceDB exists: {os.path.exists(lancedb_path)}")

if os.path.exists(lancedb_path):
    print("LanceDB: OK")
else:
    print("LanceDB: NOT FOUND (optional)")

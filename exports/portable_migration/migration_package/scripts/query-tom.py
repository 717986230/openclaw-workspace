#!/usr/bin/env python3
"""
查询心智模型表
"""
import sqlite3

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def query_tom_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tom_tables = [
        'user_beliefs',
        'intent_tracking',
        'emotional_state',
        'meta_cognition',
        'social_context'
    ]

    print("TOM Tables Status:")
    for table in tom_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} records")

    conn.close()

if __name__ == "__main__":
    query_tom_tables()

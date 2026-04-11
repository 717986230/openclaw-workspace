#!/usr/bin/env python3
import sqlite3
from datetime import datetime

DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"

def log_learning(title, content, tags):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ('learning', title, content, 'knowledge', tags, 9, now, now))
    
    memory_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return memory_id

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        title = sys.argv[1]
        content = sys.argv[2]
        tags = sys.argv[3]
        mid = log_learning(title, content, tags)
        print(f"Logged: {mid}")
    else:
        print("Usage: python log_evolution.py <title> <content> <tags>")

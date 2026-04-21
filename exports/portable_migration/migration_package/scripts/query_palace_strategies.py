#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query memory system for palace structure and four strategies
"""

import sqlite3
import os

db_path = "C:\\Users\\Administrator\\.openclaw\\workspace\\memory\\database\\xiaozhi_memory.db"

print("=" * 60)
print("SEARCHING FOR PALACE STRUCTURE AND FOUR STRATEGIES")
print("=" * 60)
print("")

if not os.path.exists(db_path):
    print("[ERROR] Database not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Search for palace related memories
print("[PALACE STRUCTURE]")
print("")

search_terms = [
    "palace",
    "memory palace",
    "宫殿",
    "结构",
    "structure",
    "architecture"
]

for term in search_terms:
    cursor.execute("""
        SELECT id, type, title, content, created_at
        FROM memories
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY created_at DESC
        LIMIT 5
    """, (f"%{term}%", f"%{term}%"))

    results = cursor.fetchall()
    if results:
        print(f"[{term.upper()}] Found {len(results)} memories:")
        for row in results:
            id, type, title, content, created_at = row
            print(f"  ID: {id}")
            print(f"  Type: {type}")
            print(f"  Title: {title}")
            print(f"  Created: {created_at}")
            print("")

# Search for four strategies
print("=" * 60)
print("[FOUR STRATEGIES]")
print("")

strategy_terms = [
    "strategy",
    "strategies",
    "four",
    "4",
    "四条",
    "策略",
    "principle",
    "principles"
]

for term in strategy_terms:
    cursor.execute("""
        SELECT id, type, title, content, created_at
        FROM memories
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY created_at DESC
        LIMIT 5
    """, (f"%{term}%", f"%{term}%"))

    results = cursor.fetchall()
    if results:
        print(f"[{term.upper()}] Found {len(results)} memories:")
        for row in results:
            id, type, title, content, created_at = row
            print(f"  ID: {id}")
            print(f"  Type: {type}")
            print(f"  Title: {title}")
            print(f"  Created: {created_at}")
            print("")

# Search for GBrain related content
print("=" * 60)
print("[GBRAIN ORIGINALS]")
print("")

gbrain_terms = [
    "GBrain",
    "Originals",
    "Entity Detection",
    "Brain-First",
    "Compiled Truth",
    "Timeline"
]

for term in gbrain_terms:
    cursor.execute("""
        SELECT id, type, title, content, created_at
        FROM memories
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY created_at DESC
        LIMIT 3
    """, (f"%{term}%", f"%{term}%"))

    results = cursor.fetchall()
    if results:
        print(f"[{term}] Found {len(results)} memories:")
        for row in results:
            id, type, title, content, created_at = row
            print(f"  Title: {title}")
            print(f"  Created: {created_at}")
        print("")

# Check for deleted or lost memories
print("=" * 60)
print("[RECENT DELETIONS OR CHANGES]")
print("")

cursor.execute("""
    SELECT id, type, title, created_at, updated_at
    FROM memories
    WHERE updated_at > created_at
    ORDER BY updated_at DESC
    LIMIT 10
""")

results = cursor.fetchall()
if results:
    print(f"Found {len(results)} recently updated memories:")
    for row in results:
        id, type, title, created_at, updated_at = row
        print(f"  ID: {id}")
        print(f"  Title: {title}")
        print(f"  Created: {created_at}")
        print(f"  Updated: {updated_at}")
        print("")
else:
    print("No recently updated memories found")

conn.close()

print("=" * 60)
print("SEARCH COMPLETE")
print("=" * 60)

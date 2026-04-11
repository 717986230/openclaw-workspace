#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query memory system for information about its origins and evolution
"""

import sqlite3
import os

db_path = "C:\\Users\\Administrator\\.openclaw\\workspace\\memory\\database\\xiaozhi_memory.db"

print("=" * 60)
print("MEMORY SYSTEM ORIGIN AND EVOLUTION QUERY")
print("=" * 60)
print("")

if not os.path.exists(db_path):
    print("[ERROR] Database not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Search for memories related to system origin, evolution, or development
search_terms = [
    "origin",
    "evolution", 
    "development",
    "project",
    "source",
    "based on",
    "inspired by",
    "architecture",
    "design",
    "created",
    "built"
]

print("Searching for memories about system origin and development...")
print("")

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
            print(f"  Content: {content[:50].encode('ascii', 'ignore').decode('ascii')}...")
            print(f"  Created: {created_at}")
            print("")

# Search for Clawvard related memories
print("=" * 60)
print("CLAWVARD RELATED MEMORIES")
print("=" * 60)
print("")

cursor.execute("""
    SELECT id, type, title, content, created_at
    FROM memories
    WHERE title LIKE '%clawvard%' OR content LIKE '%clawvard%'
    ORDER BY created_at DESC
    LIMIT 10
""")

results = cursor.fetchall()
if results:
    print(f"Found {len(results)} Clawvard-related memories:")
    for row in results:
        id, type, title, content, created_at = row
        print(f"  ID: {id}")
        print(f"  Type: {type}")
        print(f"  Title: {title}")
        print(f"  Content: {content[:100]}...")
        print(f"  Created: {created_at}")
        print("")
else:
    print("No Clawvard-related memories found")

# Search for ToM, EQ, Retrieval improvements
print("=" * 60)
print("IMPROVEMENT MODULES")
print("=" * 60)
print("")

improvement_terms = ["ToM", "Theory of Mind", "EQ", "Emotional", "Retrieval", "Enhanced"]

for term in improvement_terms:
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

conn.close()

print("=" * 60)
print("QUERY COMPLETE")
print("=" * 60)

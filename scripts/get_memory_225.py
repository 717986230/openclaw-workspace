#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get specific memory content
"""

import sqlite3
import json

db_path = "C:\\Users\\Administrator\\.openclaw\\workspace\\memory\\database\\xiaozhi_memory.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get memory ID 225
cursor.execute("SELECT id, type, title, content FROM memories WHERE id=225")
result = cursor.fetchone()

if result:
    id, type, title, content = result
    print(f"ID: {id}")
    print(f"Type: {type}")
    print(f"Title: {title}")
    print(f"Content: {content}")
else:
    print("Memory not found")

conn.close()

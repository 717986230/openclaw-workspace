#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
cursor = conn.cursor()

# 检查 FTS5 表内容
print("=== FTS5 表前 5 条记录 ===")
cursor.execute("SELECT rowid, title FROM memories_fts LIMIT 5")
for row in cursor.fetchall():
    print(f"ID:{row[0]} - {row[1]}")

# 测试搜索
print("\n=== 测试搜索 'memory' ===")
cursor.execute("SELECT rowid, title FROM memories_fts WHERE memories_fts MATCH 'memory'")
results = cursor.fetchall()
print(f"找到 {len(results)} 条结果")
for row in results[:3]:
    print(f"  ID:{row[0]} - {row[1]}")

# 测试搜索所有
print("\n=== 搜索空字符串 (获取所有) ===")
cursor.execute("SELECT rowid, title FROM memories_fts WHERE memories_fts MATCH '' LIMIT 5")
results = cursor.fetchall()
print(f"找到 {len(results)} 条结果")

# 测试 LIKE 查询
print("\n=== 测试 LIKE 查询 '%memory%' ===")
cursor.execute("""
    SELECT m.id, m.title FROM memories m
    WHERE m.title LIKE '%memory%' OR m.content LIKE '%memory%'
    LIMIT 5
""")
results = cursor.fetchall()
print(f"找到 {len(results)} 条结果")
for row in results:
    print(f"  ID:{row[0]} - {row[1]}")

conn.close()

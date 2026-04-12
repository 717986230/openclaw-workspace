#!/usr/bin/env python3
"""查看数据库表结构"""
import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
cursor = conn.cursor()

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print(f"数据库中的表: {tables}\n")

# 查看每个表的结构
for table in tables:
    print(f"=== 表: {table} ===")
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    print("列信息:")
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - 主键: {col[5]}, 非空: {col[3]}, 默认值: {col[4]}")

    # 查看表中的记录数
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"记录数: {count}\n")

# 查看数据库大小
import os
db_size = os.path.getsize('memory/database/xiaozhi_memory.db')
print(f"数据库文件大小: {db_size / 1024 / 1024:.2f} MB")

conn.close()

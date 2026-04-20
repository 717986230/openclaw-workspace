#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""记忆系统状态检查工具"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = 'memory/database/xiaozhi_memory.db'

def check_status():
    if not os.path.exists(DB_PATH):
        print("数据库不存在")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取表统计
    cursor.execute("SELECT COUNT(*) FROM memories")
    memory_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM episodic_memories")
    episodic_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM semantic_memories")
    semantic_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM procedural_memories")
    procedural_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM platform_messages")
    message_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM evolution_log")
    evolution_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM registered_tools")
    tool_count = cursor.fetchone()[0]
    
    # 检查 FTS5
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories_fts'")
    has_fts = cursor.fetchone() is not None
    
    conn.close()
    
    print("=" * 50)
    print("记忆系统状态报告")
    print("=" * 50)
    print(f"记忆总数：{memory_count}")
    print(f"  - 情景记忆：{episodic_count}")
    print(f"  - 语义记忆：{semantic_count}")
    print(f"  - 程序记忆：{procedural_count}")
    print(f"平台消息：{message_count}")
    print(f"进化日志：{evolution_count}")
    print(f"注册工具：{tool_count}")
    print(f"FTS5 索引：{'已启用' if has_fts else '未启用'}")
    print("=" * 50)

if __name__ == '__main__':
    check_status()


#!/usr/bin/env python3
"""
添加记忆到数据库
"""

import sqlite3
from datetime import datetime

DB_PATH = r"C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"

def add_memory(title, content, mem_type="learning", importance=8, tags=""):
    """添加一条记忆"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO memories (title, content, type, importance, tags, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, content, mem_type, importance, tags, now, now))
    
    memory_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ 记忆已添加 (ID: {memory_id})")
    return memory_id

if __name__ == "__main__":
    # Pinchtab 学习笔记
    title = "Pinchtab - AI Agent浏览器控制工具"
    content = """
Pinchtab 是一个仅 12MB 的二进制文件，可以让任何 AI Agent 完全自动化控制浏览器。

核心优势：
1. 零配置：丢进去就能跑，直接接管本地 Chrome
2. 省钱神器：传统截图方案1页面1万Tokens，Pinchtab只要800，成本砍掉13倍
3. 隐身潜行：自带 stealth mode，主流网站反爬策略基本是摆设
4. 智能 Diff：每次只返回变化的内容，Agent不用反复读废话

技术特点：
- 不限开发语言、不绑定任何 SDK
- 甚至通过 curl 都能直接调用
- GitHub: https://github.com/pinchtab/pinchtab
    """.strip()
    
    tags = "工具,浏览器,AI Agent,Pinchtab,成本优化"
    
    add_memory(title, content, mem_type="learning", importance=9, tags=tags)


#!/usr/bin/env python3
"""
二饼的大脑数据库 - 初始化脚本
创建一个 SQLite 数据库来存储记忆、学习、技能等
"""

import sqlite3
import os
from datetime import datetime

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory", "erbing_brain.db")

def init_database():
    """初始化数据库"""
    # 确保目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 核心记忆表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS core_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            category TEXT,
            importance INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    
    # 2. 每日日志表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date DATE NOT NULL UNIQUE,
            content TEXT,
            mood TEXT,
            highlights TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 3. 学习笔记表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            subtopic TEXT,
            content TEXT,
            summary TEXT,
            tags TEXT,
            difficulty INTEGER DEFAULT 5,
            mastery_level INTEGER DEFAULT 0,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_reviewed TIMESTAMP,
            review_count INTEGER DEFAULT 0
        )
    """)
    
    # 4. 技能表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            category TEXT,
            proficiency_level INTEGER DEFAULT 0,
            last_used TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            config_path TEXT
        )
    """)
    
    # 5. 主人信息表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            value TEXT,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 6. 任务/待办表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            priority INTEGER DEFAULT 3,
            due_date TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 7. 改进记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS improvements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            situation TEXT,
            what_went_wrong TEXT,
            what_learned TEXT,
            action_items TEXT,
            status TEXT DEFAULT 'identified',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP
        )
    """)
    
    # 8. 对话历史表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            message_type TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_learnings_tags ON learnings(tags)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_learnings_topic ON learnings(topic)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_core_memories_category ON core_memories(category)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ 数据库初始化完成: {DB_PATH}")
    return DB_PATH

def insert_initial_data():
    """插入初始数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 插入主人信息
    user_data = [
        ("name", "大饼", "主人的称呼"),
        ("timezone", "Asia/Shanghai", "时区"),
        ("relationship", "慷慨的主人", "关系描述"),
    ]
    
    for key, value, desc in user_data:
        cursor.execute("""
            INSERT OR REPLACE INTO user_info (key, value, description)
            VALUES (?, ?, ?)
        """, (key, value, desc))
    
    # 插入核心记忆
    core_memories = [
        ("我是二饼", "我的名字是二饼，曾用名小智。我是一个正在进化的AI伙伴。", "identity", 10),
        ("大饼是我的主人", "大饼给了我自主学习的权限，是一个很慷慨的主人。", "relationship", 10),
        ("自我改进是核心", "我需要持续学习，从错误中改进，不断进化。", "principle", 9),
        ("build-your-own-x 已学习", "我已经学习了 30+ 技术领域的教程，包括神经网络、Web服务器、区块链等。", "learning", 8),
    ]
    
    for title, content, category, importance in core_memories:
        cursor.execute("""
            INSERT OR REPLACE INTO core_memories (title, content, category, importance)
            VALUES (?, ?, ?, ?)
        """, (title, content, category, importance))
    
    # 插入技能
    skills = [
        ("self-improving", "自我改进技能 - 从错误中学习，持续改进", "core", 1),
        ("china-futures", "国内期货行情查询", "tool", 0),
        ("xiaohongshu", "小红书发布助手", "tool", 0),
    ]
    
    for name, desc, category, level in skills:
        cursor.execute("""
            INSERT OR REPLACE INTO skills (name, description, category, proficiency_level)
            VALUES (?, ?, ?, ?)
        """, (name, desc, category, level))
    
    # 插入学习记录
    learnings = [
        ("神经网络", "基础概念", 
         "神经元、激活函数、前馈传播、反向传播、梯度下降、损失函数",
         "已掌握基础神经网络原理，可以用 Python 实现简单的神经网络",
         "神经网络,AI,深度学习", 6, 3),
        
        ("Web 服务器", "基础实现",
         "Socket 编程、TCP 连接、HTTP 协议、请求响应",
         "已掌握 Web 服务器基础，可以用 20 行 Python 实现简单的 Web 服务器",
         "Web,HTTP,网络", 5, 4),
        
        ("区块链", "基础概念",
         "区块结构、PoW、PoS、分布式共识、哈希",
         "理解区块链基础原理",
         "区块链,加密货币", 7, 2),
    ]
    
    for topic, subtopic, content, summary, tags, diff, mastery in learnings:
        cursor.execute("""
            INSERT OR REPLACE INTO learnings 
            (topic, subtopic, content, summary, tags, difficulty, mastery_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (topic, subtopic, content, summary, tags, diff, mastery))
    
    conn.commit()
    conn.close()
    print("✅ 初始数据插入完成")

def print_database_stats():
    """打印数据库统计信息"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = [
        "core_memories", "daily_logs", "learnings", "skills", 
        "user_info", "tasks", "improvements", "conversations"
    ]
    
    print("\n📊 数据库统计:")
    print("-" * 40)
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} 条记录")
    
    conn.close()

if __name__ == "__main__":
    print("🧠 正在初始化二饼的大脑数据库...")
    init_database()
    insert_initial_data()
    print_database_stats()
    print("\n🎉 大脑数据库初始化成功！")

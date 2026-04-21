#!/usr/bin/env python3
"""
终极记忆系统 v3.0 - 数据库初始化脚本
创建14个数据库表，支持八大系统合一
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

# 数据库路径
DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"

def create_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """初始化数据库表"""
    conn = create_connection()
    cursor = conn.cursor()

    print("[INFO] 开始初始化终极记忆系统 v3.0 数据库...")

    # 1. 情景记忆表 (MemPalace)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS episodic_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            emotion TEXT,
            importance INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tags TEXT,
            layer INTEGER DEFAULT 2
        )
    """)
    print("[OK] 创建 episodic_memories 表")

    # 2. 语义记忆表 (MemPalace - 知识图谱)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS semantic_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            predicate TEXT NOT NULL,
            object TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            layer INTEGER DEFAULT 3
        )
    """)
    print("[OK] 创建 semantic_memories 表")

    # 3. 程序记忆表 (MemPalace)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS procedural_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT NOT NULL,
            procedure TEXT NOT NULL,
            mastery_level INTEGER DEFAULT 1,
            last_practiced TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            layer INTEGER DEFAULT 4
        )
    """)
    print("[OK] 创建 procedural_memories 表")

    # 4. 工作记忆表 (MemPalace)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS working_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            context TEXT,
            priority INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            layer INTEGER DEFAULT 1
        )
    """)
    print("[OK] 创建 working_memory 表")

    # 5. Agent 日历表 (MemPalace)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_diary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            summary TEXT NOT NULL,
            achievements TEXT,
            challenges TEXT,
            next_steps TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] 创建 agent_diary 表")

    # 6. 平台消息表 (Memoh)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platform_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            channel_id TEXT,
            message_id TEXT,
            sender_id TEXT,
            content TEXT NOT NULL,
            timestamp TIMESTAMP,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] 创建 platform_messages 表")

    # 7. 自进化记录表 (Phantom)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evolution_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            description TEXT NOT NULL,
            before_state TEXT,
            after_state TEXT,
            impact_score INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] 创建 evolution_log 表")

    # 8. 工具注册表 (OpenViking)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registered_tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_name TEXT NOT NULL UNIQUE,
            tool_type TEXT NOT NULL,
            description TEXT,
            capabilities TEXT,
            endpoint TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] 创建 registered_tools 表")

    # 9. 分层上下文表 (OpenViking)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS layered_context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            layer_level INTEGER NOT NULL,
            context_type TEXT NOT NULL,
            context_data TEXT NOT NULL,
            priority INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(layer_level, context_type)
        )
    """)
    print("[OK] 创建 layered_context 表")

    # 10. 会话摘要表 (综合)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            summary TEXT NOT NULL,
            key_points TEXT,
            action_items TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] 创建 session_summaries 表")

    # 11. 安全扫描表 (CyberMind)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            scan_type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            results TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] 创建 security_scans 表")

    # 12. 漏洞发现表 (HexMind)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vulnerability_findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER,
            vulnerability_type TEXT NOT NULL,
            location TEXT,
            severity TEXT,
            description TEXT,
            remediation TEXT,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scan_id) REFERENCES security_scans(id)
        )
    """)
    print("[OK] 创建 vulnerability_findings 表")

    # 13. OSINT 情报表 (HexMind)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS osint_intel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            intel_type TEXT NOT NULL,
            source TEXT,
            data TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] 创建 osint_intel 表")

    # 14. 攻击链表 (HexMind)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attack_chains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain_name TEXT NOT NULL,
            stages TEXT NOT NULL,
            mitre_techniques TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] 创建 attack_chains 表")

    # 创建索引
    print("\n[INFO] 创建索引...")

    # 情景记忆索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_episodic_type ON episodic_memories(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_episodic_importance ON episodic_memories(importance)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_episodic_created ON episodic_memories(created_at)")

    # 语义记忆索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_semantic_subject ON semantic_memories(subject)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_semantic_predicate ON semantic_memories(predicate)")

    # 平台消息索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_platform_platform ON platform_messages(platform)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_platform_timestamp ON platform_messages(timestamp)")

    # 分层上下文索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_context_layer ON layered_context(layer_level)")

    # 安全扫描索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_security_target ON security_scans(target)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_security_status ON security_scans(status)")

    conn.commit()
    conn.close()

    print("\n[SUCCESS] 数据库初始化完成！")
    print(f"[INFO] 数据库位置: {DB_PATH}")
    print("[INFO] 已创建 14 个表和多个索引")

if __name__ == "__main__":
    init_database()

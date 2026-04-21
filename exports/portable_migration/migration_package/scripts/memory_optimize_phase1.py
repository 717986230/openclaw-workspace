#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统阶段一优化脚本
实施内容:
1. 为 memories 表创建 FTS5 全文搜索索引
2. 增强 secure_credentials 表 (如果不存在则创建)
3. 增强 registered_tools 表 (如果不存在则创建)
4. 创建 MCP Server 工具配置文件
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = 'memory/database/xiaozhi_memory.db'
SCRIPTS_DIR = 'scripts'

def print_step(msg):
    print(f"\n[STEP] {msg}")

def print_success(msg):
    print(f"  [OK] {msg}")

def print_warn(msg):
    print(f"  [WARN] {msg}")

def check_table_exists(cursor, table_name):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None

def check_fts_exists(cursor, fts_name):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (fts_name,))
    return cursor.fetchone() is not None

def main():
    if not os.path.exists(DB_PATH):
        print(f"错误：数据库文件不存在：{DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("记忆系统阶段一优化 - 开始")
    print("=" * 60)
    
    # ========== 1. 创建 FTS5 全文搜索索引 ==========
    print_step("1. 创建 FTS5 全文搜索索引")
    
    if check_table_exists(cursor, 'memories'):
        if not check_fts_exists(cursor, 'memories_fts'):
            try:
                # 创建 FTS5 虚拟表
                cursor.execute("""
                    CREATE VIRTUAL TABLE memories_fts USING fts5(
                        title,
                        content,
                        content='memories',
                        content_rowid='id'
                    )
                """)
                
                # 插入现有数据
                cursor.execute("""
                    INSERT INTO memories_fts(rowid, title, content)
                    SELECT id, title, content FROM memories
                """)
                
                # 创建触发器保持同步
                cursor.execute("""
                    CREATE TRIGGER memories_ai AFTER INSERT ON memories BEGIN
                        INSERT INTO memories_fts(rowid, title, content)
                        VALUES (new.id, new.title, new.content);
                    END
                """)
                
                cursor.execute("""
                    CREATE TRIGGER memories_ad AFTER DELETE ON memories BEGIN
                        INSERT INTO memories_fts(memories_fts, rowid, title, content)
                        VALUES ('delete', old.id, old.title, old.content);
                    END
                """)
                
                cursor.execute("""
                    CREATE TRIGGER memories_au AFTER UPDATE ON memories BEGIN
                        INSERT INTO memories_fts(memories_fts, rowid, title, content)
                        VALUES ('delete', old.id, old.title, old.content);
                        INSERT INTO memories_fts(rowid, title, content)
                        VALUES (new.id, new.title, new.content);
                    END
                """)
                
                conn.commit()
                print_success("FTS5 索引 'memories_fts' 创建成功")
                print_success("已同步现有记忆数据")
                print_success("已创建自动同步触发器")
            except Exception as e:
                print_warn(f"创建 FTS5 索引失败：{e}")
                conn.rollback()
        else:
            print_warn("memories_fts 已存在，跳过")
    else:
        print_warn("memories 表不存在，跳过 FTS5 创建")
    
    # ========== 2. 增强 secure_credentials 表 ==========
    print_step("2. 检查/创建 secure_credentials 表")
    
    if not check_table_exists(cursor, 'secure_credentials'):
        try:
            cursor.execute("""
                CREATE TABLE secure_credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT UNIQUE NOT NULL,
                    credential_type TEXT DEFAULT 'api_key',
                    encrypted_value BLOB,
                    encryption_key_ref TEXT,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used_at DATETIME,
                    expires_at DATETIME,
                    metadata TEXT
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX idx_secure_service ON secure_credentials(service_name)")
            cursor.execute("CREATE INDEX idx_secure_expires ON secure_credentials(expires_at)")
            
            conn.commit()
            print_success("secure_credentials 表创建成功")
            print_success("已创建 service_name 和 expires_at 索引")
        except Exception as e:
            print_warn(f"创建 secure_credentials 表失败：{e}")
            conn.rollback()
    else:
        print_warn("secure_credentials 表已存在")
    
    # ========== 3. 增强 registered_tools 表 ==========
    print_step("3. 检查/增强 registered_tools 表")
    
    if check_table_exists(cursor, 'registered_tools'):
        # 检查是否缺少字段
        cursor.execute("PRAGMA table_info(registered_tools)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        needed_columns = {
            'description': 'TEXT',
            'capabilities': 'TEXT',
            'success_count': 'INTEGER DEFAULT 0',
            'fail_count': 'INTEGER DEFAULT 0',
            'last_used': 'DATETIME',
            'metadata': 'TEXT'
        }
        
        altered = False
        for col_name, col_type in needed_columns.items():
            if col_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE registered_tools ADD COLUMN {col_name} {col_type}")
                    print_success(f"添加列：{col_name}")
                    altered = True
                except Exception as e:
                    print_warn(f"添加列 {col_name} 失败：{e}")
        
        if altered:
            conn.commit()
            print_success("registered_tools 表增强完成")
        else:
            print_warn("registered_tools 表结构已是最新")
    else:
        # 创建表
        try:
            cursor.execute("""
                CREATE TABLE registered_tools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_name TEXT UNIQUE NOT NULL,
                    tool_type TEXT DEFAULT 'builtin',
                    endpoint TEXT,
                    description TEXT,
                    capabilities TEXT,
                    success_count INTEGER DEFAULT 0,
                    fail_count INTEGER DEFAULT 0,
                    last_used DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            cursor.execute("CREATE INDEX idx_tool_name ON registered_tools(tool_name)")
            cursor.execute("CREATE INDEX idx_tool_type ON registered_tools(tool_type)")
            
            conn.commit()
            print_success("registered_tools 表创建成功")
        except Exception as e:
            print_warn(f"创建 registered_tools 表失败：{e}")
            conn.rollback()
    
    # ========== 4. 创建 MCP Server 工具配置 ==========
    print_step("4. 创建 MCP Server 工具配置文件")
    
    mcp_config = {
        "mcpTools": {
            "read": {
                "description": "读取记忆内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键词"},
                        "limit": {"type": "integer", "default": 10, "description": "返回数量"},
                        "type": {"type": "string", "enum": ["all", "event", "learning", "improvement"], "description": "记忆类型"}
                    }
                },
                "handler": "memory_search"
            },
            "add": {
                "description": "添加新记忆",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["event", "learning", "improvement"], "required": True},
                        "title": {"type": "string", "required": True},
                        "content": {"type": "string", "required": True},
                        "category": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "importance": {"type": "integer", "default": 5}
                    }
                },
                "handler": "memory_add"
            },
            "status": {
                "description": "获取记忆系统状态",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
                "handler": "memory_status"
            },
            "diary": {
                "description": "写入 Agent 日记",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "format": "date", "required": True},
                        "summary": {"type": "string"},
                        "aaak_entry": {"type": "string"},
                        "learnings": {"type": "array", "items": {"type": "string"}},
                        "decisions": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "handler": "diary_write"
            },
            "evolution": {
                "description": "查看进化日志",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 10},
                        "evolution_type": {"type": "string"}
                    }
                },
                "handler": "evolution_log"
            },
            "tool_register": {
                "description": "注册新工具",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tool_name": {"type": "string", "required": True},
                        "tool_type": {"type": "string", "enum": ["builtin", "mcp", "http", "cli"]},
                        "endpoint": {"type": "string"},
                        "description": {"type": "string"},
                        "capabilities": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "handler": "tool_register"
            }
        },
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "description": "记忆系统 MCP Server 工具配置"
    }
    
    mcp_config_path = os.path.join(SCRIPTS_DIR, 'mcp_tools_config.json')
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    
    with open(mcp_config_path, 'w', encoding='utf-8') as f:
        json.dump(mcp_config, f, ensure_ascii=False, indent=2)
    
    print_success(f"MCP 工具配置已保存：{mcp_config_path}")
    
    # ========== 5. 创建记忆系统状态检查脚本 ==========
    print_step("5. 创建记忆系统状态检查脚本")
    
    status_script = '''#!/usr/bin/env python3
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
'''
    
    status_script_path = os.path.join(SCRIPTS_DIR, 'memory_status.py')
    with open(status_script_path, 'w', encoding='utf-8') as f:
        f.write(status_script)
    
    print_success(f"状态检查脚本已保存：{status_script_path}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("阶段一优化完成!")
    print("=" * 60)
    print("\n已实施:")
    print("  1. FTS5 全文搜索索引 (memories_fts)")
    print("  2. 凭证安全存储表 (secure_credentials)")
    print("  3. 工具注册表增强 (registered_tools)")
    print("  4. MCP Server 工具配置")
    print("  5. 状态检查脚本")
    print("\n下一步:")
    print("  - 运行 'python scripts/memory_status.py' 查看状态")
    print("  - 使用 FTS5 搜索：SELECT * FROM memories_fts WHERE memories_fts MATCH '关键词'")
    print("  - 配置 MCP Server 使用新工具")
    
    return True

if __name__ == '__main__':
    main()

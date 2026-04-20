#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统 MCP Server 实现
提供标准 MCP 接口供外部工具调用
"""

import sqlite3
import json
import os
import sys
import io
from datetime import datetime
from typing import Dict, Any, List, Optional

# 修复 Windows 编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB_PATH = os.getenv('DB_PATH', 'memory/database/xiaozhi_memory.db')

class MemoryMCP:
    def __init__(self):
        self.db_path = DB_PATH
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"数据库不存在：{self.db_path}")
    
    def _get_conn(self):
        return sqlite3.connect(self.db_path)
    
    # ========== 记忆搜索 ==========
    def memory_search(self, query: str = None, limit: int = 10, 
                      memory_type: str = None) -> List[Dict]:
        """搜索记忆"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        if query:
            # 使用 LIKE 搜索 (兼容中文)
            search_pattern = f'%{query}%'
            cursor.execute("""
                SELECT m.id, m.type, m.title, m.content, m.category, 
                       m.tags, m.importance, m.created_at
                FROM memories m
                WHERE m.title LIKE ? OR m.content LIKE ?
                ORDER BY m.importance DESC, m.created_at DESC
                LIMIT ?
            """, (search_pattern, search_pattern, limit))
        else:
            # 按类型查询
            sql = "SELECT * FROM memories"
            params = []
            if memory_type:
                sql += " WHERE type = ?"
                params.append(memory_type)
            sql += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
        
        columns = ['id', 'type', 'title', 'content', 'category', 
                   'tags', 'importance', 'created_at']
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'type': row[1],
                'title': row[2],
                'content': row[3],
                'category': row[4],
                'tags': json.loads(row[5]) if row[5] else [],
                'importance': row[6],
                'created_at': row[7]
            })
        
        conn.close()
        return results
    
    # ========== 添加记忆 ==========
    def memory_add(self, memory_type: str, title: str, content: str,
                   category: str = None, tags: List[str] = None,
                   importance: int = 5) -> int:
        """添加新记忆"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        tags_json = json.dumps(tags) if tags else None
        
        cursor.execute("""
            INSERT INTO memories (type, title, content, category, tags, importance)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (memory_type, title, content, category, tags_json, importance))
        
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return memory_id
    
    # ========== 系统状态 ==========
    def memory_status(self) -> Dict:
        """获取系统状态"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        stats = {}
        
        # 记忆统计
        cursor.execute("SELECT COUNT(*) FROM memories")
        stats['total_memories'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT type, COUNT(*) FROM memories GROUP BY type")
        stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 情景记忆
        cursor.execute("SELECT COUNT(*) FROM episodic_memories")
        stats['episodic_count'] = cursor.fetchone()[0]
        
        # 语义记忆
        cursor.execute("SELECT COUNT(*) FROM semantic_memories")
        stats['semantic_count'] = cursor.fetchone()[0]
        
        # 平台消息
        cursor.execute("SELECT COUNT(*) FROM platform_messages")
        stats['platform_messages'] = cursor.fetchone()[0]
        
        # 进化日志
        cursor.execute("SELECT COUNT(*) FROM evolution_log")
        stats['evolution_logs'] = cursor.fetchone()[0]
        
        # 工具注册
        cursor.execute("SELECT COUNT(*) FROM registered_tools")
        stats['registered_tools'] = cursor.fetchone()[0]
        
        # FTS5 状态
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories_fts'")
        stats['fts5_enabled'] = cursor.fetchone() is not None
        
        if stats['fts5_enabled']:
            cursor.execute("SELECT COUNT(*) FROM memories_fts")
            stats['fts5_indexed'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    # ========== 日记写入 ==========
    def diary_write(self, date: str, summary: str = None, 
                    aaak_entry: str = None, 
                    learnings: List[str] = None,
                    decisions: List[str] = None) -> int:
        """写入 Agent 日记"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        diary_data = {
            'summary': summary,
            'aaak_entry': aaak_entry,
            'learnings': learnings or [],
            'decisions': decisions or [],
            'created_at': datetime.now().isoformat()
        }
        
        cursor.execute("""
            INSERT INTO agent_diary (date, summary, aaak_entry, learnings, decisions)
            VALUES (?, ?, ?, ?, ?)
        """, (date, summary, aaak_entry, 
              json.dumps(learnings) if learnings else None,
              json.dumps(decisions) if decisions else None))
        
        diary_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return diary_id
    
    # ========== 进化日志 ==========
    def evolution_log(self, limit: int = 10, 
                      evolution_type: str = None) -> List[Dict]:
        """查看进化日志"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        sql = "SELECT * FROM evolution_log"
        params = []
        
        if evolution_type:
            sql += " WHERE evolution_type = ?"
            params.append(evolution_type)
        
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        
        columns = ['id', 'evolution_type', 'description', 
                   'before_state', 'after_state', 'trigger', 'created_at']
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'type': row[1],
                'description': row[2],
                'before': json.loads(row[3]) if row[3] else None,
                'after': json.loads(row[4]) if row[4] else None,
                'trigger': row[5],
                'created_at': row[6]
            })
        
        conn.close()
        return results
    
    # ========== 工具注册 ==========
    def tool_register(self, tool_name: str, tool_type: str = 'builtin',
                      endpoint: str = None, description: str = None,
                      capabilities: List[str] = None) -> int:
        """注册新工具"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO registered_tools 
            (tool_name, tool_type, endpoint, description, capabilities, last_used)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (tool_name, tool_type, endpoint, description,
              json.dumps(capabilities) if capabilities else None))
        
        tool_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return tool_id
    
    # ========== 凭证管理 ==========
    def credential_store(self, service_name: str, credential_type: str,
                         encrypted_value: bytes, description: str = None,
                         expires_at: str = None) -> int:
        """存储凭证"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO secure_credentials 
            (service_name, credential_type, encrypted_value, description, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """, (service_name, credential_type, encrypted_value, description, expires_at))
        
        cred_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return cred_id
    
    def credential_get(self, service_name: str) -> Optional[bytes]:
        """获取凭证"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT encrypted_value FROM secure_credentials 
            WHERE service_name = ? AND (expires_at IS NULL OR expires_at > date('now'))
        """, (service_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None


# ========== MCP Server 主程序 ==========
def main():
    """MCP Server 入口"""
    if len(sys.argv) < 2:
        print("用法：python mcp_server.py <method> [args]")
        print("\n可用方法:")
        print("  search <query> [limit]     - 搜索记忆")
        print("  add <type> <title> <content> - 添加记忆")
        print("  status                     - 系统状态")
        print("  diary <date> [summary]     - 写日记")
        print("  evolution [limit]          - 进化日志")
        print("  register <name> <type>     - 注册工具")
        return
    
    mcp = MemoryMCP()
    method = sys.argv[1]
    
    try:
        if method == 'search':
            query = sys.argv[2] if len(sys.argv) > 2 else None
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            results = mcp.memory_search(query, limit)
            print(json.dumps(results, ensure_ascii=False, indent=2))
        
        elif method == 'add':
            if len(sys.argv) < 5:
                print("错误：需要 type 和 title 参数")
                return
            memory_type = sys.argv[2]
            title = sys.argv[3]
            content = sys.argv[4] if len(sys.argv) > 4 else ""
            memory_id = mcp.memory_add(memory_type, title, content)
            print(json.dumps({"id": memory_id, "status": "created"}))
        
        elif method == 'status':
            status = mcp.memory_status()
            print(json.dumps(status, ensure_ascii=False, indent=2))
        
        elif method == 'diary':
            if len(sys.argv) < 3:
                print("错误：需要 date 参数")
                return
            date = sys.argv[2]
            summary = sys.argv[3] if len(sys.argv) > 3 else None
            diary_id = mcp.diary_write(date, summary)
            print(json.dumps({"id": diary_id, "status": "written"}))
        
        elif method == 'evolution':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            logs = mcp.evolution_log(limit)
            print(json.dumps(logs, ensure_ascii=False, indent=2))
        
        elif method == 'register':
            if len(sys.argv) < 4:
                print("错误：需要 tool_name 和 tool_type")
                return
            tool_name = sys.argv[2]
            tool_type = sys.argv[3]
            tool_id = mcp.tool_register(tool_name, tool_type)
            print(json.dumps({"id": tool_id, "status": "registered"}))
        
        else:
            print(f"未知方法：{method}")
    
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

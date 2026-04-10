#!/usr/bin/env python3
"""
统一记忆系统 v2.0
整合自：OpenViking, MemPalace, Engram, Memoh, Phantom, Agent-Reach
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

DB_PATH = os.path.expanduser('~/.openclaw/workspace/memory/database/xiaozhi_memory.db')

class UnifiedMemory:
    """统一记忆系统 v2.0"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
    def close(self):
        if self.conn:
            self.conn.close()
    
    # ========== 多平台消息处理 (Memoh 风格) ==========
    
    def store_message(self, platform: str, channel_id: str, 
                      content: str, sender_id: str = None,
                      message_type: str = 'text', metadata: dict = None) -> int:
        """存储平台消息"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO platform_messages 
            (platform, channel_id, sender_id, message_type, content, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (platform, channel_id, sender_id, message_type, 
              content, json.dumps(metadata) if metadata else None))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_messages(self, platform: str, channel_id: str, 
                     limit: int = 50) -> List[Dict]:
        """获取频道消息"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM platform_messages 
            WHERE platform = ? AND channel_id = ?
            ORDER BY created_at DESC LIMIT ?
        ''', (platform, channel_id, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    # ========== 自进化系统 (Phantom 风格) ==========
    
    def log_evolution(self, evolution_type: str, description: str,
                      before_state: dict = None, after_state: dict = None,
                      trigger: str = 'self_discovered') -> int:
        """记录进化"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO evolution_log 
            (evolution_type, description, before_state, after_state, trigger)
            VALUES (?, ?, ?, ?, ?)
        ''', (evolution_type, description, 
              json.dumps(before_state) if before_state else None,
              json.dumps(after_state) if after_state else None,
              trigger))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_evolution_history(self, limit: int = 20) -> List[Dict]:
        """获取进化历史"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM evolution_log 
            ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ========== 工具注册 (OpenViking 风格) ==========
    
    def register_tool(self, tool_name: str, tool_type: str,
                      description: str, endpoint: str = None,
                      capabilities: List[str] = None) -> int:
        """注册工具"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO registered_tools 
            (tool_name, tool_type, endpoint, description, capabilities)
            VALUES (?, ?, ?, ?, ?)
        ''', (tool_name, tool_type, endpoint, description,
              json.dumps(capabilities) if capabilities else None))
        self.conn.commit()
        return cursor.lastrowid
    
    def record_tool_usage(self, tool_name: str, success: bool):
        """记录工具使用"""
        cursor = self.conn.cursor()
        if success:
            cursor.execute('''
                UPDATE registered_tools 
                SET success_count = success_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE tool_name = ?
            ''', (tool_name,))
        else:
            cursor.execute('''
                UPDATE registered_tools 
                SET fail_count = fail_count + 1
                WHERE tool_name = ?
            ''', (tool_name,))
        self.conn.commit()
    
    def list_tools(self, tool_type: str = None) -> List[Dict]:
        """列出工具"""
        cursor = self.conn.cursor()
        if tool_type:
            cursor.execute('''
                SELECT * FROM registered_tools WHERE tool_type = ?
            ''', (tool_type,))
        else:
            cursor.execute('SELECT * FROM registered_tools')
        return [dict(row) for row in cursor.fetchall()]
    
    # ========== 分层上下文 (OpenViking 风格) ==========
    
    def set_context(self, layer_level: int, context_key: str,
                    context_value: Any, parent_id: int = None,
                    ttl_hours: int = None):
        """设置分层上下文
        layer_level: 1=session, 2=task, 3=project, 4=global
        """
        cursor = self.conn.cursor()
        valid_until = None
        if ttl_hours:
            valid_until = datetime.now() + timedelta(hours=ttl_hours)
        cursor.execute('''
            INSERT INTO layered_context 
            (layer_level, context_key, context_value, parent_context_id, valid_until)
            VALUES (?, ?, ?, ?, ?)
        ''', (layer_level, context_key, json.dumps(context_value), 
              parent_id, valid_until))
        self.conn.commit()
    
    def get_context(self, context_key: str = None, 
                    layer_level: int = None) -> List[Dict]:
        """获取上下文"""
        cursor = self.conn.cursor()
        # 清理过期的
        cursor.execute('''
            DELETE FROM layered_context 
            WHERE valid_until IS NOT NULL AND valid_until < CURRENT_TIMESTAMP
        ''')
        
        conditions = []
        params = []
        if context_key:
            conditions.append('context_key = ?')
            params.append(context_key)
        if layer_level:
            conditions.append('layer_level = ?')
            params.append(layer_level)
        
        if conditions:
            query = f'''
                SELECT * FROM layered_context 
                WHERE {' AND '.join(conditions)}
                ORDER BY layer_level, created_at DESC
            '''
        else:
            query = 'SELECT * FROM layered_context ORDER BY layer_level, created_at DESC'
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_full_context(self, max_level: int = 4) -> Dict:
        """获取完整分层上下文"""
        contexts = {1: {}, 2: {}, 3: {}, 4: {}}
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM layered_context 
            WHERE layer_level <= ? AND (valid_until IS NULL OR valid_until > CURRENT_TIMESTAMP)
            ORDER BY layer_level, created_at
        ''', (max_level,))
        
        for row in cursor.fetchall():
            layer = row['layer_level']
            key = row['context_key']
            value = json.loads(row['context_value']) if row['context_value'] else None
            contexts[layer][key] = value
        
        return contexts
    
    # ========== 会话摘要 ==========
    
    def create_session_summary(self, session_id: str, platform: str,
                               summary: str, key_topics: List[str] = None,
                               action_items: List[str] = None):
        """创建会话摘要"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO session_summaries 
            (session_id, platform, summary, key_topics, action_items, started_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (session_id, platform, summary, 
              json.dumps(key_topics) if key_topics else None,
              json.dumps(action_items) if action_items else None))
        self.conn.commit()
    
    def end_session(self, session_id: str):
        """结束会话"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE session_summaries 
            SET ended_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        ''', (session_id,))
        self.conn.commit()
    
    # ========== 状态报告 ==========
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        cursor = self.conn.cursor()
        
        status = {
            'tables': {},
            'tools': 0,
            'recent_evolution': 0,
        }
        
        # 统计各表记录数
        tables = ['episodic_memories', 'semantic_memories', 'procedural_memories',
                  'working_memory', 'agent_diary', 'platform_messages', 
                  'evolution_log', 'registered_tools', 'layered_context', 'session_summaries']
        
        for table in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                status['tables'][table] = cursor.fetchone()[0]
            except:
                status['tables'][table] = 0
        
        # 统计工具数
        status['tools'] = status['tables'].get('registered_tools', 0)
        
        # 统计最近进化数
        cursor.execute('''
            SELECT COUNT(*) FROM evolution_log 
            WHERE created_at > datetime('now', '-7 days')
        ''')
        status['recent_evolution'] = cursor.fetchone()[0]
        
        return status

# 单例
_unified = None

def get_unified_memory() -> UnifiedMemory:
    global _unified
    if _unified is None:
        _unified = UnifiedMemory()
        _unified.connect()
    return _unified

if __name__ == '__main__':
    mem = get_unified_memory()
    
    # 注册 Agent-Reach 工具
    mem.register_tool('agent-reach', 'mcp', '互联网数据获取', 'cli', 
                     ['web', 'github', 'youtube', 'bilibili', 'weibo'])
    
    # 设置全局上下文
    mem.set_context(4, 'system_version', '2.0')
    mem.set_context(4, 'integrations', ['OpenViking', 'MemPalace', 'Engram', 'Memoh', 'Phantom'])
    
    # 记录进化
    mem.log_evolution(
        evolution_type='system_upgrade',
        description='整合5个项目精华，升级到v2.0',
        trigger='user_request'
    )
    
    # 测试平台消息
    mem.store_message('feishu', 'test_channel', '测试消息', 'user_001')
    
    print('统一记忆系统 v2.0 初始化完成！')
    print('状态:', json.dumps(mem.get_status(), indent=2, ensure_ascii=False))

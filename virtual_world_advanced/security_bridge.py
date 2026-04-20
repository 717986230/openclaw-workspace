"""
Erbing 虚拟世界 - 安全桥梁
Security Bridge for Safe Virtual World Operations
"""

import sqlite3
import json
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum, auto


class SecurityLevel(Enum):
    """安全级别"""
    PUBLIC = 1
    PROTECTED = 2
    PRIVATE = 3
    RESTRICTED = 4
    TOP_SECRET = 5


class AccessType(Enum):
    """访问类型"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class SecurityContext:
    """安全上下文"""
    capsule_id: str
    security_level: int
    permissions: List[str]
    session_token: str
    expires_at: str
    created_at: str


class SecurityBridge:
    """
    安全桥梁
    管理虚拟世界中的安全访问、数据隔离和通信加密
    """
    
    def __init__(self, db_path: str = "security_bridge.db"):
        self.db_path = db_path
        self.init_database()
        self.active_sessions: Dict[str, SecurityContext] = {}
        
    def init_database(self):
        """初始化安全数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 安全会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_sessions (
                session_id TEXT PRIMARY KEY,
                capsule_id TEXT NOT NULL,
                session_token TEXT NOT NULL,
                security_level INTEGER DEFAULT 1,
                permissions TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # 安全事件日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                event_type TEXT NOT NULL,
                event_data TEXT,
                severity TEXT DEFAULT 'info',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES security_sessions(session_id)
            )
        ''')
        
        # 权限表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                capsule_id TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT,
                access_type TEXT NOT NULL,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                granted_by TEXT
            )
        ''')
        
        # 数据隔离区表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS isolated_data (
                data_id TEXT PRIMARY KEY,
                capsule_id TEXT NOT NULL,
                data_type TEXT NOT NULL,
                encrypted_data TEXT NOT NULL,
                encryption_key_hash TEXT NOT NULL,
                security_level INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        # 安全策略表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_policies (
                policy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_name TEXT NOT NULL,
                policy_type TEXT NOT NULL,
                rules TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # 加载默认安全策略
        self.load_default_policies()
    
    def load_default_policies(self):
        """加载默认安全策略"""
        policies = [
            {
                'policy_name': 'basic_isolation',
                'policy_type': 'data_isolation',
                'rules': json.dumps({
                    'rule': 'capsule_data_isolation',
                    'description': 'Each capsule can only access its own data',
                    'enforcement': 'strict'
                })
            },
            {
                'policy_name': 'session_timeout',
                'policy_type': 'session',
                'rules': json.dumps({
                    'max_duration_hours': 24,
                    'idle_timeout_minutes': 30,
                    'require_reauth': True
                })
            },
            {
                'policy_name': 'rate_limiting',
                'policy_type': 'access_control',
                'rules': json.dumps({
                    'max_requests_per_minute': 60,
                    'max_failed_attempts': 5,
                    'lockout_duration_minutes': 15
                })
            },
            {
                'policy_name': 'encryption_required',
                'policy_type': 'data_security',
                'rules': json.dumps({
                    'algorithm': 'AES-256-GCM',
                    'key_rotation_days': 30,
                    'require_encryption_for_sensitive': True
                })
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查是否已有策略
        cursor.execute('SELECT COUNT(*) FROM security_policies')
        count = cursor.fetchone()[0]
        
        if count == 0:
            for policy in policies:
                cursor.execute('''
                    INSERT INTO security_policies (policy_name, policy_type, rules)
                    VALUES (?, ?, ?)
                ''', (policy['policy_name'], policy['policy_type'], policy['rules']))
            
            conn.commit()
        
        conn.close()
    
    def create_session(self, capsule_id: str, security_level: int = 1,
                      duration_hours: int = 24) -> SecurityContext:
        """
        创建安全会话
        """
        # 生成会话令牌
        session_id = hashlib.sha256(f"{capsule_id}_{datetime.now()}".encode()).hexdigest()
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=duration_hours)
        
        # 根据安全级别分配权限
        permissions = self.get_permissions_for_level(security_level)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_sessions 
            (session_id, capsule_id, session_token, security_level, permissions, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, capsule_id, session_token, security_level, 
              json.dumps(permissions), expires_at.isoformat()))
        
        conn.commit()
        conn.close()
        
        # 记录安全事件
        self.log_security_event(session_id, 'session_created', {
            'capsule_id': capsule_id,
            'security_level': security_level,
            'expires_at': expires_at.isoformat()
        })
        
        context = SecurityContext(
            capsule_id=capsule_id,
            security_level=security_level,
            permissions=permissions,
            session_token=session_token,
            expires_at=expires_at.isoformat(),
            created_at=datetime.now().isoformat()
        )
        
        self.active_sessions[session_id] = context
        
        return context
    
    def get_permissions_for_level(self, level: int) -> List[str]:
        """根据安全级别获取权限"""
        permissions_map = {
            1: ['read:public', 'execute:basic'],
            2: ['read:public', 'read:protected', 'execute:basic', 'execute:intermediate'],
            3: ['read:public', 'read:protected', 'read:private', 'execute:all', 'write:own'],
            4: ['read:all', 'execute:all', 'write:all', 'admin:own'],
            5: ['read:all', 'execute:all', 'write:all', 'admin:all', 'security:manage']
        }
        
        return permissions_map.get(level, permissions_map[1])
    
    def validate_session(self, session_token: str) -> Optional[SecurityContext]:
        """
        验证会话令牌
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, capsule_id, security_level, permissions, expires_at, status
            FROM security_sessions
            WHERE session_token = ?
        ''', (session_token,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # 检查状态
        if row[5] != 'active':
            return None
        
        # 检查过期时间
        expires_at = datetime.fromisoformat(row[4])
        if datetime.now() > expires_at:
            self.invalidate_session(session_token)
            return None
        
        # 更新最后活动时间
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE security_sessions SET last_activity = CURRENT_TIMESTAMP
            WHERE session_token = ?
        ''', (session_token,))
        conn.commit()
        conn.close()
        
        return SecurityContext(
            capsule_id=row[1],
            security_level=row[2],
            permissions=json.loads(row[3]),
            session_token=session_token,
            expires_at=row[4],
            created_at=datetime.now().isoformat()
        )
    
    def invalidate_session(self, session_token: str) -> bool:
        """使会话失效"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE security_sessions SET status = 'invalidated'
            WHERE session_token = ?
        ''', (session_token,))
        
        conn.commit()
        conn.close()
        
        # 记录安全事件
        cursor.execute('''
            SELECT session_id FROM security_sessions WHERE session_token = ?
        ''', (session_token,))
        
        row = cursor.fetchone()
        if row:
            self.log_security_event(row[0], 'session_invalidated', {
                'reason': 'token_validation_failed'
            })
        
        return True
    
    def check_permission(self, session_token: str, required_permission: str) -> bool:
        """
        检查权限
        """
        context = self.validate_session(session_token)
        if not context:
            return False
        
        return required_permission in context.permissions
    
    def encrypt_data(self, capsule_id: str, data: Any, security_level: int = 1) -> str:
        """
        加密数据
        """
        # 生成加密密钥
        encryption_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(encryption_key.encode()).hexdigest()
        
        # 简单加密（实际应用中应使用AES-256-GCM）
        data_json = json.dumps(data, ensure_ascii=False)
        encrypted = hashlib.sha256(f"{encryption_key}{data_json}".encode()).hexdigest()
        
        # 存储加密数据
        data_id = f"DATA-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(8)}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO isolated_data 
            (data_id, capsule_id, data_type, encrypted_data, encryption_key_hash, security_level)
            VALUES (?, ?, 'json', ?, ?, ?)
        ''', (data_id, capsule_id, encrypted, key_hash, security_level))
        
        conn.commit()
        conn.close()
        
        # 记录安全事件
        self.log_security_event(None, 'data_encrypted', {
            'data_id': data_id,
            'capsule_id': capsule_id,
            'security_level': security_level
        })
        
        return data_id
    
    def decrypt_data(self, capsule_id: str, data_id: str, session_token: str) -> Optional[Any]:
        """
        解密数据
        """
        # 验证会话
        context = self.validate_session(session_token)
        if not context or context.capsule_id != capsule_id:
            self.log_security_event(None, 'unauthorized_access_attempt', {
                'capsule_id': capsule_id,
                'data_id': data_id,
                'reason': 'invalid_session_or_capsule_mismatch'
            }, severity='warning')
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT encrypted_data, security_level, encryption_key_hash
            FROM isolated_data
            WHERE data_id = ? AND capsule_id = ?
        ''', (data_id, capsule_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            self.log_security_event(None, 'data_not_found', {
                'capsule_id': capsule_id,
                'data_id': data_id
            }, severity='warning')
            return None
        
        # 检查安全级别
        if row[1] > context.security_level:
            self.log_security_event(None, 'insufficient_security_level', {
                'capsule_id': capsule_id,
                'data_id': data_id,
                'required_level': row[1],
                'current_level': context.security_level
            }, severity='warning')
            return None
        
        # 更新访问记录
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE isolated_data 
            SET last_accessed = CURRENT_TIMESTAMP, access_count = access_count + 1
            WHERE data_id = ?
        ''', (data_id,))
        conn.commit()
        conn.close()
        
        # 返回解密数据（实际应用中应解密）
        return {'data_id': data_id, 'encrypted_hash': row[0]}
    
    def log_security_event(self, session_id: Optional[str], event_type: str, 
                          event_data: Dict, severity: str = 'info'):
        """记录安全事件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_events (session_id, event_type, event_data, severity)
            VALUES (?, ?, ?, ?)
        ''', (session_id, event_type, json.dumps(event_data, ensure_ascii=False), severity))
        
        conn.commit()
        conn.close()
    
    def get_security_report(self, capsule_id: str) -> Dict:
        """获取安全报告"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 会话统计
        cursor.execute('''
            SELECT COUNT(*), 
                   SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN status = 'invalidated' THEN 1 ELSE 0 END)
            FROM security_sessions
            WHERE capsule_id = ?
        ''', (capsule_id,))
        
        session_stats = cursor.fetchone()
        
        # 安全事件统计
        cursor.execute('''
            SELECT severity, COUNT(*)
            FROM security_events
            WHERE event_data LIKE ?
            GROUP BY severity
        ''', (f'%{capsule_id}%',))
        
        event_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 数据统计
        cursor.execute('''
            SELECT COUNT(*), SUM(access_count)
            FROM isolated_data
            WHERE capsule_id = ?
        ''', (capsule_id,))
        
        data_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'capsule_id': capsule_id,
            'sessions': {
                'total': session_stats[0],
                'active': session_stats[1],
                'invalidated': session_stats[2]
            },
            'events': event_stats,
            'data': {
                'total_items': data_stats[0],
                'total_accesses': data_stats[1] or 0
            },
            'security_score': self.calculate_security_score(session_stats, event_stats, data_stats)
        }
    
    def calculate_security_score(self, session_stats, event_stats, data_stats) -> float:
        """计算安全评分"""
        # 基础分
        base_score = 100.0
        
        # 扣分项
        warnings = event_stats.get('warning', 0)
        errors = event_stats.get('error', 0)
        
        deduction = (warnings * 2) + (errors * 10)
        
        return max(0.0, base_score - deduction)
    
    def enforce_rate_limit(self, capsule_id: str) -> bool:
        """执行速率限制"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取最近1分钟的请求数
        one_minute_ago = (datetime.now() - timedelta(minutes=1)).isoformat()
        
        cursor.execute('''
            SELECT COUNT(*)
            FROM security_events
            WHERE event_data LIKE ? AND timestamp > ?
        ''', (f'%{capsule_id}%', one_minute_ago))
        
        request_count = cursor.fetchone()[0]
        conn.close()
        
        # 获取速率限制策略
        max_requests = 60  # 默认每分钟60次
        
        return request_count < max_requests
    
    def cleanup_expired_sessions(self):
        """清理过期会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE security_sessions 
            SET status = 'expired'
            WHERE expires_at < CURRENT_TIMESTAMP AND status = 'active'
        ''')
        
        expired_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if expired_count > 0:
            self.log_security_event(None, 'sessions_cleaned', {
                'count': expired_count
            })
        
        return expired_count

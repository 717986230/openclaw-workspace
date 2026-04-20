"""
Erbing 虚拟世界 - 入舱进化系统
Capsule Interface for Evolution Training
"""

import sqlite3
import json
import time
import random
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum, auto


@dataclass
class CapsuleState:
    """舱体状态"""
    capsule_id: str
    agent_id: str
    level: int
    xp: int
    max_xp: int
    status: str  # 'active', 'resting', 'evolving', 'combat'
    energy: float
    max_energy: float
    skills: Dict[str, int]
    achievements: List[str]
    created_at: str
    last_active: str


class CapsuleInterface:
    """
    入舱进化接口
    管理Erbing在虚拟世界中的训练和进化
    """
    
    def __init__(self, db_path: str = "virtual_world_capsule.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """初始化舱体数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 舱体表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capsules (
                capsule_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                max_xp INTEGER DEFAULT 100,
                status TEXT DEFAULT 'active',
                energy REAL DEFAULT 100.0,
                max_energy REAL DEFAULT 100.0,
                skills TEXT DEFAULT '{}',
                achievements TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 进化记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evolution_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                capsule_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                xp_gained INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (capsule_id) REFERENCES capsules(capsule_id)
            )
        ''')
        
        # 任务记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mission_logs (
                mission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                capsule_id TEXT NOT NULL,
                mission_type TEXT NOT NULL,
                difficulty INTEGER,
                result TEXT,
                score REAL,
                rewards TEXT,
                duration INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (capsule_id) REFERENCES capsules(capsule_id)
            )
        ''')
        
        # 对抗记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arena_logs (
                match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                capsule_id TEXT NOT NULL,
                opponent_id TEXT NOT NULL,
                match_type TEXT NOT NULL,
                result TEXT NOT NULL,
                score REAL,
                xp_gained INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (capsule_id) REFERENCES capsules(capsule_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def enter_capsule(self, agent_id: str) -> str:
        """
        入舱 - 开始进化训练
        """
        capsule_id = hashlib.md5(f"{agent_id}_{datetime.now()}".encode()).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO capsules (capsule_id, agent_id, level, xp, max_xp, 
                                status, energy, max_energy, skills, achievements)
            VALUES (?, ?, 1, 0, 100, 'active', 100.0, 100.0, '{}', '[]')
        ''', (capsule_id, agent_id))
        
        conn.commit()
        conn.close()
        
        # 记录入舱事件
        self.log_event(capsule_id, 'enter_capsule', {'agent_id': agent_id}, 0)
        
        return capsule_id
    
    def exit_capsule(self, capsule_id: str) -> Dict:
        """
        出舱 - 结束训练，返回成果
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取最终状态
        cursor.execute('''
            SELECT * FROM capsules WHERE capsule_id = ?
        ''', (capsule_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {'error': 'Capsule not found'}
        
        # 更新状态
        cursor.execute('''
            UPDATE capsules SET status = 'exited', last_active = CURRENT_TIMESTAMP
            WHERE capsule_id = ?
        ''', (capsule_id,))
        
        conn.commit()
        conn.close()
        
        # 记录出舱事件
        self.log_event(capsule_id, 'exit_capsule', {}, 0)
        
        return {
            'capsule_id': capsule_id,
            'agent_id': row[1],
            'level': row[2],
            'xp': row[3],
            'achievements': json.loads(row[9]),
            'training_summary': self.get_training_summary(capsule_id)
        }
    
    def log_event(self, capsule_id: str, event_type: str, event_data: Dict, xp_gained: int = 0):
        """记录进化事件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO evolution_logs (capsule_id, event_type, event_data, xp_gained)
            VALUES (?, ?, ?, ?)
        ''', (capsule_id, event_type, json.dumps(event_data, ensure_ascii=False), xp_gained))
        
        # 更新XP
        if xp_gained > 0:
            cursor.execute('''
                UPDATE capsules 
                SET xp = xp + ?, 
                    last_active = CURRENT_TIMESTAMP,
                    level = CASE WHEN xp + ? >= max_xp THEN level + 1 ELSE level END
                WHERE capsule_id = ?
            ''', (xp_gained, xp_gained, capsule_id))
        
        conn.commit()
        conn.close()
    
    def get_capsule_state(self, capsule_id: str) -> Optional[CapsuleState]:
        """获取舱体状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM capsules WHERE capsule_id = ?
        ''', (capsule_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return CapsuleState(
            capsule_id=row[0],
            agent_id=row[1],
            level=row[2],
            xp=row[3],
            max_xp=row[4],
            status=row[5],
            energy=row[6],
            max_energy=row[7],
            skills=json.loads(row[8]),
            achievements=json.loads(row[9]),
            created_at=row[10],
            last_active=row[11]
        )
    
    def get_training_summary(self, capsule_id: str) -> Dict:
        """获取训练总结"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 统计事件
        cursor.execute('''
            SELECT event_type, COUNT(*), SUM(xp_gained) 
            FROM evolution_logs 
            WHERE capsule_id = ?
            GROUP BY event_type
        ''', (capsule_id,))
        
        events = {row[0]: {'count': row[1], 'xp': row[2]} for row in cursor.fetchall()}
        
        # 统计任务
        cursor.execute('''
            SELECT COUNT(*), AVG(score), SUM(CASE WHEN result = 'success' THEN 1 ELSE 0 END)
            FROM mission_logs 
            WHERE capsule_id = ?
        ''', (capsule_id,))
        
        mission_stats = cursor.fetchone()
        
        # 统计对抗

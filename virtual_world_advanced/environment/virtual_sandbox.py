"""
Virtual Sandbox Core
"""

import sqlite3
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class SandboxState:
    """Sandbox state"""
    sandbox_id: str
    capsule_id: str
    universe_id: int
    time_dilation: float
    status: str
    created_at: str


class VirtualSandbox:
    """
    Virtual Sandbox Core
    Isolated environment for training and evolution
    """
    
    def __init__(self, db_path: str = "sandbox.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sandboxes (
                sandbox_id TEXT PRIMARY KEY,
                capsule_id TEXT NOT NULL,
                universe_id INTEGER DEFAULT 0,
                time_dilation REAL DEFAULT 1.0,
                status TEXT DEFAULT 'active',
                isolation_level INTEGER DEFAULT 1,
                resources TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sandbox_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sandbox_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_sandbox(self, capsule_id: str, universe_id: int = 0, 
                      time_dilation: float = 1.0) -> SandboxState:
        sandbox_id = f"SBX-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sandboxes (sandbox_id, capsule_id, universe_id, time_dilation)
            VALUES (?, ?, ?, ?)
        ''', (sandbox_id, capsule_id, universe_id, time_dilation))
        
        conn.commit()
        conn.close()
        
        self.log_event(sandbox_id, 'sandbox_created', {'capsule_id': capsule_id})
        
        return SandboxState(
            sandbox_id=sandbox_id,
            capsule_id=capsule_id,
            universe_id=universe_id,
            time_dilation=time_dilation,
            status='active',
            created_at=datetime.now().isoformat()
        )
    
    def log_event(self, sandbox_id: str, event_type: str, event_data: Dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sandbox_events (sandbox_id, event_type, event_data)
            VALUES (?, ?, ?)
        ''', (sandbox_id, event_type, json.dumps(event_data, ensure_ascii=False)))
        
        conn.commit()
        conn.close()
    
    def get_sandbox_state(self, sandbox_id: str) -> Optional[SandboxState]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sandboxes WHERE sandbox_id = ?', (sandbox_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return SandboxState(
            sandbox_id=row[0],
            capsule_id=row[1],
            universe_id=row[2],
            time_dilation=row[3],
            status=row[4],
            created_at=row[6]
        )
    
    def destroy_sandbox(self, sandbox_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE sandboxes SET status = ? WHERE sandbox_id = ?', 
                      ('destroyed', sandbox_id))
        
        conn.commit()
        conn.close()
        
        self.log_event(sandbox_id, 'sandbox_destroyed', {})

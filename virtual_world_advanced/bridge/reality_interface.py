"""
Reality Interface
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class RealitySync:
    sync_id: str
    capsule_id: str
    sync_type: str
    status: str
    timestamp: str


class RealityInterface:
    """
    Bridge between virtual world and reality
    """
    
    def __init__(self, db_path: str = "reality_interface.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reality_sync (
                sync_id TEXT PRIMARY KEY,
                capsule_id TEXT NOT NULL,
                sync_type TEXT NOT NULL,
                data TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def sync_to_reality(self, capsule_id: str, data: Dict) -> RealitySync:
        sync_id = f"SYNC-OUT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reality_sync (sync_id, capsule_id, sync_type, data, status)
            VALUES (?, ?, 'export', ?, 'completed')
        ''', (sync_id, capsule_id, json.dumps(data, ensure_ascii=False)))
        
        conn.commit()
        conn.close()
        
        return RealitySync(
            sync_id=sync_id,
            capsule_id=capsule_id,
            sync_type='export',
            status='completed',
            timestamp=datetime.now().isoformat()
        )
    
    def sync_from_reality(self, capsule_id: str, data: Dict) -> RealitySync:
        sync_id = f"SYNC-IN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reality_sync (sync_id, capsule_id, sync_type, data, status)
            VALUES (?, ?, 'import', ?, 'completed')
        ''', (sync_id, capsule_id, json.dumps(data, ensure_ascii=False)))
        
        conn.commit()
        conn.close()
        
        return RealitySync(
            sync_id=sync_id,
            capsule_id=capsule_id,
            sync_type='import',
            status='completed',
            timestamp=datetime.now().isoformat()
        )
    
    def get_sync_history(self, capsule_id: str, limit: int = 20) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM reality_sync 
            WHERE capsule_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (capsule_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'sync_id': r[0],
            'sync_type': r[2],
            'status': r[4],
            'created_at': r[5]
        } for r in rows]

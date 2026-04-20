"""
Capability Exporter
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ExportedCapability:
    capability_id: str
    capsule_id: str
    capability_type: str
    level: int
    data: Dict
    exported_at: str


class CapabilityExporter:
    """
    Export trained capabilities to reality
    """
    
    def __init__(self, db_path: str = "capability_export.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capabilities (
                capability_id TEXT PRIMARY KEY,
                capsule_id TEXT NOT NULL,
                capability_type TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                data TEXT NOT NULL,
                verified BOOLEAN DEFAULT 0,
                exported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def export_capability(self, capsule_id: str, capability_type: str, 
                         level: int, data: Dict) -> ExportedCapability:
        capability_id = f"CAP-{capability_type[:3].upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO capabilities (capability_id, capsule_id, capability_type, level, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (capability_id, capsule_id, capability_type, level, 
              json.dumps(data, ensure_ascii=False)))
        
        conn.commit()
        conn.close()
        
        return ExportedCapability(
            capability_id=capability_id,
            capsule_id=capsule_id,
            capability_type=capability_type,
            level=level,
            data=data,
            exported_at=datetime.now().isoformat()
        )
    
    def get_capabilities(self, capsule_id: str) -> List[ExportedCapability]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT capability_id, capsule_id, capability_type, level, data, exported_at
            FROM capabilities WHERE capsule_id = ?
        ''', (capsule_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [ExportedCapability(
            capability_id=r[0],
            capsule_id=r[1],
            capability_type=r[2],
            level=r[3],
            data=json.loads(r[4]),
            exported_at=r[5]
        ) for r in rows]
    
    def get_capability_summary(self, capsule_id: str) -> Dict:
        capabilities = self.get_capabilities(capsule_id)
        
        summary = {}
        for cap in capabilities:
            if cap.capability_type not in summary:
                summary[cap.capability_type] = {
                    'count': 0,
                    'max_level': 0,
                    'avg_level': 0,
                    'levels': []
                }
            summary[cap.capability_type]['count'] += 1
            summary[cap.capability_type]['levels'].append(cap.level)
            summary[cap.capability_type]['max_level'] = max(
                summary[cap.capability_type]['max_level'], cap.level)
        
        for cap_type in summary:
            levels = summary[cap_type]['levels']
            summary[cap_type]['avg_level'] = sum(levels) / len(levels)
        
        return summary

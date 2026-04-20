"""
Safety Guardian
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ThreatLevel(Enum):
    SAFE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SafetyReport:
    capsule_id: str
    threat_level: int
    violations: List[str]
    recommendations: List[str]
    timestamp: str


class SafetyGuardian:
    """
    Safety monitoring and protection system
    """
    
    def __init__(self, db_path: str = "safety_guardian.db"):
        self.db_path = db_path
        self.init_database()
        self.safety_rules = self.load_safety_rules()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS safety_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                capsule_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                details TEXT,
                action_taken TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS safety_violations (
                violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                capsule_id TEXT NOT NULL,
                rule_id TEXT NOT NULL,
                severity INTEGER,
                resolved BOOLEAN DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_safety_rules(self) -> Dict:
        return {
            'data_exfiltration': {
                'description': 'Prevent unauthorized data export',
                'severity': 4,
                'action': 'block'
            },
            'resource_abuse': {
                'description': 'Prevent excessive resource usage',
                'severity': 3,
                'action': 'throttle'
            },
            'unauthorized_access': {
                'description': 'Prevent access to restricted areas',
                'severity': 4,
                'action': 'block'
            },
            'malicious_code': {
                'description': 'Detect and block malicious code',
                'severity': 5,
                'action': 'quarantine'
            },
            'policy_violation': {
                'description': 'Enforce security policies',
                'severity': 2,
                'action': 'alert'
            }
        }
    
    def check_safety(self, capsule_id: str, action: str, data: Dict) -> SafetyReport:
        violations = []
        recommendations = []
        threat_level = ThreatLevel.SAFE.value
        
        # Check for data exfiltration
        if action == 'export' and data.get('sensitive', False):
            violations.append('data_exfiltration')
            threat_level = max(threat_level, self.safety_rules['data_exfiltration']['severity'])
            recommendations.append('Review data export permissions')
        
        # Check for resource abuse
        if data.get('resource_usage', 0) > 90:
            violations.append('resource_abuse')
            threat_level = max(threat_level, self.safety_rules['resource_abuse']['severity'])
            recommendations.append('Reduce resource consumption')
        
        # Check for unauthorized access
        if data.get('access_level', 0) > data.get('allowed_level', 0):
            violations.append('unauthorized_access')
            threat_level = max(threat_level, self.safety_rules['unauthorized_access']['severity'])
            recommendations.append('Verify access permissions')
        
        # Log event
        if violations:
            self.log_safety_event(capsule_id, 'violation', 
                                 self.severity_to_str(threat_level),
                                 {'violations': violations, 'action': action})
        
        return SafetyReport(
            capsule_id=capsule_id,
            threat_level=threat_level,
            violations=violations,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    def severity_to_str(self, level: int) -> str:
        mapping = {0: 'safe', 1: 'low', 2: 'medium', 3: 'high', 4: 'critical'}
        return mapping.get(level, 'unknown')
    
    def log_safety_event(self, capsule_id: str, event_type: str, 
                        severity: str, details: Dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO safety_events (capsule_id, event_type, severity, details)
            VALUES (?, ?, ?, ?)
        ''', (capsule_id, event_type, severity, json.dumps(details, ensure_ascii=False)))
        
        conn.commit()
        conn.close()
    
    def get_safety_report(self, capsule_id: str) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT severity, COUNT(*) 
            FROM safety_events 
            WHERE capsule_id = ?
            GROUP BY severity
        ''', (capsule_id,))
        
        severity_counts = {r[0]: r[1] for r in cursor.fetchall()}
        
        cursor.execute('''
            SELECT COUNT(*) FROM safety_violations
            WHERE capsule_id = ? AND resolved = 0
        ''', (capsule_id,))
        
        unresolved = cursor.fetchone()[0]
        conn.close()
        
        return {
            'capsule_id': capsule_id,
            'severity_counts': severity_counts,
            'unresolved_violations': unresolved,
            'safety_score': self.calculate_safety_score(severity_counts, unresolved)
        }
    
    def calculate_safety_score(self, severity_counts: Dict, unresolved: int) -> float:
        base_score = 100.0
        
        deductions = {
            'critical': 20,
            'high': 10,
            'medium': 5,
            'low': 2
        }
        
        for severity, count in severity_counts.items():
            if severity in deductions:
                base_score -= deductions[severity] * count
        
        base_score -= unresolved * 5
        
        return max(0.0, base_score)
    
    def quarantine_capsule(self, capsule_id: str, reason: str):
        self.log_safety_event(capsule_id, 'quarantine', 'critical', {'reason': reason})

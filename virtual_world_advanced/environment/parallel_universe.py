"""
Parallel Universe System
"""

import sqlite3
import json
import random
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Universe:
    universe_id: int
    name: str
    theme: str
    difficulty: float
    status: str


class ParallelUniverse:
    """
    Parallel Multiverse System
    Multiple training environments with different themes
    """
    
    def __init__(self, db_path: str = "multiverse.db"):
        self.db_path = db_path
        self.init_database()
        self.universes = self.load_universes()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS universes (
                universe_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                theme TEXT NOT NULL,
                difficulty REAL DEFAULT 1.0,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_universes(self) -> List[Universe]:
        default_universes = [
            Universe(1, "Tutorial World", "basic_training", 0.5, 'active'),
            Universe(2, "Code Forge", "coding_mastery", 1.0, 'active'),
            Universe(3, "Security Nexus", "hacking_defense", 1.5, 'active'),
            Universe(4, "AI Laboratory", "ai_development", 2.0, 'active'),
            Universe(5, "Battle Arena", "adversarial_training", 2.5, 'active'),
            Universe(6, "Research Hub", "knowledge_discovery", 1.8, 'active'),
            Universe(7, "System Core", "architecture_design", 2.2, 'active'),
            Universe(8, "Edge Cases", "extreme_scenarios", 3.0, 'active'),
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM universes')
        count = cursor.fetchone()[0]
        
        if count == 0:
            for u in default_universes:
                cursor.execute('''
                    INSERT INTO universes (universe_id, name, theme, difficulty, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (u.universe_id, u.name, u.theme, u.difficulty, u.status))
            conn.commit()
        
        cursor.execute('SELECT * FROM universes WHERE status = ?', ('active',))
        rows = cursor.fetchall()
        conn.close()
        
        return [Universe(r[0], r[1], r[2], r[3], r[4]) for r in rows]
    
    def get_universe(self, universe_id: int) -> Optional[Universe]:
        for u in self.universes:
            if u.universe_id == universe_id:
                return u
        return None
    
    def get_random_universe(self) -> Universe:
        return random.choice(self.universes)
    
    def list_universes(self) -> List[Universe]:
        return self.universes
    
    def get_difficulty_range(self) -> Dict:
        return {
            'min': min(u.difficulty for u in self.universes),
            'max': max(u.difficulty for u in self.universes),
            'avg': sum(u.difficulty for u in self.universes) / len(self.universes)
        }

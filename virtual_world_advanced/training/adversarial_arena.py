"""
Erbing 虚拟世界 - 对抗训练场
Adversarial Training Arena for Combat Learning
"""

import sqlite3
import json
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum, auto


class MatchType(Enum):
    """对抗类型"""
    PVP = auto()  # 玩家对战
    PVE = auto()  # 对战环境
    TEAM_BATTLE = auto()  # 团队战
    TOURNAMENT = auto()  # 锦标赛
    RANKED = auto()  # 排位赛
    CASUAL = auto()  # 休闲赛


class ArenaResult(Enum):
    """对抗结果"""
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"
    FORFEIT = "forfeit"


@dataclass
class Opponent:
    """对手数据"""
    opponent_id: str
    name: str
    level: int
    strength: float
    skills: Dict[str, int]
    style: str  # aggressive, defensive, balanced, adaptive


@dataclass
class Match:
    """对战数据"""
    match_id: str
    capsule_id: str
    opponent: Opponent
    match_type: str
    status: str
    started_at: Optional[str]
    ended_at: Optional[str]
    result: Optional[str]
    score: Optional[float]
    xp_gained: int


class AdversarialArena:
    """
    对抗训练场
    提供各种对抗训练模式，帮助Erbing在实战中学习
    """
    
    def __init__(self, db_path: str = "adversarial_arena.db"):
        self.db_path = db_path
        self.init_database()
        self.load_ai_opponents()
        
    def init_database(self):
        """初始化对抗数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # AI对手表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_opponents (
                opponent_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                level INTEGER NOT NULL,
                strength REAL NOT NULL,
                skills TEXT NOT NULL,
                style TEXT NOT NULL,
                win_count INTEGER DEFAULT 0,
                lose_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 对战记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                match_id TEXT PRIMARY KEY,
                capsule_id TEXT NOT NULL,
                opponent_id TEXT NOT NULL,
                match_type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                result TEXT,
                score REAL,
                xp_gained INTEGER DEFAULT 0,
                moves TEXT,
                duration INTEGER
            )
        ''')
        
        # 对战详情表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_details (
                detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT NOT NULL,
                round_num INTEGER,
                action TEXT,
                actor TEXT,
                result TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES matches(match_id)
            )
        ''')
        
        # 排行榜表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard (
                capsule_id TEXT PRIMARY KEY,
                rating INTEGER DEFAULT 1000,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                win_streak INTEGER DEFAULT 0,
                best_streak INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_ai_opponents(self):
        """加载AI对手"""
        opponents = [
            # 初级对手
            {'name': '新手训练师', 'level': 1, 'strength': 0.3, 
             'skills': {'coding': 1, 'security': 1, 'problem_solving': 1}, 'style': 'defensive'},
            {'name': '代码学徒', 'level': 2, 'strength': 0.4,
             'skills': {'coding': 2, 'tool_use': 1}, 'style': 'balanced'},
            {'name': '安全学员', 'level': 2, 'strength': 0.4,
             'skills': {'security': 2, 'coding': 1}, 'style': 'aggressive'},
            
            # 中级对手
            {'name': '全栈工程师', 'level': 5, 'strength': 0.6,
             'skills': {'coding': 5, 'deployment': 4, 'tool_use': 4}, 'style': 'balanced'},
            {'name': '安全研究员', 'level': 5, 'strength': 0.6,
             'skills': {'security': 5, 'problem_solving': 4}, 'style': 'aggressive'},
            {'name': 'AI专家', 'level': 5, 'strength': 0.6,
             'skills': {'ai_tech': 5, 'problem_solving': 5}, 'style': 'adaptive'},
            
            # 高级对手
            {'name': '架构大师', 'level': 8, 'strength': 0.75,
             'skills': {'coding': 8, 'deployment': 7, 'problem_solving': 7}, 'style': 'adaptive'},
            {'name': '黑客高手', 'level': 8, 'strength': 0.75,
             'skills': {'security': 8, 'problem_solving': 8, 'tool_use': 7}, 'style': 'aggressive'},
            {'name': '算法专家', 'level': 8, 'strength': 0.75,
             'skills': {'ai_tech': 8, 'coding': 7, 'problem_solving': 8}, 'style': 'balanced'},
            
            # 顶级对手
            {'name': '系统大师', 'level': 10, 'strength': 0.85,
             'skills': {'coding': 10, 'security': 9, 'deployment': 10}, 'style': 'adaptive'},
            {'name': '攻防专家', 'level': 10, 'strength': 0.85,
             'skills': {'security': 10, 'problem_solving': 10, 'ai_tech': 8}, 'style': 'aggressive'},
            {'name': '全能战士', 'level': 10, 'strength': 0.9,
             'skills': {'coding': 10, 'security': 10, 'ai_tech': 10, 'problem_solving': 10}, 'style': 'adaptive'}
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查是否已有对手
        cursor.execute('SELECT COUNT(*) FROM ai_opponents')
        count = cursor.fetchone()[0]
        
        if count == 0:
            for i, opp in enumerate(opponents, 1):
                opponent_id = f"AI-{i:03d}"
                cursor.execute('''
                    INSERT INTO ai_opponents (opponent_id, name, level, strength, skills, style)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    opponent_id,
                    opp['name'],
                    opp['level'],
                    opp['strength'],
                    json.dumps(opp['skills']),
                    opp['style']
                ))
            
            conn.commit()
        
        conn.close()
    
    def find_opponent(self, capsule_level: int, match_type: str = 'pve') -> Opponent:
        """
        寻找合适的对手
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 根据等级寻找对手
        min_level = max(1, capsule_level - 2)
        max_level = capsule_level + 2
        
        cursor.execute('''
            SELECT opponent_id, name, level, strength, skills, style
            FROM ai_opponents
            WHERE level BETWEEN ? AND ?
            ORDER BY ABS(level - ?), RANDOM()
            LIMIT 1
        ''', (min_level, max_level, capsule_level))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            # 如果没有合适等级的对手，随机选择一个
            return self.get_random_opponent()
        
        return Opponent(
            opponent_id=row[0],
            name=row[1],
            level=row[2],
            strength=row[3],
            skills=json.loads(row[4]),
            style=row[5]
        )
    
    def get_random_opponent(self) -> Opponent:
        """随机获取对手"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT opponent_id, name, level, strength, skills, style
            FROM ai_opponents
            ORDER BY RANDOM()
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        return Opponent(
            opponent_id=row[0],
            name=row[1],
            level=row[2],
            strength=row[3],
            skills=json.loads(row[4]),
            style=row[5]
        )
    
    def start_match(self, capsule_id: str, match_type: str = 'pve', 
                   preferred_opponent: Optional[str] = None) -> Match:
        """
        开始对战
        """
        # 获取对手
        if preferred_opponent:
            opponent = self.get_opponent_by_id(preferred_opponent)
        else:
            opponent = self.find_opponent(1)  # TODO: 获取实际capsule等级
        
        match_id = f"MTCH-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        
        # 记录对战
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO matches (match_id, capsule_id, opponent_id, match_type, status, started_at)
            VALUES (?, ?, ?, ?, 'active', CURRENT_TIMESTAMP)
        ''', (match_id, capsule_id, opponent.opponent_id, match_type))
        
        conn.commit()
        conn.close()
        
        return Match(
            match_id=match_id,
            capsule_id=capsule_id,
            opponent=opponent,
            match_type=match_type,
            status='active',
            started_at=datetime.now().isoformat(),
            ended_at=None,
            result=None,
            score=None,
            xp_gained=0
        )
    
    def get_opponent_by_id(self, opponent_id: str) -> Opponent:
        """根据ID获取对手"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT opponent_id, name, level, strength, skills, style
            FROM ai_opponents
            WHERE opponent_id = ?
        ''', (opponent_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return Opponent(
            opponent_id=row[0],
            name=row[1],
            level=row[2],
            strength=row[3],
            skills=json.loads(row[4]),
            style=row[5]
        )
    
    def execute_round(self, match_id: str, capsule_action: str, 
                     capsule_skills: Dict[str, int]) -> Dict:
        """
        执行一轮对战
        """
        # 获取对战信息
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT capsule_id, opponent_id, match_type FROM matches WHERE match_id = ?
        ''', (match_id,))
        
        match_info = cursor.fetchone()
        if not match_info:
            conn.close()
            return {'error': 'Match not found'}
        
        opponent = self.get_opponent_by_id(match_info[1])
        
        # 计算双方实力
        capsule_strength = self.calculate_strength(capsule_skills)
        opponent_strength = opponent.strength
        
        # 根据动作类型决定胜负
        action_outcomes = {
            'attack': self._resolve_attack(capsule_strength, opponent_strength, capsule_skills, opponent.skills),
            'defend': self._resolve_defend(capsule_strength, opponent_strength, capsule_skills, opponent.skills),
            'skill': self._resolve_skill(capsule_strength, opponent_strength, capsule_skills, opponent.skills)
        }
        
        outcome = action_outcomes.get(capsule_action, action_outcomes['attack'])
        
        # 记录动作
        cursor.execute('''
            INSERT INTO match_details (match_id, round_num, action, actor, result)
            VALUES (?, 
                (SELECT COALESCE(MAX(round_num), 0) + 1 FROM match_details WHERE match_id = ?),
                ?, 'capsule', ?
            )
        ''', (match_id, match_id, capsule_action, outcome['result']))
        
        conn.commit()
        conn.close()
        
        return outcome
    
    def _resolve_attack(self, capsule_str: float, opp_str: float, 
                       capsule_skills: Dict, opp_skills: Dict) -> Dict:
        """解析攻击动作"""
        base_chance = 0.5 + (capsule_str - opp_str) * 0.3
        random_factor = random.uniform(-0.1, 0.1)
        success = random.random() < (base_chance + random_factor)
        
        return {
            'action': 'attack',
            'result': 'success' if success else 'failed',
            'damage': random.uniform(0.1, 0.3) if success else 0,
            'message': '攻击成功！' if success else '攻击被闪避'
        }
    
    def _resolve_defend(self, capsule_str: float, opp_str: float,
                       capsule_skills: Dict, opp_skills: Dict) -> Dict:
        """解析防御动作"""
        defense_bonus = 0.2
        success = random.random() < (0.6 + defense_bonus)
        
        return {
            'action': 'defend',
            'result': 'success' if success else 'failed',
            'damage': -random.uniform(0.05, 0.15) if success else random.uniform(0.1, 0.2),
            'message': '防御成功，减少伤害' if success else '防御被突破'
        }
    
    def _resolve_skill(self, capsule_str: float, opp_str: float,
                      capsule_skills: Dict, opp_skills: Dict) -> Dict:
        """解析技能动作"""
        # 找出最高技能
        best_skill = max(capsule_skills, key=capsule_skills.get)
        skill_level = capsule_skills[best_skill]
        
        base_chance = 0.4 + (skill_level * 0.05) + (capsule_str - opp_str) * 0.2
        success = random.random() < base_chance
        
        return {
            'action': 'skill',
            'result': 'success' if success else 'failed',
            'damage': random.uniform(0.2, 0.4) * skill_level / 10 if success else 0,
            'skill_used': best_skill,
            'message': f'使用{best_skill}技能成功！' if success else f'{best_skill}技能被反制'
        }
    
    def calculate_strength(self, skills: Dict[str, int]) -> float:
        """计算综合实力"""
        if not skills:
            return 0.5
        
        total = sum(skills.values())
        count = len(skills)
        avg = total / count
        
        return min(1.0, avg / 10.0)
    
    def end_match(self, match_id: str, result: str, final_score: float) -> Dict:
        """
        结束对战
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取对战信息
        cursor.execute('''
            SELECT capsule_id, opponent_id, match_type, started_at
            FROM matches
            WHERE match_id = ?
        ''', (match_id,))
        
        match_data = cursor.fetchone()
        if not match_data:
            conn.close()
            return {'error': 'Match not found'}
        
        capsule_id = match_data[0]
        
        # 计算XP
        base_xp = 10
        result_bonus = {'win': 2.0, 'draw': 1.0, 'lose': 0.5}
        xp_gained = int(base_xp * result_bonus.get(result, 1.0) * (1 + final_score))
        
        # 更新对战记录
        started_at = match_data[3]
        duration = int((datetime.now() - datetime.fromisoformat(started_at.replace('Z', '+00:00'))).total_seconds())
        
        cursor.execute('''
            UPDATE matches 
            SET status = 'completed',
                ended_at = CURRENT_TIMESTAMP,
                result = ?,
                score = ?,
                xp_gained = ?,
                duration = ?
            WHERE match_id = ?
        ''', (result, final_score, xp_gained, duration, match_id))
        
        # 更新排行榜
        if result == 'win':
            cursor.execute('''
                INSERT INTO leaderboard (capsule_id, wins, win_streak, best_streak)
                VALUES (?, 1, 1, 1)
                ON CONFLICT(capsule_id) DO UPDATE SET
                    wins = wins + 1,
                    win_streak = win_streak + 1,
                    best_streak = MAX(best_streak, win_streak + 1),
                    rating = rating + 25,
                    updated_at = CURRENT_TIMESTAMP
            ''', (capsule_id,))
        elif result == 'lose':
            cursor.execute('''
                INSERT INTO leaderboard (capsule_id, losses)
                VALUES (?, 1)
                ON CONFLICT(capsule_id) DO UPDATE SET
                    losses = losses + 1,
                    win_streak = 0,
                    rating = MAX(0, rating - 20),
                    updated_at = CURRENT_TIMESTAMP
            ''', (capsule_id,))
        else:  # draw
            cursor.execute('''
                INSERT INTO leaderboard (capsule_id, draws)
                VALUES (?, 1)
                ON CONFLICT(capsule_id) DO UPDATE SET
                    draws = draws + 1,
                    rating = rating + 5,
                    updated_at = CURRENT_TIMESTAMP
            ''', (capsule_id,))
        
        conn.commit()
        conn.close()
        
        return {
            'match_id': match_id,
            'result': result,
            'score': final_score,
            'xp_gained': xp_gained,
            'duration': duration
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """获取排行榜"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT capsule_id, rating, wins, losses, draws, win_streak, best_streak
            FROM leaderboard
            ORDER BY rating DESC
            LIMIT ?
        ''', (limit,))
        
        leaderboard = []
        for row in cursor.fetchall():
            leaderboard.append({
                'capsule_id': row[0],
                'rating': row[1],
                'wins': row[2],
                'losses': row[3],
                'draws': row[4],
                'win_streak': row[5],
                'best_streak': row[6]
            })
        
        conn.close()
        return leaderboard

    def get_match_history(self, capsule_id: str, limit: int = 20) -> List[Dict]:
        """获取对战历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.match_id, m.opponent_id, o.name, m.match_type, m.result, m.score, m.xp_gained, m.duration, m.timestamp
            FROM matches m
            JOIN ai_opponents o ON m.opponent_id = o.opponent_id
            WHERE m.capsule_id = ?
            ORDER BY m.timestamp DESC
            LIMIT ?
        ''', (capsule_id, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'match_id': row[0],
                'opponent_id': row[1],
                'opponent_name': row[2],
                'match_type': row[3],
                'result': row[4],
                'score': row[5],
                'xp_gained': row[6],
                'duration': row[7],
                'timestamp': row[8]
            })
        
        conn.close()
        return history
"""
Erbing 虚拟世界 - 任务模拟器
Mission Simulator for Virtual World Training
"""

import sqlite3
import json
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum, auto


class MissionType(Enum):
    """任务类型"""
    CODING = auto()
    SECURITY = auto()
    AI_TECH = auto()
    PROBLEM_SOLVING = auto()
    DEPLOYMENT = auto()
    TOOL_USE = auto()
    COMMUNICATION = auto()
    COLLABORATION = auto()
    RESEARCH = auto()
    DEBUGGING = auto()


class Difficulty(Enum):
    """难度等级"""
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXTREME = 4
    NIGHTMARE = 5


@dataclass
class Mission:
    """任务数据"""
    mission_id: str
    mission_type: str
    difficulty: int
    title: str
    description: str
    objectives: List[str]
    constraints: List[str]
    rewards: Dict[str, float]
    time_limit: int  # seconds
    xp_reward: int


class MissionSimulator:
    """
    任务模拟器
    生成和管理虚拟世界中的各种训练任务
    """
    
    def __init__(self, db_path: str = "mission_simulator.db"):
        self.db_path = db_path
        self.init_database()
        self.load_mission_templates()
        
    def init_database(self):
        """初始化任务数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 任务模板表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mission_templates (
                template_id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_type TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                objectives TEXT NOT NULL,
                constraints TEXT,
                rewards TEXT NOT NULL,
                time_limit INTEGER DEFAULT 300,
                xp_reward INTEGER DEFAULT 10
            )
        ''')
        
        # 任务实例表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mission_instances (
                mission_id TEXT PRIMARY KEY,
                template_id INTEGER,
                capsule_id TEXT,
                status TEXT DEFAULT 'pending',
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                result TEXT,
                score REAL,
                rewards_earned TEXT,
                FOREIGN KEY (template_id) REFERENCES mission_templates(template_id)
            )
        ''')
        
        # 任务执行日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mission_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mission_id) REFERENCES mission_instances(mission_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_mission_templates(self):
        """加载任务模板"""
        templates = [
            # Coding 任务
            {
                'mission_type': 'coding',
                'difficulty': 1,
                'title': '基础代码修复',
                'description': '修复一个简单的bug，例如空指针异常或数组越界',
                'objectives': json.dumps(['识别bug位置', '理解bug原因', '修复bug', '验证修复']),
                'constraints': json.dumps(['不能修改现有测试用例', '必须保持代码风格一致']),
                'rewards': json.dumps({'coding_xp': 5, 'problem_solving_xp': 2}),
                'time_limit': 300,
                'xp_reward': 10
            },
            {
                'mission_type': 'coding',
                'difficulty': 3,
                'title': '算法优化挑战',
                'description': '将O(n²)算法优化到O(n log n)或更好',
                'objectives': json.dumps(['分析当前算法复杂度', '设计优化方案', '实现优化', '性能测试验证']),
                'constraints': json.dumps(['必须通过所有测试用例', '内存使用不能超过限制']),
                'rewards': json.dumps({'coding_xp': 15, 'problem_solving_xp': 10}),
                'time_limit': 600,
                'xp_reward': 30
            },
            
            # Security 任务
            {
                'mission_type': 'security',
                'difficulty': 1,
                'title': '漏洞识别训练',
                'description': '识别代码中的常见安全漏洞（SQL注入、XSS等）',
                'objectives': json.dumps(['扫描代码', '识别漏洞类型', '评估风险等级', '提出修复建议']),
                'constraints': json.dumps(['仅限OWASP Top 10漏洞', '必须提供修复代码']),
                'rewards': json.dumps({'security_xp': 10, 'coding_xp': 5}),
                'time_limit': 300,
                'xp_reward': 15
            },
            {
                'mission_type': 'security',
                'difficulty': 4,
                'title': '渗透测试模拟',
                'description': '对模拟系统进行渗透测试，发现并利用漏洞',
                'objectives': json.dumps(['信息收集', '漏洞扫描', '漏洞利用', '权限提升', '后渗透']),
                'constraints': json.dumps(['仅限授权范围', '必须记录所有操作', '不能破坏系统可用性']),
                'rewards': json.dumps({'security_xp': 25, 'problem_solving_xp': 15}),
                'time_limit': 1800,
                'xp_reward': 50
            },
            
            # AI Tech 任务
            {
                'mission_type': 'ai_tech',
                'difficulty': 2,
                'title': '模型调优训练',
                'description': '调整模型超参数以提升性能指标',
                'objectives': json.dumps(['分析基线性能', '选择调优参数', '执行调优实验', '评估结果']),
                'constraints': json.dumps(['训练时间限制', '资源使用限制']),
                'rewards': json.dumps({'ai_tech_xp': 12, 'problem_solving_xp': 8}),
                'time_limit': 900,
                'xp_reward': 25
            },
            
            # Deployment 任务
            {
                'mission_type': 'deployment',
                'difficulty': 2,
                'title': '容器化部署',
                'description': '将应用容器化并部署到Kubernetes集群',
                'objectives': json.dumps(['编写Dockerfile', '创建K8s配置', '部署应用', '验证健康状态']),
                'constraints': json.dumps(['必须使用最佳实践', '必须包含健康检查']),
                'rewards': json.dumps({'deployment_xp': 15, 'tool_use_xp': 5}),
                'time_limit': 600,
                'xp_reward': 20
            },
            
            # Problem Solving 任务
            {
                'mission_type': 'problem_solving',
                'difficulty': 3,
                'title': '系统故障排查',
                'description': '诊断并修复一个复杂的系统故障',
                'objectives': json.dumps(['收集日志', '分析错误', '定位根因', '实施修复', '验证解决']),
                'constraints': json.dumps(['不能影响其他服务', '必须记录排查过程']),
                'rewards': json.dumps({'problem_solving_xp': 20, 'tool_use_xp': 10}),
                'time_limit': 1200,
                'xp_reward': 35
            },
            
            # Communication 任务
            {
                'mission_type': 'communication',
                'difficulty': 2,
                'title': '技术文档编写',
                'description': '编写清晰的技术文档和API说明',
                'objectives': json.dumps(['分析需求', '编写文档', '添加示例', '同行评审']),
                'constraints': json.dumps(['符合文档规范', '必须包含代码示例']),
                'rewards': json.dumps({'communication_xp': 15, 'collaboration_xp': 5}),
                'time_limit': 600,
                'xp_reward': 20
            },
            
            # Research 任务
            {
                'mission_type': 'research',
                'difficulty': 4,
                'title': '新技术调研',
                'description': '研究一项新技术并评估其应用价值',
                'objectives': json.dumps(['文献调研', '技术分析', '原型实现', '风险评估', '应用建议']),
                'constraints': json.dumps(['必须引用权威来源', '必须提供实施路径']),
                'rewards': json.dumps({'ai_tech_xp': 20, 'problem_solving_xp': 15}),
                'time_limit': 2400,
                'xp_reward': 45
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查是否已有模板
        cursor.execute('SELECT COUNT(*) FROM mission_templates')
        count = cursor.fetchone()[0]
        
        if count == 0:
            for template in templates:
                cursor.execute('''
                    INSERT INTO mission_templates 
                    (mission_type, difficulty, title, description, objectives, constraints, rewards, time_limit, xp_reward)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    template['mission_type'],
                    template['difficulty'],
                    template['title'],
                    template['description'],
                    template['objectives'],
                    template['constraints'],
                    template['rewards'],
                    template['time_limit'],
                    template['xp_reward']
                ))
            
            conn.commit()
        
        conn.close()
    
    def generate_mission(self, capsule_id: str, preferred_type: Optional[str] = None, 
                         difficulty_range: tuple = (1, 5)) -> Mission:
        """
        生成新任务
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 选择模板
        if preferred_type:
            cursor.execute('''
                SELECT * FROM mission_templates 
                WHERE mission_type = ? AND difficulty BETWEEN ? AND ?
                ORDER BY RANDOM() LIMIT 1
            ''', (preferred_type, difficulty_range[0], difficulty_range[1]))
        else:
            cursor.execute('''
                SELECT * FROM mission_templates 
                WHERE difficulty BETWEEN ? AND ?
                ORDER BY RANDOM() LIMIT 1
            ''', (difficulty_range[0], difficulty_range[1]))
        
        template = cursor.fetchone()
        conn.close()
        
        if not template:
            raise ValueError("No suitable mission template found")
        
        # 生成任务ID
        mission_id = f"M-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        
        mission = Mission(
            mission_id=mission_id,
            mission_type=template[1],
            difficulty=template[2],
            title=template[3],
            description=template[4],
            objectives=json.loads(template[5]),
            constraints=json.loads(template[6]) if template[6] else [],
            rewards=json.loads(template[7]),
            time_limit=template[8],
            xp_reward=template[9]
        )
        
        # 记录任务实例
        self.create_mission_instance(mission, capsule_id)
        
        return mission
    
    def create_mission_instance(self, mission: Mission, capsule_id: str):
        """创建任务实例"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mission_instances (mission_id, capsule_id, status, started_at)
            VALUES (?, ?, 'active', CURRENT_TIMESTAMP)
        ''', (mission.mission_id, capsule_id))
        
        conn.commit()
        conn.close()
    
    def start_mission(self, mission_id: str) -> Dict:
        """开始任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE mission_instances 
            SET status = 'in_progress', started_at = CURRENT_TIMESTAMP
            WHERE mission_id = ?
        ''', (mission_id,))
        
        conn.commit()
        conn.close()
        
        # 记录开始
        self.log_mission_action(mission_id, 'mission_started', {'timestamp': datetime.now().isoformat()})
        
        return {'status': 'started', 'mission_id': mission_id}
    
    def complete_mission(self, mission_id: str, result: str, score: float, 
                        completed_objectives: List[str]) -> Dict:
        """完成任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取任务信息
        cursor.execute('''
            SELECT m.mission_id, m.template_id, mt.xp_reward, mt.rewards
            FROM mission_instances m
            JOIN mission_templates mt ON m.template_id = mt.template_id
            WHERE m.mission_id = ?
        ''', (mission_id,))
        
        mission_data = cursor.fetchone()
        if not mission_data:
            conn.close()
            return {'error': 'Mission not found'}
        
        # 计算奖励
        base_xp = mission_data[2]
        xp_earned = int(base_xp * score)
        rewards = json.loads(mission_data[3])
        
        # 更新任务状态
        cursor.execute('''
            UPDATE mission_instances 
            SET status = 'completed', 
                completed_at = CURRENT_TIMESTAMP,
                result = ?,
                score = ?,
                rewards_earned = ?
            WHERE mission_id = ?
        ''', (result, score, json.dumps({'xp': xp_earned, **rewards}), mission_id))
        
        conn.commit()
        conn.close()
        
        # 记录完成
        self.log_mission_action(mission_id, 'mission_completed', {
            'result': result,
            'score': score,
            'xp_earned': xp_earned,
            'completed_objectives': completed_objectives
        })
        
        return {
            'mission_id': mission_id,
            'result': result,
            'score': score,
            'xp_earned': xp_earned,
            'rewards': rewards
        }
    
    def fail_mission(self, mission_id: str, reason: str) -> Dict:
        """任务失败"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE mission_instances 
            SET status = 'failed', completed_at = CURRENT_TIMESTAMP, result = ?
            WHERE mission_id = ?
        ''', (reason, mission_id))
        
        conn.commit()
        conn.close()
        
        # 记录失败
        self.log_mission_action(mission_id, 'mission_failed', {'reason': reason})
        
        return {'status': 'failed', 'reason': reason}
    
    def log_mission_action(self, mission_id: str, action: str, details: Dict):
        """记录任务动作"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mission_logs (mission_id, action, details)
            VALUES (?, ?, ?)
        ''', (mission_id, action, json.dumps(details, ensure_ascii=False)))
        
        conn.commit()
        conn.close()
    
    def get_available_missions(self, capsule_id: str, mission_type: Optional[str] = None) -> List[Dict]:
        """获取可用任务列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if mission_type:
            cursor.execute('''
                SELECT template_id, mission_type, difficulty, title, description, time_limit, xp_reward
                FROM mission_templates
                WHERE mission_type = ?
                ORDER BY difficulty ASC
            ''', (mission_type,))
        else:
            cursor.execute('''
                SELECT template_id, mission_type, difficulty, title, description, time_limit, xp_reward
                FROM mission_templates
                ORDER BY difficulty ASC
            ''')
        
        missions = []
        for row in cursor.fetchall():
            missions.append({
                'template_id': row[0],
                'mission_type': row[1],
                'difficulty': row[2],
                'title': row[3],
                'description': row[4],
                'time_limit': row[5],
                'xp_reward': row[6]
            })
        
        conn.close()
        return missions
    
    def get_mission_stats(self, capsule_id: str) -> Dict:
        """获取任务统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总任务数
        cursor.execute('''
            SELECT COUNT(*) FROM mission_instances WHERE capsule_id = ?
        ''', (capsule_id,))
        total = cursor.fetchone()[0]
        
        # 成功任务数
        cursor.execute('''
            SELECT COUNT(*) FROM mission_instances 
            WHERE capsule_id = ? AND status = 'completed'
        ''', (capsule_id,))
        completed = cursor.fetchone()[0]
        
        # 平均得分
        cursor.execute('''
            SELECT AVG(score) FROM mission_instances 
            WHERE capsule_id = ? AND score IS NOT NULL
        ''', (capsule_id,))
        avg_score = cursor.fetchone()[0] or 0.0
        
        # 总XP
        cursor.execute('''
            SELECT SUM(CASE WHEN status = 'completed' THEN mt.xp_reward ELSE 0 END)
            FROM mission_instances m
            JOIN mission_templates mt ON m.template_id = mt.template_id
            WHERE m.capsule_id = ?
        ''', (capsule_id,))
        total_xp = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_missions': total,
            'completed_missions': completed,
            'success_rate': completed / total if total > 0 else 0.0,
            'avg_score': avg_score,
            'total_xp_earned': total_xp
        }

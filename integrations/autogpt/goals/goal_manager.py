"""
AutoGPT Goal Manager
目标管理器 - 结构化的目标定义和追踪系统
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set
from enum import Enum
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class GoalStatus(Enum):
    """目标状态"""
    PROPOSED = "proposed"       # 提议中
    ACCEPTED = "accepted"       # 已接受
    IN_PROGRESS = "in_progress" # 进行中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"           # 失败
    CANCELLED = "cancelled"     # 已取消
    ON_HOLD = "on_hold"        # 暂停


class GoalPriority(Enum):
    """目标优先级"""
    CRITICAL = "critical"  # 关键
    HIGH = "high"          # 高
    MEDIUM = "medium"      # 中
    LOW = "low"            # 低


class GoalType(Enum):
    """目标类型"""
    ACHIEVEMENT = "achievement"  # 成就型（一次性完成）
    CONTINUOUS = "continuous"    # 持续型（持续进行）
    MILESTONE = "milestone"      # 里程碑型（多个子目标）


@dataclass
class GoalMetric:
    """目标度量指标"""
    name: str
    target_value: float
    current_value: float = 0.0
    unit: str = ""
    weight: float = 1.0
    
    @property
    def progress(self) -> float:
        """进度百分比"""
        if self.target_value == 0:
            return 100.0 if self.current_value > 0 else 0.0
        progress = (self.current_value / self.target_value) * 100
        return min(100.0, progress)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "unit": self.unit,
            "weight": self.weight,
            "progress": self.progress
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GoalMetric':
        return cls(
            name=data["name"],
            target_value=data["target_value"],
            current_value=data.get("current_value", 0.0),
            unit=data.get("unit", ""),
            weight=data.get("weight", 1.0)
        )


@dataclass
class Goal:
    """
    目标数据结构
    
    支持多层级目标结构，每个目标可以有子目标
    """
    id: str
    name: str
    description: str
    status: GoalStatus = GoalStatus.PROPOSED
    priority: GoalPriority = GoalPriority.MEDIUM
    goal_type: GoalType = GoalType.ACHIEVEMENT
    
    # 层级结构
    parent_goal: Optional[str] = None
    subgoals: List[str] = field(default_factory=list)
    
    # 时间信息
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 度量指标
    metrics: List[GoalMetric] = field(default_factory=list)
    
    # 进度追踪
    progress_percentage: float = 0.0
    
    # 验证条件
    completion_criteria: List[str] = field(default_factory=list)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_complete(self) -> bool:
        """是否完成"""
        return self.status == GoalStatus.COMPLETED
    
    @property
    def is_active(self) -> bool:
        """是否活跃"""
        return self.status in [GoalStatus.ACCEPTED, GoalStatus.IN_PROGRESS]
    
    def add_metric(self, metric: GoalMetric):
        """添加度量指标"""
        self.metrics.append(metric)
    
    def update_metric(self, name: str, value: float):
        """更新度量指标"""
        for metric in self.metrics:
            if metric.name == name:
                metric.current_value = value
                break
    
    def calculate_progress(self) -> float:
        """计算进度"""
        if not self.metrics:
            return self.progress_percentage
        
        total_weight = sum(m.weight for m in self.metrics)
        weighted_progress = sum(
            (m.progress * m.weight) for m in self.metrics
        )
        
        if total_weight > 0:
            self.progress_percentage = weighted_progress / total_weight
        
        return self.progress_percentage
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "goal_type": self.goal_type.value,
            "parent_goal": self.parent_goal,
            "subgoals": self.subgoals,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metrics": [m.to_dict() for m in self.metrics],
            "progress_percentage": self.progress_percentage,
            "completion_criteria": self.completion_criteria,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Goal':
        """从字典创建"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            status=GoalStatus(data.get("status", "proposed")),
            priority=GoalPriority(data.get("priority", "medium")),
            goal_type=GoalType(data.get("goal_type", "achievement")),
            parent_goal=data.get("parent_goal"),
            subgoals=data.get("subgoals", []),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            deadline=datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            metrics=[GoalMetric.from_dict(m) for m in data.get("metrics", [])],
            progress_percentage=data.get("progress_percentage", 0.0),
            completion_criteria=data.get("completion_criteria", []),
            metadata=data.get("metadata", {})
        )


class GoalManager:
    """
    目标管理器
    
    负责：
    - 目标的创建、更新、删除
    - 目标层级关系管理
    - 目标状态转换
    - 目标进度追踪
    """
    
    def __init__(self):
        """初始化目标管理器"""
        self.goals: Dict[str, Goal] = {}
        self._goal_counter = 0
        self._active_goals: Set[str] = set()
    
    def _generate_goal_id(self) -> str:
        """生成目标 ID"""
        self._goal_counter += 1
        return f"goal_{self._goal_counter:04d}"
    
    def create_goal(
        self,
        name: str,
        description: str,
        priority: str = "medium",
        goal_type: str = "achievement",
        parent_goal: Optional[str] = None,
        subgoals: Optional[List[str]] = None,
        deadline: Optional[datetime] = None,
        metrics: Optional[List[Dict[str, Any]]] = None,
        completion_criteria: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Goal:
        """
        创建目标
        
        Args:
            name: 目标名称
            description: 目标描述
            priority: 优先级 (critical, high, medium, low)
            goal_type: 目标类型 (achievement, continuous, milestone)
            parent_goal: 父目标 ID
            subgoals: 子目标列表
            deadline: 截止日期
            metrics: 度量指标列表
            completion_criteria: 完成条件列表
            metadata: 元数据
            
        Returns:
            创建的目标
        """
        goal_id = self._generate_goal_id()
        
        goal = Goal(
            id=goal_id,
            name=name,
            description=description,
            priority=GoalPriority(priority),
            goal_type=GoalType(goal_type),
            parent_goal=parent_goal,
            subgoals=subgoals or [],
            deadline=deadline,
            completion_criteria=completion_criteria or [],
            metadata=metadata or {}
        )
        
        # 添加度量指标
        if metrics:
            for metric_data in metrics:
                metric = GoalMetric(
                    name=metric_data.get("name", ""),
                    target_value=metric_data.get("target_value", 0),
                    unit=metric_data.get("unit", ""),
                    weight=metric_data.get("weight", 1.0)
                )
                goal.add_metric(metric)
        
        # 建立层级关系
        if parent_goal and parent_goal in self.goals:
            parent = self.goals[parent_goal]
            if goal_id not in parent.subgoals:
                parent.subgoals.append(goal_id)
        
        # 添加子目标
        if subgoals:
            for subgoal_id in subgoals:
                if subgoal_id in self.goals:
                    self.goals[subgoal_id].parent_goal = goal_id
        
        self.goals[goal_id] = goal
        logger.info(f"Created goal: {goal_id} - {name}")
        
        return goal
    
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """获取目标"""
        return self.goals.get(goal_id)
    
    def update_goal(
        self,
        goal_id: str,
        **updates
    ) -> Optional[Goal]:
        """
        更新目标
        
        Args:
            goal_id: 目标 ID
            **updates: 要更新的字段
            
        Returns:
            更新后的目标
        """
        goal = self.goals.get(goal_id)
        if not goal:
            logger.warning(f"Goal not found: {goal_id}")
            return None
        
        # 允许更新的字段
        allowed_fields = {
            "name", "description", "priority", "goal_type",
            "deadline", "completion_criteria", "metadata"
        }
        
        for field_name, value in updates.items():
            if field_name in allowed_fields:
                if field_name in ["priority", "goal_type"]:
                    # 枚举类型转换
                    if field_name == "priority":
                        value = GoalPriority(value)
                    else:
                        value = GoalType(value)
                setattr(goal, field_name, value)
        
        logger.info(f"Updated goal: {goal_id}")
        return goal
    
    def delete_goal(self, goal_id: str, cascade: bool = False) -> bool:
        """
        删除目标
        
        Args:
            goal_id: 目标 ID
            cascade: 是否级联删除子目标
            
        Returns:
            是否成功删除
        """
        goal = self.goals.get(goal_id)
        if not goal:
            return False
        
        # 从父目标中移除
        if goal.parent_goal and goal.parent_goal in self.goals:
            parent = self.goals[goal.parent_goal]
            if goal_id in parent.subgoals:
                parent.subgoals.remove(goal_id)
        
        # 处理子目标
        if cascade:
            for subgoal_id in goal.subgoals[:]:
                self.delete_goal(subgoal_id, cascade=True)
        else:
            # 将子目标的父目标设为 None
            for subgoal_id in goal.subgoals:
                if subgoal_id in self.goals:
                    self.goals[subgoal_id].parent_goal = None
        
        del self.goals[goal_id]
        self._active_goals.discard(goal_id)
        
        logger.info(f"Deleted goal: {goal_id}")
        return True
    
    def accept_goal(self, goal_id: str) -> bool:
        """接受目标"""
        goal = self.goals.get(goal_id)
        if not goal:
            return False
        
        if goal.status == GoalStatus.PROPOSED:
            goal.status = GoalStatus.ACCEPTED
            self._active_goals.add(goal_id)
            logger.info(f"Goal accepted: {goal_id}")
            return True
        
        return False
    
    def start_goal(self, goal_id: str) -> bool:
        """开始目标"""
        goal = self.goals.get(goal_id)
        if not goal:
            return False
        
        if goal.status in [GoalStatus.PROPOSED, GoalStatus.ACCEPTED, GoalStatus.ON_HOLD]:
            goal.status = GoalStatus.IN_PROGRESS
            goal.started_at = datetime.now()
            self._active_goals.add(goal_id)
            logger.info(f"Goal started: {goal_id}")
            return True
        
        return False
    
    def complete_goal(self, goal_id: str) -> bool:
        """完成目标"""
        goal = self.goals.get(goal_id)
        if not goal:
            return False
        
        if goal.status in [GoalStatus.IN_PROGRESS, GoalStatus.ACCEPTED]:
            goal.status = GoalStatus.COMPLETED
            goal.completed_at = datetime.now()
            goal.progress_percentage = 100.0
            self._active_goals.discard(goal_id)
            
            # 检查父目标进度
            if goal.parent_goal:
                self._update_parent_progress(goal.parent_goal)
            
            logger.info(f"Goal completed: {goal_id}")
            return True
        
        return False
    
    def fail_goal(self, goal_id: str, reason: Optional[str] = None) -> bool:
        """标记目标失败"""
        goal = self.goals.get(goal_id)
        if not goal:
            return False
        
        goal.status = GoalStatus.FAILED
        goal.completed_at = datetime.now()
        goal.metadata["failure_reason"] = reason
        self._active_goals.discard(goal_id)
        
        logger.warning(f"Goal failed: {goal_id}, reason: {reason}")
        return True
    
    def cancel_goal(self, goal_id: str, reason: Optional[str] = None) -> bool:
        """取消目标"""
        goal = self.goals.get(goal_id)
        if not goal:
            return False
        
        goal.status = GoalStatus.CANCELLED
        goal.completed_at = datetime.now()
        goal.metadata["cancellation_reason"] = reason
        self._active_goals.discard(goal_id)
        
        logger.info(f"Goal cancelled: {goal_id}, reason: {reason}")
        return True
    
    def hold_goal(self, goal_id: str, reason: Optional[str] = None) -> bool:
        """暂停目标"""
        goal = self.goals.get(goal_id)
        if not goal:
            return False
        
        if goal.status == GoalStatus.IN_PROGRESS:
            goal.status = GoalStatus.ON_HOLD
            goal.metadata["hold_reason"] = reason
            logger.info(f"Goal on hold: {goal_id}, reason: {reason}")
            return True
        
        return False
    
    def _update_parent_progress(self, parent_id: str):
        """更新父目标进度"""
        parent = self.goals.get(parent_id)
        if not parent or not parent.subgoals:
            return
        
        # 计算子目标的平均进度
        total_progress = 0.0
        for subgoal_id in parent.subgoals:
            if subgoal_id in self.goals:
                subgoal = self.goals[subgoal_id]
                total_progress += subgoal.progress_percentage
        
        if parent.subgoals:
            parent.progress_percentage = total_progress / len(parent.subgoals)
        
        # 检查是否所有子目标都完成
        all_complete = all(
            self.goals.get(sg_id, Goal(id="", name="", description="")).is_complete
            for sg_id in parent.subgoals
        )
        
        if all_complete:
            parent.status = GoalStatus.COMPLETED
            parent.completed_at = datetime.now()
            
            # 递归更新
            if parent.parent_goal:
                self._update_parent_progress(parent.parent_goal)
    
    def get_active_goals(self) -> List[Goal]:
        """获取所有活跃目标"""
        return [self.goals[gid] for gid in self._active_goals if gid in self.goals]
    
    def get_root_goals(self) -> List[Goal]:
        """获取所有根目标（没有父目标）"""
        return [g for g in self.goals.values() if g.parent_goal is None]
    
    def get_goal_tree(self, goal_id: str) -> Dict[str, Any]:
        """
        获取目标树
        
        Args:
            goal_id: 目标 ID
            
        Returns:
            目标树结构
        """
        goal = self.goals.get(goal_id)
        if not goal:
            return {}
        
        tree = goal.to_dict()
        tree["subgoals"] = [
            self.get_goal_tree(sg_id)
            for sg_id in goal.subgoals
            if sg_id in self.goals
        ]
        
        return tree
    
    def get_goal_path(self, goal_id: str) -> List[Goal]:
        """获取从根目标到指定目标的路径"""
        path = []
        current_id = goal_id
        
        while current_id:
            goal = self.goals.get(current_id)
            if not goal:
                break
            path.append(goal)
            current_id = goal.parent_goal
        
        return list(reversed(path))
    
    def find_goals_by_status(self, status: GoalStatus) -> List[Goal]:
        """按状态查找目标"""
        return [g for g in self.goals.values() if g.status == status]
    
    def find_goals_by_priority(self, priority: GoalPriority) -> List[Goal]:
        """按优先级查找目标"""
        return [g for g in self.goals.values() if g.priority == priority]
    
    def get_summary(self) -> Dict[str, Any]:
        """获取目标管理摘要"""
        total = len(self.goals)
        status_counts = {}
        
        for status in GoalStatus:
            status_counts[status.value] = len([
                g for g in self.goals.values() if g.status == status
            ])
        
        return {
            "total_goals": total,
            "active_goals": len(self._active_goals),
            "status_distribution": status_counts,
            "root_goals": len(self.get_root_goals())
        }
    
    def export_to_json(self) -> str:
        """导出为 JSON"""
        return json.dumps({
            goal_id: goal.to_dict()
            for goal_id, goal in self.goals.items()
        }, indent=2)
    
    @classmethod
    def import_from_json(cls, json_data: str) -> 'GoalManager':
        """从 JSON 导入"""
        manager = cls()
        data = json.loads(json_data)
        
        for goal_id, goal_data in data.items():
            manager.goals[goal_id] = Goal.from_dict(goal_data)
            if goal_data.get("status") in ["accepted", "in_progress"]:
                manager._active_goals.add(goal_id)
        
        return manager


# 导出
__all__ = [
    "GoalStatus",
    "GoalPriority",
    "GoalType",
    "GoalMetric",
    "Goal",
    "GoalManager"
]
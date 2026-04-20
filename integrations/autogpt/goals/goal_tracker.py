"""
AutoGPT Goal Tracker
目标进度追踪器
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

from .goal_manager import Goal, GoalStatus, GoalManager

logger = logging.getLogger(__name__)


@dataclass
class ProgressSnapshot:
    """进度快照"""
    timestamp: datetime
    goal_id: str
    progress_percentage: float
    status: GoalStatus
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "goal_id": self.goal_id,
            "progress_percentage": self.progress_percentage,
            "status": self.status.value,
            "metrics": self.metrics
        }


@dataclass
class ProgressHistory:
    """进度历史"""
    goal_id: str
    snapshots: List[ProgressSnapshot] = field(default_factory=list)
    
    def add_snapshot(self, snapshot: ProgressSnapshot):
        """添加快照"""
        self.snapshots.append(snapshot)
    
    def get_latest(self) -> Optional[ProgressSnapshot]:
        """获取最新快照"""
        return self.snapshots[-1] if self.snapshots else None
    
    def get_progress_trend(self) -> str:
        """获取进度趋势"""
        if len(self.snapshots) < 2:
            return "insufficient_data"
        
        recent = self.snapshots[-5:]  # 最近5个快照
        if len(recent) < 2:
            return "insufficient_data"
        
        first = recent[0].progress_percentage
        last = recent[-1].progress_percentage
        
        if last > first:
            return "improving"
        elif last < first:
            return "declining"
        else:
            return "stable"
    
    def calculate_velocity(self) -> float:
        """计算进度速度（百分比/小时）"""
        if len(self.snapshots) < 2:
            return 0.0
        
        first = self.snapshots[0]
        last = self.snapshots[-1]
        
        time_diff = (last.timestamp - first.timestamp).total_seconds() / 3600
        if time_diff == 0:
            return 0.0
        
        progress_diff = last.progress_percentage - first.progress_percentage
        return progress_diff / time_diff


class GoalTracker:
    """
    目标进度追踪器
    
    负责：
    - 定期记录目标进度
    - 分析进度趋势
    - 预测完成时间
    - 生成进度报告
    """
    
    def __init__(
        self,
        goal_manager: GoalManager,
        snapshot_interval: int = 60  # 分钟
    ):
        """
        初始化追踪器
        
        Args:
            goal_manager: 目标管理器
            snapshot_interval: 快照间隔（分钟）
        """
        self.goal_manager = goal_manager
        self.snapshot_interval = snapshot_interval
        
        self.progress_history: Dict[str, ProgressHistory] = {}
        self._tracking_goals: Dict[str, datetime] = {}  # goal_id -> last_snapshot_time
    
    def track_goal(self, goal_id: str):
        """开始追踪目标"""
        if goal_id not in self.progress_history:
            self.progress_history[goal_id] = ProgressHistory(goal_id=goal_id)
        
        self._tracking_goals[goal_id] = datetime.now()
        logger.info(f"Started tracking goal: {goal_id}")
    
    def stop_tracking(self, goal_id: str):
        """停止追踪目标"""
        if goal_id in self._tracking_goals:
            del self._tracking_goals[goal_id]
            logger.info(f"Stopped tracking goal: {goal_id}")
    
    def take_snapshot(self, goal_id: str) -> Optional[ProgressSnapshot]:
        """拍摄进度快照"""
        goal = self.goal_manager.get_goal(goal_id)
        if not goal:
            return None
        
        snapshot = ProgressSnapshot(
            timestamp=datetime.now(),
            goal_id=goal_id,
            progress_percentage=goal.progress_percentage,
            status=goal.status,
            metrics={
                m.name: m.current_value
                for m in goal.metrics
            }
        )
        
        if goal_id not in self.progress_history:
            self.progress_history[goal_id] = ProgressHistory(goal_id=goal_id)
        
        self.progress_history[goal_id].add_snapshot(snapshot)
        self._tracking_goals[goal_id] = snapshot.timestamp
        
        return snapshot
    
    def take_all_snapshots(self) -> List[ProgressSnapshot]:
        """为所有追踪中的目标拍摄快照"""
        snapshots = []
        for goal_id in list(self._tracking_goals.keys()):
            snapshot = self.take_snapshot(goal_id)
            if snapshot:
                snapshots.append(snapshot)
        return snapshots
    
    def get_progress_report(self, goal_id: str) -> Dict[str, Any]:
        """生成进度报告"""
        goal = self.goal_manager.get_goal(goal_id)
        if not goal:
            return {"error": "Goal not found"}
        
        history = self.progress_history.get(goal_id)
        
        report = {
            "goal_id": goal_id,
            "goal_name": goal.name,
            "status": goal.status.value,
            "current_progress": goal.progress_percentage,
            "priority": goal.priority.value,
            "created_at": goal.created_at.isoformat(),
            "metrics": [m.to_dict() for m in goal.metrics],
            "subgoals_count": len(goal.subgoals)
        }
        
        if history and history.snapshots:
            latest = history.get_latest()
            if latest:
                report["last_snapshot"] = latest.to_dict()
            
            report["trend"] = history.get_progress_trend()
            report["velocity"] = history.calculate_velocity()
            report["snapshot_count"] = len(history.snapshots)
            
            # 预测完成时间
            if goal.status == GoalStatus.IN_PROGRESS:
                eta = self.predict_completion(goal_id)
                if eta:
                    report["estimated_completion"] = eta.isoformat()
        
        return report
    
    def predict_completion(self, goal_id: str) -> Optional[datetime]:
        """
        预测完成时间
        
        基于历史进度速度预测
        """
        history = self.progress_history.get(goal_id)
        if not history or len(history.snapshots) < 2:
            return None
        
        goal = self.goal_manager.get_goal(goal_id)
        if not goal or goal.status != GoalStatus.IN_PROGRESS:
            return None
        
        velocity = history.calculate_velocity()
        if velocity <= 0:
            return None
        
        remaining_progress = 100.0 - goal.progress_percentage
        hours_remaining = remaining_progress / velocity
        
        return datetime.now() + timedelta(hours=hours_remaining)
    
    def check_overdue_goals(self) -> List[Dict[str, Any]]:
        """检查过期目标"""
        overdue = []
        
        for goal in self.goal_manager.get_active_goals():
            if goal.deadline and datetime.now() > goal.deadline:
                overdue.append({
                    "goal_id": goal.id,
                    "goal_name": goal.name,
                    "deadline": goal.deadline.isoformat(),
                    "progress": goal.progress_percentage,
                    "days_overdue": (datetime.now() - goal.deadline).days
                })
        
        return overdue
    
    def get_slow_goals(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """
        获取进度缓慢的目标
        
        Args:
            threshold: 速度阈值（百分比/小时）
            
        Returns:
            进度缓慢的目标列表
        """
        slow = []
        
        for goal_id in self._tracking_goals:
            history = self.progress_history.get(goal_id)
            if not history:
                continue
            
            velocity = history.calculate_velocity()
            if 0 < velocity < threshold:
                goal = self.goal_manager.get_goal(goal_id)
                if goal:
                    slow.append({
                        "goal_id": goal_id,
                        "goal_name": goal.name,
                        "velocity": velocity,
                        "current_progress": goal.progress_percentage
                    })
        
        return slow
    
    def get_tracking_summary(self) -> Dict[str, Any]:
        """获取追踪摘要"""
        return {
            "tracking_count": len(self._tracking_goals),
            "total_history_entries": sum(
                len(h.snapshots) for h in self.progress_history.values()
            ),
            "goals_with_history": len(self.progress_history)
        }
    
    def export_progress_data(self) -> Dict[str, Any]:
        """导出进度数据"""
        return {
            goal_id: {
                "snapshots": [s.to_dict() for s in history.snapshots]
            }
            for goal_id, history in self.progress_history.items()
        }


# 导出
__all__ = [
    "ProgressSnapshot",
    "ProgressHistory",
    "GoalTracker"
]

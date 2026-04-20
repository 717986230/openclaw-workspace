"""
AutoGPT Execution Analyzer
执行结果分析器
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class TaskExecutionStats:
    """任务执行统计"""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    error_types: Dict[str, int] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "success_rate": self.success_rate,
            "avg_duration": self.avg_duration,
            "min_duration": self.min_duration if self.min_duration != float('inf') else 0,
            "max_duration": self.max_duration,
            "error_types": self.error_types
        }


@dataclass
class ExecutionTrend:
    """执行趋势"""
    metric: str
    values: List[float] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)
    
    @property
    def trend_direction(self) -> str:
        """趋势方向"""
        if len(self.values) < 2:
            return "stable"
        
        recent = self.values[-5:]
        if len(recent) < 2:
            return "stable"
        
        first_half = sum(recent[:len(recent)//2]) / (len(recent)//2)
        second_half = sum(recent[len(recent)//2:]) / (len(recent) - len(recent)//2)
        
        if second_half > first_half * 1.1:
            return "improving"
        elif second_half < first_half * 0.9:
            return "declining"
        else:
            return "stable"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric": self.metric,
            "trend_direction": self.trend_direction,
            "latest_value": self.values[-1] if self.values else None,
            "data_points": len(self.values)
        }


class ExecutionAnalyzer:
    """
    执行分析器
    
    负责：
    - 收集执行指标
    - 统计分析执行结果
    - 识别趋势和异常
    - 生成分析报告
    """
    
    def __init__(self, max_history: int = 100):
        """
        初始化分析器
        
        Args:
            max_history: 最大历史记录数
        """
        self.max_history = max_history
        
        # 执行记录
        self.execution_records: List[Dict[str, Any]] = []
        
        # 任务级别统计
        self.task_stats: Dict[str, TaskExecutionStats] = defaultdict(TaskExecutionStats)
        
        # 趋势追踪
        self.trends: Dict[str, ExecutionTrend] = {
            "success_rate": ExecutionTrend(metric="success_rate"),
            "avg_duration": ExecutionTrend(metric="avg_duration"),
            "throughput": ExecutionTrend(metric="throughput")
        }
        
        # 异常记录
        self.anomalies: List[Dict[str, Any]] = []
    
    def record_execution(
        self,
        task_id: str,
        success: bool,
        duration: float,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        记录执行结果
        
        Args:
            task_id: 任务 ID
            success: 是否成功
            duration: 执行时长（秒）
            error: 错误信息（如果有）
            metadata: 额外元数据
        """
        record = {
            "task_id": task_id,
            "success": success,
            "duration": duration,
            "error": error,
            "metadata": metadata or {},
            "recorded_at": datetime.now()
        }
        
        self.execution_records.append(record)
        
        # 限制历史记录大小
        if len(self.execution_records) > self.max_history:
            self.execution_records = self.execution_records[-self.max_history:]
        
        # 更新任务统计
        self._update_task_stats(record)
        
        # 检测异常
        self._detect_anomaly(record)
    
    def _update_task_stats(self, record: Dict[str, Any]):
        """更新任务统计"""
        task_id = record["task_id"]
        stats = self.task_stats[task_id]
        
        stats.total_executions += 1
        if record["success"]:
            stats.successful_executions += 1
        else:
            stats.failed_executions += 1
            if record["error"]:
                error_type = self._categorize_error(record["error"])
                stats.error_types[error_type] = stats.error_types.get(error_type, 0) + 1
        
        stats.total_duration += record["duration"]
        stats.avg_duration = stats.total_duration / stats.total_executions
        stats.min_duration = min(stats.min_duration, record["duration"])
        stats.max_duration = max(stats.max_duration, record["duration"])
    
    def _categorize_error(self, error: str) -> str:
        """分类错误类型"""
        error_lower = error.lower()
        
        if "timeout" in error_lower:
            return "timeout"
        elif "connection" in error_lower or "network" in error_lower:
            return "network"
        elif "memory" in error_lower or "oom" in error_lower:
            return "resource"
        elif "permission" in error_lower or "access" in error_lower:
            return "permission"
        elif "not found" in error_lower or "missing" in error_lower:
            return "missing_resource"
        else:
            return "unknown"
    
    def _detect_anomaly(self, record: Dict[str, Any]):
        """检测异常"""
        task_id = record["task_id"]
        stats = self.task_stats[task_id]
        
        # 异常长的执行时间
        if stats.total_executions > 5:  # 需要足够的历史数据
            if record["duration"] > stats.avg_duration * 3:
                self.anomalies.append({
                    "type": "long_execution",
                    "task_id": task_id,
                    "duration": record["duration"],
                    "expected": stats.avg_duration,
                    "ratio": record["duration"] / stats.avg_duration,
                    "detected_at": datetime.now().isoformat()
                })
        
        # 连续失败
        recent_records = [
            r for r in self.execution_records[-10:]
            if r["task_id"] == task_id
        ]
        if len(recent_records) >= 3:
            recent_failures = sum(1 for r in recent_records if not r["success"])
            if recent_failures >= len(recent_records) * 0.8:
                self.anomalies.append({
                    "type": "consecutive_failures",
                    "task_id": task_id,
                    "failure_count": recent_failures,
                    "total_recent": len(recent_records),
                    "detected_at": datetime.now().isoformat()
                })
    
    def update_trends(self):
        """更新趋势数据"""
        now = datetime.now()
        
        # 计算当前指标
        recent_records = self.execution_records[-20:]  # 最近20条记录
        
        if recent_records:
            # 成功率
            success_rate = sum(1 for r in recent_records if r["success"]) / len(recent_records)
            self.trends["success_rate"].values.append(success_rate)
            self.trends["success_rate"].timestamps.append(now)
            
            # 平均时长
            avg_duration = sum(r["duration"] for r in recent_records) / len(recent_records)
            self.trends["avg_duration"].values.append(avg_duration)
            self.trends["avg_duration"].timestamps.append(now)
            
            # 吞吐量（每分钟任务数）
            if len(recent_records) >= 2:
                time_span = (recent_records[-1]["recorded_at"] - recent_records[0]["recorded_at"]).total_seconds()
                if time_span > 0:
                    throughput = len(recent_records) / (time_span / 60)
                    self.trends["throughput"].values.append(throughput)
                    self.trends["throughput"].timestamps.append(now)
    
    def get_task_stats(self, task_id: str) -> Optional[TaskExecutionStats]:
        """获取任务统计"""
        return self.task_stats.get(task_id)
    
    def get_all_stats(self) -> Dict[str, TaskExecutionStats]:
        """获取所有任务统计"""
        return dict(self.task_stats)
    
    def get_trend_report(self) -> Dict[str, Any]:
        """获取趋势报告"""
        return {
            metric: trend.to_dict()
            for metric, trend in self.trends.items()
        }
    
    def get_anomalies(
        self,
        task_id: Optional[str] = None,
        anomaly_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取异常记录
        
        Args:
            task_id: 过滤特定任务
            anomaly_type: 过滤异常类型
            
        Returns:
            异常记录列表
        """
        anomalies = self.anomalies
        
        if task_id:
            anomalies = [a for a in anomalies if a.get("task_id") == task_id]
        
        if anomaly_type:
            anomalies = [a for a in anomalies if a.get("type") == anomaly_type]
        
        return anomalies
    
    def get_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        if not self.execution_records:
            return {
                "total_executions": 0,
                "message": "No execution records available"
            }
        
        # 总体统计
        total = len(self.execution_records)
        successful = sum(1 for r in self.execution_records if r["success"])
        
        # 时长统计
        durations = [r["duration"] for r in self.execution_records]
        avg_duration = sum(durations) / len(durations)
        
        # 错误类型分布
        error_distribution: Dict[str, int] = defaultdict(int)
        for record in self.execution_records:
            if not record["success"] and record["error"]:
                error_type = self._categorize_error(record["error"])
                error_distribution[error_type] += 1
        
        # 任务分布
        task_distribution: Dict[str, int] = defaultdict(int)
        for record in self.execution_records:
            task_distribution[record["task_id"]] += 1
        
        return {
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "avg_duration": avg_duration,
            "min_duration": min(durations),
            "max_duration": max(durations),
            "error_distribution": dict(error_distribution),
            "task_distribution": dict(task_distribution),
            "unique_tasks": len(task_distribution),
            "anomalies_detected": len(self.anomalies),
            "trends": self.get_trend_report()
        }
    
    def get_task_comparison(self) -> List[Dict[str, Any]]:
        """比较不同任务的性能"""
        comparison = []
        
        for task_id, stats in self.task_stats.items():
            comparison.append({
                "task_id": task_id,
                "success_rate": stats.success_rate,
                "avg_duration": stats.avg_duration,
                "reliability": self._calculate_reliability(stats),
                "performance_score": self._calculate_performance_score(stats)
            })
        
        # 按性能分数排序
        comparison.sort(key=lambda x: x["performance_score"], reverse=True)
        
        return comparison
    
    def _calculate_reliability(self, stats: TaskExecutionStats) -> float:
        """计算可靠性分数"""
        if stats.total_executions < 3:
            return 0.5  # 数据不足，返回中性值
        
        # 综合考虑成功率和稳定性
        success_rate = stats.success_rate
        
        # 检查执行时间的稳定性
        duration_range = stats.max_duration - stats.min_duration
        duration_variability = duration_range / stats.avg_duration if stats.avg_duration > 0 else 0
        
        # 可靠性 = 成功率 / (1 + 变异系数)
        reliability = success_rate / (1 + duration_variability)
        
        return min(1.0, reliability)
    
    def _calculate_performance_score(self, stats: TaskExecutionStats) -> float:
        """计算性能分数"""
        # 综合考虑成功率和执行速度
        if stats.total_executions == 0:
            return 0.0
        
        # 成功率权重
        success_weight = 0.6
        speed_weight = 0.4
        
        # 标准化成功率和速度
        success_score = stats.success_rate
        
        # 速度分数：越快越好，假设合理范围是0-60秒
        speed_score = max(0, 1 - stats.avg_duration / 60)
        
        return success_weight * success_score + speed_weight * speed_score
    
    def clear_stats(self):
        """清空统计数据"""
        self.execution_records.clear()
        self.task_stats.clear()
        self.anomalies.clear()
        for trend in self.trends.values():
            trend.values.clear()
            trend.timestamps.clear()
        
        logger.info("Execution stats cleared")


# 导出
__all__ = [
    "TaskExecutionStats",
    "ExecutionTrend",
    "ExecutionAnalyzer"
]

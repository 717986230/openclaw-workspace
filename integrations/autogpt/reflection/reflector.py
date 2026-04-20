"""
AutoGPT Reflector
自我反思模块 - 任务执行后的反思和改进机制
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ReflectionPoint:
    """反思点"""
    category: str  # success, failure, improvement, observation
    description: str
    impact: str  # high, medium, low
    actionable: bool
    suggested_action: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "description": self.description,
            "impact": self.impact,
            "actionable": self.actionable,
            "suggested_action": self.suggested_action
        }


@dataclass
class AnalysisResult:
    """分析结果"""
    task_id: str
    success: bool
    success_rate: float
    execution_time: float
    points: List[ReflectionPoint] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    analyzed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "success": self.success,
            "success_rate": self.success_rate,
            "execution_time": self.execution_time,
            "points": [p.to_dict() for p in self.points],
            "patterns": self.patterns,
            "metrics": self.metrics,
            "analyzed_at": self.analyzed_at.isoformat()
        }


@dataclass
class ImprovementSuggestion:
    """改进建议"""
    id: str
    type: str  # add_task, modify_task, reorder_tasks, change_strategy, adjust_parameters
    description: str
    priority: str  # critical, high, medium, low
    estimated_impact: str  # high, medium, low
    implementation_effort: str  # high, medium, low
    target: str  # 目标对象（任务ID、策略名称等）
    changes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "priority": self.priority,
            "estimated_impact": self.estimated_impact,
            "implementation_effort": self.implementation_effort,
            "target": self.target,
            "changes": self.changes
        }


class Reflector:
    """
    自我反思器 - AutoGPT 的核心反思组件
    
    负责：
    - 分析任务执行结果
    - 识别成功和失败模式
    - 生成改进建议
    - 持续优化执行策略
    """
    
    def __init__(self):
        """初始化反思器"""
        self.analysis_history: List[AnalysisResult] = []
        self.suggestion_counter = 0
        self._patterns_db: Dict[str, int] = {}  # pattern -> occurrence_count
        self._success_patterns: Dict[str, List[str]] = {}
        self._failure_patterns: Dict[str, List[str]] = {}
    
    def _generate_suggestion_id(self) -> str:
        """生成建议 ID"""
        self.suggestion_counter += 1
        return f"suggestion_{self.suggestion_counter:04d}"
    
    async def analyze_execution(
        self,
        execution_result: Any,  # ExecutionResult or ExecutionReport
        context: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """
        分析执行结果
        
        Args:
            execution_result: 执行结果（任务结果或报告）
            context: 额外上下文
            
        Returns:
            分析结果
        """
        # 提取执行信息
        task_id = getattr(execution_result, "task_id", "unknown")
        success = getattr(execution_result, "success", False)
        
        # 处理单个任务结果或完整报告
        if hasattr(execution_result, "success_rate"):
            # ExecutionReport
            success_rate = execution_result.success_rate
            execution_time = 0.0
            metrics = {
                "total_tasks": execution_result.total_tasks,
                "completed_tasks": execution_result.completed_tasks,
                "failed_tasks": execution_result.failed_tasks
            }
        else:
            # ExecutionResult
            success_rate = 1.0 if success else 0.0
            execution_time = getattr(execution_result, "duration_seconds", 0.0)
            metrics = {}
        
        # 创建分析结果
        analysis = AnalysisResult(
            task_id=task_id,
            success=success,
            success_rate=success_rate,
            execution_time=execution_time,
            metrics=metrics
        )
        
        # 分析成功点
        await self._analyze_successes(execution_result, analysis)
        
        # 分析失败点
        await self._analyze_failures(execution_result, analysis)
        
        # 识别模式
        await self._identify_patterns(execution_result, analysis)
        
        # 分析改进机会
        await self._analyze_improvements(execution_result, analysis)
        
        # 记录到历史
        self.analysis_history.append(analysis)
        
        # 更新模式数据库
        for pattern in analysis.patterns:
            self._patterns_db[pattern] = self._patterns_db.get(pattern, 0) + 1
        
        return analysis
    
    async def _analyze_successes(
        self,
        execution_result: Any,
        analysis: AnalysisResult
    ):
        """分析成功点"""
        if analysis.success_rate >= 0.8:
            point = ReflectionPoint(
                category="success",
                description="High success rate achieved",
                impact="high",
                actionable=False
            )
            analysis.points.append(point)
        
        if analysis.execution_time < 5.0:  # 少于5秒
            point = ReflectionPoint(
                category="success",
                description="Fast execution time",
                impact="medium",
                actionable=False
            )
            analysis.points.append(point)
        
        # 检查是否有高效完成的具体指标
        metrics = getattr(execution_result, "metrics", {})
        if metrics:
            for metric_name, value in metrics.items():
                if value > 0:
                    point = ReflectionPoint(
                        category="success",
                        description=f"Metric '{metric_name}' shows positive result",
                        impact="medium",
                        actionable=False
                    )
                    analysis.points.append(point)
    
    async def _analyze_failures(
        self,
        execution_result: Any,
        analysis: AnalysisResult
    ):
        """分析失败点"""
        if analysis.success_rate < 0.5:
            point = ReflectionPoint(
                category="failure",
                description="Low success rate indicates systematic issues",
                impact="high",
                actionable=True,
                suggested_action="Review task decomposition and execution strategy"
            )
            analysis.points.append(point)
        
        # 检查错误信息
        error = getattr(execution_result, "error", None)
        if error:
            point = ReflectionPoint(
                category="failure",
                description=f"Error encountered: {error}",
                impact="high",
                actionable=True,
                suggested_action="Investigate and fix the root cause of the error"
            )
            analysis.points.append(point)
        
        # 检查超时
        if analysis.execution_time > 60.0:  # 超过60秒
            point = ReflectionPoint(
                category="observation",
                description="Long execution time detected",
                impact="medium",
                actionable=True,
                suggested_action="Consider optimizing execution or breaking down into smaller tasks"
            )
            analysis.points.append(point)
    
    async def _identify_patterns(
        self,
        execution_result: Any,
        analysis: AnalysisResult
    ):
        """识别模式"""
        # 基于历史识别重复模式
        if len(self.analysis_history) > 0:
            # 检查是否有重复的成功模式
            if analysis.success_rate >= 0.8:
                recent_success_rate = sum(
                    1 for a in self.analysis_history[-5:]
                    if a.success_rate >= 0.8
                ) / min(5, len(self.analysis_history))
                
                if recent_success_rate >= 0.6:
                    analysis.patterns.append("consistent_high_success_rate")
            
            # 检查是否有重复的失败模式
            if analysis.success_rate < 0.5:
                recent_failure_rate = sum(
                    1 for a in self.analysis_history[-5:]
                    if a.success_rate < 0.5
                ) / min(5, len(self.analysis_history))
                
                if recent_failure_rate >= 0.4:
                    analysis.patterns.append("consistent_low_success_rate")
        
        # 执行时间模式
        if analysis.execution_time > 30:
            analysis.patterns.append("long_execution_time")
        elif analysis.execution_time < 1:
            analysis.patterns.append("quick_execution")
    
    async def _analyze_improvements(
        self,
        execution_result: Any,
        analysis: AnalysisResult
    ):
        """分析改进机会"""
        # 基于分析结果添加改进反思点
        if 0.5 <= analysis.success_rate < 0.8:
            point = ReflectionPoint(
                category="improvement",
                description="Success rate is moderate, room for improvement",
                impact="medium",
                actionable=True,
                suggested_action="Analyze which tasks failed and why, then adjust strategy"
            )
            analysis.points.append(point)
        
        # 检查是否有未利用的优化机会
        if analysis.execution_time > 10 and analysis.success_rate > 0.9:
            point = ReflectionPoint(
                category="improvement",
                description="Good success rate but slow execution, potential for optimization",
                impact="medium",
                actionable=True,
                suggested_action="Profile execution to find bottlenecks"
            )
            analysis.points.append(point)
    
    async def suggest_improvements(
        self,
        analysis: AnalysisResult,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ImprovementSuggestion]:
        """
        生成改进建议
        
        Args:
            analysis: 分析结果
            context: 额外上下文
            
        Returns:
            改进建议列表
        """
        suggestions = []
        
        # 基于分析结果生成建议
        for point in analysis.points:
            if point.actionable and point.suggested_action:
                suggestion = self._create_suggestion_from_point(point, analysis)
                if suggestion:
                    suggestions.append(suggestion)
        
        # 基于模式生成建议
        for pattern in analysis.patterns:
            pattern_suggestions = self._get_pattern_suggestions(pattern, analysis)
            suggestions.extend(pattern_suggestions)
        
        # 按优先级排序
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        suggestions.sort(key=lambda s: priority_order.get(s.priority, 3))
        
        return suggestions
    
    def _create_suggestion_from_point(
        self,
        point: ReflectionPoint,
        analysis: AnalysisResult
    ) -> Optional[ImprovementSuggestion]:
        """从反思点创建改进建议"""
        # 根据反思点类型确定建议类型
        suggestion_type = "change_strategy"
        if "task" in point.description.lower():
            suggestion_type = "modify_task"
        elif "optimi" in point.description.lower():
            suggestion_type = "adjust_parameters"
        
        return ImprovementSuggestion(
            id=self._generate_suggestion_id(),
            type=suggestion_type,
            description=point.suggested_action,
            priority="high" if point.impact == "high" else "medium",
            estimated_impact=point.impact,
            implementation_effort="medium",
            target=analysis.task_id,
            changes={"reflection_point": point.description}
        )
    
    def _get_pattern_suggestions(
        self,
        pattern: str,
        analysis: AnalysisResult
    ) -> List[ImprovementSuggestion]:
        """基于模式生成建议"""
        suggestions = []
        
        if pattern == "consistent_low_success_rate":
            suggestions.append(ImprovementSuggestion(
                id=self._generate_suggestion_id(),
                type="change_strategy",
                description="Fundamental strategy change needed due to consistent low success rate",
                priority="critical",
                estimated_impact="high",
                implementation_effort="high",
                target="execution_strategy",
                changes={"pattern": pattern}
            ))
        
        elif pattern == "long_execution_time":
            suggestions.append(ImprovementSuggestion(
                id=self._generate_suggestion_id(),
                type="adjust_parameters",
                description="Optimize execution parameters to reduce time",
                priority="medium",
                estimated_impact="medium",
                implementation_effort="low",
                target="execution_parameters",
                changes={"target_time_reduction": "30%"}
            ))
        
        return suggestions
    
    def get_analysis_history(
        self,
        limit: int = 10
    ) -> List[AnalysisResult]:
        """获取分析历史"""
        return self.analysis_history[-limit:]
    
    def get_frequent_patterns(self, threshold: int = 3) -> List[Dict[str, Any]]:
        """获取频繁出现的模式"""
        return [
            {"pattern": pattern, "count": count}
            for pattern, count in sorted(
                self._patterns_db.items(),
                key=lambda x: x[1],
                reverse=True
            )
            if count >= threshold
        ]
    
    def get_reflection_summary(self) -> Dict[str, Any]:
        """获取反思摘要"""
        total_analyses = len(self.analysis_history)
        
        if total_analyses == 0:
            return {
                "total_analyses": 0,
                "average_success_rate": 0,
                "patterns_identified": 0
            }
        
        avg_success = sum(a.success_rate for a in self.analysis_history) / total_analyses
        
        return {
            "total_analyses": total_analyses,
            "average_success_rate": avg_success,
            "patterns_identified": len(self._patterns_db),
            "frequent_patterns": len(self.get_frequent_patterns()),
            "last_analysis": self.analysis_history[-1].analyzed_at.isoformat()
        }
    
    def clear_history(self):
        """清空历史"""
        self.analysis_history.clear()
        self._patterns_db.clear()
        logger.info("Reflection history cleared")


# 导出
__all__ = [
    "ReflectionPoint",
    "AnalysisResult",
    "ImprovementSuggestion",
    "Reflector"
]

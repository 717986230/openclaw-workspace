"""
AutoGPT Improvement Suggester
改进建议生成器
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .reflector import AnalysisResult, ImprovementSuggestion

logger = logging.getLogger(__name__)


@dataclass
class SuggestionRule:
    """建议规则"""
    condition: str  # 条件描述
    check_func: Any  # 检查函数
    suggestion_template: str  # 建议模板
    priority: str  # 优先级
    impact: str  # 预期影响
    effort: str  # 实施难度


class ImprovementSuggester:
    """
    改进建议生成器
    
    负责：
    - 根据分析结果生成具体改进建议
    - 优先级排序
    - 影响评估
    """
    
    def __init__(self):
        """初始化建议生成器"""
        self.suggestion_counter = 0
        self._rules: List[SuggestionRule] = []
        self._initialize_rules()
    
    def _generate_suggestion_id(self) -> str:
        """生成建议 ID"""
        self.suggestion_counter += 1
        return f"improvement_{self.suggestion_counter:04d}"
    
    def _initialize_rules(self):
        """初始化建议规则"""
        # 成功率相关规则
        self._rules.append(SuggestionRule(
            condition="low_success_rate",
            check_func=lambda a: a.success_rate < 0.5,
            suggestion_template="Success rate is critically low ({success_rate:.1%}). Consider: 1) Review task decomposition, 2) Simplify task requirements, 3) Add more validation steps.",
            priority="critical",
            impact="high",
            effort="medium"
        ))
        
        self._rules.append(SuggestionRule(
            condition="moderate_success_rate",
            check_func=lambda a: 0.5 <= a.success_rate < 0.8,
            suggestion_template="Success rate is moderate ({success_rate:.1%}). Consider: 1) Identify specific failure points, 2) Add error handling, 3) Improve task sequencing.",
            priority="high",
            impact="medium",
            effort="low"
        ))
        
        # 执行时间相关规则
        self._rules.append(SuggestionRule(
            condition="slow_execution",
            check_func=lambda a: a.execution_time > 60,
            suggestion_template="Execution time is long ({execution_time:.1f}s). Consider: 1) Parallel execution, 2) Caching results, 3) Optimizing algorithms.",
            priority="medium",
            impact="medium",
            effort="medium"
        ))
        
        # 模式相关规则
        self._rules.append(SuggestionRule(
            condition="consistent_failures",
            check_func=lambda a: "consistent_low_success_rate" in a.patterns,
            suggestion_template="Consistent failure pattern detected. Consider: 1) Fundamental strategy change, 2) Root cause analysis, 3) Alternative approach.",
            priority="critical",
            impact="high",
            effort="high"
        ))
        
        self._rules.append(SuggestionRule(
            condition="improving_trend",
            check_func=lambda a: "consistent_high_success_rate" in a.patterns,
            suggestion_template="Good performance trend. Consider: 1) Document current approach, 2) Share best practices, 3) Further optimization.",
            priority="low",
            impact="low",
            effort="low"
        ))
    
    def generate_suggestions(
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
        context = context or {}
        
        # 应用所有规则
        for rule in self._rules:
            try:
                if rule.check_func(analysis):
                    suggestion = self._create_suggestion_from_rule(rule, analysis, context)
                    suggestions.append(suggestion)
            except Exception as e:
                logger.error(f"Error applying rule {rule.condition}: {e}")
        
        # 基于反思点生成额外建议
        for point in analysis.points:
            if point.category == "improvement" and point.actionable:
                suggestion = ImprovementSuggestion(
                    id=self._generate_suggestion_id(),
                    type="improvement_action",
                    description=point.suggested_action or point.description,
                    priority="high" if point.impact == "high" else "medium",
                    estimated_impact=point.impact,
                    implementation_effort="medium",
                    target=analysis.task_id,
                    changes={"reflection_point": point.description}
                )
                suggestions.append(suggestion)
        
        # 去重并排序
        suggestions = self._deduplicate_suggestions(suggestions)
        suggestions = self._prioritize_suggestions(suggestions)
        
        return suggestions
    
    def _create_suggestion_from_rule(
        self,
        rule: SuggestionRule,
        analysis: AnalysisResult,
        context: Dict[str, Any]
    ) -> ImprovementSuggestion:
        """从规则创建建议"""
        # 格式化建议描述
        description = rule.suggestion_template.format(
            success_rate=analysis.success_rate,
            execution_time=analysis.execution_time,
            **context
        )
        
        return ImprovementSuggestion(
            id=self._generate_suggestion_id(),
            type=self._determine_suggestion_type(rule.condition),
            description=description,
            priority=rule.priority,
            estimated_impact=rule.impact,
            implementation_effort=rule.effort,
            target=analysis.task_id,
            changes={"rule": rule.condition}
        )
    
    def _determine_suggestion_type(self, condition: str) -> str:
        """确定建议类型"""
        type_mapping = {
            "low_success_rate": "change_strategy",
            "moderate_success_rate": "adjust_parameters",
            "slow_execution": "adjust_parameters",
            "consistent_failures": "change_strategy",
            "improving_trend": "document_best_practice"
        }
        return type_mapping.get(condition, "improvement_action")
    
    def _deduplicate_suggestions(
        self,
        suggestions: List[ImprovementSuggestion]
    ) -> List[ImprovementSuggestion]:
        """去重建议"""
        seen = set()
        unique = []
        
        for suggestion in suggestions:
            key = (suggestion.type, suggestion.target)
            if key not in seen:
                seen.add(key)
                unique.append(suggestion)
        
        return unique
    
    def _prioritize_suggestions(
        self,
        suggestions: List[ImprovementSuggestion]
    ) -> List[ImprovementSuggestion]:
        """按优先级排序建议"""
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        
        return sorted(
            suggestions,
            key=lambda s: (
                priority_order.get(s.priority, 3),
                -len(s.changes)  # 有更多细节的优先
            )
        )
    
    def get_actionable_suggestions(
        self,
        suggestions: List[ImprovementSuggestion],
        max_effort: str = "high"
    ) -> List[ImprovementSuggestion]:
        """
        筛选可执行的建议
        
        Args:
            suggestions: 建议列表
            max_effort: 最大可接受难度
            
        Returns:
            可执行的建议列表
        """
        effort_order = {"low": 0, "medium": 1, "high": 2}
        max_effort_level = effort_order.get(max_effort, 2)
        
        return [
            s for s in suggestions
            if effort_order.get(s.implementation_effort, 2) <= max_effort_level
        ]
    
    def generate_implementation_plan(
        self,
        suggestions: List[ImprovementSuggestion]
    ) -> Dict[str, Any]:
        """
        生成实施计划
        
        Args:
            suggestions: 建议列表
            
        Returns:
            实施计划
        """
        phases = {
            "immediate": [],  # 立即执行（critical优先级）
            "short_term": [],  # 短期执行（high优先级）
            "medium_term": [],  # 中期执行（medium优先级）
            "long_term": []  # 长期执行（low优先级）
        }
        
        for suggestion in suggestions:
            if suggestion.priority == "critical":
                phases["immediate"].append(suggestion)
            elif suggestion.priority == "high":
                phases["short_term"].append(suggestion)
            elif suggestion.priority == "medium":
                phases["medium_term"].append(suggestion)
            else:
                phases["long_term"].append(suggestion)
        
        return {
            "phases": {
                phase: [
                    {
                        "id": s.id,
                        "description": s.description,
                        "effort": s.implementation_effort,
                        "impact": s.estimated_impact
                    }
                    for s in items
                ]
                for phase, items in phases.items()
            },
            "summary": {
                "total_suggestions": len(suggestions),
                "immediate_actions": len(phases["immediate"]),
                "estimated_total_effort": self._estimate_total_effort(suggestions)
            }
        }
    
    def _estimate_total_effort(self, suggestions: List[ImprovementSuggestion]) -> str:
        """估算总工作量"""
        effort_hours = {
            "low": 1,
            "medium": 4,
            "high": 16
        }
        
        total_hours = sum(
            effort_hours.get(s.implementation_effort, 4)
            for s in suggestions
        )
        
        if total_hours < 4:
            return "quick (< 4 hours)"
        elif total_hours < 16:
            return "moderate (4-16 hours)"
        elif total_hours < 40:
            return "significant (16-40 hours)"
        else:
            return "major (> 40 hours)"
    
    def add_custom_rule(
        self,
        condition: str,
        check_func: Any,
        suggestion_template: str,
        priority: str = "medium",
        impact: str = "medium",
        effort: str = "medium"
    ):
        """
        添加自定义规则
        
        Args:
            condition: 条件名称
            check_func: 检查函数
            suggestion_template: 建议模板
            priority: 优先级
            impact: 预期影响
            effort: 实施难度
        """
        rule = SuggestionRule(
            condition=condition,
            check_func=check_func,
            suggestion_template=suggestion_template,
            priority=priority,
            impact=impact,
            effort=effort
        )
        self._rules.append(rule)
        logger.info(f"Added custom rule: {condition}")


# 导出
__all__ = [
    "SuggestionRule",
    "ImprovementSuggester"
]

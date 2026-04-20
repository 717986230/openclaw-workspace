"""
AutoGPT Goal Validator
目标完成验证器
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging
import re

from .goal_manager import Goal, GoalStatus, GoalManager

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """验证结果"""
    goal_id: str
    is_valid: bool
    score: float  # 0-1
    passed_criteria: List[str] = field(default_factory=list)
    failed_criteria: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    validated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "is_valid": self.is_valid,
            "score": self.score,
            "passed_criteria": self.passed_criteria,
            "failed_criteria": self.failed_criteria,
            "warnings": self.warnings,
            "details": self.details,
            "validated_at": self.validated_at.isoformat()
        }


class CriterionType:
    """验证条件类型"""
    METRIC_THRESHOLD = "metric_threshold"      # 指标阈值
    SUBGOAL_COMPLETION = "subgoal_completion"  # 子目标完成
    TIME_CONSTRAINT = "time_constraint"        # 时间约束
    CUSTOM_CHECK = "custom_check"              # 自定义检查
    PATTERN_MATCH = "pattern_match"            # 模式匹配


class GoalValidator:
    """
    目标完成验证器
    
    负责：
    - 验证目标是否满足完成条件
    - 执行各种类型的验证检查
    - 生成验证报告
    """
    
    def __init__(self, goal_manager: GoalManager):
        """
        初始化验证器
        
        Args:
            goal_manager: 目标管理器
        """
        self.goal_manager = goal_manager
        
        # 自定义验证函数注册表
        self.custom_validators: Dict[str, Callable] = {}
        
        # 验证历史
        self.validation_history: Dict[str, List[ValidationResult]] = {}
    
    def register_validator(self, name: str, validator_func: Callable):
        """
        注册自定义验证器
        
        Args:
            name: 验证器名称
            validator_func: 验证函数，签名为 (goal: Goal) -> bool
        """
        self.custom_validators[name] = validator_func
        logger.info(f"Registered custom validator: {name}")
    
    def validate_goal(self, goal_id: str) -> ValidationResult:
        """
        验证目标
        
        执行所有验证检查并返回综合结果
        
        Args:
            goal_id: 目标 ID
            
        Returns:
            验证结果
        """
        goal = self.goal_manager.get_goal(goal_id)
        if not goal:
            return ValidationResult(
                goal_id=goal_id,
                is_valid=False,
                score=0.0,
                failed_criteria=["Goal not found"]
            )
        
        result = ValidationResult(
            goal_id=goal_id,
            is_valid=True,
            score=1.0,
            details={"goal_name": goal.name}
        )
        
        # 1. 验证度量指标
        self._validate_metrics(goal, result)
        
        # 2. 验证完成条件
        self._validate_completion_criteria(goal, result)
        
        # 3. 验证子目标
        self._validate_subgoals(goal, result)
        
        # 4. 验证时间约束
        self._validate_time_constraint(goal, result)
        
        # 计算最终得分
        total_checks = len(result.passed_criteria) + len(result.failed_criteria)
        if total_checks > 0:
            result.score = len(result.passed_criteria) / total_checks
        
        # 确定是否有效
        result.is_valid = (
            len(result.failed_criteria) == 0 and
            result.score >= 0.8  # 至少80%通过
        )
        
        # 记录验证历史
        if goal_id not in self.validation_history:
            self.validation_history[goal_id] = []
        self.validation_history[goal_id].append(result)
        
        return result
    
    def _validate_metrics(self, goal: Goal, result: ValidationResult):
        """验证度量指标"""
        for metric in goal.metrics:
            criterion_name = f"metric_{metric.name}"
            
            # 检查是否达到目标值
            if metric.current_value >= metric.target_value:
                result.passed_criteria.append(criterion_name)
                result.details[f"{criterion_name}_value"] = metric.current_value
            else:
                result.failed_criteria.append(criterion_name)
                result.details[f"{criterion_name}_value"] = f"{metric.current_value}/{metric.target_value}"
                
                # 检查是否接近目标（至少80%）
                if metric.progress >= 80:
                    result.warnings.append(f"Metric '{metric.name}' is close to target ({metric.progress:.1f}%)")
    
    def _validate_completion_criteria(self, goal: Goal, result: ValidationResult):
        """验证完成条件"""
        for criterion in goal.completion_criteria:
            # 尝试解析条件
            check_result = self._check_criterion(goal, criterion)
            
            if check_result["passed"]:
                result.passed_criteria.append(criterion)
            else:
                result.failed_criteria.append(criterion)
                if "warning" in check_result:
                    result.warnings.append(check_result["warning"])
    
    def _check_criterion(self, goal: Goal, criterion: str) -> Dict[str, Any]:
        """检查单个条件"""
        # 指标阈值检查: "metric:name>=value"
        if criterion.startswith("metric:"):
            match = re.match(r"metric:(\w+)(>=|<=|==|>|<)([\d.]+)", criterion)
            if match:
                metric_name, operator, value = match.groups()
                value = float(value)
                
                metric = next(
                    (m for m in goal.metrics if m.name == metric_name),
                    None
                )
                
                if not metric:
                    return {"passed": False, "warning": f"Metric '{metric_name}' not found"}
                
                current = metric.current_value
                
                if operator == ">=":
                    passed = current >= value
                elif operator == "<=":
                    passed = current <= value
                elif operator == "==":
                    passed = abs(current - value) < 0.01
                elif operator == ">":
                    passed = current > value
                else:  # <
                    passed = current < value
                
                return {"passed": passed}
        
        # 自定义验证器检查: "custom:validator_name"
        elif criterion.startswith("custom:"):
            validator_name = criterion.split(":", 1)[1]
            
            if validator_name in self.custom_validators:
                try:
                    passed = self.custom_validators[validator_name](goal)
                    return {"passed": passed}
                except Exception as e:
                    logger.error(f"Custom validator error: {e}")
                    return {"passed": False, "warning": str(e)}
            else:
                return {"passed": False, "warning": f"Validator '{validator_name}' not found"}
        
        # 模式匹配检查: "pattern:field:regex"
        elif criterion.startswith("pattern:"):
            parts = criterion.split(":", 2)
            if len(parts) == 3:
                _, field, pattern = parts
                
                field_value = getattr(goal, field, "")
                if not field_value:
                    field_value = goal.metadata.get(field, "")
                
                try:
                    passed = bool(re.search(pattern, str(field_value)))
                    return {"passed": passed}
                except re.error:
                    return {"passed": False, "warning": "Invalid regex pattern"}
        
        # 默认：尝试作为布尔条件
        return {"passed": False, "warning": f"Unknown criterion format: {criterion}"}
    
    def _validate_subgoals(self, goal: Goal, result: ValidationResult):
        """验证子目标"""
        if not goal.subgoals:
            return
        
        completed_subgoals = 0
        for subgoal_id in goal.subgoals:
            subgoal = self.goal_manager.get_goal(subgoal_id)
            if subgoal and subgoal.status == GoalStatus.COMPLETED:
                completed_subgoals += 1
        
        criterion_name = "subgoals_completion"
        
        # 至少80%子目标完成
        completion_rate = completed_subgoals / len(goal.subgoals)
        
        if completion_rate >= 0.8:
            result.passed_criteria.append(criterion_name)
            result.details["subgoals_completed"] = f"{completed_subgoals}/{len(goal.subgoals)}"
        else:
            result.failed_criteria.append(criterion_name)
            result.details["subgoals_completed"] = f"{completed_subgoals}/{len(goal.subgoals)}"
            
            if completion_rate >= 0.5:
                result.warnings.append(f"Most subgoals completed ({completion_rate:.0%}), but not enough")
    
    def _validate_time_constraint(self, goal: Goal, result: ValidationResult):
        """验证时间约束"""
        if not goal.deadline:
            return
        
        criterion_name = "time_constraint"
        now = datetime.now()
        
        if goal.completed_at:
            # 已完成，检查是否按时完成
            if goal.completed_at <= goal.deadline:
                result.passed_criteria.append(criterion_name)
            else:
                result.failed_criteria.append(criterion_name)
                result.warnings.append("Goal completed after deadline")
        else:
            # 未完成，检查是否超期
            if now > goal.deadline and goal.status == GoalStatus.IN_PROGRESS:
                result.failed_criteria.append(criterion_name)
                result.warnings.append("Goal is overdue")
            elif goal.status == GoalStatus.IN_PROGRESS:
                # 还在期限内，通过
                result.passed_criteria.append(criterion_name)
    
    def validate_all_active(self) -> Dict[str, ValidationResult]:
        """验证所有活跃目标"""
        results = {}
        
        for goal in self.goal_manager.get_active_goals():
            results[goal.id] = self.validate_goal(goal.id)
        
        return results
    
    def can_complete_goal(self, goal_id: str) -> Dict[str, Any]:
        """
        检查目标是否可以标记为完成
        
        Returns:
            包含 can_complete, issues, suggestions 的字典
        """
        result = self.validate_goal(goal_id)
        
        return {
            "can_complete": result.is_valid,
            "issues": result.failed_criteria,
            "warnings": result.warnings,
            "score": result.score,
            "suggestions": self._generate_completion_suggestions(result)
        }
    
    def _generate_completion_suggestions(self, result: ValidationResult) -> List[str]:
        """生成完成建议"""
        suggestions = []
        
        for failed in result.failed_criteria:
            if failed.startswith("metric_"):
                metric_name = failed.replace("metric_", "")
                suggestions.append(f"Work on improving metric '{metric_name}'")
            elif failed == "subgoals_completion":
                suggestions.append("Complete more subgoals before marking this goal as complete")
            elif failed == "time_constraint":
                suggestions.append("Consider adjusting the deadline or accepting the overdue status")
        
        if result.score < 0.5:
            suggestions.append("Consider breaking down this goal into smaller, more achievable subgoals")
        
        return suggestions
    
    def get_validation_history(self, goal_id: str) -> List[ValidationResult]:
        """获取验证历史"""
        return self.validation_history.get(goal_id, [])
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """获取验证摘要"""
        total_validations = sum(len(h) for h in self.validation_history.values())
        
        recent_results = []
        for history in self.validation_history.values():
            if history:
                recent_results.append(history[-1])
        
        valid_count = sum(1 for r in recent_results if r.is_valid)
        
        return {
            "total_validations": total_validations,
            "goals_validated": len(self.validation_history),
            "recent_valid": valid_count,
            "recent_invalid": len(recent_results) - valid_count,
            "average_score": sum(r.score for r in recent_results) / len(recent_results) if recent_results else 0
        }


# 导出
__all__ = [
    "ValidationResult",
    "CriterionType",
    "GoalValidator"
]

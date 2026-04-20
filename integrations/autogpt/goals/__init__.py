"""
AutoGPT Goals Module
目标管理模块
"""

from .goal_manager import (
    GoalStatus,
    GoalPriority,
    GoalType,
    GoalMetric,
    Goal,
    GoalManager
)
from .goal_tracker import (
    ProgressSnapshot,
    ProgressHistory,
    GoalTracker
)
from .goal_validator import (
    ValidationResult,
    CriterionType,
    GoalValidator
)

__all__ = [
    # Goal Manager
    "GoalStatus",
    "GoalPriority",
    "GoalType",
    "GoalMetric",
    "Goal",
    "GoalManager",
    
    # Goal Tracker
    "ProgressSnapshot",
    "ProgressHistory",
    "GoalTracker",
    
    # Goal Validator
    "ValidationResult",
    "CriterionType",
    "GoalValidator",
]

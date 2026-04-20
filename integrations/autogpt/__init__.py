"""
AutoGPT Integration for OpenClaw

将 AutoGPT 框架的核心能力集成到 OpenClaw 平台。

主要组件：
- Planning: 自主任务规划与分解
- Goals: 目标管理与追踪
- Reflection: 自我反思与优化

使用示例：
    from integrations.autogpt import AutoGPTAgent
    
    # 创建代理
    agent = AutoGPTAgent(name="分析助手")
    
    # 设置目标
    agent.set_goal("分析销售数据并生成报告")
    
    # 运行
    result = await agent.run()
"""

__version__ = "1.0.0"

# 导入主要组件
from integrations.autogpt.planning import (
    Task,
    TaskStatus,
    TaskPriority,
    Plan,
    TaskPlanner,
    PlanExecutor,
    ExecutionResult,
    ExecutionReport,
    TaskDependencyManager
)

from integrations.autogpt.goals import (
    GoalStatus,
    GoalPriority,
    GoalType,
    GoalMetric,
    Goal,
    GoalManager,
    GoalTracker,
    GoalValidator
)

from integrations.autogpt.reflection import (
    Reflector,
    ExecutionAnalyzer,
    ImprovementSuggester,
    AnalysisResult,
    ImprovementSuggestion
)

# 便捷导出
__all__ = [
    # Version
    "__version__",
    
    # Planning
    "Task",
    "TaskStatus",
    "TaskPriority",
    "Plan",
    "TaskPlanner",
    "PlanExecutor",
    "ExecutionResult",
    "ExecutionReport",
    "TaskDependencyManager",
    
    # Goals
    "GoalStatus",
    "GoalPriority",
    "GoalType",
    "GoalMetric",
    "Goal",
    "GoalManager",
    "GoalTracker",
    "GoalValidator",
    
    # Reflection
    "Reflector",
    "ExecutionAnalyzer",
    "ImprovementSuggester",
    "AnalysisResult",
    "ImprovementSuggestion",
]

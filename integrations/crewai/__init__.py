"""
CrewAI Integration for OpenClaw

多智能体协作框架集成。
"""

from .roles import (
    BaseAgent,
    AgentConfig,
    AgentRole,
    AgentFactory,
    ResearcherAgent,
    WriterAgent,
    ReviewerAgent
)

from .tasks import (
    TaskManager,
    TaskQueue,
    TaskDefinition,
    TaskResult,
    TaskType,
    TaskPriority,
    TaskStatus
)

from .workflows import (
    BaseWorkflow,
    WorkflowConfig,
    WorkflowResult,
    WorkflowRegistry,
    ResearchWorkflow,
    ContentWorkflow
)

__version__ = "1.0.0"

__all__ = [
    # Roles
    'BaseAgent',
    'AgentConfig',
    'AgentRole',
    'AgentFactory',
    'ResearcherAgent',
    'WriterAgent',
    'ReviewerAgent',
    
    # Tasks
    'TaskManager',
    'TaskQueue',
    'TaskDefinition',
    'TaskResult',
    'TaskType',
    'TaskPriority',
    'TaskStatus',
    
    # Workflows
    'BaseWorkflow',
    'WorkflowConfig',
    'WorkflowResult',
    'WorkflowRegistry',
    'ResearchWorkflow',
    'ContentWorkflow'
]

"""
CrewAI 角色定义模块

提供各种预定义的智能体角色。
"""

from .base_role import (
    BaseAgent,
    AgentConfig,
    AgentRole,
    AgentFactory
)
from .researcher import ResearcherAgent
from .writer import WriterAgent
from .reviewer import ReviewerAgent

__all__ = [
    'BaseAgent',
    'AgentConfig',
    'AgentRole',
    'AgentFactory',
    'ResearcherAgent',
    'WriterAgent',
    'ReviewerAgent'
]

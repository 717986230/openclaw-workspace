"""
CrewAI 示例模块

提供基础和高级使用示例。
"""

from .basic_crew import (
    example_basic_research,
    example_task_manager,
    example_task_template,
    example_content_creation,
    example_custom_agent
)

from .advanced_crew import (
    example_hierarchical_process,
    example_task_dependencies,
    example_dynamic_allocation,
    example_workflow_orchestration,
    example_error_handling,
    example_parallel_workflows
)

__all__ = [
    'example_basic_research',
    'example_task_manager',
    'example_task_template',
    'example_content_creation',
    'example_custom_agent',
    'example_hierarchical_process',
    'example_task_dependencies',
    'example_dynamic_allocation',
    'example_workflow_orchestration',
    'example_error_handling',
    'example_parallel_workflows'
]

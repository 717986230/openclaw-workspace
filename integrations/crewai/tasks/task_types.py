"""
CrewAI 任务类型定义

定义不同类型的任务及其属性。
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


class TaskPriority(Enum):
    """任务优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """任务类型"""
    RESEARCH = "research"
    WRITING = "writing"
    REVIEW = "review"
    ANALYSIS = "analysis"
    COORDINATION = "coordination"
    EXECUTION = "execution"
    CUSTOM = "custom"


@dataclass
class TaskDefinition:
    """任务定义"""
    task_id: str
    task_type: TaskType
    description: str
    expected_output: str
    agent_role: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    tools: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300  # 秒
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    
@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    status: TaskStatus
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    tokens_used: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    

@dataclass
class TaskTemplate:
    """任务模板"""
    name: str
    task_type: TaskType
    description_template: str
    output_template: str
    default_agent_role: str
    default_tools: List[str] = field(default_factory=list)
    default_priority: TaskPriority = TaskPriority.MEDIUM
    
    def create_task(self, task_id: str, **kwargs) -> TaskDefinition:
        """
        从模板创建任务实例
        
        Args:
            task_id: 任务ID
            **kwargs: 模板变量
            
        Returns:
            任务定义实例
        """
        description = self.description_template.format(**kwargs)
        expected_output = self.output_template.format(**kwargs)
        
        return TaskDefinition(
            task_id=task_id,
            task_type=self.task_type,
            description=description,
            expected_output=expected_output,
            agent_role=self.default_agent_role,
            tools=self.default_tools.copy(),
            priority=self.default_priority
        )


# 预定义任务模板
TASK_TEMPLATES = {
    "research_topic": TaskTemplate(
        name="研究主题",
        task_type=TaskType.RESEARCH,
        description_template="研究主题：{topic}。请提供关于该主题的详细信息。",
        output_template="一份包含以下内容的研究报告：\n1. 主题概述\n2. 关键发现\n3. 相关资源\n4. 结论",
        default_agent_role="researcher",
        default_tools=["search", "web_scraper"]
    ),
    
    "write_article": TaskTemplate(
        name="撰写文章",
        task_type=TaskType.WRITING,
        description_template="撰写关于 {topic} 的文章，风格：{style}，长度：{length}",
        output_template="一篇完整的文章，包含：\n1. 标题\n2. 引言\n3. 正文内容\n4. 结论",
        default_agent_role="writer",
        default_tools=["file_reader"]
    ),
    
    "review_content": TaskTemplate(
        name="审核内容",
        task_type=TaskType.REVIEW,
        description_template="审核以下内容的{criteria}：\n{content}",
        output_template="审核报告，包含：\n1. 各项评分\n2. 具体问题\n3. 改进建议\n4. 总体评价",
        default_agent_role="reviewer",
        default_tools=["file_reader"]
    ),
    
    "analyze_data": TaskTemplate(
        name="分析数据",
        task_type=TaskType.ANALYSIS,
        description_template="分析以下数据，寻找 {analysis_type}：\n{data}",
        output_template="分析报告，包含：\n1. 数据概述\n2. 分析方法\n3. 关键发现\n4. 建议措施",
        default_agent_role="analyzer",
        default_tools=["data_processor"]
    )
}

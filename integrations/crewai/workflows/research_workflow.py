"""
CrewAI 研究工作流

专门用于研究任务的协作工作流。
"""

from typing import List, Any, Optional
from .base_workflow import (
    BaseWorkflow,
    WorkflowConfig,
    ProcessType
)


class ResearchWorkflow(BaseWorkflow):
    """
    研究工作流
    
    协调研究员智能体完成复杂的研究任务。
    """
    
    def __init__(
        self,
        topic: Optional[str] = None,
        depth: str = "medium"
    ):
        """
        初始化研究工作流
        
        Args:
            topic: 研究主题（可选，可在执行时提供）
            depth: 研究深度 (shallow/medium/deep)
        """
        config = WorkflowConfig(
            name="research_workflow",
            description="多智能体协作研究工作流",
            process_type=ProcessType.SEQUENTIAL,
            max_agents=3,
            timeout=600
        )
        super().__init__(config)
        
        self.topic = topic
        self.depth = depth
        self._agents = []
        
    def create_crew(self) -> Any:
        """
        创建 CrewAI Crew 实例
        
        Returns:
            CrewAI Crew 对象
        """
        try:
            from crewai import Crew, Process
            
            # 创建智能体
            agents = self._create_agents()
            
            # 创建 Crew
            crew = Crew(
                agents=agents,
                process=Process.sequential,
                verbose=self.config.verbose
            )
            
            return crew
            
        except ImportError:
            # 返回模拟对象
            return {
                'name': self.config.name,
                'agents': self._agents,
                'process': 'sequential'
            }
            
    def create_tasks(self) -> List[Any]:
        """
        创建研究任务列表
        
        Returns:
            任务列表
        """
        topic = self.topic or "未指定主题"
        
        try:
            from crewai import Task
            
            tasks = [
                Task(
                    description=f"研究主题: {topic}。收集相关信息和背景资料。",
                    expected_output="详细的研究笔记，包括信息来源",
                    agent=self._agents[0] if self._agents else None
                ),
                Task(
                    description=f"分析收集的信息，提取关键发现和洞察。",
                    expected_output="结构化的分析报告，包含关键发现",
                    agent=self._agents[1] if len(self._agents) > 1 else None
                ),
                Task(
                    description=f"整合研究结果，撰写完整的研究报告。",
                    expected_output="完整的研究报告，包含概述、分析和结论",
                    agent=self._agents[2] if len(self._agents) > 2 else None
                )
            ]
            
            return tasks
            
        except ImportError:
            # 返回模拟任务
            return [
                {'description': f'研究: {topic}', 'type': 'research'},
                {'description': '分析信息', 'type': 'analysis'},
                {'description': '撰写报告', 'type': 'writing'}
            ]
            
    def _create_agents(self) -> List[Any]:
        """创建研究智能体"""
        agents = []
        
        try:
            from integrations.crewai.roles import (
                ResearcherAgent,
                WriterAgent,
                ReviewerAgent
            )
            
            # 主要研究员
            researcher = ResearcherAgent()
            agents.append(researcher.get_agent())
            self._agents.append(researcher)
            
            # 分析师（使用研究员配置）
            analyst = ResearcherAgent()
            agents.append(analyst.get_agent())
            self._agents.append(analyst)
            
            # 写作者
            writer = WriterAgent()
            agents.append(writer.get_agent())
            self._agents.append(writer)
            
        except ImportError:
            pass
            
        return agents
        
    def research(self, topic: str) -> str:
        """
        执行研究（简化接口）
        
        Args:
            topic: 研究主题
            
        Returns:
            研究结果
        """
        self.topic = topic
        result = self.execute({'topic': topic})
        return result.output or ""


# 注册工作流
from .base_workflow import WorkflowRegistry
WorkflowRegistry.register('research', ResearchWorkflow)

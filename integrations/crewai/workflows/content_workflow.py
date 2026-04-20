"""
CrewAI 内容创作工作流

用于文章、报告等内容创作的协作工作流。
"""

from typing import List, Any, Optional
from .base_workflow import (
    BaseWorkflow,
    WorkflowConfig,
    ProcessType
)


class ContentWorkflow(BaseWorkflow):
    """
    内容创作工作流
    
    协调研究员、写作者和审核者完成内容创作任务。
    """
    
    def __init__(
        self,
        agents: Optional[List[Any]] = None,
        style: str = "professional"
    ):
        """
        初始化内容创作工作流
        
        Args:
            agents: 智能体列表（可选）
            style: 写作风格
        """
        config = WorkflowConfig(
            name="content_workflow",
            description="多智能体协作内容创作工作流",
            process_type=ProcessType.SEQUENTIAL,
            max_agents=5,
            timeout=900
        )
        super().__init__(config)
        
        self.style = style
        self._agents = agents or []
        
    def create_crew(self) -> Any:
        """
        创建 CrewAI Crew 实例
        
        Returns:
            CrewAI Crew 对象
        """
        try:
            from crewai import Crew, Process
            
            # 如果没有提供智能体，创建默认
            if not self._agents:
                self._agents = self._create_default_agents()
                
            # 创建 Crew
            crew = Crew(
                agents=[a.get_agent() if hasattr(a, 'get_agent') else a for a in self._agents],
                process=Process.sequential,
                verbose=self.config.verbose
            )
            
            return crew
            
        except ImportError:
            return {
                'name': self.config.name,
                'agents': self._agents,
                'process': 'sequential'
            }
            
    def create_tasks(self) -> List[Any]:
        """
        创建内容创作任务列表
        
        Returns:
            任务列表
        """
        try:
            from crewai import Task
            
            tasks = [
                Task(
                    description="研究主题背景，收集相关信息和素材。",
                    expected_output="研究笔记和素材清单",
                    agent=self._get_agent_by_role('researcher')
                ),
                Task(
                    description="基于研究结果，撰写初稿内容。",
                    expected_output="内容初稿",
                    agent=self._get_agent_by_role('writer')
                ),
                Task(
                    description="审核内容质量，提出修改建议。",
                    expected_output="审核报告和修改建议",
                    agent=self._get_agent_by_role('reviewer')
                ),
                Task(
                    description="根据审核意见修改完善内容。",
                    expected_output="最终版本内容",
                    agent=self._get_agent_by_role('writer')
                )
            ]
            
            return tasks
            
        except ImportError:
            return [
                {'description': '研究背景', 'type': 'research'},
                {'description': '撰写初稿', 'type': 'writing'},
                {'description': '审核内容', 'type': 'review'},
                {'description': '修改完善', 'type': 'writing'}
            ]
            
    def _create_default_agents(self) -> List[Any]:
        """创建默认智能体集"""
        agents = []
        
        try:
            from integrations.crewai.roles import (
                ResearcherAgent,
                WriterAgent,
                ReviewerAgent
            )
            
            agents.append(ResearcherAgent())
            agents.append(WriterAgent())
            agents.append(ReviewerAgent())
            
        except ImportError:
            pass
            
        return agents
        
    def _get_agent_by_role(self, role: str) -> Any:
        """根据角色获取智能体"""
        role_map = {
            'researcher': 0,
            'writer': 1,
            'reviewer': 2
        }
        
        if self._agents and role in role_map:
            idx = role_map[role]
            if idx < len(self._agents):
                agent = self._agents[idx]
                return agent.get_agent() if hasattr(agent, 'get_agent') else agent
                
        return None
        
    def write(self, topic: str, length: str = "medium") -> str:
        """
        执行写作（简化接口）
        
        Args:
            topic: 写作主题
            length: 内容长度
            
        Returns:
            写作结果
        """
        result = self.execute({
            'topic': topic,
            'style': self.style,
            'length': length
        })
        return result.output or ""


# 注册工作流
from .base_workflow import WorkflowRegistry
WorkflowRegistry.register('content', ContentWorkflow)

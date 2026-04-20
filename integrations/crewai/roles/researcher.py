"""
CrewAI 研究员角色

专门负责信息搜索、分析和整理的智能体。
"""

from typing import List, Any, Optional
from .base_role import BaseAgent, AgentConfig, AgentRole, AgentFactory


class ResearcherAgent(BaseAgent):
    """
    研究员智能体
    
    负责搜索、收集、分析和整理信息。
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        初始化研究员智能体
        
        Args:
            config: 可选配置，默认使用研究员默认配置
        """
        if config is None:
            config = AgentConfig(
                role=AgentRole.RESEARCHER,
                goal="搜索、分析和整理信息，提供准确的研究结果",
                backstory="""你是一个经验丰富的研究员，擅长从各种来源收集和验证信息。
                你具有以下特点：
                - 注重信息的准确性和可靠性
                - 善于从多个角度分析问题
                - 能够快速识别关键信息
                - 擅长总结和归纳复杂内容""",
                verbose=True,
                allow_delegation=False,
                memory=True
            )
        super().__init__(config)
        
    def create_agent(self) -> Any:
        """
        创建 CrewAI Agent 实例
        
        Returns:
            CrewAI Agent 对象
        """
        try:
            from crewai import Agent
            
            agent = Agent(
                role=self.config.role.value,
                goal=self.config.goal,
                backstory=self.config.backstory,
                verbose=self.config.verbose,
                allow_delegation=self.config.allow_delegation,
                max_iter=self.config.max_iter,
                max_rpm=self.config.max_rpm,
                memory=self.config.memory,
                tools=self.get_tools()
            )
            return agent
            
        except ImportError:
            # CrewAI 未安装时返回模拟对象
            return self._create_mock_agent()
            
    def _create_mock_agent(self) -> dict:
        """创建模拟智能体（用于测试）"""
        return {
            "role": self.config.role.value,
            "goal": self.config.goal,
            "backstory": self.config.backstory,
            "tools": self._tools
        }
        
    def get_tools(self) -> List[Any]:
        """
        获取研究员可用工具
        
        研究员通常需要：
        - 搜索工具（Web 搜索、知识库搜索）
        - 文档读取工具
        - 信息提取工具
        """
        if not self._tools:
            self._tools = self._create_default_tools()
        return self._tools
        
    def _create_default_tools(self) -> List[Any]:
        """创建默认工具集"""
        tools = []
        
        try:
            from crewai_tools import (
                SerperDevTool,
                ScrapeWebsiteTool,
                FileReadTool
            )
            
            # 搜索工具
            tools.append(SerperDevTool())
            
            # 网页抓取工具
            tools.append(ScrapeWebsiteTool())
            
            # 文件读取工具
            tools.append(FileReadTool())
            
        except ImportError:
            # 工具未安装时跳过
            pass
            
        return tools
        
    def research(self, topic: str, depth: str = "medium") -> str:
        """
        执行研究任务
        
        Args:
            topic: 研究主题
            depth: 研究深度 (shallow/medium/deep)
            
        Returns:
            研究结果
        """
        depth_prompts = {
            "shallow": "提供简要概述",
            "medium": "提供详细分析",
            "deep": "提供全面深入的分析，包括多个视角"
        }
        
        prompt = f"""
请研究主题：{topic}

研究深度：{depth_prompts.get(depth, depth_prompts['medium'])}

要求：
1. 收集相关信息
2. 验证信息准确性
3. 整理并总结关键发现
4. 注明信息来源
"""
        return prompt


# 注册到工厂
AgentFactory.register(AgentRole.RESEARCHER, ResearcherAgent)

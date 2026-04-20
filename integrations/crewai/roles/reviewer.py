"""
CrewAI 审核者角色

专门负责内容审核、质量把关的智能体。
"""

from typing import List, Any, Optional
from .base_role import BaseAgent, AgentConfig, AgentRole, AgentFactory


class ReviewerAgent(BaseAgent):
    """
    审核者智能体
    
    负责审核内容质量，提出改进建议。
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        初始化审核者智能体
        
        Args:
            config: 可选配置，默认使用审核者默认配置
        """
        if config is None:
            config = AgentConfig(
                role=AgentRole.REVIEWER,
                goal="审核和改进内容，确保质量和准确性",
                backstory="""你是一个严谨的审核者，擅长发现问题和提出改进建议。
                你具有以下特点：
                - 注重细节和质量
                - 能够从多角度评估内容
                - 提供建设性的反馈意见
                - 确保内容的准确性和完整性""",
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
        获取审核者可用工具
        
        审核者通常需要：
        - 内容分析工具
        - 语法检查工具
        - 事实核查工具
        """
        if not self._tools:
            self._tools = self._create_default_tools()
        return self._tools
        
    def _create_default_tools(self) -> List[Any]:
        """创建默认工具集"""
        tools = []
        
        try:
            from crewai_tools import FileReadTool
            
            tools.append(FileReadTool())
            
        except ImportError:
            pass
            
        return tools
        
    def review(self, content: str, criteria: Optional[List[str]] = None) -> str:
        """
        执行审核任务
        
        Args:
            content: 待审核内容
            criteria: 审核标准列表
            
        Returns:
            审核提示
        """
        default_criteria = [
            "内容准确性",
            "逻辑连贯性",
            "语言表达",
            "结构完整性",
            "可读性"
        ]
        
        review_criteria = criteria or default_criteria
        
        prompt = f"""
请审核以下内容：

{content}

审核标准：
{chr(10).join(f'- {c}' for c in review_criteria)}

要求：
1. 对每个标准进行评分（1-10分）
2. 指出具体问题
3. 提供改进建议
4. 总结整体质量
"""
        return prompt


# 注册到工厂
AgentFactory.register(AgentRole.REVIEWER, ReviewerAgent)

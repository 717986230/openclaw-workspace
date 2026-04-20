"""
CrewAI 写作者角色

专门负责内容创作、编辑和优化的智能体。
"""

from typing import List, Any, Optional
from .base_role import BaseAgent, AgentConfig, AgentRole, AgentFactory


class WriterAgent(BaseAgent):
    """
    写作者智能体
    
    负责创作、编辑和优化各种类型的内容。
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        初始化写作者智能体
        
        Args:
            config: 可选配置，默认使用写作者默认配置
        """
        if config is None:
            config = AgentConfig(
                role=AgentRole.WRITER,
                goal="创作高质量的内容，包括文章、报告和文档",
                backstory="""你是一个专业的写作者，擅长将复杂信息转化为清晰易懂的内容。
                你具有以下特点：
                - 文字表达能力强
                - 善于组织内容结构
                - 注重内容的可读性和吸引力
                - 能够适应不同的写作风格和受众""",
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
        获取写作者可用工具
        
        写作者通常需要：
        - 文档读写工具
        - 格式转换工具
        - 语法检查工具
        """
        if not self._tools:
            self._tools = self._create_default_tools()
        return self._tools
        
    def _create_default_tools(self) -> List[Any]:
        """创建默认工具集"""
        tools = []
        
        try:
            from crewai_tools import (
                FileReadTool,
                DirectoryReadTool
            )
            
            # 文件读取工具
            tools.append(FileReadTool())
            
            # 目录读取工具
            tools.append(DirectoryReadTool())
            
        except ImportError:
            pass
            
        return tools
        
    def write(self, topic: str, style: str = "professional", length: str = "medium") -> str:
        """
        执行写作任务
        
        Args:
            topic: 写作主题
            style: 写作风格 (professional/casual/academic)
            length: 内容长度 (short/medium/long)
            
        Returns:
            写作提示
        """
        style_guides = {
            "professional": "使用专业、正式的语言风格",
            "casual": "使用轻松、易懂的语言风格",
            "academic": "使用学术、严谨的语言风格"
        }
        
        length_guides = {
            "short": "控制在 500 字以内",
            "medium": "控制在 500-1500 字",
            "long": "可以超过 1500 字"
        }
        
        prompt = f"""
请撰写关于 {topic} 的内容。

写作风格：{style_guides.get(style, style_guides['professional'])}

内容长度：{length_guides.get(length, length_guides['medium'])}

要求：
1. 内容结构清晰，逻辑连贯
2. 语言表达准确，易于理解
3. 包含必要的例子或数据支撑
4. 注意受众的接受程度
"""
        return prompt


# 注册到工厂
AgentFactory.register(AgentRole.WRITER, WriterAgent)

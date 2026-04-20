"""
CrewAI 基础角色类

提供 OpenClaw 中 CrewAI 智能体的基础抽象。
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class AgentRole(Enum):
    """智能体角色枚举"""
    RESEARCHER = "researcher"
    WRITER = "writer"
    REVIEWER = "reviewer"
    ANALYZER = "analyzer"
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"


@dataclass
class AgentConfig:
    """智能体配置"""
    role: AgentRole
    goal: str
    backstory: str
    verbose: bool = True
    allow_delegation: bool = False
    max_iter: int = 15
    max_rpm: Optional[int] = None
    memory: bool = True
    tools: List[Any] = field(default_factory=list)
    
    
class BaseAgent(ABC):
    """
    基础智能体抽象类
    
    所有 CrewAI 智能体都应继承此类，实现具体的角色逻辑。
    """
    
    def __init__(self, config: AgentConfig):
        """
        初始化智能体
        
        Args:
            config: 智能体配置
        """
        self.config = config
        self._agent = None
        self._tools = []
        
    @abstractmethod
    def create_agent(self) -> Any:
        """
        创建 CrewAI Agent 实例
        
        Returns:
            CrewAI Agent 对象
        """
        pass
        
    @abstractmethod
    def get_tools(self) -> List[Any]:
        """
        获取智能体可用工具
        
        Returns:
            工具列表
        """
        pass
        
    def get_agent(self) -> Any:
        """
        获取或创建 Agent 实例
        
        Returns:
            CrewAI Agent 对象
        """
        if self._agent is None:
            self._agent = self.create_agent()
        return self._agent
        
    def add_tool(self, tool: Any) -> None:
        """
        添加工具到智能体
        
        Args:
            tool: 要添加的工具
        """
        self._tools.append(tool)
        
    def set_tools(self, tools: List[Any]) -> None:
        """
        设置智能体工具列表
        
        Args:
            tools: 工具列表
        """
        self._tools = tools
        
    def get_role_prompt(self) -> str:
        """
        获取角色提示词
        
        Returns:
            角色提示字符串
        """
        return f"""
你是一个 {self.config.role.value}。

目标：{self.config.goal}

背景：{self.config.backstory}

请根据你的角色特点完成任务。
"""
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(role={self.config.role.value})"


class AgentFactory:
    """智能体工厂类"""
    
    _registry: Dict[AgentRole, type] = {}
    
    @classmethod
    def register(cls, role: AgentRole, agent_class: type) -> None:
        """
        注册智能体类
        
        Args:
            role: 角色类型
            agent_class: 智能体类
        """
        cls._registry[role] = agent_class
        
    @classmethod
    def create(cls, role: AgentRole, config: Optional[AgentConfig] = None) -> BaseAgent:
        """
        创建智能体实例
        
        Args:
            role: 角色类型
            config: 可选配置，如不提供则使用默认
            
        Returns:
            智能体实例
            
        Raises:
            ValueError: 未注册的角色
        """
        if role not in cls._registry:
            raise ValueError(f"未注册的角色: {role}")
            
        agent_class = cls._registry[role]
        
        if config is None:
            config = cls._get_default_config(role)
            
        return agent_class(config)
        
    @classmethod
    def _get_default_config(cls, role: AgentRole) -> AgentConfig:
        """获取角色默认配置"""
        default_configs = {
            AgentRole.RESEARCHER: AgentConfig(
                role=AgentRole.RESEARCHER,
                goal="搜索、分析和整理信息，提供准确的研究结果",
                backstory="你是一个经验丰富的研究员，擅长从各种来源收集和验证信息。"
            ),
            AgentRole.WRITER: AgentConfig(
                role=AgentRole.WRITER,
                goal="创作高质量的内容，包括文章、报告和文档",
                backstory="你是一个专业的写作者，擅长将复杂信息转化为清晰易懂的内容。"
            ),
            AgentRole.REVIEWER: AgentConfig(
                role=AgentRole.REVIEWER,
                goal="审核和改进内容，确保质量和准确性",
                backstory="你是一个严谨的审核者，擅长发现问题和提出改进建议。"
            ),
            AgentRole.ANALYZER: AgentConfig(
                role=AgentRole.ANALYZER,
                goal="分析数据和趋势，提供洞察和建议",
                backstory="你是一个数据分析专家，擅长从数据中发现模式和趋势。"
            ),
            AgentRole.COORDINATOR: AgentConfig(
                role=AgentRole.COORDINATOR,
                goal="协调团队成员，确保任务顺利完成",
                backstory="你是一个出色的协调者，擅长管理团队和分配任务。"
            ),
            AgentRole.EXECUTOR: AgentConfig(
                role=AgentRole.EXECUTOR,
                goal="执行具体任务，交付成果",
                backstory="你是一个高效的执行者，擅长将计划转化为实际成果。"
            )
        }
        return default_configs.get(role, AgentConfig(
            role=role,
            goal="完成任务",
            backstory="你是一个通用智能体。"
        ))

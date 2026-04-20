"""
基础角色类

所有角色的基类，定义了角色的通用属性和方法。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Message:
    """角色间通信的标准消息格式"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: str = ""  # 发送者角色
    content: str = ""  # 消息内容
    cause_by: str = ""  # 触发原因
    send_to: str = ""  # 接收者
    state: str = "pending"  # pending, processing, completed, failed
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "cause_by": self.cause_by,
            "send_to": self.send_to,
            "state": self.state,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Action:
    """角色可执行的动作"""
    
    name: str
    description: str
    inputs: List[str]  # 输入参数
    outputs: List[str]  # 输出参数
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    

class Role(ABC):
    """
    角色基类
    
    所有具体角色（产品经理、架构师、工程师等）都继承自此类。
    """
    
    def __init__(
        self,
        name: str,
        profile: str,
        goal: str,
        constraints: Optional[List[str]] = None
    ):
        """
        初始化角色
        
        Args:
            name: 角色名称
            profile: 角色描述/简介
            goal: 角色目标
            constraints: 约束条件列表
        """
        self.name = name
        self.profile = profile
        self.goal = goal
        self.constraints = constraints or []
        self.actions: List[Action] = []
        self._message_queue: List[Message] = []
        self._state: str = "idle"  # idle, busy, waiting
        
    @abstractmethod
    async def _observe(self) -> None:
        """
        观察环境，接收消息
        
        子类需要实现具体的观察逻辑。
        """
        pass
    
    @abstractmethod
    async def _react(self) -> Message:
        """
        对观察到的内容做出反应
        
        子类需要实现具体的反应逻辑。
        
        Returns:
            反应产生的消息
        """
        pass
    
    async def run(self) -> Optional[Message]:
        """
        运行角色的主循环
        
        Returns:
            产生的消息，如果没有则返回 None
        """
        self._state = "busy"
        
        try:
            # 观察环境
            await self._observe()
            
            # 做出反应
            message = await self._react()
            
            return message
            
        finally:
            self._state = "idle"
    
    def receive_message(self, message: Message) -> None:
        """
        接收消息
        
        Args:
            message: 接收到的消息
        """
        self._message_queue.append(message)
    
    def get_pending_messages(self) -> List[Message]:
        """
        获取待处理的消息
        
        Returns:
            待处理消息列表
        """
        return [msg for msg in self._message_queue if msg.state == "pending"]
    
    def add_action(self, action: Action) -> None:
        """
        添加动作
        
        Args:
            action: 要添加的动作
        """
        self.actions.append(action)
    
    def get_profile(self) -> Dict[str, Any]:
        """
        获取角色档案信息
        
        Returns:
            角色档案字典
        """
        return {
            "name": self.name,
            "profile": self.profile,
            "goal": self.goal,
            "constraints": self.constraints,
            "actions": [action.name for action in self.actions],
            "state": self._state
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"

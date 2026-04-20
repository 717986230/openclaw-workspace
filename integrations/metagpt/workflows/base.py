"""
基础工作流类

所有工作流的基类。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import asyncio


@dataclass
class WorkflowState:
    """工作流状态"""
    name: str
    current_step: int = 0
    total_steps: int = 0
    status: str = "idle"  # idle, running, paused, completed, failed
    error: Optional[str] = None


class Workflow(ABC):
    """
    工作流基类
    
    所有具体工作流都继承自此类。
    """
    
    def __init__(self, name: str):
        """
        初始化工作流
        
        Args:
            name: 工作流名称
        """
        self.name = name
        self.state = WorkflowState(name=name)
        self._steps: List[Dict[str, Any]] = []
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> Any:
        """
        运行工作流
        
        子类必须实现此方法。
        """
        pass
    
    def add_step(
        self,
        name: str,
        action: callable,
        preconditions: Optional[List[callable]] = None,
        postconditions: Optional[List[callable]] = None
    ) -> None:
        """
        添加工作流步骤
        
        Args:
            name: 步骤名称
            action: 步骤动作
            preconditions: 前置条件列表
            postconditions: 后置条件列表
        """
        self._steps.append({
            "name": name,
            "action": action,
            "preconditions": preconditions or [],
            "postconditions": postconditions or []
        })
        self.state.total_steps = len(self._steps)
    
    async def execute_step(self, step_index: int, *args, **kwargs) -> Any:
        """
        执行单个步骤
        
        Args:
            step_index: 步骤索引
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            步骤执行结果
        """
        if step_index >= len(self._steps):
            raise IndexError(f"Step index {step_index} out of range")
        
        step = self._steps[step_index]
        
        # 检查前置条件
        for precondition in step.get("preconditions", []):
            if not await precondition():
                raise RuntimeError(f"Precondition failed for step {step['name']}")
        
        # 执行步骤
        self.state.current_step = step_index
        self.state.status = "running"
        
        try:
            result = await step["action"](*args, **kwargs)
            
            # 检查后置条件
            for postcondition in step.get("postconditions", []):
                if not await postcondition(result):
                    raise RuntimeError(f"Postcondition failed for step {step['name']}")
            
            return result
            
        except Exception as e:
            self.state.status = "failed"
            self.state.error = str(e)
            raise
    
    async def pause(self) -> None:
        """暂停工作流"""
        self.state.status = "paused"
    
    async def resume(self) -> None:
        """恢复工作流"""
        self.state.status = "running"
    
    async def stop(self) -> None:
        """停止工作流"""
        self.state.status = "stopped"
    
    def get_progress(self) -> Dict[str, Any]:
        """
        获取工作流进度
        
        Returns:
            进度信息
        """
        return {
            "name": self.name,
            "current_step": self.state.current_step,
            "total_steps": self.state.total_steps,
            "status": self.state.status,
            "error": self.state.error,
            "progress_percent": (
                (self.state.current_step / self.state.total_steps * 100)
                if self.state.total_steps > 0 else 0
            )
        }

"""
CrewAI 基础工作流

定义工作流的基础抽象类和通用组件。
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Type
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """工作流状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessType(Enum):
    """执行流程类型"""
    SEQUENTIAL = "sequential"      # 顺序执行
    HIERARCHICAL = "hierarchical"  # 层级执行（管理者分配）
    CONSENSUAL = "consensual"      # 协商执行（共同决策)


@dataclass
class WorkflowConfig:
    """工作流配置"""
    name: str
    description: str = ""
    process_type: ProcessType = ProcessType.SEQUENTIAL
    max_agents: int = 5
    timeout: int = 600  # 秒
    max_retries: int = 3
    verbose: bool = True
    memory: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """工作流结果"""
    workflow_id: str
    status: WorkflowStatus
    output: Optional[str] = None
    task_results: List[Dict[str, Any]] = field(default_factory=list)
    execution_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseWorkflow(ABC):
    """
    基础工作流抽象类
    
    所有工作流都应继承此类，实现具体的执行逻辑。
    """
    
    def __init__(self, config: WorkflowConfig):
        """
        初始化工作流
        
        Args:
            config: 工作流配置
        """
        self.config = config
        self._crew = None
        self._status = WorkflowStatus.PENDING
        
    @abstractmethod
    def create_crew(self) -> Any:
        """
        创建 CrewAI Crew 实例
        
        Returns:
            CrewAI Crew 对象
        """
        pass
        
    @abstractmethod
    def create_tasks(self) -> List[Any]:
        """
        创建任务列表
        
        Returns:
            任务列表
        """
        pass
        
    def get_crew(self) -> Any:
        """
        获取或创建 Crew 实例
        
        Returns:
            CrewAI Crew 对象
        """
        if self._crew is None:
            self._crew = self.create_crew()
        return self._crew
        
    def execute(self, inputs: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """
        同步执行工作流
        
        Args:
            inputs: 输入参数
            
        Returns:
            工作流结果
        """
        import time
        start_time = time.time()
        workflow_id = f"wf_{int(start_time * 1000)}"
        
        try:
            self._status = WorkflowStatus.RUNNING
            
            # 获取 Crew 和 Tasks
            crew = self.get_crew()
            tasks = self.create_tasks()
            
            # 执行
            result = self._execute_crew(crew, tasks, inputs or {})
            
            self._status = WorkflowStatus.COMPLETED
            
            return WorkflowResult(
                workflow_id=workflow_id,
                status=WorkflowStatus.COMPLETED,
                output=str(result),
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self._status = WorkflowStatus.FAILED
            logger.error(f"工作流执行失败: {e}")
            
            return WorkflowResult(
                workflow_id=workflow_id,
                status=WorkflowStatus.FAILED,
                error=str(e),
                execution_time=time.time() - start_time
            )
            
    async def execute_async(self, inputs: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """
        异步执行工作流
        
        Args:
            inputs: 输入参数
            
        Returns:
            工作流结果
        """
        import time
        start_time = time.time()
        workflow_id = f"wf_{int(start_time * 1000)}"
        
        try:
            self._status = WorkflowStatus.RUNNING
            
            # 在线程池中执行（CrewAI 目前主要是同步）
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.execute(inputs)
            )
            
            return result
            
        except Exception as e:
            self._status = WorkflowStatus.FAILED
            
            return WorkflowResult(
                workflow_id=workflow_id,
                status=WorkflowStatus.FAILED,
                error=str(e),
                execution_time=time.time() - start_time
            )
            
    def _execute_crew(
        self,
        crew: Any,
        tasks: List[Any],
        inputs: Dict[str, Any]
    ) -> Any:
        """
        执行 Crew（实际调用 CrewAI）
        
        Args:
            crew: Crew 实例
            tasks: 任务列表
            inputs: 输入参数
            
        Returns:
            执行结果
        """
        try:
            # 尝试使用 CrewAI
            from crewai import Crew
            
            if isinstance(crew, Crew):
                return crew.kickoff(inputs=inputs)
            else:
                # 模拟执行
                return self._mock_execution(tasks, inputs)
                
        except ImportError:
            # CrewAI 未安装，使用模拟
            return self._mock_execution(tasks, inputs)
            
    def _mock_execution(
        self,
        tasks: List[Any],
        inputs: Dict[str, Any]
    ) -> str:
        """
        模拟执行（用于测试）
        
        Args:
            tasks: 任务列表
            inputs: 输入参数
            
        Returns:
            模拟结果
        """
        return f"工作流 '{self.config.name}' 执行完成，任务数: {len(tasks)}"
        
    def cancel(self) -> bool:
        """
        取消工作流执行
        
        Returns:
            是否成功取消
        """
        if self._status == WorkflowStatus.RUNNING:
            self._status = WorkflowStatus.CANCELLED
            return True
        return False
        
    def get_status(self) -> WorkflowStatus:
        """获取工作流状态"""
        return self._status


class WorkflowRegistry:
    """工作流注册表"""
    
    _workflows: Dict[str, Type[BaseWorkflow]] = {}
    
    @classmethod
    def register(cls, name: str, workflow_class: Type[BaseWorkflow]) -> None:
        """
        注册工作流
        
        Args:
            name: 工作流名称
            workflow_class: 工作流类
        """
        cls._workflows[name] = workflow_class
        
    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseWorkflow]]:
        """
        获取已注册的工作流类
        
        Args:
            name: 工作流名称
            
        Returns:
            工作流类，如果不存在返回 None
        """
        return cls._workflows.get(name)
        
    @classmethod
    def list_workflows(cls) -> List[str]:
        """列出所有已注册的工作流"""
        return list(cls._workflows.keys())

"""
CrewAI 任务管理器

统一管理任务的创建、分配、执行和监控。
"""

from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import uuid
import threading
import time
import logging

from .task_types import (
    TaskDefinition,
    TaskResult,
    TaskType,
    TaskPriority,
    TaskStatus,
    TASK_TEMPLATES
)
from .task_queue import TaskQueue, TaskDependencyGraph


logger = logging.getLogger(__name__)


class TaskManager:
    """
    任务管理器
    
    负责：
    - 任务创建和验证
    - 任务分配和调度
    - 执行监控和错误处理
    - 结果收集和报告
    """
    
    def __init__(
        self,
        max_queue_size: int = 1000,
        enable_tracing: bool = False
    ):
        """
        初始化任务管理器
        
        Args:
            max_queue_size: 队列最大容量
            enable_tracing: 是否启用追踪
        """
        self.queue = TaskQueue(max_size=max_queue_size)
        self.dep_graph = TaskDependencyGraph()
        self.enable_tracing = enable_tracing
        
        self._results: Dict[str, TaskResult] = {}
        self._trace: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        
    def create_task(
        self,
        task_type: TaskType,
        description: str,
        expected_output: str,
        agent_role: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None,
        **kwargs
    ) -> TaskDefinition:
        """
        创建新任务
        
        Args:
            task_type: 任务类型
            description: 任务描述
            expected_output: 预期输出
            agent_role: 指定的智能体角色
            priority: 任务优先级
            dependencies: 依赖的任务 ID 列表
            **kwargs: 其他参数
            
        Returns:
            创建的任务定义
        """
        task_id = str(uuid.uuid4())
        
        task = TaskDefinition(
            task_id=task_id,
            task_type=task_type,
            description=description,
            expected_output=expected_output,
            agent_role=agent_role,
            priority=priority,
            dependencies=dependencies or [],
            **kwargs
        )
        
        # 添加到依赖图
        self.dep_graph.add_task(task)
        
        return task
        
    def create_from_template(
        self,
        template_name: str,
        **kwargs
    ) -> TaskDefinition:
        """
        从模板创建任务
        
        Args:
            template_name: 模板名称
            **kwargs: 模板参数
            
        Returns:
            创建的任务定义
            
        Raises:
            ValueError: 模板不存在
        """
        if template_name not in TASK_TEMPLATES:
            raise ValueError(f"未知的任务模板: {template_name}")
            
        template = TASK_TEMPLATES[template_name]
        task_id = str(uuid.uuid4())
        
        task = template.create_task(task_id, **kwargs)
        
        # 添加到依赖图
        self.dep_graph.add_task(task)
        
        return task
        
    def submit_task(self, task: TaskDefinition) -> bool:
        """
        提交任务到队列
        
        Args:
            task: 任务定义
            
        Returns:
            是否成功提交
        """
        success = self.queue.enqueue(task)
        
        if success and self.enable_tracing:
            self._add_trace('submit', task.task_id, {
                'type': task.task_type.value,
                'priority': task.priority.value
            })
            
        return success
        
    def delegate_task(
        self,
        task_type: str,
        description: str,
        priority: str = "medium",
        agent_role: Optional[str] = None
    ) -> TaskResult:
        """
        委托任务（简化接口）
        
        Args:
            task_type: 任务类型字符串
            description: 任务描述
            priority: 优先级字符串
            agent_role: 指定角色
            
        Returns:
            任务结果
        """
        # 转换类型
        task_type_enum = TaskType(task_type) if task_type in [t.value for t in TaskType] else TaskType.CUSTOM
        priority_enum = TaskPriority(priority) if priority in [p.value for p in TaskPriority] else TaskPriority.MEDIUM
        
        # 创建任务
        task = self.create_task(
            task_type=task_type_enum,
            description=description,
            expected_output="根据任务描述完成相应工作",
            agent_role=agent_role,
            priority=priority_enum
        )
        
        # 提交并执行
        self.submit_task(task)
        
        # 模拟执行（实际应调用 CrewAI）
        return self._execute_task(task)
        
    def _execute_task(self, task: TaskDefinition) -> TaskResult:
        """
        执行单个任务
        
        Args:
            task: 任务定义
            
        Returns:
            任务结果
        """
        start_time = time.time()
        
        try:
            # 这里应该调用实际的 CrewAI 执行逻辑
            # 目前返回模拟结果
            
            result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                output=f"已完成任务: {task.description}",
                execution_time=time.time() - start_time,
                metadata={'task_type': task.task_type.value}
            )
            
            if self.enable_tracing:
                self._add_trace('execute', task.task_id, {
                    'status': 'completed',
                    'time': result.execution_time
                })
                
        except Exception as e:
            result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                execution_time=time.time() - start_time
            )
            
            if self.enable_tracing:
                self._add_trace('execute', task.task_id, {
                    'status': 'failed',
                    'error': str(e)
                })
                
        with self._lock:
            self._results[task.task_id] = result
            
        return result
        
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """
        获取任务结果
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务结果，如果不存在返回 None
        """
        with self._lock:
            return self._results.get(task_id)
            
    def get_next_task(self) -> Optional[TaskDefinition]:
        """
        获取下一个可执行任务
        
        Returns:
            任务定义，如果队列为空返回 None
        """
        # 检查依赖是否满足
        completed = list(self._results.keys())
        
        while True:
            task = self.queue.dequeue()
            if task is None:
                return None
                
            # 检查依赖
            if all(dep in completed for dep in task.dependencies):
                return task
            else:
                # 重新入队（简化处理）
                self.queue.enqueue(task)
                return None
                
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否成功取消
        """
        success = self.queue.remove(task_id)
        
        if success and self.enable_tracing:
            self._add_trace('cancel', task_id, {})
            
        return success
        
    def get_queue_stats(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        return self.queue.get_stats()
        
    def get_trace(self) -> List[Dict[str, Any]]:
        """获取执行轨迹"""
        with self._lock:
            return self._trace.copy()
            
    def _add_trace(self, action: str, task_id: str, data: Dict[str, Any]) -> None:
        """添加追踪记录"""
        with self._lock:
            self._trace.append({
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'task_id': task_id,
                'data': data
            })
            
    def clear_trace(self) -> None:
        """清空追踪记录"""
        with self._lock:
            self._trace.clear()

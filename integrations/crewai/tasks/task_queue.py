"""
CrewAI 任务队列

管理任务的排队、调度和执行。
"""

from typing import Optional, List, Dict, Any
from collections import deque
from datetime import datetime
import threading
import heapq

from .task_types import TaskDefinition, TaskResult, TaskPriority, TaskStatus


class TaskQueue:
    """
    优先级任务队列
    
    支持按优先级排序的任务队列，提供任务的添加、获取和管理功能。
    """
    
    def __init__(self, max_size: int = 1000):
        """
        初始化任务队列
        
        Args:
            max_size: 队列最大容量
        """
        self.max_size = max_size
        self._queue: List[tuple] = []  # (priority_counter, task)
        self._counter = 0  # 用于同优先级的 FIFO 排序
        self._lock = threading.Lock()
        self._task_index: Dict[str, TaskDefinition] = {}  # 快速查找
        
        # 优先级映射（数值越小优先级越高）
        self._priority_map = {
            TaskPriority.URGENT: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        
    def enqueue(self, task: TaskDefinition) -> bool:
        """
        将任务加入队列
        
        Args:
            task: 任务定义
            
        Returns:
            是否成功加入
        """
        with self._lock:
            if len(self._queue) >= self.max_size:
                return False
                
            priority_value = self._priority_map.get(task.priority, 2)
            self._counter += 1
            
            heapq.heappush(self._queue, (priority_value, self._counter, task))
            self._task_index[task.task_id] = task
            
            return True
            
    def dequeue(self) -> Optional[TaskDefinition]:
        """
        从队列取出最高优先级任务
        
        Returns:
            任务定义，如果队列为空返回 None
        """
        with self._lock:
            if not self._queue:
                return None
                
            _, _, task = heapq.heappop(self._queue)
            del self._task_index[task.task_id]
            return task
            
    def peek(self) -> Optional[TaskDefinition]:
        """
        查看队首任务但不取出
        
        Returns:
            任务定义，如果队列为空返回 None
        """
        with self._lock:
            if not self._queue:
                return None
            return self._queue[0][2]
            
    def get_by_id(self, task_id: str) -> Optional[TaskDefinition]:
        """
        根据 ID 获取任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务定义，如果不存在返回 None
        """
        with self._lock:
            return self._task_index.get(task_id)
            
    def remove(self, task_id: str) -> bool:
        """
        从队列移除任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否成功移除
        """
        with self._lock:
            if task_id not in self._task_index:
                return False
                
            # 标记为已删除（堆中保留但标记删除）
            task = self._task_index[task_id]
            task.metadata['_deleted'] = True
            del self._task_index[task_id]
            return True
            
    def update_priority(self, task_id: str, priority: TaskPriority) -> bool:
        """
        更新任务优先级
        
        Args:
            task_id: 任务 ID
            priority: 新优先级
            
        Returns:
            是否成功更新
        """
        with self._lock:
            if task_id not in self._task_index:
                return False
                
            # 简单实现：移除旧任务，重新入队
            task = self._task_index[task_id]
            self.remove(task_id)
            
            task.priority = priority
            self.enqueue(task)
            return True
            
    def size(self) -> int:
        """获取队列大小"""
        with self._lock:
            return len(self._queue)
            
    def is_empty(self) -> bool:
        """队列是否为空"""
        with self._lock:
            return len(self._queue) == 0
            
    def clear(self) -> None:
        """清空队列"""
        with self._lock:
            self._queue.clear()
            self._task_index.clear()
            self._counter = 0
            
    def get_all_tasks(self) -> List[TaskDefinition]:
        """获取所有任务（按优先级排序）"""
        with self._lock:
            return [task for _, _, task in sorted(self._queue)]
            
    def get_stats(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        with self._lock:
            stats = {
                'total': len(self._queue),
                'max_size': self.max_size,
                'by_priority': {}
            }
            
            for priority in TaskPriority:
                count = sum(1 for _, _, task in self._queue 
                           if task.priority == priority)
                stats['by_priority'][priority.value] = count
                
            return stats


class TaskDependencyGraph:
    """
    任务依赖图
    
    管理任务之间的依赖关系，确保按正确顺序执行。
    """
    
    def __init__(self):
        """初始化依赖图"""
        self._dependencies: Dict[str, List[str]] = {}  # task_id -> 依赖的任务列表
        self._dependents: Dict[str, List[str]] = {}    # task_id -> 依赖此任务的任务列表
        self._lock = threading.Lock()
        
    def add_task(self, task: TaskDefinition) -> None:
        """
        添加任务及其依赖关系
        
        Args:
            task: 任务定义
        """
        with self._lock:
            # 添加依赖关系
            self._dependencies[task.task_id] = task.dependencies.copy()
            
            # 更新反向依赖
            for dep_id in task.dependencies:
                if dep_id not in self._dependents:
                    self._dependents[dep_id] = []
                self._dependents[dep_id].append(task.task_id)
                
    def remove_task(self, task_id: str) -> None:
        """
        移除任务
        
        Args:
            task_id: 任务 ID
        """
        with self._lock:
            # 从依赖列表中移除
            if task_id in self._dependencies:
                for dep_id in self._dependencies[task_id]:
                    if dep_id in self._dependents:
                        self._dependents[dep_id].remove(task_id)
                del self._dependencies[task_id]
                
            # 从被依赖列表中移除
            if task_id in self._dependents:
                for dep_id in self._dependents[task_id]:
                    if dep_id in self._dependencies:
                        self._dependencies[dep_id].remove(task_id)
                del self._dependents[task_id]
                
    def get_ready_tasks(self, completed_tasks: List[str]) -> List[str]:
        """
        获取可以执行的任务（依赖已满足）
        
        Args:
            completed_tasks: 已完成的任务 ID 列表
            
        Returns:
            可执行的任务 ID 列表
        """
        with self._lock:
            ready = []
            completed_set = set(completed_tasks)
            
            for task_id, deps in self._dependencies.items():
                if task_id not in completed_set:
                    if all(dep in completed_set for dep in deps):
                        ready.append(task_id)
                        
            return ready
            
    def has_cycle(self) -> bool:
        """
        检测是否存在循环依赖
        
        Returns:
            是否存在循环依赖
        """
        with self._lock:
            visited = set()
            rec_stack = set()
            
            def dfs(task_id: str) -> bool:
                visited.add(task_id)
                rec_stack.add(task_id)
                
                for dep_id in self._dependencies.get(task_id, []):
                    if dep_id not in visited:
                        if dfs(dep_id):
                            return True
                    elif dep_id in rec_stack:
                        return True
                        
                rec_stack.remove(task_id)
                return False
                
            for task_id in self._dependencies:
                if task_id not in visited:
                    if dfs(task_id):
                        return True
                        
            return False

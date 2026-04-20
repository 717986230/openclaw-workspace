"""
AutoGPT Task Dependency Manager
任务依赖关系管理
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import logging

from .task_planner import Task, TaskStatus, Plan

logger = logging.getLogger(__name__)


@dataclass
class DependencyNode:
    """依赖关系节点"""
    task_id: str
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    
    def add_dependency(self, task_id: str):
        """添加依赖"""
        self.dependencies.add(task_id)
    
    def add_dependent(self, task_id: str):
        """添加被依赖"""
        self.dependents.add(task_id)
    
    def remove_dependency(self, task_id: str):
        """移除依赖"""
        self.dependencies.discard(task_id)
    
    def remove_dependent(self, task_id: str):
        """移除被依赖"""
        self.dependents.discard(task_id)


@dataclass
class DependencyCycle:
    """依赖环"""
    cycle_tasks: List[str]
    
    def __str__(self) -> str:
        return " -> ".join(self.cycle_tasks)


class TaskDependencyManager:
    """
    任务依赖关系管理器
    
    负责：
    - 维护任务依赖图
    - 检测依赖环
    - 计算执行顺序
    - 分析依赖影响
    """
    
    def __init__(self):
        """初始化依赖管理器"""
        self.nodes: Dict[str, DependencyNode] = {}
        self._dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_graph: Dict[str, Set[str]] = defaultdict(set)
    
    def add_task(self, task: Task) -> None:
        """
        添加任务到依赖图
        
        Args:
            task: 要添加的任务
        """
        if task.id in self.nodes:
            logger.warning(f"Task {task.id} already exists in dependency graph")
            return
        
        node = DependencyNode(task_id=task.id)
        
        # 添加依赖关系
        for dep_id in task.dependencies:
            if dep_id in self.nodes:
                node.add_dependency(dep_id)
                self.nodes[dep_id].add_dependent(task.id)
                self._dependency_graph[task.id].add(dep_id)
                self._reverse_graph[dep_id].add(task.id)
        
        self.nodes[task.id] = node
    
    def remove_task(self, task_id: str) -> bool:
        """
        从依赖图中移除任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否成功移除
        """
        if task_id not in self.nodes:
            return False
        
        node = self.nodes[task_id]
        
        # 移除所有依赖关系
        for dep_id in node.dependencies:
            if dep_id in self.nodes:
                self.nodes[dep_id].remove_dependent(task_id)
                self._reverse_graph[dep_id].discard(task_id)
        
        for dependent_id in node.dependents:
            if dependent_id in self.nodes:
                self.nodes[dependent_id].remove_dependency(task_id)
                self._dependency_graph[dependent_id].discard(task_id)
        
        del self.nodes[task_id]
        del self._dependency_graph[task_id]
        
        return True
    
    def add_dependency(self, task_id: str, depends_on: str) -> bool:
        """
        添加依赖关系
        
        Args:
            task_id: 任务 ID
            depends_on: 依赖的任务 ID
            
        Returns:
            是否成功添加（添加后不会形成环）
        """
        if task_id not in self.nodes or depends_on not in self.nodes:
            logger.error(f"One or both tasks not found: {task_id}, {depends_on}")
            return False
        
        # 检查是否会形成环
        if self._would_create_cycle(task_id, depends_on):
            logger.warning(f"Adding dependency would create cycle: {task_id} -> {depends_on}")
            return False
        
        node = self.nodes[task_id]
        node.add_dependency(depends_on)
        self.nodes[depends_on].add_dependent(task_id)
        
        self._dependency_graph[task_id].add(depends_on)
        self._reverse_graph[depends_on].add(task_id)
        
        return True
    
    def remove_dependency(self, task_id: str, depends_on: str) -> bool:
        """
        移除依赖关系
        
        Args:
            task_id: 任务 ID
            depends_on: 依赖的任务 ID
            
        Returns:
            是否成功移除
        """
        if task_id not in self.nodes:
            return False
        
        node = self.nodes[task_id]
        node.remove_dependency(depends_on)
        
        if depends_on in self.nodes:
            self.nodes[depends_on].remove_dependent(task_id)
        
        self._dependency_graph[task_id].discard(depends_on)
        self._reverse_graph[depends_on].discard(task_id)
        
        return True
    
    def detect_cycles(self) -> List[DependencyCycle]:
        """
        检测依赖环
        
        Returns:
            检测到的所有依赖环
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            path.append(task_id)
            
            for dep_id in self._dependency_graph.get(task_id, set()):
                if dep_id not in visited:
                    if dfs(dep_id):
                        return True
                elif dep_id in rec_stack:
                    # 找到环
                    cycle_start = path.index(dep_id)
                    cycle_tasks = path[cycle_start:] + [dep_id]
                    cycles.append(DependencyCycle(cycle_tasks=cycle_tasks))
                    return True
            
            path.pop()
            rec_stack.discard(task_id)
            return False
        
        for task_id in self.nodes:
            if task_id not in visited:
                dfs(task_id)
        
        return cycles
    
    def _would_create_cycle(self, task_id: str, depends_on: str) -> bool:
        """检查添加依赖是否会形成环"""
        # 检查 depends_on 是否可达 task_id
        visited = set()
        queue = [depends_on]
        
        while queue:
            current = queue.pop(0)
            if current == task_id:
                return True
            
            if current in visited:
                continue
            
            visited.add(current)
            queue.extend(self._dependency_graph.get(current, set()))
        
        return False
    
    def topological_sort(self) -> List[str]:
        """
        拓扑排序
        
        Returns:
            排序后的任务 ID 列表
        """
        in_degree: Dict[str, int] = defaultdict(int)
        
        # 计算入度
        for task_id in self.nodes:
            in_degree[task_id] = len(self._dependency_graph[task_id])
        
        # 找出所有入度为 0 的节点
        queue = [task_id for task_id in self.nodes if in_degree[task_id] == 0]
        result = []
        
        while queue:
            # 按任务 ID 排序以保证确定性
            queue.sort()
            current = queue.pop(0)
            result.append(current)
            
            # 减少所有依赖于此节点的节点的入度
            for dependent_id in self._reverse_graph.get(current, set()):
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)
        
        if len(result) != len(self.nodes):
            # 存在环
            cycles = self.detect_cycles()
            logger.error(f"Cannot perform topological sort due to cycles: {cycles}")
            return []
        
        return result
    
    def get_execution_order(self, plan: Plan) -> List[List[str]]:
        """
        获取分层执行顺序
        
        返回可以并行执行的任务层
        
        Args:
            plan: 执行计划
            
        Returns:
            分层的任务 ID 列表，每层可以并行执行
        """
        # 从计划构建依赖图
        self.nodes.clear()
        self._dependency_graph.clear()
        self._reverse_graph.clear()
        
        for task in plan.tasks.values():
            self.add_task(task)
        
        # 分层
        layers: List[List[str]] = []
        completed: Set[str] = set()
        remaining = set(self.nodes.keys())
        
        while remaining:
            # 找出所有依赖已满足的任务
            layer = []
            for task_id in list(remaining):
                deps = self._dependency_graph.get(task_id, set())
                if all(dep in completed for dep in deps):
                    layer.append(task_id)
            
            if not layer:
                # 无法继续，可能存在环
                cycles = self.detect_cycles()
                logger.error(f"Cannot determine execution order, cycles detected: {cycles}")
                break
            
            layer.sort()  # 确保确定性
            layers.append(layer)
            
            for task_id in layer:
                completed.add(task_id)
                remaining.discard(task_id)
        
        return layers
    
    def get_dependencies(self, task_id: str) -> List[str]:
        """
        获取任务的所有依赖
        
        Args:
            task_id: 任务 ID
            
        Returns:
            依赖任务 ID 列表
        """
        if task_id not in self.nodes:
            return []
        
        return list(self.nodes[task_id].dependencies)
    
    def get_dependents(self, task_id: str) -> List[str]:
        """
        获取所有依赖于此任务的任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            依赖此任务的任务 ID 列表
        """
        if task_id not in self.nodes:
            return []
        
        return list(self.nodes[task_id].dependents)
    
    def get_transitive_dependencies(self, task_id: str) -> Set[str]:
        """
        获取传递依赖（所有直接和间接依赖）
        
        Args:
            task_id: 任务 ID
            
        Returns:
            所有传递依赖的集合
        """
        if task_id not in self.nodes:
            return set()
        
        visited = set()
        
        def dfs(current_id: str):
            if current_id in visited:
                return
            visited.add(current_id)
            
            for dep_id in self._dependency_graph.get(current_id, set()):
                dfs(dep_id)
        
        dfs(task_id)
        visited.discard(task_id)  # 排除自身
        
        return visited
    
    def get_transitive_dependents(self, task_id: str) -> Set[str]:
        """
        获取传递被依赖（所有直接和间接依赖于此任务的任务）
        
        Args:
            task_id: 任务 ID
            
        Returns:
            所有传递被依赖的集合
        """
        if task_id not in self.nodes:
            return set()
        
        visited = set()
        
        def dfs(current_id: str):
            if current_id in visited:
                return
            visited.add(current_id)
            
            for dep_id in self._reverse_graph.get(current_id, set()):
                dfs(dep_id)
        
        dfs(task_id)
        visited.discard(task_id)  # 排除自身
        
        return visited
    
    def analyze_impact(self, task_id: str) -> Dict[str, Set[str]]:
        """
        分析任务失败的影响范围
        
        Args:
            task_id: 任务 ID
            
        Returns:
            包含直接影响和间接影响的字典
        """
        if task_id not in self.nodes:
            return {"direct_impact": set(), "indirect_impact": set()}
        
        direct = self.get_dependents(task_id)
        indirect = self.get_transitive_dependents(task_id) - set(direct)
        
        return {
            "direct_impact": set(direct),
            "indirect_impact": indirect
        }
    
    def find_critical_path(self, plan: Plan) -> Tuple[List[str], int]:
        """
        找到关键路径（最长依赖链）
        
        Args:
            plan: 执行计划
            
        Returns:
            (关键路径任务列表, 路径长度)
        """
        # 重建依赖图
        self.nodes.clear()
        self._dependency_graph.clear()
        self._reverse_graph.clear()
        
        for task in plan.tasks.values():
            self.add_task(task)
        
        # 记录到每个节点的最长路径
        longest_path: Dict[str, int] = {task_id: 0 for task_id in self.nodes}
        predecessor: Dict[str, Optional[str]] = {task_id: None for task_id in self.nodes}
        
        # 拓扑顺序处理
        order = self.topological_sort()
        
        for task_id in order:
            for dep_id in self._dependency_graph.get(task_id, set()):
                if longest_path[dep_id] + 1 > longest_path[task_id]:
                    longest_path[task_id] = longest_path[dep_id] + 1
                    predecessor[task_id] = dep_id
        
        # 找到最远节点
        max_length = max(longest_path.values())
        end_task = max(longest_path.keys(), key=lambda x: longest_path[x])
        
        # 回溯构建路径
        path = []
        current: Optional[str] = end_task
        while current is not None:
            path.append(current)
            current = predecessor[current]
        
        path.reverse()
        
        return path, max_length
    
    def to_dict(self) -> Dict:
        """导出为字典"""
        return {
            "nodes": {
                task_id: {
                    "dependencies": list(node.dependencies),
                    "dependents": list(node.dependents)
                }
                for task_id, node in self.nodes.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TaskDependencyManager':
        """从字典导入"""
        manager = cls()
        
        for task_id, node_data in data.get("nodes", {}).items():
            node = DependencyNode(task_id=task_id)
            node.dependencies = set(node_data.get("dependencies", []))
            node.dependents = set(node_data.get("dependents", []))
            manager.nodes[task_id] = node
            
            for dep_id in node.dependencies:
                manager._dependency_graph[task_id].add(dep_id)
            for dep_id in node.dependents:
                manager._reverse_graph[task_id].add(dep_id)
        
        return manager


# 导出
__all__ = [
    "DependencyNode",
    "DependencyCycle",
    "TaskDependencyManager"
]

"""
AutoGPT Task Planner
自主任务规划器 - 将复杂目标分解为可执行的子任务
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import json


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Task:
    """任务数据结构"""
    id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    parent_task: Optional[str] = None
    estimated_duration: Optional[int] = None  # 分钟
    actual_duration: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "dependencies": self.dependencies,
            "subtasks": self.subtasks,
            "parent_task": self.parent_task,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """从字典创建任务"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            status=TaskStatus(data.get("status", "pending")),
            priority=TaskPriority(data.get("priority", "medium")),
            dependencies=data.get("dependencies", []),
            subtasks=data.get("subtasks", []),
            parent_task=data.get("parent_task"),
            estimated_duration=data.get("estimated_duration"),
            actual_duration=data.get("actual_duration"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            result=data.get("result"),
            metadata=data.get("metadata", {})
        )


@dataclass
class Plan:
    """执行计划"""
    id: str
    name: str
    goal: str
    tasks: Dict[str, Task] = field(default_factory=dict)
    root_tasks: List[str] = field(default_factory=list)  # 无依赖的顶层任务
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_task(self, task: Task):
        """添加任务到计划"""
        self.tasks[task.id] = task
        if not task.dependencies:
            self.root_tasks.append(task.id)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def get_ready_tasks(self) -> List[Task]:
        """获取准备就绪的任务（依赖已完成）"""
        ready = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                dependencies_met = all(
                    self.tasks[dep_id].status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                    if dep_id in self.tasks
                )
                if dependencies_met:
                    ready.append(task)
        return ready
    
    def get_progress(self) -> Dict[str, Any]:
        """获取计划进度"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        running = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
        pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        
        return {
            "total_tasks": total,
            "completed": completed,
            "running": running,
            "pending": pending,
            "failed": failed,
            "completion_percentage": (completed / total * 100) if total > 0 else 0,
            "is_complete": completed == total and failed == 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "goal": self.goal,
            "tasks": {k: v.to_dict() for k, v in self.tasks.items()},
            "root_tasks": self.root_tasks,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


class TaskPlanner:
    """
    任务规划器 - AutoGPT 的核心组件
    负责将复杂目标分解为可执行的子任务
    """
    
    def __init__(self, llm_provider: Optional[str] = None):
        """
        初始化任务规划器
        
        Args:
            llm_provider: LLM 提供者，用于任务分解
        """
        self.llm_provider = llm_provider or "nvidia-main/z-ai/glm5"
        self.plans: Dict[str, Plan] = {}
        self._task_counter = 0
        self._plan_counter = 0
    
    def _generate_task_id(self) -> str:
        """生成任务 ID"""
        self._task_counter += 1
        return f"task_{self._task_counter:04d}"
    
    def _generate_plan_id(self) -> str:
        """生成计划 ID"""
        self._plan_counter += 1
        return f"plan_{self._plan_counter:04d}"
    
    async def create_plan(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        max_depth: int = 3,
        max_subtasks: int = 5
    ) -> Plan:
        """
        创建执行计划
        
        Args:
            goal: 目标描述
            context: 额外上下文信息
            max_depth: 最大分解深度
            max_subtasks: 每层最大子任务数
            
        Returns:
            执行计划
        """
        plan_id = self._generate_plan_id()
        plan = Plan(
            id=plan_id,
            name=f"Plan for: {goal[:50]}",
            goal=goal,
            metadata={"context": context or {}}
        )
        
        # 分解目标为任务
        root_tasks = await self._decompose_goal(goal, context, max_depth, max_subtasks)
        
        for task_data in root_tasks:
            task = Task(
                id=self._generate_task_id(),
                name=task_data["name"],
                description=task_data["description"],
                priority=TaskPriority(task_data.get("priority", "medium")),
                dependencies=task_data.get("dependencies", [])
            )
            plan.add_task(task)
            
            # 添加子任务
            if "subtasks" in task_data:
                await self._add_subtasks(plan, task, task_data["subtasks"], max_subtasks)
        
        self.plans[plan.id] = plan
        return plan
    
    async def _decompose_goal(
        self,
        goal: str,
        context: Optional[Dict[str, Any]],
        max_depth: int,
        max_subtasks: int
    ) -> List[Dict[str, Any]]:
        """
        分解目标为任务
        
        这是核心分解逻辑，可以根据不同类型的目标采用不同的分解策略
        """
        # 简化的分解逻辑 - 实际应用中可以使用 LLM 进行智能分解
        task_templates = self._get_task_templates(goal)
        
        tasks = []
        for i, template in enumerate(task_templates[:max_subtasks]):
            task_data = {
                "name": template["name"],
                "description": template["description"],
                "priority": template.get("priority", "medium"),
                "dependencies": [] if i == 0 else [tasks[i-1]["id"]] if self._needs_sequential_execution(goal) else []
            }
            tasks.append(task_data)
        
        return tasks
    
    def _get_task_templates(self, goal: str) -> List[Dict[str, Any]]:
        """
        根据目标类型获取任务模板
        
        实际应用中，这里可以使用 LLM 进行智能任务识别
        """
        goal_lower = goal.lower()
        
        # 分析类任务
        if any(kw in goal_lower for kw in ["分析", "analyze", "analysis"]):
            return [
                {"name": "数据收集", "description": "收集所需的数据和信息", "priority": "high"},
                {"name": "数据预处理", "description": "清洗和准备数据", "priority": "high"},
                {"name": "分析方法选择", "description": "确定合适的分析方法", "priority": "medium"},
                {"name": "执行分析", "description": "运行分析流程", "priority": "high"},
                {"name": "结果总结", "description": "总结分析结果", "priority": "medium"}
            ]
        
        # 开发类任务
        elif any(kw in goal_lower for kw in ["开发", "创建", "develop", "create", "build"]):
            return [
                {"name": "需求分析", "description": "明确需求和功能", "priority": "critical"},
                {"name": "设计架构", "description": "设计系统架构", "priority": "high"},
                {"name": "编写代码", "description": "实现核心功能", "priority": "high"},
                {"name": "测试验证", "description": "测试和验证功能", "priority": "high"},
                {"name": "文档编写", "description": "编写相关文档", "priority": "medium"}
            ]
        
        # 研究类任务
        elif any(kw in goal_lower for kw in ["研究", "调研", "research"]):
            return [
                {"name": "文献搜索", "description": "搜索相关文献和资料", "priority": "high"},
                {"name": "信息整理", "description": "整理和分类信息", "priority": "medium"},
                {"name": "深度分析", "description": "深入分析关键内容", "priority": "high"},
                {"name": "撰写报告", "description": "撰写研究报告", "priority": "medium"}
            ]
        
        # 默认通用任务
        else:
            return [
                {"name": "理解目标", "description": "深入理解目标要求", "priority": "high"},
                {"name": "制定方案", "description": "制定执行方案", "priority": "high"},
                {"name": "执行任务", "description": "执行主要任务", "priority": "high"},
                {"name": "检查结果", "description": "检查和验证结果", "priority": "medium"},
                {"name": "优化改进", "description": "优化和改进结果", "priority": "low"}
            ]
    
    def _needs_sequential_execution(self, goal: str) -> bool:
        """判断是否需要顺序执行"""
        # 简化逻辑 - 实际可以使用 LLM 判断
        sequential_keywords = ["步骤", "流程", "step", "process", "sequence"]
        return any(kw in goal.lower() for kw in sequential_keywords)
    
    async def _add_subtasks(
        self,
        plan: Plan,
        parent_task: Task,
        subtask_data: List[Dict[str, Any]],
        max_subtasks: int
    ):
        """递归添加子任务"""
        for data in subtask_data[:max_subtasks]:
            subtask = Task(
                id=self._generate_task_id(),
                name=data["name"],
                description=data["description"],
                priority=TaskPriority(data.get("priority", "medium")),
                dependencies=data.get("dependencies", []),
                parent_task=parent_task.id
            )
            plan.add_task(subtask)
            parent_task.subtasks.append(subtask.id)
            
            # 递归添加子任务
            if "subtasks" in data:
                await self._add_subtasks(plan, subtask, data["subtasks"], max_subtasks)
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """获取计划"""
        return self.plans.get(plan_id)
    
    def update_task_status(self, plan_id: str, task_id: str, status: TaskStatus):
        """更新任务状态"""
        plan = self.plans.get(plan_id)
        if plan:
            task = plan.get_task(task_id)
            if task:
                task.status = status
                if status == TaskStatus.RUNNING:
                    task.started_at = datetime.now()
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    task.completed_at = datetime.now()
    
    def get_next_executable_tasks(self, plan_id: str) -> List[Task]:
        """获取下一个可执行的任务"""
        plan = self.plans.get(plan_id)
        if not plan:
            return []
        return plan.get_ready_tasks()
    
    def optimize_plan(self, plan_id: str) -> Plan:
        """
        优化执行计划
        
        包括：
        - 任务重排序
        - 并行任务识别
        - 资源分配优化
        """
        plan = self.plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        # 识别可以并行的任务
        parallel_groups = self._identify_parallel_tasks(plan)
        plan.metadata["parallel_groups"] = parallel_groups
        
        # 重新计算优先级
        self._recalculate_priorities(plan)
        
        return plan
    
    def _identify_parallel_tasks(self, plan: Plan) -> List[List[str]]:
        """识别可以并行执行的任务组"""
        parallel_groups = []
        processed = set()
        
        for task_id, task in plan.tasks.items():
            if task_id in processed:
                continue
            
            # 找出所有与当前任务无依赖关系的同层级任务
            group = [task_id]
            processed.add(task_id)
            
            for other_id, other_task in plan.tasks.items():
                if other_id in processed:
                    continue
                if other_task.parent_task == task.parent_task:
                    if not self._has_dependency(plan, task_id, other_id):
                        group.append(other_id)
                        processed.add(other_id)
            
            if len(group) > 1:
                parallel_groups.append(group)
        
        return parallel_groups
    
    def _has_dependency(self, plan: Plan, task_id1: str, task_id2: str) -> bool:
        """检查两个任务之间是否存在依赖关系"""
        task1 = plan.get_task(task_id1)
        task2 = plan.get_task(task_id2)
        
        if not task1 or not task2:
            return False
        
        return task_id2 in task1.dependencies or task_id1 in task2.dependencies
    
    def _recalculate_priorities(self, plan: Plan):
        """重新计算任务优先级"""
        # 基于依赖深度和重要性重新计算
        for task_id, task in plan.tasks.items():
            depth = self._calculate_dependency_depth(plan, task_id)
            importance_factor = 1.0 - (depth * 0.1)  # 深度越大，优先级越低
            
            if task.priority == TaskPriority.CRITICAL:
                importance_factor *= 1.5
            elif task.priority == TaskPriority.HIGH:
                importance_factor *= 1.2
            
            task.metadata["calculated_priority"] = importance_factor
    
    def _calculate_dependency_depth(self, plan: Plan, task_id: str, visited: Optional[set] = None) -> int:
        """计算依赖深度"""
        if visited is None:
            visited = set()
        
        if task_id in visited:
            return 0
        
        visited.add(task_id)
        task = plan.get_task(task_id)
        
        if not task or not task.dependencies:
            return 0
        
        max_depth = 0
        for dep_id in task.dependencies:
            depth = self._calculate_dependency_depth(plan, dep_id, visited)
            max_depth = max(max_depth, depth + 1)
        
        return max_depth


# 导出
__all__ = [
    "Task",
    "TaskStatus",
    "TaskPriority",
    "Plan",
    "TaskPlanner"
]

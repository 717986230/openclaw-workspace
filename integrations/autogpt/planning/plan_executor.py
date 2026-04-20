"""
AutoGPT Plan Executor
计划执行器 - 管理计划的执行流程
"""

from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

from .task_planner import Plan, Task, TaskStatus

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """执行结果"""
    task_id: str
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionReport:
    """执行报告"""
    plan_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    results: List[ExecutionResult] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_tasks == 0:
            return 0.0
        return self.completed_tasks / self.total_tasks
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "plan_id": self.plan_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": self.success_rate,
            "results": [
                {
                    "task_id": r.task_id,
                    "success": r.success,
                    "error": r.error,
                    "duration_seconds": r.duration_seconds
                }
                for r in self.results
            ]
        }


class PlanExecutor:
    """
    计划执行器
    负责管理计划的执行流程，包括任务调度、并行执行、错误处理等
    """
    
    def __init__(
        self,
        max_parallel_tasks: int = 3,
        retry_failed_tasks: bool = True,
        max_retries: int = 2
    ):
        """
        初始化执行器
        
        Args:
            max_parallel_tasks: 最大并行任务数
            retry_failed_tasks: 是否重试失败任务
            max_retries: 最大重试次数
        """
        self.max_parallel_tasks = max_parallel_tasks
        self.retry_failed_tasks = retry_failed_tasks
        self.max_retries = max_retries
        
        # 执行状态
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.execution_reports: Dict[str, ExecutionReport] = {}
        
        # 任务处理器注册表
        self.task_handlers: Dict[str, Callable] = {}
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """
        注册任务处理器
        
        Args:
            task_type: 任务类型
            handler: 处理函数，签名为 async (task: Task) -> Any
        """
        self.task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")
    
    async def execute_plan(
        self,
        plan: Plan,
        progress_callback: Optional[Callable[[Dict], None]] = None
    ) -> ExecutionReport:
        """
        执行计划
        
        Args:
            plan: 要执行的计划
            progress_callback: 进度回调函数
            
        Returns:
            执行报告
        """
        logger.info(f"Starting execution of plan: {plan.id}")
        
        report = ExecutionReport(
            plan_id=plan.id,
            start_time=datetime.now(),
            total_tasks=len(plan.tasks)
        )
        
        self.execution_reports[plan.id] = report
        
        try:
            # 持续执行直到所有任务完成或无法继续
            while True:
                # 获取可执行的任务
                ready_tasks = plan.get_ready_tasks()
                
                if not ready_tasks:
                    # 检查是否所有任务都已完成
                    progress = plan.get_progress()
                    if progress["is_complete"] or progress["pending"] == 0:
                        break
                    
                    # 检查是否有失败导致无法继续
                    if progress["failed"] > 0:
                        logger.warning("Some tasks failed, cannot continue")
                        break
                    
                    # 等待正在运行的任务完成
                    await asyncio.sleep(0.5)
                    continue
                
                # 执行任务（并行）
                await self._execute_tasks_parallel(plan, ready_tasks, report, progress_callback)
        
        except Exception as e:
            logger.error(f"Plan execution failed: {e}")
            report.metadata["error"] = str(e)
        
        finally:
            report.end_time = datetime.now()
            self.execution_reports[plan.id] = report
        
        return report
    
    async def _execute_tasks_parallel(
        self,
        plan: Plan,
        tasks: List[Task],
        report: ExecutionReport,
        progress_callback: Optional[Callable]
    ):
        """并行执行任务"""
        # 限制并行数量
        tasks_to_run = tasks[:self.max_parallel_tasks]
        
        # 创建异步任务
        coroutines = [
            self._execute_single_task(plan, task, report)
            for task in tasks_to_run
        ]
        
        if coroutines:
            await asyncio.gather(*coroutines, return_exceptions=True)
        
        # 触发进度回调
        if progress_callback:
            progress = plan.get_progress()
            progress_callback(progress)
    
    async def _execute_single_task(
        self,
        plan: Plan,
        task: Task,
        report: ExecutionReport
    ) -> ExecutionResult:
        """执行单个任务"""
        logger.info(f"Executing task: {task.id} - {task.name}")
        
        # 更新任务状态
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        start_time = datetime.now()
        result = ExecutionResult(task_id=task.id, success=False)
        retries = 0
        
        while retries <= (self.max_retries if self.retry_failed_tasks else 0):
            try:
                # 获取任务处理器
                handler = self._get_task_handler(task)
                
                # 执行任务
                output = await handler(task)
                
                # 成功
                result.success = True
                result.output = output
                task.status = TaskStatus.COMPLETED
                task.result = {"output": output}
                report.completed_tasks += 1
                
                logger.info(f"Task completed successfully: {task.id}")
                break
                
            except Exception as e:
                retries += 1
                error_msg = str(e)
                logger.warning(f"Task {task.id} failed (attempt {retries}): {error_msg}")
                
                if retries > self.max_retries:
                    task.status = TaskStatus.FAILED
                    task.result = {"error": error_msg}
                    result.error = error_msg
                    report.failed_tasks += 1
                    
                    logger.error(f"Task failed after {retries} attempts: {task.id}")
        
        # 计算执行时间
        end_time = datetime.now()
        task.completed_at = end_time
        result.duration_seconds = (end_time - start_time).total_seconds()
        
        report.results.append(result)
        return result
    
    def _get_task_handler(self, task: Task) -> Callable:
        """获取任务处理器"""
        # 检查是否有特定类型的处理器
        task_type = task.metadata.get("type", "default")
        
        if task_type in self.task_handlers:
            return self.task_handlers[task_type]
        
        # 返回默认处理器
        return self._default_task_handler
    
    async def _default_task_handler(self, task: Task) -> Any:
        """
        默认任务处理器
        
        实际应用中，这里可以调用 OpenClaw 的任务执行系统
        """
        logger.info(f"Executing default handler for task: {task.name}")
        
        # 模拟执行
        await asyncio.sleep(0.1)
        
        return {
            "status": "completed",
            "task_id": task.id,
            "message": f"Task '{task.name}' executed successfully"
        }
    
    def get_execution_report(self, plan_id: str) -> Optional[ExecutionReport]:
        """获取执行报告"""
        return self.execution_reports.get(plan_id)
    
    def cancel_execution(self, plan_id: str) -> bool:
        """取消执行"""
        if plan_id in self.running_tasks:
            for task_name, task in self.running_tasks.items():
                if plan_id in task_name:
                    task.cancel()
            return True
        return False
    
    async def execute_with_reflection(
        self,
        plan: Plan,
        reflector: Any,  # Reflector from reflection module
        max_iterations: int = 5
    ) -> ExecutionReport:
        """
        带反思的执行
        
        执行计划后进行反思，根据反思结果调整并重新执行
        """
        from integrations.autogpt.reflection.reflector import Reflector
        
        if not isinstance(reflector, Reflector):
            raise ValueError("Invalid reflector provided")
        
        best_report = None
        best_success_rate = 0.0
        
        for iteration in range(max_iterations):
            logger.info(f"Starting execution iteration {iteration + 1}")
            
            # 执行计划
            report = await self.execute_plan(plan)
            
            # 检查是否完全成功
            if report.success_rate == 1.0:
                logger.info("Plan executed perfectly!")
                return report
            
            # 更新最佳结果
            if report.success_rate > best_success_rate:
                best_success_rate = report.success_rate
                best_report = report
            
            # 如果达到可接受的成功率，可以提前结束
            if report.success_rate >= 0.8:
                logger.info(f"Reached acceptable success rate: {report.success_rate:.2%}")
                break
            
            # 反思并获取改进建议
            analysis = await reflector.analyze_execution(report)
            suggestions = await reflector.suggest_improvements(analysis)
            
            # 应用改进建议到计划
            await self._apply_improvements(plan, suggestions)
        
        return best_report or report
    
    async def _apply_improvements(self, plan: Plan, suggestions: List[Dict[str, Any]]):
        """应用改进建议到计划"""
        for suggestion in suggestions:
            suggestion_type = suggestion.get("type")
            
            if suggestion_type == "add_task":
                # 添加新任务
                pass
            elif suggestion_type == "modify_task":
                # 修改任务
                task_id = suggestion.get("task_id")
                task = plan.get_task(task_id)
                if task:
                    task.metadata.update(suggestion.get("changes", {}))
            elif suggestion_type == "reorder_tasks":
                # 重新排序任务
                pass
        
        logger.info(f"Applied {len(suggestions)} improvements to plan")


# 导出
__all__ = [
    "ExecutionResult",
    "ExecutionReport",
    "PlanExecutor"
]

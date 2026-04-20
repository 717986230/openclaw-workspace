"""
Plan-Approve-Execute（整合 Maestro）
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import uuid


class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = "pending"
    PLANNED = "planned"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class Plan:
    """计划"""
    id: str
    task: str
    steps: List[Dict[str, Any]]
    estimated_duration: Optional[int] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Execution:
    """执行"""
    id: str
    plan_id: str
    status: ExecutionStatus
    results: List[Dict[str, Any]]
    errors: List[str]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class PlanApproveExecute:
    """Plan-Approve-Execute"""

    def __init__(self):
        self.plans: Dict[str, Plan] = {}
        self.executions: Dict[str, Execution] = {}

    def create_plan(
        self,
        task: str,
        steps: List[Dict[str, Any]],
        estimated_duration: Optional[int] = None,
    ) -> Plan:
        """创建计划"""
        plan = Plan(
            id=self._generate_plan_id(),
            task=task,
            steps=steps,
            estimated_duration=estimated_duration,
        )

        self.plans[plan.id] = plan
        return plan

    def approve_plan(self, plan_id: str) -> bool:
        """批准计划"""
        if plan_id not in self.plans:
            return False

        execution = Execution(
            id=self._generate_execution_id(),
            plan_id=plan_id,
            status=ExecutionStatus.APPROVED,
            results=[],
            errors=[],
        )

        self.executions[execution.id] = execution
        return True

    def reject_plan(self, plan_id: str, reason: str) -> bool:
        """拒绝计划"""
        if plan_id not in self.plans:
            return False

        execution = Execution(
            id=self._generate_execution_id(),
            plan_id=plan_id,
            status=ExecutionStatus.REJECTED,
            results=[],
            errors=[reason],
        )

        self.executions[execution.id] = execution
        return True

    def execute_plan(self, plan_id: str) -> Optional[Execution]:
        """执行计划"""
        if plan_id not in self.plans:
            return None

        plan = self.plans[plan_id]

        execution = Execution(
            id=self._generate_execution_id(),
            plan_id=plan_id,
            status=ExecutionStatus.EXECUTING,
            results=[],
            errors=[],
            started_at=datetime.now(),
        )

        self.executions[execution.id] = execution

        try:
            for step in plan.steps:
                result = self._execute_step(step)
                execution.results.append(result)

            execution.status = ExecutionStatus.COMPLETED
            execution.completed_at = datetime.now()

        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.errors.append(str(e))
            execution.completed_at = datetime.now()

        return execution

    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """执行步骤"""
        return {
            "step": step,
            "status": "completed",
            "result": f"Step executed: {step.get('action', 'unknown')}",
        }

    def _generate_plan_id(self) -> str:
        """生成计划 ID"""
        return f"plan_{uuid.uuid4()}"

    def _generate_execution_id(self) -> str:
        """生成执行 ID"""
        return f"execution_{uuid.uuid4()}"

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """获取计划"""
        return self.plans.get(plan_id)

    def get_execution(self, execution_id: str) -> Optional[Execution]:
        """获取执行"""
        return self.executions.get(execution_id)

    def get_all_plans(self) -> List[Plan]:
        """获取所有计划"""
        return list(self.plans.values())

    def get_all_executions(self) -> List[Execution]:
        """获取所有执行"""
        return list(self.executions.values())

    def get_summary(self) -> Dict[str, Any]:
        """获取摘要"""
        return {
            "total_plans": len(self.plans),
            "total_executions": len(self.executions),
            "by_status": {
                status.value: len([e for e in self.executions.values() if e.status == status])
                for status in ExecutionStatus
            },
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "plans": [
                {
                    "id": p.id,
                    "task": p.task,
                    "steps": p.steps,
                    "estimated_duration": p.estimated_duration,
                    "created_at": p.created_at.isoformat(),
                }
                for p in self.plans.values()
            ],
            "executions": [
                {
                    "id": e.id,
                    "plan_id": e.plan_id,
                    "status": e.status.value,
                    "results": e.results,
                    "errors": e.errors,
                    "started_at": e.started_at.isoformat() if e.started_at else None,
                    "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                }
                for e in self.executions.values()
            ],
            "summary": self.get_summary(),
        }

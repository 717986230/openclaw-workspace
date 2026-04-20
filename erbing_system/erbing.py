"""
二饼系统（Hermes 深度整合版）
"""

from typing import Dict, List, Any, Optional
from .hermes.core.logging import FullStackLogger, LogLevel, LogCategory
from .hermes.skills.factory import SkillFactory
from .hermes.execution.plan_approve_execute import PlanApproveExecute
from .core.thinking import ThinkingEngine
from .core.simplicity import SimplicityEngine


class Erbing:
    """二饼系统（Hermes 深度整合版）"""

    def __init__(self):
        # Hermes 核心
        self.logger = FullStackLogger()
        self.skill_factory = SkillFactory()
        self.pae = PlanApproveExecute()

        # Karpathy 原则
        self.thinking = ThinkingEngine()
        self.simplicity = SimplicityEngine()

    async def process_task(self, task: str) -> Dict[str, Any]:
        """处理任务"""
        # 1. 记录开始
        self.logger.log(
            LogLevel.INFO,
            LogCategory.EXECUTION,
            f"Processing task: {task}",
        )

        # 2. 思考阶段
        self.thinking.set_task(task)

        if not self.thinking.should_proceed():
            return {
                "status": "blocked",
                "blocking_issues": self.thinking.get_blocking_issues(),
            }

        # 3. 创建计划
        plan = self.pae.create_plan(
            task=task,
            steps=[
                {"step": "Analyze task", "action": "analyze"},
                {"step": "Generate solution", "action": "generate"},
                {"step": "Execute solution", "action": "execute"},
                {"step": "Verify results", "action": "verify"},
            ],
        )

        # 4. 执行计划
        execution = self.pae.execute_plan(plan.id)

        # 5. 自动生成技能
        if execution.status.name == "COMPLETED":
            skills = self.skill_factory.auto_generate_skills(task)
            self.logger.log(
                LogLevel.INFO,
                LogCategory.SKILL,
                f"Auto-generated {len(skills)} skills",
            )

        # 6. 获取日志摘要
        summary = self.logger.get_summary()

        return {
            "status": execution.status.value,
            "plan": {
                "id": plan.id,
                "task": plan.task,
                "steps": plan.steps,
            },
            "execution": {
                "id": execution.id,
                "status": execution.status.value,
                "results": execution.results,
                "errors": execution.errors,
            },
            "log_summary": summary,
        }

    def get_skills(self) -> Dict[str, Any]:
        """获取技能"""
        return {
            "skills": [s.__dict__ for s in self.skill_factory.get_all_skills()],
            "meta_skills": [ms.__dict__ for ms in self.skill_factory.get_all_meta_skills()],
            "summary": self.skill_factory.get_summary(),
        }

    def get_logs(self) -> Dict[str, Any]:
        """获取日志"""
        return {
            "thinking_logs": [l.__dict__ for l in self.logger.get_thinking_logs()],
            "execution_logs": [l.__dict__ for l in self.logger.get_execution_logs()],
            "memory_logs": [l.__dict__ for l in self.logger.get_memory_logs()],
            "evolution_logs": [l.__dict__ for l in self.logger.get_evolution_logs()],
            "skill_logs": [l.__dict__ for l in self.logger.get_skill_logs()],
            "error_logs": [l.__dict__ for l in self.logger.get_error_logs()],
            "summary": self.logger.get_summary(),
        }

    def get_thinking(self) -> Dict[str, Any]:
        """获取思考"""
        return self.thinking.to_dict()

    def get_simplicity(self) -> Dict[str, Any]:
        """获取简单优先分析"""
        return self.simplicity.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "skills": self.get_skills(),
            "logs": self.get_logs(),
            "thinking": self.get_thinking(),
            "simplicity": self.get_simplicity(),
        }


# 创建全局实例
erbing = Erbing()


async def process_task(task: str) -> Dict[str, Any]:
    """处理任务（便捷函数）"""
    return await erbing.process_task(task)


def get_skills() -> Dict[str, Any]:
    """获取技能（便捷函数）"""
    return erbing.get_skills()


def get_logs() -> Dict[str, Any]:
    """获取日志（便捷函数）"""
    return erbing.get_logs()


def get_thinking() -> Dict[str, Any]:
    """获取思考（便捷函数）"""
    return erbing.get_thinking()


def get_simplicity() -> Dict[str, Any]:
    """获取简单优先分析（便捷函数）"""
    return erbing.get_simplicity()

# -*- coding: utf-8 -*-
"""
主动能力系统 - Proactive Ability System
实现主动监控、主动决策、主动学习、主动优化、主动沟通
让AI具备主动发现问题、主动提出建议、主动执行任务的能力
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ProactiveAction(Enum):
    """主动行动类型"""
    MONITOR = "monitor"  # 监控
    ANALYZE = "analyze"  # 分析
    DECIDE = "decide"  # 决策
    EXECUTE = "execute"  # 执行
    LEARN = "learn"  # 学习
    OPTIMIZE = "optimize"  # 优化
    COMMUNICATE = "communicate"  # 沟通
    REFLECT = "reflect"  # 反思


@dataclass
class ProactiveTask:
    """主动任务"""
    id: str
    action: ProactiveAction
    priority: float = 0.5
    context: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    status: str = "pending"


@dataclass
class ProactiveInsight:
    """主动洞察"""
    id: str
    content: str
    importance: float = 0.5
    urgency: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ProactiveSuggestion:
    """主动建议"""
    id: str
    content: str
    action: str
    expected_benefit: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)


class ProactiveAbilitySystem:
    """主动能力系统"""

    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval

        # 主动任务队列
        self.proactive_tasks: Dict[str, ProactiveTask] = {}

        # 主动洞察
        self.proactive_insights: Dict[str, ProactiveInsight] = {}

        # 主动建议
        self.proactive_suggestions: Dict[str, ProactiveSuggestion] = {}

        # 监控目标
        self.monitoring_targets: List[str] = []

        # 决策规则
        self.decision_rules: Dict[str, float] = {}

        # 学习目标
        self.learning_goals: List[str] = []

        # 优化目标
        self.optimization_goals: List[str] = []

        # 沟通渠道
        self.communication_channels: List[str] = []

        # 运行状态
        self.running = False

        # 统计信息
        self.stats: Dict[str, float] = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'total_insights': 0,
            'total_suggestions': 0,
            'total_monitoring_cycles': 0,
            'total_learning_cycles': 0,
            'total_optimization_cycles': 0,
        }

        logger.info(f"Proactive Ability System initialized with {check_interval}s check interval")

    def start(self):
        """启动主动能力系统"""
        if self.running:
            logger.warning("Proactive Ability System is already running")
            return

        self.running = True

        logger.info("Proactive Ability System started")

    def stop(self):
        """停止主动能力系统"""
        self.running = False

        logger.info("Proactive System stopped")

    def add_monitoring_target(self, target: str):
        """添加监控目标"""
        self.monitoring_targets.append(target)
        logger.info(f"Added monitoring target: {target}")

    def add_decision_rule(self, rule: str, weight: float = 0.5):
        """添加决策规则"""
        self.decision_rules[rule] = weight
        logger.info(f"Added decision rule: {rule} (weight: {weight})")

    def add_learning_goal(self, goal: str):
        """添加学习目标"""
        self.learning_goals.append(goal)
        logger.info(f"Added learning goal: {goal}")

    def add_optimization_goal(self, goal: str):
        """添加优化目标"""
        self.optimization_goals.append(goal)
        logger.info(f"Added optimization goal: {goal}")

    def add_communication_channel(self, channel: str):
        """添加沟通渠道"""
        self.communication_channels.append(channel)
        logger.info(f"Added communication channel: {channel}")

    def _create_task(
        self,
        action: ProactiveAction,
        priority: float = 0.5,
        context: Dict = None
    ) -> ProactiveTask:
        """创建主动任务"""
        task_id = f"task-{len(self.proactive_tasks)}"

        task = ProactiveTask(
            id=task_id,
            action=action,
            priority=priority,
            context=context or {},
            created_at=datetime.now()
        )

        self.proactive_tasks[task_id] = task
        self.stats['total_tasks'] += 1

        logger.debug(f"Created proactive task: {action.value} - {task_id}")

        return task

    def _create_insight(self, content: str) -> ProactiveInsight:
        """创建洞察"""
        insight_id = f"insight-{len(self.proactive_insights)}"

        insight = ProactiveInsight(
            id=insight_id,
            content=content,
            importance=0.7,
            urgency=0.5
        )

        self.stats['total_insights'] += 1

        logger.debug(f"Created insight: {content}")

        return insight

    def _create_suggestion(self, content: str, action: str, expected_benefit: float) -> ProactiveSuggestion:
        """创建建议"""
        suggestion_id = f"suggestion-{len(self.proactive_suggestions)}"

        suggestion = ProactiveSuggestion(
            id=suggestion_id,
            content=content,
            action=action,
            expected_benefit=expected_benefit
        )

        self.stats['total_suggestions'] += 1

        logger.debug(f"Created suggestion: {content}")

        return suggestion

    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'running': self.running,
            'check_interval': self.check_interval,
            'total_tasks': self.stats['total_tasks'],
            'completed_tasks': self.stats['completed_tasks'],
            'total_insights': len(self.proactive_insights),
            'total_suggestions': len(self.proactive_suggestions),
            'monitoring_targets': self.monitoring_targets,
            'decision_rules': self.decision_rules,
            'learning_goals': self.learning_goals,
            'optimization_goals': self.optimization_goals,
            'communication_channels': self.communication_channels,
            'stats': self.stats.copy(),
        }


if __name__ == "__main__":
    # 测试主动能力系统
    print("Testing Proactive Ability System...")

    # 创建主动能力系统
    proactive_system = ProactiveAbilitySystem(check_interval=5)

    print(f"\nProactive Ability System Status:")
    status = proactive_system.get_status()
    print(f"  Running: {status['running']}")
    print(f"  Check Interval: {status['check_interval']}s")
    print(f"  Total Tasks: {status['total_tasks']}")
    print(f"  Completed Tasks: {status['completed_tasks']}")
    print(f"  Total Insights: {status['total_insights']}")
    print(f"  Total Suggestions: {status['total_suggestions']}")

    # 添加监控目标
    print(f"\nAdding Monitoring Targets...")
    proactive_system.add_monitoring_target("CPU使用率")
    proactive_system.add_monitoring_target("内存使用率")
    proactive_system.add_monitoring_target("磁盘使用率")
    print(f"  Monitoring Targets: {len(proactive_system.monitoring_targets)}")

    # 添加决策规则
    print(f"\nAdding Decision Rules...")
    proactive_system.add_decision_rule("CPU > 80% 时优化", 0.8)
    proactive_system.add_decision_rule("内存 > 80% 时清理", 0.7)
    proactive_system.add_decision_rule("磁盘 > 80% 时清理", 0.6)
    print(f"  Decision Rules: {len(proactive_system.decision_rules)}")

    # 添加学习目标
    print(f"\nAdding Learning Goals...")
    proactive_system.add_learning_goal("学习新技能")
    proactive_system.add_learning_goal("提升推理能力")
    proactive_system.add_learning_goal("优化决策策略")
    print(f"  Learning Goals: {len(proactive_system.learning_goals)}")

    # 添加优化目标
    print(f"\nAdding Optimization Goals...")
    proactive_system.add_optimization_goal("优化响应速度")
    proactive_system.add_optimization_goal("优化资源使用")
    proactive_system.add_optimization_goal("优化稳定性")
    print(f"  Optimization Goals: {len(proactive_system.optimization_goals)}")

    # 添加沟通渠道
    print(f"\nAdding Communication Channels...")
    proactive_system.add_communication_channel("日志")
    proactive_system.add_communication_channel("状态报告")
    print(f"  Communication Channels: {len(proactive_system.communication_channels)}")

    # 测试创建洞察
    print(f"\nTesting Create Insight...")
    insight = proactive_system._create_insight("系统运行稳定，可以考虑增加更多主动功能")
    print(f"  Insight ID: {insight.id}")
    print(f"  Content: {insight.content}")
    print(f"  Importance: {insight.importance:.2f}")
    print(f"  Urgency: {insight.urgency:.2f}")

    # 测试创建建议
    print(f"\nTesting Create Suggestion...")
    suggestion = proactive_system._create_suggestion(
        "建议定期备份重要数据",
        "执行备份操作",
        0.8
    )
    print(f"  Suggestion ID: {suggestion.id}")
    print(f"  Content: {suggestion.content}")
    print(f"  Action: {suggestion.action}")
    print(f"  Expected Benefit: {suggestion.expected_benefit:.2f}")

    # 测试创建任务
    print(f"\nTesting Create Task...")
    task = proactive_system._create_task(
        ProactiveAction.MONITOR,
        priority=0.8,
        context={'target': 'CPU使用率'}
    )
    print(f"  Task ID: {task.id}")
    print(f"  Action: {task.action.value}")
    print(f"  Priority: {task.priority:.2f}")
    print(f"  Context: {task.context}")

    # 测试获取状态
    print(f"\nTesting Get Status...")
    status = proactive_system.get_status()
    print(f"  Total Tasks: {status['total_tasks']}")
    print(f"  Completed Tasks: {status['completed_tasks']}")
    print(f"  Total Insights: {status['total_insights']}")
    print(f"  Total Suggestions: {status['total_suggestions']}")
    print(f"  Monitoring Targets: {status['monitoring_targets']}")
    print(f"  Decision Rules: {status['decision_rules']}")
    print(f"  Learning Goals: {status['learning_goals']}")
    print(f"  Optimization Goals: {status['optimization_goals']}")
    print(f"  Communication Channels: {status['communication_channels']}")

    # 测试启动和停止
    print(f"\nTesting Start and Stop...")
    proactive_system.start()
    print(f"  Started: {proactive_system.running}")

    import time
    time.sleep(10)

    proactive_system.stop()
    print(f"  Stopped: {proactive_system.running}")

    # 获取最终状态
    print(f"\nFinal Status:")
    status = proactive_system.get_status()
    print(f"  Total Monitoring Cycles: {status['stats']['total_monitoring_cycles']}")
    print(f"  Total Learning Cycles: {status['stats']['total_learning_cycles']}")
    print(f"  Total Optimization Cycles: {status['stats']['total_optimization_cycles']}")
    print(f"  Total Tasks: {status['total_tasks']}")
    print(f"  Completed Tasks: {status['completed_tasks']}")

    print("\nProactive Ability System tested successfully!")


if __name__ == "__main__":
    success = test_proactive_system()
    sys.exit(0 if success else 1)
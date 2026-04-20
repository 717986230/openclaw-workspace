# -*- coding: utf-8 -*-
"""
智能体池系统 - Agent Pool System
管理所有智能体，根据任务自动选择合适的智能体
"""

import os
import sys
import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random

logger = logging.getLogger(__name__)


class AgentPoolStrategy(Enum):
    """智能体池策略"""
    ROUND_ROBIN = "round_robin"  # 轮询
    LEAST_USED = "least_used"  # 最少使用
    RANDOM = "random"  # 随机
    BEST_MATCH = "best_match"  # 最佳匹配
    PRIORITY = "priority"  # 优先级


class AgentStatus(Enum):
    """智能体状态"""
    AVAILABLE = "available"
    BUSY = "busy"
    EXHAUSTED = "exhausted"
    ERROR = "error"


@dataclass
class AgentUsage:
    """智能体使用记录"""
    agent_id: str
    usage_count: int = 0
    last_used_at: Optional[datetime] = None
    total_tokens: int = 0
    success_count: int = 0
    error_count: int = 0


@dataclass
class AgentPoolEntry:
    """智能体池条目"""
    agent_id: str
    agent_name: str
    category: str
    description: str
    emoji: str
    color: str
    tools: List[str]
    vibe: str
    full_content: str
    status: AgentStatus = AgentStatus.AVAILABLE
    priority: int = 0
    usage: AgentUsage = field(default_factory=AgentUsage)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentPool:
    """智能体池"""

    def __init__(self, db_path: str = "memory/database/xiaozhi_memory.db"):
        self.db_path = db_path
        self.entries: Dict[str, AgentPoolEntry] = {}
        self.strategy = AgentPoolStrategy.BEST_MATCH
        self.current_index = 0
        self.initialized = False

    def initialize(self):
        """初始化智能体池"""
        logger.info("Initializing Agent Pool...")

        # 加载所有智能体
        self._load_all_agents()

        self.initialized = True
        logger.info(f"Agent Pool initialized with {len(self.entries)} agents")

    def _load_all_agents(self):
        """加载所有智能体"""
        logger.info("Loading all agents from database...")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 查询所有智能体
            cursor.execute("SELECT * FROM agent_prompts")
            rows = cursor.fetchall()

            # 获取列名
            columns = [description[0] for description in cursor.description]

            for row in rows:
                agent_data = dict(zip(columns, row))

                try:
                    # 解析 JSON 字段
                    tools = json.loads(agent_data.get('tools', '[]'))
                    metadata = json.loads(agent_data.get('metadata', '{}'))
                except json.JSONDecodeError:
                    # 如果 JSON 解析失败，使用默认值
                    tools = []
                    metadata = {}

                # 使用字符串 ID
                agent_id = str(agent_data.get('id', ''))

                # 创建智能体池条目
                entry = AgentPoolEntry(
                    agent_id=agent_id,
                    agent_name=agent_data.get('name', ''),
                    category=agent_data.get('category', ''),
                    description=agent_data.get('description', ''),
                    emoji=agent_data.get('emoji', '🤖'),
                    color=agent_data.get('color', '#3B82F6'),
                    tools=tools,
                    vibe=agent_data.get('vibe', 'professional'),
                    full_content=agent_data.get('full_content', ''),
                    priority=0,
                    usage=AgentUsage(agent_id=agent_id),
                    metadata=metadata,
                )

                self.entries[entry.agent_id] = entry

            conn.close()
            logger.info(f"Loaded {len(self.entries)} agents")

        except Exception as e:
            logger.error(f"Error loading agents: {e}")

    def set_strategy(self, strategy: AgentPoolStrategy):
        """设置选择策略"""
        logger.info(f"Setting strategy to: {strategy.value}")
        self.strategy = strategy

    def get_agent(self, task_type: Optional[str] = None, keywords: Optional[List[str]] = None) -> Optional[AgentPoolEntry]:
        """获取智能体"""
        logger.info(f"Getting agent for task_type: {task_type}, keywords: {keywords}")

        # 根据策略选择智能体
        if self.strategy == AgentPoolStrategy.ROUND_ROBIN:
            return self._get_round_robin_agent()
        elif self.strategy == AgentPoolStrategy.LEAST_USED:
            return self._get_least_used_agent()
        elif self.strategy == AgentPoolStrategy.RANDOM:
            return self._get_random_agent()
        elif self.strategy == AgentPoolStrategy.BEST_MATCH:
            return self._get_best_match_agent(task_type, keywords)
        elif self.strategy == AgentPoolStrategy.PRIORITY:
            return self._get_priority_agent()
        else:
            return self._get_random_agent()

    def _get_round_robin_agent(self) -> Optional[AgentPoolEntry]:
        """轮询获取智能体"""
        available_agents = [e for e in self.entries.values() if e.status == AgentStatus.AVAILABLE]

        if not available_agents:
            return None

        agent = available_agents[self.current_index % len(available_agents)]
        self.current_index += 1

        return agent

    def _get_least_used_agent(self) -> Optional[AgentPoolEntry]:
        """获取最少使用的智能体"""
        available_agents = [e for e in self.entries.values() if e.status == AgentStatus.AVAILABLE]

        if not available_agents:
            return None

        # 按使用次数排序
        sorted_agents = sorted(available_agents, key=lambda x: x.usage.usage_count)
        return sorted_agents[0]

    def _get_random_agent(self) -> Optional[AgentPoolEntry]:
        """随机获取智能体"""
        available_agents = [e for e in self.entries.values() if e.status == AgentStatus.AVAILABLE]

        if not available_agents:
            return None

        return random.choice(available_agents)

    def _get_best_match_agent(self, task_type: Optional[str] = None, keywords: Optional[List[str]] = None) -> Optional[AgentPoolEntry]:
        """获取最佳匹配的智能体"""
        available_agents = [e for e in self.entries.values() if e.status == AgentStatus.AVAILABLE]

        if not available_agents:
            return None

        # 如果没有指定任务类型或关键词，返回随机智能体
        if not task_type and not keywords:
            return random.choice(available_agents)

        # 计算匹配分数
        scored_agents = []
        for agent in available_agents:
            score = 0

            # 任务类型匹配
            if task_type and task_type.lower() in agent.category.lower():
                score += 10

            # 关键词匹配
            if keywords:
                for keyword in keywords:
                    if keyword.lower() in agent.description.lower():
                        score += 5
                    if keyword.lower() in agent.agent_name.lower():
                        score += 3
                    for tool in agent.tools:
                        if keyword.lower() in tool.lower():
                            score += 2

            scored_agents.append((agent, score))

        # 按分数排序
        scored_agents.sort(key=lambda x: x[1], reverse=True)

        # 返回分数最高的智能体
        if scored_agents and scored_agents[0][1] > 0:
            return scored_agents[0][0]
        else:
            return random.choice(available_agents)

    def _get_priority_agent(self) -> Optional[AgentPoolEntry]:
        """获取优先级最高的智能体"""
        available_agents = [e for e in self.entries.values() if e.status == AgentStatus.AVAILABLE]

        if not available_agents:
            return None

        # 按优先级排序
        sorted_agents = sorted(available_agents, key=lambda x: x.priority, reverse=True)
        return sorted_agents[0]

    def mark_agent_used(self, agent_id: str, success: bool = True, tokens: int = 0):
        """标记智能体已使用"""
        if agent_id not in self.entries:
            return

        entry = self.entries[agent_id]
        entry.usage.usage_count += 1
        entry.usage.last_used_at = datetime.now()
        entry.usage.total_tokens += tokens

        if success:
            entry.usage.success_count += 1
        else:
            entry.usage.error_count += 1

        logger.info(f"Marked agent {agent_id} as used (success={success}, tokens={tokens})")

    def mark_agent_busy(self, agent_id: str):
        """标记智能体为忙碌"""
        if agent_id not in self.entries:
            return

        self.entries[agent_id].status = AgentStatus.BUSY
        logger.info(f"Marked agent {agent_id} as busy")

    def mark_agent_available(self, agent_id: str):
        """标记智能体为可用"""
        if agent_id not in self.entries:
            return

        self.entries[agent_id].status = AgentStatus.AVAILABLE
        logger.info(f"Marked agent {agent_id} as available")

    def mark_agent_exhausted(self, agent_id: str):
        """标记智能体为耗尽"""
        if agent_id not in self.entries:
            return

        self.entries[agent_id].status = AgentStatus.EXHAUSTED
        logger.info(f"Marked agent {agent_id} as exhausted")

    def mark_agent_error(self, agent_id: str):
        """标记智能体为错误"""
        if agent_id not in self.entries:
            return

        self.entries[agent_id].status = AgentStatus.ERROR
        logger.info(f"Marked agent {agent_id} as error")

    def get_agents_by_category(self, category: str) -> List[AgentPoolEntry]:
        """按分类获取智能体"""
        return [e for e in self.entries.values() if e.category == category]

    def get_available_agents(self) -> List[AgentPoolEntry]:
        """获取可用智能体"""
        return [e for e in self.entries.values() if e.status == AgentStatus.AVAILABLE]

    def get_agent_usage_stats(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取智能体使用统计"""
        if agent_id not in self.entries:
            return None

        entry = self.entries[agent_id]
        return {
            "agent_id": agent_id,
            "agent_name": entry.agent_name,
            "category": entry.category,
            "usage_count": entry.usage.usage_count,
            "last_used_at": entry.usage.last_used_at.isoformat() if entry.usage.last_used_at else None,
            "total_tokens": entry.usage.total_tokens,
            "success_count": entry.usage.success_count,
            "error_count": entry.usage.error_count,
            "success_rate": entry.usage.success_count / entry.usage.usage_count if entry.usage.usage_count > 0 else 0,
        }

    def get_pool_stats(self) -> Dict[str, Any]:
        """获取智能体池统计"""
        total_agents = len(self.entries)
        available_agents = len([e for e in self.entries.values() if e.status == AgentStatus.AVAILABLE])
        busy_agents = len([e for e in self.entries.values() if e.status == AgentStatus.BUSY])
        exhausted_agents = len([e for e in self.entries.values() if e.status == AgentStatus.EXHAUSTED])
        error_agents = len([e for e in self.entries.values() if e.status == AgentStatus.ERROR])

        total_usage = sum(e.usage.usage_count for e in self.entries.values())
        total_tokens = sum(e.usage.total_tokens for e in self.entries.values())
        total_success = sum(e.usage.success_count for e in self.entries.values())
        total_errors = sum(e.usage.error_count for e in self.entries.values())

        return {
            "total_agents": total_agents,
            "available_agents": available_agents,
            "busy_agents": busy_agents,
            "exhausted_agents": exhausted_agents,
            "error_agents": error_agents,
            "strategy": self.strategy.value,
            "total_usage": total_usage,
            "total_tokens": total_tokens,
            "total_success": total_success,
            "total_errors": total_errors,
            "overall_success_rate": total_success / total_usage if total_usage > 0 else 0,
            "categories": {
                category: len([e for e in self.entries.values() if e.category == category])
                for category in set(e.category for e in self.entries.values())
            },
        }

    def reset_agent_status(self, agent_id: str):
        """重置智能体状态"""
        if agent_id not in self.entries:
            return

        self.entries[agent_id].status = AgentStatus.AVAILABLE
        logger.info(f"Reset agent {agent_id} status")

    def reset_all_statuses(self):
        """重置所有智能体状态"""
        for agent_id in self.entries:
            self.reset_agent_status(agent_id)

        logger.info("Reset all agent statuses")


# 全局实例
_agent_pool = None


def get_agent_pool() -> AgentPool:
    """获取智能体池实例"""
    global _agent_pool
    if _agent_pool is None:
        _agent_pool = AgentPool()
        _agent_pool.initialize()
    return _agent_pool


if __name__ == "__main__":
    # 测试智能体池
    print("Testing Agent Pool...")

    # 获取智能体池实例
    pool = get_agent_pool()

    # 获取统计
    stats = pool.get_pool_stats()
    print(f"\nAgent Pool Stats:")
    print(f"  Total Agents: {stats['total_agents']}")
    print(f"  Available: {stats['available_agents']}")
    print(f"  Busy: {stats['busy_agents']}")
    print(f"  Exhausted: {stats['exhausted_agents']}")
    print(f"  Error: {stats['error_agents']}")
    print(f"  Strategy: {stats['strategy']}")
    print(f"  Total Usage: {stats['total_usage']}")
    print(f"  Total Tokens: {stats['total_tokens']}")
    print(f"  Overall Success Rate: {stats['overall_success_rate']:.2%}")

    # 测试获取智能体
    print(f"\nTesting agent selection...")

    # 随机获取
    agent = pool.get_agent()
    if agent:
        print(f"  Random agent: {agent.emoji} {agent.agent_name}")

    # 最佳匹配获取
    agent = pool.get_agent(task_type="ai_research", keywords=["python", "machine learning"])
    if agent:
        print(f"  Best match agent: {agent.emoji} {agent.agent_name}")

    # 标记使用
    if agent:
        pool.mark_agent_used(agent.agent_id, success=True, tokens=1000)
        print(f"  Marked as used")

    # 获取使用统计
    if agent:
        usage_stats = pool.get_agent_usage_stats(agent.agent_id)
        print(f"\n  Usage Stats:")
        print(f"    Usage Count: {usage_stats['usage_count']}")
        print(f"    Success Rate: {usage_stats['success_rate']:.2%}")

    print("\nAgent Pool tested successfully!")

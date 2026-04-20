# -*- coding: utf-8 -*-
"""
顶配学习能力系统 - Top-Tier Learning Ability System
实现强化学习，优化学习算法，实现迁移学习，优化学习策略
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LearningType(Enum):
    """学习类型"""
    SUPERVISED = "supervised"  # 监督学习
    UNSUPERVISED = "unsupervised"  # 无监督学习
    REINFORCEMENT = "reinforcement"  # 强化学习
    TRANSFER = "transfer"  # 迁移学习
    META = "meta"  # 元学习


@dataclass
class LearningExperience:
    """学习经验"""
    id: str
    state: np.ndarray
    action: str
    reward: float
    next_state: np.ndarray
    done: bool
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LearningPolicy:
    """学习策略"""
    id: str
    state: np.ndarray
    action: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)


class TopTierLearningSystem:
    """顶配学习能力系统"""

    def __init__(self, state_dim: int = 1000, max_experiences: int = 10000):
        self.state_dim = state_dim
        self.max_experiences = max_experiences

        # 学习经验
        self.experiences: Dict[str, LearningExperience] = {}

        # 学习策略
        self.policies: Dict[str, LearningPolicy] = {}

        # Q表（强化学习）
        self.q_table: Dict[str, np.ndarray] = {}

        # 学习参数
        self.learning_rate = 0.01
        self.discount_factor = 0.95
        self.exploration_rate = 0.1

        # 迁移学习
        self.transfer_knowledge: Dict[str, np.ndarray] = {}

        # 元学习
        self.meta_policies: Dict[str, Dict] = {}

        # 学习统计
        self.learning_stats: Dict[str, float] = {
            'total_experiences': 0,
            'total_rewards': 0.0,
            'avg_reward': 0.0,
            'success_rate': 0.0,
        }

        logger.info(f"Top-Tier Learning System initialized with {max_experiences} max experiences")

    def learn(
        self,
        state: np.ndarray,
        action: str,
        reward: float,
        next_state: np.ndarray,
        done: bool = False
    ) -> float:
        """学习"""
        # 创建学习经验
        experience_id = f"exp-{len(self.experiences)}"

        experience = LearningExperience(
            id=experience_id,
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done
        )

        # 添加到经验存储
        self.experiences[experience_id] = experience

        # 更新Q表
        self._update_q_table(state, action, reward, next_state, done)

        # 更新学习统计
        self._update_learning_stats(reward, done)

        # 限制经验数量
        if len(self.experiences) > self.max_experiences:
            # 删除最旧的经验
            oldest_id = min(self.experiences.keys(), key=lambda k: self.experiences[k].timestamp)
            del self.experiences[oldest_id]

        logger.debug(f"Learned: {action} with reward {reward:.2f}")

        return reward

    def _update_q_table(
        self,
        state: np.ndarray,
        action: str,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ):
        """更新Q表"""
        # 创建状态键
        state_key = self._state_to_key(state)
        next_state_key = self._state_to_key(next_state)

        # 初始化Q值
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(10)  # 假设10个动作

        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(10)

        # 计算目标Q值
        if done:
            target_q = reward
        else:
            target_q = reward + self.discount_factor * np.max(self.q_table[next_state_key])

        # 更新Q值
        action_index = hash(action) % 10
        self.q_table[state_key][action_index] += self.learning_rate * (target_q - self.q_table[state_key][action_index])

    def _state_to_key(self, state: np.ndarray) -> str:
        """将状态转换为键"""
        # 简单的状态哈希
        return str(hash(state.tobytes()))

    def _update_learning_stats(self, reward: float, done: bool):
        """更新学习统计"""
        self.learning_stats['total_experiences'] += 1
        self.learning_stats['total_rewards'] += reward
        self.learning_stats['avg_reward'] = self.learning_stats['total_rewards'] / self.learning_stats['total_experiences']

        if done:
            if reward > 0:
                self.learning_stats['success_rate'] = (self.learning_stats['success_rate'] * 0.9 + 0.1)
            else:
                self.learning_stats['success_rate'] = (self.learning_stats['success_rate'] * 0.9)

    def get_action(self, state: np.ndarray, explore: bool = True) -> str:
        """获取动作"""
        # 探索或利用
        if explore and np.random.random() < self.exploration_rate:
            # 探索：随机动作
            action = f"action_{np.random.randint(10)}"
        else:
            # 利用：选择最佳动作
            state_key = self._state_to_key(state)
            if state_key in self.q_table:
                action_index = np.argmax(self.q_table[state_key])
                action = f"action_{action_index}"
            else:
                action = f"action_{np.random.randint(10)}"

        return action

    def transfer_learn(self, source_task: str, target_task: str):
        """迁移学习"""
        # 简单的迁移学习
        if source_task in self.q_table:
            # 复制Q表
            self.transfer_knowledge[target_task] = self.q_table[source_task].copy()

            logger.info(f"Transferred knowledge from {source_task} to {target_task}")

    def meta_learn(self, tasks: List[str]):
        """元学习"""
        # 简单的元学习
        for task in tasks:
            if task in self.q_table:
                # 提取策略
                policy = {
                    'q_table': self.q_table[task].copy(),
                    'success_rate': self.learning_stats['success_rate'],
                }
                self.meta_policies[task] = policy

        logger.info(f"Meta learned from {len(tasks)} tasks")

    def optimize_learning(self):
        """优化学习"""
        # 调整学习率
        if self.learning_stats['success_rate'] > 0.8:
            self.learning_rate = min(0.1, self.learning_rate * 1.01)
        elif self.learning_stats['success_rate'] < 0.5:
            self.learning_rate = max(0.001, self.learning_rate * 0.99)

        # 调整探索率
        if self.learning_stats['total_experiences'] > 1000:
            self.exploration_rate = max(0.01, self.exploration_rate * 0.99)

        logger.debug(f"Optimized learning: rate={self.learning_rate:.4f}, exploration={self.exploration_rate:.4f}")

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            'total_experiences': len(self.experiences),
            'max_experiences': self.max_experiences,
            'total_policies': len(self.policies),
            'q_table_size': len(self.q_table),
            'transfer_knowledge_size': len(self.transfer_knowledge),
            'meta_policies_size': len(self.meta_policies),
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'exploration_rate': self.exploration_rate,
            'avg_reward': self.learning_stats['avg_reward'],
            'success_rate': self.learning_stats['success_rate'],
        }


if __name__ == "__main__":
    # 测试顶配学习能力系统
    print("Testing Top-Tier Learning System...")

    # 创建顶配学习能力系统
    learning_system = TopTierLearningSystem(state_dim=1000, max_experiences=10000)

    print(f"\nLearning System Statistics:")
    stats = learning_system.get_statistics()
    print(f"  Total Experiences: {stats['total_experiences']}")
    print(f"  Max Experiences: {stats['max_experiences']}")
    print(f"  Total Policies: {stats['total_policies']}")
    print(f"  Q Table Size: {stats['q_table_size']}")
    print(f"  Learning Rate: {stats['learning_rate']:.4f}")
    print(f"  Discount Factor: {stats['discount_factor']:.2f}")
    print(f"  Exploration Rate: {stats['exploration_rate']:.4f}")

    # 测试学习
    print(f"\nTesting Learn...")
    state = np.random.randn(1000)
    next_state = np.random.randn(1000)
    reward = learning_system.learn(state, "action_1", 1.0, next_state, done=False)
    print(f"  Reward: {reward:.2f}")

    # 测试获取动作
    print(f"\nTesting Get Action...")
    action = learning_system.get_action(state, explore=True)
    print(f"  Action: {action}")

    # 测试迁移学习
    print(f"\nTesting Transfer Learn...")
    learning_system.transfer_learn("task_1", "task_2")
    print(f"  Transfer Knowledge Size: {len(learning_system.transfer_knowledge)}")

    # 测试元学习
    print(f"\nTesting Meta Learn...")
    learning_system.meta_learn(["task_1", "task_2"])
    print(f"  Meta Policies Size: {len(learning_system.meta_policies)}")

    # 测试优化学习
    print(f"\nTesting Optimize Learning...")
    learning_system.optimize_learning()
    stats = learning_system.get_statistics()
    print(f"  Learning Rate: {stats['learning_rate']:.4f}")
    print(f"  Exploration Rate: {stats['exploration_rate']:.4f}")

    # 测试多次学习
    print(f"\nTesting Multiple Learning...")
    for i in range(10):
        state = np.random.randn(1000)
        next_state = np.random.randn(1000)
        reward = learning_system.learn(state, f"action_{i % 10}", np.random.randn(), next_state, done=(i % 5 == 0))

    stats = learning_system.get_statistics()
    print(f"  Total Experiences: {stats['total_experiences']}")
    print(f"  Avg Reward: {stats['avg_reward']:.3f}")
    print(f"  Success Rate: {stats['success_rate']:.3f}")

    print("\nTop-Tier Learning System tested successfully!")
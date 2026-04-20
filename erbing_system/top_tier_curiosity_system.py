# -*- coding: utf-8 -*-
"""
顶配好奇心系统 - Top-Tier Curiosity System
实现主动探索，优化学习驱动，实现好奇心衰减，优化新奇性检测
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CuriosityType(Enum):
    """好奇心类型"""
    EXPLORATORY = "exploratory"  # 探索性
    LEARNING = "learning"  # 学习性
    SOCIAL = "social"  # 社交性
    CREATIVE = "creative"  # 创造性
    PROBLEM_SOLVING = "problem_solving"  # 问题解决


@dataclass
class CuriosityState:
    """好奇心状态"""
    curiosity_level: float = 0.5
    exploration_drive: float = 0.5
    learning_drive: float = 0.5
    novelty_threshold: float = 0.3
    curiosity_decay: float = 0.01
    curiosity_types: Dict[str, float] = field(default_factory=dict)
    exploration_history: List[str] = field(default_factory=list)
    learning_history: List[str] = field(default_factory=list)


@dataclass
class ExplorationTarget:
    """探索目标"""
    id: str
    target: str
    novelty_score: float
    importance: float
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "pending"


class TopTierCuriositySystem:
    """顶配好奇心系统"""

    def __init__(self, max_targets: int = 10000):
        self.max_targets = max_targets

        # 好奇心状态
        self.curiosity_state = CuriosityState()

        # 探索目标
        self.exploration_targets: Dict[str, ExplorationTarget] = {}

        # 新奇性检测
        self.novelty_detector: Dict[str, float] = {}

        # 好奇心衰减
        self.decay_rate = 0.01

        # 主动探索
        self.active_exploration: bool = False
        self.exploration_strategy: str = "random"

        logger.info(f"Top-Tier Curiosity System initialized with {max_targets} max targets")

    def evaluate_novelty(self, input_text: str) -> Dict:
        """评估新奇性"""
        # 计算新奇性分数
        novelty_score = self._calculate_novelty(input_text)

        # 更新好奇心水平
        self.curiosity_state.curiosity_level = novelty_score

        # 更新新奇性检测器
        self._update_novelty_detector(input_text, novelty_score)

        # 返回状态
        return self.get_state()

    def _calculate_novelty(self, input_text: str) -> float:
        """计算新奇性"""
        # 基础新奇性
        base_novelty = 0.5

        # 检测关键词
        novelty_keywords = {
            "新": 0.8,
            "new": 0.8,
            "学习": 0.7,
            "learn": 0.7,
            "探索": 0.9,
            "explore": 0.9,
            "发现": 0.8,
            "discover": 0.8,
            "创新": 0.9,
            "innovate": 0.9,
            "未知": 0.9,
            "unknown": 0.9,
        }

        # 检测关键词
        text_lower = input_text.lower()
        for keyword, score in novelty_keywords.items():
            if keyword in text_lower:
                base_novelty = max(base_novelty, score)

        # 检测历史
        if input_text in self.novelty_detector:
            # 如果已经见过，降低新奇性
            base_novelty *= 0.5

        return min(base_novelty, 1.0)

    def _update_novelty_detector(self, input_text: str, novelty_score: float):
        """更新新奇性检测器"""
        # 更新检测器
        self.novelty_detector[input_text] = novelty_score

        # 限制检测器大小
        if len(self.novelty_detector) > 10000:
            # 删除最旧的条目
            oldest_key = min(self.novelty_detector.keys(), key=lambda k: self.novelty_detector[k])
            del self.novelty_detector[oldest_key]

    def explore(self, target: str, strategy: str = "random") -> ExplorationTarget:
        """探索"""
        # 创建探索目标
        target_id = f"target-{len(self.exploration_targets)}"

        # 计算新奇性分数
        novelty_score = self._calculate_novelty(target)

        # 计算重要性
        importance = self._calculate_importance(target, novelty_score)

        # 创建探索目标
        exploration_target = ExplorationTarget(
            id=target_id,
            target=target,
            novelty_score=novelty_score,
            importance=importance
        )

        # 添加到探索目标
        self.exploration_targets[target_id] = exploration_target

        # 更新探索历史
        self.curiosity_state.exploration_history.append(target)

        # 更新探索驱动
        self.curiosity_state.exploration_drive = min(1.0, self.curiosity_state.exploration_drive + 0.05)

        # 设置探索策略
        self.exploration_strategy = strategy

        logger.debug(f"Exploring: {target} with strategy {strategy}")

        return exploration_target

    def _calculate_importance(self, target: str, novelty_score: float) -> float:
        """计算重要性"""
        # 基础重要性
        base_importance = 0.5

        # 根据新奇性调整
        base_importance += novelty_score * 0.3

        # 根据目标长度调整
        base_importance += min(len(target) / 100, 0.2)

        return min(base_importance, 1.0)

    def learn(self, topic: str, success: bool = True):
        """学习"""
        # 添加到学习历史
        self.curiosity_state.learning_history.append(topic)

        # 更新学习驱动
        if success:
            self.curiosity_state.learning_drive = min(1.0, self.curiosity_state.learning_drive + 0.1)
        else:
            self.curiosity_state.learning_drive = max(0.0, self.curiosity_state.learning_drive - 0.05)

        # 更新好奇心类型
        self._update_curiosity_types(topic)

        logger.debug(f"Learned: {topic} (Success: {success})")

    def _update_curiosity_types(self, topic: str):
        """更新好奇心类型"""
        # 简单的类型检测
        type_keywords = {
            CuriosityType.EXPLORATORY: ["探索", "发现", "explore", "discover"],
            CuriosityType.LEARNING: ["学习", "学习", "learn", "study"],
            CuriosityType.SOCIAL: ["社交", "交流", "social", "interact"],
            CuriosityType.CREATIVE: ["创造", "创新", "create", "innovate"],
            CuriosityType.PROBLEM_SOLVING: ["解决", "问题", "solve", "problem"],
        }

        # 检测类型
        text_lower = topic.lower()
        for curiosity_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    type_name = curiosity_type.value
                    self.curiosity_state.curiosity_types[type_name] = \
                        self.curiosity_state.curiosity_types.get(type_name, 0.0) + 0.1
                    break

    def decay_curiosity(self):
        """好奇心衰减"""
        # 应用衰减
        self.curiosity_state.curiosity_level = max(0.0, self.curiosity_state.curiosity_level - self.decay_rate)

        # 衰减探索驱动
        self.curiosity_state.exploration_drive = max(0.0, self.curiosity_state.exploration_drive - self.decay_rate * 0.5)

        # 衰减学习驱动
        self.curiosity_state.learning_drive = max(0.0, self.curiosity_state.learning_drive - self.decay_rate * 0.3)

        logger.debug(f"Curiosity decayed to {self.curiosity_state.curiosity_level:.3f}")

    def get_state(self) -> Dict:
        """获取状态"""
        return {
            'curiosity_level': self.curiosity_state.curiosity_level,
            'exploration_drive': self.curiosity_state.exploration_drive,
            'learning_drive': self.curiosity_state.learning_drive,
            'novelty_threshold': self.curiosity_state.novelty_threshold,
            'curiosity_types': self.curiosity_state.curiosity_types.copy(),
        }

    def learn_from_experience(self, experience: str, success: bool):
        """从经验中学习"""
        if success:
            self.learn(experience, success)
            self.curiosity_state.curiosity_level = min(1.0, self.curiosity_state.curiosity_level + 0.05)
        else:
            self.curiosity_state.curiosity_level = max(0.0, self.curiosity_state.curiosity_level - 0.02)

    def evolve(self):
        """进化"""
        # 好奇心系统进化：提高好奇心水平
        self.curiosity_state.curiosity_level = min(1.0, self.curiosity_state.curiosity_level + 0.01)

    def increase_exploration_drive(self):
        """提高探索驱动"""
        self.curiosity_state.exploration_drive = min(1.0, self.curiosity_state.exploration_drive + 0.05)

    def increase_learning_drive(self):
        """提高学习驱动"""
        self.curiosity_state.learning_drive = min(1.0, self.curiosity_state.learning_drive + 0.05)

    def get_balance(self) -> float:
        """获取平衡性"""
        return (self.curiosity_state.exploration_drive + self.curiosity_state.learning_drive) / 2

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            'total_targets': len(self.exploration_targets),
            'max_targets': self.max_targets,
            'novelty_detector_size': len(self.novelty_detector),
            'exploration_history_length': len(self.curiosity_state.exploration_history),
            'learning_history_length': len(self.curiosity_state.learning_history),
            'curiosity_types_count': len(self.curiosity_state.curiosity_types),
            'avg_curiosity_level': self.curiosity_state.curiosity_level,
        }


if __name__ == "__main__":
    # 测试顶配好奇心系统
    print("Testing Top-Tier Curiosity System...")

    # 创建顶配好奇心系统
    curiosity_system = TopTierCuriositySystem(max_targets=10000)

    print(f"\nCuriosity System Statistics:")
    stats = curiosity_system.get_statistics()
    print(f"  Total Targets: {stats['total_targets']}")
    print(f"  Max Targets: {stats['max_targets']}")
    print(f"  Novelty Detector Size: {stats['novelty_detector_size']}")
    print(f"  Exploration History: {stats['exploration_history_length']}")
    print(f"  Learning History: {stats['learning_history_length']}")

    # 测试新奇性评估
    print(f"\nTesting Evaluate Novelty...")
    response = curiosity_system.evaluate_novelty("I want to learn something new")
    print(f"  Curiosity Level: {response['curiosity_level']:.2f}")
    print(f"  Exploration Drive: {response['exploration_drive']:.2f}")
    print(f"  Learning Drive: {response['learning_drive']:.2f}")

    # 测试探索
    print(f"\nTesting Explore...")
    target = curiosity_system.explore("Explore new technologies")
    print(f"  Target ID: {target.id}")
    print(f"  Target: {target.target}")
    print(f"  Novelty Score: {target.novelty_score:.2f}")
    print(f"  Importance: {target.importance:.2f}")

    # 测试学习
    print(f"\nTesting Learn...")
    curiosity_system.learn("Learn Python programming", success=True)
    curiosity_system.learn("Learn machine learning", success=True)
    print(f"  Learning History: {curiosity_system.curiosity_state.learning_history}")
    print(f"  Learning Drive: {curiosity_system.curiosity_state.learning_drive:.2f}")

    # 测试好奇心衰减
    print(f"\nTesting Curiosity Decay...")
    curiosity_system.decay_curiosity()
    print(f"  Curiosity Level: {curiosity_system.curiosity_state.curiosity_level:.3f}")

    # 测试好奇心类型
    print(f"\nTesting Curiosity Types...")
    curiosity_system.learn("Explore new places", success=True)
    curiosity_system.learn("Create new things", success=True)
    print(f"  Curiosity Types: {curiosity_system.curiosity_state.curiosity_types}")

    print("\nTop-Tier Curiosity System tested successfully!")
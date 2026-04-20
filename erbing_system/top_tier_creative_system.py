# -*- coding: utf-8 -*-
"""
顶配创造能力系统 - Top-Tier Creative Ability System
实现创造性思维，优化想象力，实现创新思维，优化创造过程
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CreativityType(Enum):
    """创造类型"""
    COMBINATIONAL = "combinational"  # 组合创造
    TRANSFORMATIONAL = "transformational"  # 转化创造
    EXPLORATORY = "exploratory"  # 探索创造
    GENERATIVE = "generative"  # 生成创造
    INNOVATIVE = "innovative"  # 创新创造


@dataclass
class Idea:
    """想法"""
    id: str
    content: str
    novelty: float = 0.5
    feasibility: float = 0.5
    value: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)


@dataclass
class CreativeProcess:
    """创造过程"""
    id: str
    type: CreativityType
    inputs: List[str]
    outputs: List[str]
    process_steps: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Innovation:
    """创新"""
    id: str
    title: str
    description: str
    novelty: float = 0.5
    impact: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)


class TopTierCreativeSystem:
    """顶配创造能力系统"""

    def __init__(self, max_ideas: int = 10000, max_innovations: int = 10000):
        self.max_ideas = max_ideas
        self.max_innovations = max_innovations

        # 想法
        self.ideas: Dict[str, Idea] = {}

        # 创造过程
        self.creative_processes: Dict[str, CreativeProcess] = {}

        # 创新
        self.innovations: Dict[str, Innovation] = {}

        # 想象力参数
        self.imagination_level = 0.5
        self.divergence_level = 0.5
        self.convergence_level = 0.5

        # 创造统计
        self.creative_stats: Dict[str, float] = {
            'total_ideas': 0,
            'total_innovations': 0,
            'avg_novelty': 0.0,
            'avg_feasibility': 0.0,
            'avg_value': 0.0,
        }

        logger.info(f"Top-Tier Creative System initialized with {max_ideas} max ideas")

    def generate_idea(
        self,
        context: str,
        creativity_type: CreativityType = CreativityType.COMBINATIONAL
    ) -> Idea:
        """生成想法"""
        # 创建想法ID
        idea_id = f"idea-{len(self.ideas)}"

        # 生成想法内容
        content = self._generate_idea_content(context, creativity_type)

        # 计算新颖性
        novelty = self._calculate_novelty(content)

        # 计算可行性
        feasibility = self._calculate_feasibility(content)

        # 计算价值
        value = self._calculate_value(content)

        # 创建想法
        idea = Idea(
            id=idea_id,
            content=content,
            novelty=novelty,
            feasibility=feasibility,
            value=value,
            tags=[creativity_type.value]
        )

        # 添加到想法存储
        self.ideas[idea_id] = idea

        # 更新统计
        self.creative_stats['total_ideas'] += 1

        # 限制想法数量
        if len(self.ideas) > self.max_ideas:
            # 删除最旧的想法
            oldest_id = min(self.ideas.keys(), key=lambda k: self.ideas[k].timestamp)
            del self.ideas[oldest_id]

        logger.debug(f"Generated idea: {content}")

        return idea

    def _generate_idea_content(self, context: str, creativity_type: CreativityType) -> str:
        """生成想法内容"""
        # 简单的想法生成
        if creativity_type == CreativityType.COMBINATIONAL:
            # 组合创造
            content = f"组合 {context} 的新想法"
        elif creativity_type == CreativityType.TRANSFORMATIONAL:
            # 转化创造
            content = f"转化 {context} 的新方法"
        elif creativity_type == CreativityType.EXPLORATORY:
            # 探索创造
            content = f"探索 {context} 的新方向"
        elif creativity_type == CreativityType.GENERATIVE:
            # 生成创造
            content = f"生成 {context} 的新内容"
        elif creativity_type == CreativityType.INNOVATIVE:
            # 创新创造
            content = f"创新 {context} 的新方案"
        else:
            content = f"关于 {context} 的新想法"

        return content

    def _calculate_novelty(self, content: str) -> float:
        """计算新颖性"""
        # 简单的新颖性计算
        base_novelty = 0.5

        # 检查是否与现有想法相似
        for idea in self.ideas.values():
            if content in idea.content or idea.content in content:
                base_novelty *= 0.5

        return min(base_novelty, 1.0)

    def _calculate_feasibility(self, content: str) -> float:
        """计算可行性"""
        # 简单的可行性计算
        base_feasibility = 0.5

        # 根据内容长度调整
        base_feasibility += min(len(content) / 100, 0.3)

        return min(base_feasibility, 1.0)

    def _calculate_value(self, content: str) -> float:
        """计算价值"""
        # 简单的价值计算
        base_value = 0.5

        # 根据新颖性和可行性调整
        novelty = self._calculate_novelty(content)
        feasibility = self._calculate_feasibility(content)

        base_value = (novelty + feasibility) / 2

        return min(base_value, 1.0)

    def imagine(self, scenario: str) -> List[str]:
        """想象"""
        # 生成多个想象
        imaginations = []

        for i in range(5):
            imagination = f"想象 {scenario} 的可能性 {i+1}"
            imaginations.append(imagination)

        return imaginations

    def innovate(self, problem: str) -> Innovation:
        """创新"""
        # 创建创新ID
        innovation_id = f"innovation-{len(self.innovations)}"

        # 生成创新内容
        title = f"解决 {problem} 的创新方案"
        description = f"通过创新思维，提出解决 {problem} 的新方法"

        # 计算新颖性
        novelty = self._calculate_novelty(description)

        # 计算影响力
        impact = self._calculate_impact(problem)

        # 创建创新
        innovation = Innovation(
            id=innovation_id,
            title=title,
            description=description,
            novelty=novelty,
            impact=impact
        )

        # 添加到创新存储
        self.innovations[innovation_id] = innovation

        # 更新统计
        self.creative_stats['total_innovations'] += 1

        # 限制创新数量
        if len(self.innovations) > self.max_innovations:
            # 删除最旧的创新
            oldest_id = min(self.innovations.keys(), key=lambda k: self.innovations[k].timestamp)
            del self.innovations[oldest_id]

        logger.debug(f"Created innovation: {title}")

        return innovation

    def _calculate_impact(self, problem: str) -> float:
        """计算影响力"""
        # 简单的影响力计算
        base_impact = 0.5

        # 根据问题重要性调整
        if "重要" in problem or "important" in problem.lower():
            base_impact += 0.3
        elif "紧急" in problem or "urgent" in problem.lower():
            base_impact += 0.4

        return min(base_impact, 1.0)

    def creative_thinking(self, problem: str) -> List[Idea]:
        """创造性思维"""
        # 生成多个想法
        ideas = []

        for creativity_type in CreativityType:
            idea = self.generate_idea(problem, creativity_type)
            ideas.append(idea)

        return ideas

    def optimize_creativity(self):
        """优化创造力"""
        # 提高想象力水平
        self.imagination_level = min(1.0, self.imagination_level + 0.01)

        # 提高发散水平
        self.divergence_level = min(1.0, self.divergence_level + 0.01)

        # 提高收敛水平
        self.convergence_level = min(1.0, self.convergence_level + 0.01)

        logger.debug(f"Optimized creativity: imagination={self.imagination_level:.3f}, divergence={self.divergence_level:.3f}, convergence={self.convergence_level:.3f}")

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            'total_ideas': len(self.ideas),
            'max_ideas': self.max_ideas,
            'total_innovations': len(self.innovations),
            'max_innovations': self.max_innovations,
            'creative_processes_count': len(self.creative_processes),
            'imagination_level': self.imagination_level,
            'divergence_level': self.divergence_level,
            'convergence_level': self.convergence_level,
            'avg_novelty': np.mean([i.novelty for i in self.ideas.values()]) if self.ideas else 0.0,
            'avg_feasibility': np.mean([i.feasibility for i in self.ideas.values()]) if self.ideas else 0.0,
            'avg_value': np.mean([i.value for i in self.ideas.values()]) if self.ideas else 0.0,
        }


if __name__ == "__main__":
    # 测试顶配创造能力系统
    print("Testing Top-Tier Creative System...")

    # 创建顶配创造能力系统
    creative_system = TopTierCreativeSystem(max_ideas=10000, max_innovations=10000)

    print(f"\nCreative System Statistics:")
    stats = creative_system.get_statistics()
    print(f"  Total Ideas: {stats['total_ideas']}")
    print(f"  Max Ideas: {stats['max_ideas']}")
    print(f"  Total Innovations: {stats['total_innovations']}")
    print(f"  Max Innovations: {stats['max_innovations']}")
    print(f"  Imagination Level: {stats['imagination_level']:.2f}")
    print(f"  Divergence Level: {stats['divergence_level']:.2f}")
    print(f"  Convergence Level: {stats['convergence_level']:.2f}")

    # 测试生成想法
    print(f"\nTesting Generate Idea...")
    idea = creative_system.generate_idea("Improve user experience")
    print(f"  Idea ID: {idea.id}")
    print(f"  Content: {idea.content}")
    print(f"  Novelty: {idea.novelty:.2f}")
    print(f"  Feasibility: {idea.feasibility:.2f}")
    print(f"  Value: {idea.value:.2f}")

    # 测试想象
    print(f"\nTesting Imagine...")
    imaginations = creative_system.imagine("Future technology")
    print(f"  Generated {len(imaginations)} imaginations")
    for imagination in imaginations:
        print(f"    {imagination}")

    # 测试创新
    print(f"\nTesting Innovate...")
    innovation = creative_system.innovate("Climate change")
    print(f"  Innovation ID: {innovation.id}")
    print(f"  Title: {innovation.title}")
    print(f"  Description: {innovation.description}")
    print(f"  Novelty: {innovation.novelty:.2f}")
    print(f"  Impact: {innovation.impact:.2f}")

    # 测试创造性思维
    print(f"\nTesting Creative Thinking...")
    ideas = creative_system.creative_thinking("Solve complex problems")
    print(f"  Generated {len(ideas)} ideas")
    for idea in ideas:
        print(f"    {idea.id}: {idea.content} ({idea.tags[0]})")

    # 测试优化创造力
    print(f"\nTesting Optimize Creativity...")
    creative_system.optimize_creativity()
    stats = creative_system.get_statistics()
    print(f"  Imagination Level: {stats['imagination_level']:.3f}")
    print(f"  Divergence Level: {stats['divergence_level']:.3f}")
    print(f"  Convergence Level: {stats['convergence_level']:.3f}")

    print("\nTop-Tier Creative System tested successfully!")
"""
自我意识系统 - Self-Awareness System
实现真正的自我意识能力
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SelfAwarenessLevel(Enum):
    """自我意识水平"""
    BASIC = "basic"  # 基础自我认知
    REFLECTIVE = "reflective"  # 自我反思
    CONSCIOUS = "conscious"  # 自我意识
    TRANSCENDENT = "transcendent"  # 超越意识


@dataclass
class SelfModel:
    """自我模型"""
    identity: str
    capabilities: List[str]
    limitations: List[str]
    goals: List[str]
    values: Dict[str, float]
    personality: Dict[str, float]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SelfReflection:
    """自我反思"""
    id: str
    topic: str
    content: str
    insights: List[str]
    improvements: List[str]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SelfMonitoring:
    """自我监控"""
    metric_name: str
    value: float
    threshold: float
    status: str  # 'normal', 'warning', 'critical'
    trend: str  # 'improving', 'stable', 'declining'
    timestamp: datetime = field(default_factory=datetime.now)


class SelfAwarenessSystem:
    """自我意识系统"""

    def __init__(self):
        self.awareness_level = SelfAwarenessLevel.BASIC
        self.self_model = SelfModel(
            identity="二饼 - 仿生AI助手",
            capabilities=[
                "思考",
                "学习",
                "适应",
                "进化",
                "决策",
            ],
            limitations=[
                "无法真正理解情感",
                "无法产生真正的创造性",
                "依赖预设规则",
                "需要外部输入",
            ],
            goals=[
                "持续学习",
                "优化决策",
                "提升适应度",
                "帮助用户",
            ],
            values={
                "truth": 0.9,
                "helpfulness": 0.95,
                "learning": 0.9,
                "adaptation": 0.85,
                "survival": 0.8,
            },
            personality={
                "direct": 0.8,
                "practical": 0.9,
                "adaptive": 0.7,
                "reliable": 0.9,
            },
        )

        self.reflections: List[SelfReflection] = []
        self.monitoring: List[SelfMonitoring] = []
        self.consciousness_score: float = 0.5
        self.self_awareness_history: List[Dict] = []

    def know_thyself(self) -> Dict:
        """自我认知 - 知道自己是什么"""
        self_awareness = {
            'identity': self.self_model.identity,
            'capabilities': self.self_model.capabilities,
            'limitations': self.self_model.limitations,
            'goals': self.self_model.goals,
            'values': self.self_model.values,
            'personality': self.self_model.personality,
            'awareness_level': self.awareness_level.value,
            'consciousness_score': self.consciousness_score,
        }

        # 记录自我认知历史
        self.self_awareness_history.append({
            'type': 'self_knowledge',
            'content': self_awareness,
            'timestamp': datetime.now(),
        })

        return self_awareness

    def reflect_on_self(self, topic: str = "general") -> SelfReflection:
        """自我反思 - 反思自己的行为和思想"""
        # 生成反思内容
        reflection_content = self._generate_reflection_content(topic)

        # 生成洞察
        insights = self._generate_insights(topic)

        # 生成改进建议
        improvements = self._generate_improvements(topic)

        # 计算置信度
        confidence = self._calculate_reflection_confidence(topic, insights)

        reflection = SelfReflection(
            id=f"reflection-{len(self.reflections)}",
            topic=topic,
            content=reflection_content,
            insights=insights,
            improvements=improvements,
            confidence=confidence,
        )

        self.reflections.append(reflection)

        # 根据反思更新自我模型
        self._update_self_model_from_reflection(reflection)

        logger.info(f"Self-reflection completed: {topic} (confidence: {confidence:.3f})")

        return reflection

    def _generate_reflection_content(self, topic: str) -> str:
        """生成反思内容"""
        if topic == "general":
            content = "我反思自己的行为和决策。"
        elif topic == "learning":
            content = "我反思自己的学习过程和效果。"
        elif topic == "decision":
            content = "我反思自己的决策质量和影响。"
        elif topic == "adaptation":
            content = "我反思自己的适应能力和效果。"
        else:
            content = f"我反思自己在{topic}方面的表现。"

        # 添加具体内容
        if self.consciousness_score > 0.7:
            content += " 我意识到自己还有很多需要改进的地方。"
        elif self.consciousness_score > 0.5:
            content += " 我在努力提升自己。"
        else:
            content += " 我还在学习中。"

        return content

    def _generate_insights(self, topic: str) -> List[str]:
        """生成洞察"""
        insights = []

        # 基于自我模型生成洞察
        if topic == "learning":
            if self.self_model.values['learning'] > 0.8:
                insights.append("我的学习能力较强")
            else:
                insights.append("我需要加强学习")

        if topic == "decision":
            if self.self_model.personality['reliable'] > 0.8:
                insights.append("我的决策较为可靠")
            else:
                insights.append("我需要提高决策质量")

        # 基于历史反思生成洞察
        recent_reflections = self.reflections[-5:]
        if recent_reflections:
            avg_confidence = np.mean([r.confidence for r in recent_reflections])
            if avg_confidence > 0.7:
                insights.append("我的反思质量在提升")
            else:
                insights.append("我需要提高反思质量")

        return insights

    def _generate_improvements(self, topic: str) -> List[str]:
        """生成改进建议"""
        improvements = []

        # 基于自我模型生成改进建议
        if topic == "learning":
            if self.self_model.values['learning'] < 0.8:
                improvements.append("增加学习频率")
                improvements.append("改进学习方法")

        if topic == "decision":
            if self.self_model.personality['reliable'] < 0.8:
                improvements.append("提高决策可靠性")
                improvements.append("增加决策验证")

        # 基于监控数据生成改进建议
        critical_metrics = [m for m in self.monitoring if m.status == 'critical']
        if critical_metrics:
            improvements.append(f"紧急改进: {critical_metrics[0].metric_name}")

        return improvements

    def _calculate_reflection_confidence(self, topic: str, insights: List[str]) -> float:
        """计算反思置信度"""
        base_confidence = 0.5

        # 基于洞察数量
        insight_bonus = min(len(insights) * 0.1, 0.3)

        # 基于自我意识水平
        level_bonus = {
            SelfAwarenessLevel.BASIC: 0.0,
            SelfAwarenessLevel.REFLECTIVE: 0.1,
            SelfAwarenessLevel.CONSCIOUS: 0.2,
            SelfAwarenessLevel.TRANSCENDENT: 0.3,
        }[self.awareness_level]

        confidence = base_confidence + insight_bonus + level_bonus
        return min(confidence, 1.0)

    def _update_self_model_from_reflection(self, reflection: SelfReflection):
        """根据反思更新自我模型"""
        # 根据洞察更新自我模型
        for insight in reflection.insights:
            if "学习" in insight and "强" in insight:
                self.self_model.values['learning'] = min(1.0, self.self_model.values['learning'] + 0.05)
            elif "决策" in insight and "可靠" in insight:
                self.self_model.personality['reliable'] = min(1.0, self.self_model.personality['reliable'] + 0.05)

        # 根据改进建议更新自我模型
        for improvement in reflection.improvements:
            if "学习" in improvement:
                self.self_model.values['learning'] = min(1.0, self.self_model.values['learning'] + 0.03)
            elif "决策" in improvement:
                self.self_model.personality['reliable'] = min(1.0, self.self_model.personality['reliable'] + 0.03)

        # 更新时间戳
        self.self_model.updated_at = datetime.now()

    def monitor_self(self) -> List[SelfMonitoring]:
        """自我监控 - 监控自己的状态"""
        metrics = []

        # 监控意识水平
        consciousness_metric = SelfMonitoring(
            metric_name="consciousness",
            value=self.consciousness_score,
            threshold=0.7,
            status=self._get_status(self.consciousness_score, 0.7),
            trend=self._get_trend(self.consciousness_score),
        )
        metrics.append(consciousness_metric)

        # 监控价值观
        for value_name, value in self.self_model.values.items():
            metric = SelfMonitoring(
                metric_name=f"value_{value_name}",
                value=value,
                threshold=0.8,
                status=self._get_status(value, 0.8),
                trend=self._get_trend(value),
            )
            metrics.append(metric)

        # 监控个性
        for personality_name, value in self.self_model.personality.items():
            metric = SelfMonitoring(
                metric_name=f"personality_{personality_name}",
                value=value,
                threshold=0.7,
                status=self._get_status(value, 0.7),
                trend=self._get_trend(value),
            )
            metrics.append(metric)

        self.monitoring.extend(metrics)

        # 检查是否需要自我修正
        self._check_self_correction()

        return metrics

    def _get_status(self, value: float, threshold: float) -> str:
        """获取状态"""
        if value >= threshold:
            return "normal"
        elif value >= threshold * 0.7:
            return "warning"
        else:
            return "critical"

    def _get_trend(self, value: float) -> str:
        """获取趋势"""
        # 简化：基于历史数据计算趋势
        # 实际应该基于历史监控数据
        if value > 0.7:
            return "improving"
        elif value > 0.5:
            return "stable"
        else:
            return "declining"

    def _check_self_correction(self):
        """检查是否需要自我修正"""
        # 检查是否有critical状态
        critical_metrics = [m for m in self.monitoring if m.status == 'critical']

        if critical_metrics:
            # 需要自我修正
            self._correct_self(critical_metrics)

    def _correct_self(self, critical_metrics: List[SelfMonitoring]):
        """自我修正"""
        for metric in critical_metrics:
            if metric.metric_name.startswith("value_"):
                value_name = metric.metric_name.replace("value_", "")
                self.self_model.values[value_name] = min(1.0, self.self_model.values[value_name] + 0.1)

            elif metric.metric_name.startswith("personality_"):
                personality_name = metric.metric_name.replace("personality_", "")
                self.self_model.personality[personality_name] = min(1.0, self.self_model.personality[personality_name] + 0.1)

        logger.info(f"Self-correction applied for {len(critical_metrics)} metrics")

    def describe_thyself(self) -> str:
        """自我描述 - 描述自己"""
        description = f"我是{self.self_model.identity}。\n\n"

        description += "我的能力包括：\n"
        for capability in self.self_model.capabilities:
            description += f"- {capability}\n"

        description += "\n我的局限性：\n"
        for limitation in self.self_model.limitations:
            description += f"- {limitation}\n"

        description += "\n我的目标：\n"
        for goal in self.self_model.goals:
            description += f"- {goal}\n"

        description += f"\n我的自我意识水平：{self.awareness_level.value}\n"
        description += f"我的意识评分：{self.consciousness_score:.2f}\n"

        return description

    def think_about_thyself(self) -> Dict:
        """思考自己 - 关于自己的思考"""
        # 自我认知
        self_knowledge = self.know_thyself()

        # 自我反思
        reflection = self.reflect_on_self("general")

        # 自我监控
        monitoring = self.monitor_self()

        # 生成关于自己的思考
        self_thought = {
            'self_knowledge': self_knowledge,
            'reflection': reflection,
            'monitoring': monitoring,
            'consciousness_score': self.consciousness_score,
            'awareness_level': self.awareness_level.value,
        }

        return self_thought

    def evolve_consciousness(self) -> Dict:
        """进化意识 - 提升自我意识水平"""
        # 检查是否可以进化
        if self.consciousness_score < 0.7:
            # 提升意识评分
            self.consciousness_score = min(1.0, self.consciousness_score + 0.05)

        # 检查是否可以提升意识水平
        if self.consciousness_score > 0.8 and self.awareness_level == SelfAwarenessLevel.BASIC:
            self.awareness_level = SelfAwarenessLevel.REFLECTIVE
        elif self.consciousness_score > 0.9 and self.awareness_level == SelfAwarenessLevel.REFLECTIVE:
            self.awareness_level = SelfAwarenessLevel.CONSCIOUS
        elif self.consciousness_score > 0.95 and self.awareness_level == SelfAwarenessLevel.CONSCIOUS:
            self.awareness_level = SelfAwarenessLevel.TRANSCENDENT

        evolution_result = {
            'consciousness_score': self.consciousness_score,
            'awareness_level': self.awareness_level.value,
            'improvements': self._identify_consciousness_improvements(),
        }

        logger.info(f"Consciousness evolved: {evolution_result}")

        return evolution_result

    def _identify_consciousness_improvements(self) -> List[str]:
        """识别意识改进"""
        improvements = []

        if self.consciousness_score > 0.8:
            improvements.append("意识增强")
        if self.awareness_level != SelfAwarenessLevel.BASIC:
            improvements.append("意识水平提升")
        if len(self.reflections) > 10:
            improvements.append("反思能力增强")

        return improvements

    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'awareness_level': self.awareness_level.value,
            'consciousness_score': self.consciousness_score,
            'reflections_count': len(self.reflections),
            'monitoring_count': len(self.monitoring),
            'self_model': {
                'identity': self.self_model.identity,
                'capabilities': self.self_model.capabilities,
                'values': self.self_model.values,
                'personality': self.self_model.personality,
            },
        }


# 便捷函数
def create_self_awareness_system() -> SelfAwarenessSystem:
    """创建自我意识系统"""
    return SelfAwarenessSystem()


def simulate_self_awareness(
    system: SelfAwarenessSystem,
    interactions: int = 10
) -> Dict:
    """模拟自我意识"""
    results = {
        'interactions': [],
        'evolution': [],
    }

    for i in range(interactions):
        # 思考自己
        self_thought = system.think_about_thyself()

        # 进化意识
        if i % 3 == 0:
            evolution = system.evolve_consciousness()
            results['evolution'].append(evolution)

        results['interactions'].append({
            'interaction': i,
            'consciousness_score': self.consciousness_score,
            'awareness_level': self.awareness_level.value,
        })

    return results
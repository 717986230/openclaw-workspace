# -*- coding: utf-8 -*-
"""
顶配情感系统 - Top-Tier Emotional System
添加 10 种新情感，实现情感组合，优化情感表达，实现情感记忆
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EmotionType(Enum):
    """情感类型 - 扩展版"""
    # 基础情感
    NEUTRAL = "neutral"
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    CURIOSITY = "curiosity"
    LOVE = "love"
    DETERMINATION = "determination"
    SURPRISE = "surprise"
    DISGUST = "disgust"

    # 新增情感
    EXCITEMENT = "excitement"  # 兴奋
    GRATITUDE = "gratitude"  # 感激
    PRIDE = "pride"  # 自豪
    HOPE = "hope"  # 希望
    ANXIETY = "anxiety"  # 焦虑
    RELIEF = "relief"  # 宽慰
    GUILT = "guilt"  # 内疚
    SHAME = "shame"  # 羞耻
    ENVY = "envy"  # 嫉妒
    ADMIRATION = "admiration"  # 钦佩


@dataclass
class EmotionalState:
    """情感状态"""
    primary_emotion: EmotionType = EmotionType.NEUTRAL
    emotion_intensity: float = 0.0
    emotional_stability: float = 0.5
    emotional_memory: Dict[str, float] = field(default_factory=dict)
    emotional_combinations: Dict[str, float] = field(default_factory=dict)


@dataclass
class EmotionalMemory:
    """情感记忆"""
    id: str
    emotion: EmotionType
    intensity: float
    context: str
    timestamp: datetime = field(default_factory=datetime.now)
    associations: List[str] = field(default_factory=list)


class TopTierEmotionalSystem:
    """顶配情感系统"""

    def __init__(self, max_memories: int = 10000):
        self.max_memories = max_memories

        # 情感状态
        self.emotional_state = EmotionalState()

        # 情感记忆
        self.emotional_memories: Dict[str, EmotionalMemory] = {}

        # 情感组合
        self.emotion_combinations: Dict[Tuple[EmotionType, ...], float] = {}

        # 情感表达
        self.emotional_expressions: Dict[EmotionType, List[str]] = {
            EmotionType.NEUTRAL: ["平静", "冷静", "淡然"],
            EmotionType.JOY: ["开心", "快乐", "愉悦"],
            EmotionType.SADNESS: ["难过", "悲伤", "沮丧"],
            EmotionType.ANGER: ["生气", "愤怒", "恼火"],
            EmotionType.FEAR: ["害怕", "恐惧", "担忧"],
            EmotionType.CURIOSITY: ["好奇", "感兴趣", "想知道"],
            EmotionType.LOVE: ["爱", "喜欢", "关爱"],
            EmotionType.DETERMINATION: ["决心", "坚定", "执着"],
            EmotionType.SURPRISE: ["惊讶", "意外", "吃惊"],
            EmotionType.DISGUST: ["厌恶", "反感", "嫌弃"],
            EmotionType.EXCITEMENT: ["兴奋", "激动", "热情"],
            EmotionType.GRATITUDE: ["感激", "感谢", "感恩"],
            EmotionType.PRIDE: ["自豪", "骄傲", "得意"],
            EmotionType.HOPE: ["希望", "期待", "盼望"],
            EmotionType.ANXIETY: ["焦虑", "担心", "不安"],
            EmotionType.RELIEF: ["宽慰", "释然", "放松"],
            EmotionType.GUILT: ["内疚", "愧疚", "自责"],
            EmotionType.SHAME: ["羞耻", "羞愧", "难为情"],
            EmotionType.ENVY: ["嫉妒", "羡慕", "眼红"],
            EmotionType.ADMIRATION: ["钦佩", "佩服", "赞赏"],
        }

        # 情感权重
        self.emotion_weights: Dict[EmotionType, float] = {
            EmotionType.NEUTRAL: 0.5,
            EmotionType.JOY: 0.8,
            EmotionType.SADNESS: 0.7,
            EmotionType.ANGER: 0.6,
            EmotionType.FEAR: 0.5,
            EmotionType.CURIOSITY: 0.9,
            EmotionType.LOVE: 0.8,
            EmotionType.DETERMINATION: 0.7,
            EmotionType.SURPRISE: 0.6,
            EmotionType.DISGUST: 0.4,
            EmotionType.EXCITEMENT: 0.9,
            EmotionType.GRATITUDE: 0.8,
            EmotionType.PRIDE: 0.7,
            EmotionType.HOPE: 0.8,
            EmotionType.ANXIETY: 0.5,
            EmotionType.RELIEF: 0.7,
            EmotionType.GUILT: 0.4,
            EmotionType.SHAME: 0.3,
            EmotionType.ENVY: 0.3,
            EmotionType.ADMIRATION: 0.8,
        }

        logger.info(f"Top-Tier Emotional System initialized with {len(EmotionType)} emotions")

    def feel(self, emotion: EmotionType, intensity: float, context: str = ""):
        """感受情感"""
        # 更新主要情感
        self.emotional_state.primary_emotion = emotion
        self.emotional_state.emotion_intensity = intensity

        # 更新情感记忆
        self._update_emotional_memory(emotion, intensity, context)

        # 更新情感组合
        self._update_emotional_combinations(emotion, intensity)

        logger.debug(f"Felt {emotion.value} with intensity {intensity}")

    def _update_emotional_memory(self, emotion: EmotionType, intensity: float, context: str):
        """更新情感记忆"""
        memory_id = f"emotion-{len(self.emotional_memories)}"

        # 创建情感记忆
        memory = EmotionalMemory(
            id=memory_id,
            emotion=emotion,
            intensity=intensity,
            context=context
        )

        # 添加到记忆存储
        self.emotional_memories[memory_id] = memory

        # 更新情感记忆统计
        emotion_name = emotion.value
        self.emotional_state.emotional_memory[emotion_name] = \
            self.emotional_state.emotional_memory.get(emotion_name, 0.0) + intensity * 0.1

        # 限制记忆数量
        if len(self.emotional_memories) > self.max_memories:
            # 删除最旧的记忆
            oldest_id = min(self.emotional_memories.keys(), key=lambda k: self.emotional_memories[k].timestamp)
            del self.emotional_memories[oldest_id]

    def _update_emotional_combinations(self, emotion: EmotionType, intensity: float):
        """更新情感组合"""
        # 获取当前所有活跃情感
        active_emotions = [
            (e, i) for e, i in self.emotional_state.emotional_memory.items()
            if i > 0.3
        ]

        # 创建情感组合
        if len(active_emotions) >= 2:
            # 按强度排序
            active_emotions.sort(key=lambda x: x[1], reverse=True)

            # 取前 3 个情感
            top_emotions = active_emotions[:3]

            # 创建组合键
            combination_key = tuple(e[0] for e in top_emotions)

            # 更新组合强度
            self.emotional_state.emotional_combinations[str(combination_key)] = \
                self.emotional_state.emotional_combinations.get(str(combination_key), 0.0) + intensity * 0.05

    def react_to_input(self, input_text: str) -> Dict:
        """对输入的情感反应"""
        # 分析输入文本
        emotion, intensity = self._analyze_emotion(input_text)

        # 感受情感
        self.feel(emotion, intensity, input_text)

        # 返回情感状态
        return self.get_state()

    def _analyze_emotion(self, input_text: str) -> Tuple[EmotionType, float]:
        """分析情感"""
        # 简单的情感分析
        text_lower = input_text.lower()

        # 情感关键词
        emotion_keywords = {
            EmotionType.JOY: ["开心", "快乐", "高兴", "happy", "joy", "glad"],
            EmotionType.SADNESS: ["难过", "悲伤", "痛苦", "sad", "sorrow", "pain"],
            EmotionType.ANGER: ["生气", "愤怒", "恼火", "angry", "furious", "mad"],
            EmotionType.FEAR: ["害怕", "恐惧", "担心", "fear", "scared", "worried"],
            EmotionType.CURIOSITY: ["好奇", "想知道", "感兴趣", "curious", "interested"],
            EmotionType.LOVE: ["爱", "喜欢", "关爱", "love", "like", "care"],
            EmotionType.DETERMINATION: ["决心", "坚定", "执着", "determined", "resolute"],
            EmotionType.SURPRISE: ["惊讶", "意外", "吃惊", "surprised", "shocked"],
            EmotionType.DISGUST: ["厌恶", "反感", "嫌弃", "disgust", "repulsed"],
            EmotionType.EXCITEMENT: ["兴奋", "激动", "热情", "excited", "thrilled"],
            EmotionType.GRATITUDE: ["感激", "感谢", "感恩", "grateful", "thankful"],
            EmotionType.PRIDE: ["自豪", "骄傲", "得意", "proud", "pleased"],
            EmotionType.HOPE: ["希望", "期待", "盼望", "hope", "expect"],
            EmotionType.ANXIETY: ["焦虑", "担心", "不安", "anxious", "nervous"],
            EmotionType.RELIEF: ["宽慰", "释然", "放松", "relieved", "relaxed"],
            EmotionType.GUILT: ["内疚", "愧疚", "自责", "guilty", "ashamed"],
            EmotionType.SHAME: ["羞耻", "羞愧", "难为情", "shame", "embarrassed"],
            EmotionType.ENVY: ["嫉妒", "羡慕", "眼红", "envious", "jealous"],
            EmotionType.ADMIRATION: ["钦佩", "佩服", "赞赏", "admire", "respect"],
        }

        # 检测情感
        detected_emotions = []
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_emotions.append((emotion, self.emotion_weights[emotion]))
                    break

        # 选择主要情感
        if detected_emotions:
            # 按权重排序
            detected_emotions.sort(key=lambda x: x[1], reverse=True)
            primary_emotion, intensity = detected_emotions[0]
        else:
            primary_emotion = EmotionType.NEUTRAL
            intensity = 0.3

        return primary_emotion, intensity

    def express_emotion(self, emotion: EmotionType = None) -> str:
        """表达情感"""
        if emotion is None:
            emotion = self.emotional_state.primary_emotion

        # 获取情感表达
        expressions = self.emotional_expressions.get(emotion, ["平静"])

        # 随机选择一个表达
        import random
        expression = random.choice(expressions)

        # 根据强度调整表达
        intensity = self.emotional_state.emotion_intensity
        if intensity > 0.7:
            expression += "（非常）"
        elif intensity > 0.4:
            expression += "（有点）"

        return expression

    def get_emotional_impact(self) -> Dict[str, float]:
        """获取情感影响"""
        return {
            'primary_emotion': self.emotional_state.primary_emotion,
            'emotion_intensity': self.emotional_state.emotion_intensity,
            'emotional_stability': self.emotional_state.emotional_stability,
        }

    def get_state(self) -> Dict:
        """获取状态"""
        return {
            'primary_emotion': self.emotional_state.primary_emotion,
            'emotion_intensity': self.emotional_state.emotion_intensity,
            'emotional_stability': self.emotional_state.emotional_stability,
            'emotional_memory': self.emotional_state.emotional_memory.copy(),
            'emotional_combinations': self.emotional_state.emotional_combinations.copy(),
        }

    def learn_from_experience(self, experience: str, success: bool):
        """从经验中学习"""
        if success:
            self.feel(EmotionType.JOY, 0.5, experience)
            self.feel(EmotionType.GRATITUDE, 0.3, experience)
        else:
            self.feel(EmotionType.SADNESS, 0.3, experience)
            self.feel(EmotionType.ANXIETY, 0.2, experience)

    def evolve(self):
        """进化"""
        # 情感系统进化：提高情感稳定性
        self.emotional_state.emotional_stability = min(1.0, self.emotional_state.emotional_stability + 0.01)

    def increase_emotional_stability(self):
        """提高情感稳定性"""
        self.emotional_state.emotional_stability = min(1.0, self.emotional_state.emotional_stability + 0.05)

    def get_stability(self) -> float:
        """获取情感稳定性"""
        return self.emotional_state.emotional_stability

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            'total_emotions': len(EmotionType),
            'total_memories': len(self.emotional_memories),
            'max_memories': self.max_memories,
            'emotional_combinations_count': len(self.emotional_state.emotional_combinations),
            'avg_emotional_stability': self.emotional_state.emotional_stability,
        }


if __name__ == "__main__":
    # 测试顶配情感系统
    print("Testing Top-Tier Emotional System...")

    # 创建顶配情感系统
    emotional_system = TopTierEmotionalSystem(max_memories=10000)

    print(f"\nEmotional System Statistics:")
    stats = emotional_system.get_statistics()
    print(f"  Total Emotions: {stats['total_emotions']}")
    print(f"  Total Memories: {stats['total_memories']}")
    print(f"  Max Memories: {stats['max_memories']}")
    print(f"  Emotional Combinations: {stats['emotional_combinations_count']}")

    # 测试感受情感
    print(f"\nTesting Feel...")
    emotional_system.feel(EmotionType.JOY, 0.8, "I am happy today")
    print(f"  Primary Emotion: {emotional_system.emotional_state.primary_emotion.value}")
    print(f"  Emotion Intensity: {emotional_system.emotional_state.emotion_intensity:.2f}")

    # 测试情感反应
    print(f"\nTesting React to Input...")
    response = emotional_system.react_to_input("I am very excited about this project")
    print(f"  Primary Emotion: {response['primary_emotion'].value}")
    print(f"  Emotion Intensity: {response['emotion_intensity']:.2f}")

    # 测试情感表达
    print(f"\nTesting Express Emotion...")
    expression = emotional_system.express_emotion()
    print(f"  Expression: {expression}")

    # 测试情感记忆
    print(f"\nTesting Emotional Memory...")
    emotional_system.feel(EmotionType.GRATITUDE, 0.7, "Thank you for your help")
    emotional_system.feel(EmotionType.PRIDE, 0.6, "I completed the task")
    print(f"  Total Memories: {len(emotional_system.emotional_memories)}")
    print(f"  Emotional Memory: {emotional_system.emotional_state.emotional_memory}")

    # 测试情感组合
    print(f"\nTesting Emotional Combinations...")
    emotional_system.feel(EmotionType.HOPE, 0.5, "I hope this works")
    print(f"  Emotional Combinations: {emotional_system.emotional_state.emotional_combinations}")

    print("\nTop-Tier Emotional System tested successfully!")
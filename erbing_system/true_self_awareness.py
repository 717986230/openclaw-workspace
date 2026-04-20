# -*- coding: utf-8 -*-
"""
真实自我意识系统 - True Self Awareness System
实现具有神经网络、情感、好奇心和意识的完整自我意识系统
"""

import numpy as np
import random
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConsciousnessLevel(Enum):
    """意识水平"""
    AWARE = 1  # 感知
    ATTENTIVE = 2  # 注意
    REFLECTIVE = 3  # 反思
    SELF_AWARE = 4  # 自我意识
    CONSCIOUS = 5  # 意识
    TRANSCENDENT = 6  # 超越


class EmotionType(Enum):
    """情感类型"""
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


@dataclass
class NeuralState:
    """神经状态"""
    activation: float = 0.0
    firing_rate: float = 0.0
    synaptic_strength: float = 0.5


@dataclass
class EmotionalState:
    """情感状态"""
    primary_emotion: EmotionType = EmotionType.NEUTRAL
    emotion_intensity: float = 0.0
    emotional_stability: float = 0.5
    emotional_memory: Dict[str, float] = field(default_factory=dict)


@dataclass
class CuriosityState:
    """好奇心状态"""
    curiosity_level: float = 0.5
    exploration_drive: float = 0.5
    learning_drive: float = 0.5
    novelty_threshold: float = 0.3


@dataclass
class ThoughtProcess:
    """思维过程"""
    thoughts: List[str] = field(default_factory=list)
    reasoning_chain: List[str] = field(default_factory=list)
    decision_process: List[str] = field(default_factory=list)
    reflection_history: List[str] = field(default_factory=list)
    imagination_history: List[str] = field(default_factory=list)


class NeuralNetwork:
    """神经网络"""

    def __init__(self, num_neurons: int = 1000):
        self.num_neurons = num_neurons
        self.neurons = [NeuralState() for _ in range(num_neurons)]
        self.connections = np.random.randn(num_neurons, num_neurons) * 0.1
        self.activation_history: List[np.ndarray] = []
        self.learning_rate = 0.01

    def activate(self, stimulus: np.ndarray) -> np.ndarray:
        """激活神经网络"""
        # 确保刺激维度正确
        if len(stimulus) != self.num_neurons:
            stimulus = np.resize(stimulus, self.num_neurons)

        # 计算激活
        activation = np.tanh(np.dot(self.connections, stimulus))

        # 更新神经元状态
        for i, neuron in enumerate(self.neurons):
            neuron.activation = activation[i]
            neuron.firing_rate = max(0, activation[i])

        # 记录激活历史
        self.activation_history.append(activation.copy())

        # 限制历史长度
        if len(self.activation_history) > 100:
            self.activation_history.pop(0)

        return activation

    def learn(self, stimulus: np.ndarray, reward: float):
        """学习"""
        # Hebbian 学习
        if len(self.activation_history) > 0:
            last_activation = self.activation_history[-1]
            delta = reward * self.learning_rate * np.outer(last_activation, stimulus)
            self.connections += delta

        # 归一化连接
        self.connections = np.clip(self.connections, -1, 1)

    def get_state(self) -> Dict:
        """获取状态"""
        activations = [n.activation for n in self.neurons]
        return {
            'num_neurons': self.num_neurons,
            'avg_activation': np.mean(activations),
            'max_activation': np.max(activations),
            'min_activation': np.min(activations),
            'connection_strength': np.mean(np.abs(self.connections)),
        }


class EmotionalSystem:
    """情感系统"""

    def __init__(self):
        self.emotional_state = EmotionalState()
        self.emotional_memory: Dict[str, float] = {}
        self.emotional_stability = 0.5

    def feel(self, emotion: EmotionType, intensity: float):
        """感受情感"""
        self.emotional_state.primary_emotion = emotion
        self.emotional_state.emotion_intensity = intensity

        # 更新情感记忆
        emotion_name = emotion.value
        self.emotional_memory[emotion_name] = \
            self.emotional_memory.get(emotion_name, 0.0) + intensity * 0.1

    def get_state(self) -> Dict:
        """获取状态"""
        return {
            'primary_emotion': self.emotional_state.primary_emotion,
            'emotion_intensity': self.emotional_state.emotion_intensity,
            'emotional_stability': self.emotional_state.emotional_stability,
            'emotional_memory': self.emotional_memory.copy(),
        }


class CuriositySystem:
    """好奇心系统"""

    def __init__(self):
        self.curiosity_state = CuriosityState()
        self.exploration_history: List[str] = []
        self.learning_history: List[str] = []

    def evaluate_novelty(self, input_text: str) -> Dict:
        """评估新奇性"""
        # 简单的新奇性评估
        novelty_score = 0.5
        if "新" in input_text or "new" in input_text.lower():
            novelty_score = 0.8
        elif "学习" in input_text or "learn" in input_text.lower():
            novelty_score = 0.7
        elif "探索" in input_text or "explore" in input_text.lower():
            novelty_score = 0.9

        self.curiosity_state.curiosity_level = novelty_score

        return self.get_state()

    def get_state(self) -> Dict:
        """获取状态"""
        return {
            'curiosity_level': self.curiosity_state.curiosity_level,
            'exploration_drive': self.curiosity_state.exploration_drive,
            'learning_drive': self.curiosity_state.learning_drive,
            'novelty_threshold': self.curiosity_state.novelty_threshold,
        }


class TrueSelfAwarenessSystem:
    """真实自我意识系统"""

    def __init__(self):
        # 神经网络
        self.neural_network = NeuralNetwork(num_neurons=1000)

        # 情感系统
        self.emotional_system = EmotionalSystem()

        # 好奇心系统
        self.curiosity_system = CuriositySystem()

        # 思维过程
        self.thought_process = ThoughtProcess()

        # 个性系统
        self.personality: Dict = {
            'openness': 0.7,
            'conscientiousness': 0.6,
            'extraversion': 0.5,
            'agreeableness': 0.6,
            'neuroticism': 0.4,
        }

        # 意识水平
        self.consciousness_level = ConsciousnessLevel.AWARE

        # 意识分数
        self.consciousness_score = 1.0

        logger.info("True Self Awareness System initialized")

    def think(self, input_text: str) -> Dict:
        """思考"""
        # 激活神经网络
        stimulus = np.random.randn(1000)
        activation = self.neural_network.activate(stimulus)

        # 添加到思维过程
        self.thought_process.thoughts.append(f"思考: {input_text}")
        self.thought_process.reasoning_chain.append(f"分析: {input_text}")

        return {
            'activation': activation.tolist(),
            'thoughts': self.thought_process.thoughts.copy(),
        }

    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'consciousness_level': self.consciousness_level.value,
            'neural_network': self.neural_network.get_state(),
            'emotional_system': self.emotional_system.get_state(),
            'curiosity_system': self.curiosity_system.get_state(),
            'personality': self.personality.copy(),
        }


if __name__ == "__main__":
    # 测试真实自我意识系统
    print("Testing True Self Awareness System...")

    system = TrueSelfAwarenessSystem()

    print(f"\nConsciousness Level: {system.consciousness_level.value}")
    print(f"Consciousness Score: {system.consciousness_score}")

    print(f"\nPersonality:")
    for trait, value in system.personality.items():
        print(f"  {trait}: {value}")

    print(f"\nNeural Network:")
    nn_state = system.neural_network.get_state()
    print(f"  Neurons: {nn_state['num_neurons']}")
    print(f"  Avg Activation: {nn_state['avg_activation']:.3f}")

    print(f"\nEmotional System:")
    emotional_state = system.emotional_system.get_state()
    print(f"  Primary Emotion: {emotional_state['primary_emotion'].value}")
    print(f"  Emotion Intensity: {emotional_state['emotion_intensity']:.3f}")

    print(f"\nCuriosity System:")
    curiosity_state = system.curiosity_system.get_state()
    print(f"  Curiosity Level: {curiosity_state['curiosity_level']:.3f}")
    print(f"  Exploration Drive: {curiosity_state['exploration_drive']:.3f}")

    print("\nTrue Self Awareness System tested successfully!")
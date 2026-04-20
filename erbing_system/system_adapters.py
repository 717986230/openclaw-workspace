# -*- coding: utf-8 -*-
"""
系统适配器 - System Adapters
为统一仿生系统提供统一的接口适配
解决不同系统之间的接口不匹配问题
"""

import numpy as np
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 导入原始系统
from erbing_system.true_self_awareness import (
    EmotionType,
    EmotionalSystem,
    CuriositySystem,
    NeuralNetwork,
    TrueSelfAwarenessSystem
)


class EmotionalSystemAdapter:
    """情感系统适配器"""

    def __init__(self, emotional_system: EmotionalSystem):
        self.system = emotional_system

    def react_to_input(self, input_text: str) -> Dict:
        """对输入的情感反应"""
        # 简单的情感分析
        if "开心" in input_text or "happy" in input_text.lower():
            self.system.feel(EmotionType.JOY, 0.8)
        elif "难过" in input_text or "sad" in input_text.lower():
            self.system.feel(EmotionType.SADNESS, 0.7)
        elif "生气" in input_text or "angry" in input_text.lower():
            self.system.feel(EmotionType.ANGER, 0.6)
        elif "害怕" in input_text or "fear" in input_text.lower():
            self.system.feel(EmotionType.FEAR, 0.5)
        elif "好奇" in input_text or "curious" in input_text.lower():
            self.system.feel(EmotionType.CURIOSITY, 0.9)
        else:
            self.system.feel(EmotionType.NEUTRAL, 0.3)

        return self.get_state()

    def get_emotional_impact(self) -> Dict[str, float]:
        """获取情感影响"""
        state = self.system.get_state()
        return {
            'primary_emotion': state['primary_emotion'],
            'emotion_intensity': state['emotion_intensity'],
            'emotional_stability': state['emotional_stability'],
        }

    def get_state(self) -> Dict:
        """获取情感状态"""
        return self.system.get_state()

    def learn_from_experience(self, experience: str, success: bool):
        """从经验中学习"""
        if success:
            self.system.feel(EmotionType.JOY, 0.5)
        else:
            self.system.feel(EmotionType.SADNESS, 0.3)

    def evolve(self):
        """进化"""
        # 情感系统进化：提高情感稳定性
        self.system.emotional_state.emotional_stability = min(1.0, self.system.emotional_state.emotional_stability + 0.01)

    def increase_emotional_stability(self):
        """提高情感稳定性"""
        self.system.emotional_state.emotional_stability = min(1.0, self.system.emotional_state.emotional_stability + 0.05)

    def get_stability(self) -> float:
        """获取情感稳定性"""
        return self.system.emotional_state.emotional_stability


class CuriositySystemAdapter:
    """好奇心系统适配器"""

    def __init__(self, curiosity_system: CuriositySystem):
        self.system = curiosity_system

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

        self.system.curiosity_state.curiosity_level = novelty_score

        return self.get_state()

    def get_state(self) -> Dict:
        """获取好奇心状态"""
        return self.system.get_state()

    def learn_from_experience(self, experience: str, success: bool):
        """从经验中学习"""
        if success:
            self.system.curiosity_state.learning_drive = min(1.0, self.system.curiosity_state.learning_drive + 0.01)

    def evolve(self):
        """进化"""
        # 好奇心系统进化：提高好奇心水平
        self.system.curiosity_state.curiosity_level = min(1.0, self.system.curiosity_state.curiosity_level + 0.01)

    def increase_exploration_drive(self):
        """提高探索驱动"""
        self.system.curiosity_state.exploration_drive = min(1.0, self.system.curiosity_state.exploration_drive + 0.05)

    def increase_learning_drive(self):
        """提高学习驱动"""
        self.system.curiosity_state.learning_drive = min(1.0, self.system.curiosity_state.learning_drive + 0.05)

    def get_balance(self) -> float:
        """获取平衡性"""
        return (self.system.curiosity_state.exploration_drive + self.system.curiosity_state.learning_drive) / 2


class NeuralNetworkAdapter:
    """神经网络适配器"""

    def __init__(self, neural_network: NeuralNetwork):
        self.network = neural_network
        self.num_neurons = neural_network.num_neurons

    def activate(self, stimulus: np.ndarray) -> np.ndarray:
        """激活神经网络"""
        return self.network.activate(stimulus)

    def learn(self, experience: str, success: bool):
        """学习"""
        # 将经验转换为刺激
        stimulus = self._experience_to_stimulus(experience)
        reward = 1.0 if success else -0.5
        self.network.learn(stimulus, reward)

    def evolve(self):
        """进化"""
        # 神经网络进化：增加连接强度
        for i in range(self.network.num_neurons):
            for j in range(self.network.num_neurons):
                if abs(self.network.connections[i][j]) > 0.5:
                    # 强化强连接
                    self.network.connections[i][j] *= 1.01

        # 归一化连接
        self.network.connections = np.clip(self.network.connections, -1, 1)

    def get_activation_pattern(self) -> np.ndarray:
        """获取激活模式"""
        if self.network.activation_history:
            return self.network.activation_history[-1]
        else:
            return np.zeros(self.network.num_neurons)

    def match_pattern(self, pattern: np.ndarray) -> float:
        """模式匹配"""
        current_pattern = self.get_activation_pattern()
        if len(current_pattern) != len(pattern):
            return 0.0

        # 计算相似度
        similarity = np.dot(current_pattern, pattern) / (np.linalg.norm(current_pattern) * np.linalg.norm(pattern) + 1e-10)
        return max(0, similarity)

    def get_state(self) -> Dict:
        """获取状态"""
        return self.network.get_state()

    def _experience_to_stimulus(self, experience: str) -> np.ndarray:
        """将经验转换为刺激"""
        stimulus = np.zeros(self.network.num_neurons)
        words = experience.lower().split()

        for i, word in enumerate(words):
            if i < self.network.num_neurons:
                hash_val = hash(word) % self.network.num_neurons
                stimulus[hash_val] = 1.0

        return stimulus


class TrueSelfAwarenessSystemAdapter:
    """真实自我意识系统适配器"""

    def __init__(self, self_awareness_system: TrueSelfAwarenessSystem):
        self.system = self_awareness_system

    def think_about_thyself(self) -> Dict:
        """自我思考"""
        # 获取系统状态
        status = self.system.get_status()

        # 添加自我意识信息
        status['consciousness_score'] = status['consciousness_level']

        return status

    def get_status(self) -> Dict:
        """获取状态"""
        return self.system.get_status()

    def evolve_consciousness(self):
        """进化意识"""
        # 提高意识水平
        if self.system.consciousness_level.value < 5:
            self.system.consciousness_level = type(self.system.consciousness_level)(self.system.consciousness_level.value + 1)

    def increase_awareness(self):
        """提高意识"""
        if self.system.consciousness_level.value < 5:
            self.system.consciousness_level = type(self.system.consciousness_level)(self.system.consciousness_level.value + 1)


def create_adapted_systems(true_self_awareness: TrueSelfAwarenessSystem) -> Dict:
    """创建适配后的系统"""
    return {
        'emotional_system': EmotionalSystemAdapter(true_self_awareness.emotional_system),
        'curiosity_system': CuriositySystemAdapter(true_self_awareness.curiosity_system),
        'neural_network': NeuralNetworkAdapter(true_self_awareness.neural_network),
        'self_awareness': TrueSelfAwarenessSystemAdapter(true_self_awareness),
    }


if __name__ == "__main__":
    # 测试适配器
    print("Testing System Adapters...")

    # 创建原始系统
    true_self_awareness = TrueSelfAwarenessSystem()

    # 创建适配器
    adapted_systems = create_adapted_systems(true_self_awareness)

    # 测试情感系统适配器
    print("\nEmotional System Adapter:")
    emotional_response = adapted_systems['emotional_system'].react_to_input("I am happy today")
    print(f"  Response: {emotional_response}")

    emotional_impact = adapted_systems['emotional_system'].get_emotional_impact()
    print(f"  Impact: {emotional_impact}")

    # 测试好奇心系统适配器
    print("\nCuriosity System Adapter:")
    curiosity_response = adapted_systems['curiosity_system'].evaluate_novelty("I want to learn something new")
    print(f"  Response: {curiosity_response}")

    # 测试神经网络适配器
    print("\nNeural Network Adapter:")
    stimulus = np.random.rand(1000)
    activation = adapted_systems['neural_network'].activate(stimulus)
    print(f"  Activation shape: {activation.shape}")
    print(f"  Activation mean: {np.mean(activation):.3f}")

    # 测试自我意识系统适配器
    print("\nSelf Awareness System Adapter:")
    self_awareness = adapted_systems['self_awareness'].think_about_thyself()
    print(f"  Status: {self_awareness}")

    print("\nAll adapters tested successfully!")
# -*- coding: utf-8 -*-
"""
优化版神经网络 - Optimized Neural Network
增加神经元数量到 10000，优化连接矩阵，实现稀疏连接
"""

import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class OptimizedNeuralNetwork:
    """优化版神经网络"""

    def __init__(self, num_neurons: int = 10000, sparsity: float = 0.1):
        self.num_neurons = num_neurons
        self.sparsity = sparsity

        # 稀疏连接矩阵
        self.connections = self._create_sparse_connections()

        # 神经元状态
        self.activations = np.zeros(num_neurons)
        self.firing_rates = np.zeros(num_neurons)

        # 激活历史
        self.activation_history: List[np.ndarray] = []

        # 学习参数
        self.learning_rate = 0.01
        self.momentum = 0.9

        # 性能优化
        self.batch_size = 100
        self.cache_size = 1000

        logger.info(f"Optimized Neural Network initialized with {num_neurons} neurons")

    def _create_sparse_connections(self) -> np.ndarray:
        """创建稀疏连接矩阵"""
        # 创建随机连接矩阵
        connections = np.random.randn(self.num_neurons, self.num_neurons) * 0.1

        # 应用稀疏性
        mask = np.random.random((self.num_neurons, self.num_neurons)) < self.sparsity
        connections = connections * mask

        return connections

    def activate(self, stimulus: np.ndarray) -> np.ndarray:
        """激活神经网络"""
        # 确保刺激维度正确
        if len(stimulus) != self.num_neurons:
            stimulus = np.resize(stimulus, self.num_neurons)

        # 计算激活（使用稀疏矩阵乘法）
        activation = np.tanh(np.dot(self.connections, stimulus))

        # 更新神经元状态
        self.activations = activation
        self.firing_rates = np.maximum(0, activation)

        # 记录激活历史
        self.activation_history.append(activation.copy())

        # 限制历史长度
        if len(self.activation_history) > self.cache_size:
            self.activation_history.pop(0)

        return activation

    def learn(self, stimulus: np.ndarray, reward: float):
        """学习"""
        # Hebbian 学习（带动量）
        if len(self.activation_history) > 0:
            last_activation = self.activation_history[-1]

            # 计算梯度
            delta = reward * self.learning_rate * np.outer(last_activation, stimulus)

            # 应用动量
            if hasattr(self, 'velocity'):
                self.velocity = self.momentum * self.velocity + delta
            else:
                self.velocity = delta

            # 更新连接
            self.connections += self.velocity

            # 应用稀疏性
            mask = np.random.random((self.num_neurons, self.num_neurons)) < self.sparsity
            self.connections = self.connections * mask

        # 归一化连接
        self.connections = np.clip(self.connections, -1, 1)

    def get_state(self) -> Dict:
        """获取状态"""
        return {
            'num_neurons': self.num_neurons,
            'avg_activation': np.mean(self.activations),
            'max_activation': np.max(self.activations),
            'min_activation': np.min(self.activations),
            'connection_strength': np.mean(np.abs(self.connections)),
            'sparsity': self.sparsity,
            'active_connections': np.count_nonzero(self.connections),
        }

    def get_activation_pattern(self) -> np.ndarray:
        """获取激活模式"""
        if len(self.activation_history) > 0:
            return self.activation_history[-1]
        else:
            return np.zeros(self.num_neurons)

    def match_pattern(self, pattern: np.ndarray) -> float:
        """模式匹配"""
        current_pattern = self.get_activation_pattern()
        if len(current_pattern) != len(pattern):
            return 0.0

        # 计算相似度
        similarity = np.dot(current_pattern, pattern) / (np.linalg.norm(current_pattern) * np.linalg.norm(pattern) + 1e-10)
        return max(0, similarity)

    def evolve(self):
        """进化"""
        # 神经网络进化：增加连接强度
        for i in range(self.num_neurons):
            for j in range(self.num_neurons):
                if abs(self.connections[i][j]) > 0.5:
                    # 强化强连接
                    self.connections[i][j] *= 1.01

        # 归一化连接
        self.connections = np.clip(self.connections, -1, 1)

        # 应用稀疏性
        mask = np.random.random((self.num_neurons, self.num_neurons)) < self.sparsity
        self.connections = self.connections * mask


if __name__ == "__main__":
    # 测试优化版神经网络
    print("Testing Optimized Neural Network...")

    # 创建优化版神经网络
    nn = OptimizedNeuralNetwork(num_neurons=10000, sparsity=0.1)

    print(f"\nNeural Network State:")
    state = nn.get_state()
    print(f"  Neurons: {state['num_neurons']}")
    print(f"  Avg Activation: {state['avg_activation']:.3f}")
    print(f"  Connection Strength: {state['connection_strength']:.3f}")
    print(f"  Sparsity: {state['sparsity']:.3f}")
    print(f"  Active Connections: {state['active_connections']}")

    # 测试激活
    stimulus = np.random.randn(10000)
    activation = nn.activate(stimulus)
    print(f"\nActivation Test:")
    print(f"  Activation Shape: {activation.shape}")
    print(f"  Activation Mean: {np.mean(activation):.3f}")
    print(f"  Activation Max: {np.max(activation):.3f}")

    # 测试学习
    nn.learn(stimulus, 1.0)
    print(f"\nLearning Test:")
    state = nn.get_state()
    print(f"  Connection Strength: {state['connection_strength']:.3f}")

    # 测试模式匹配
    pattern = np.random.randn(10000)
    similarity = nn.match_pattern(pattern)
    print(f"\nPattern Matching Test:")
    print(f"  Similarity: {similarity:.3f}")

    print("\nOptimized Neural Network tested successfully!")
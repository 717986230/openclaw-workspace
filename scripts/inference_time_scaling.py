#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推理时缩放
Inference-Time Scaling

基于Reasoning-from-Scratch项目的推理时缩放技术
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ScalingMethod(Enum):
    """缩放方法"""
    TEMPERATURE = "temperature"
    TOP_P = "top_p"
    TOP_K = "top_k"
    SELF_CONSISTENCY = "self_consistency"
    CHAIN_OF_THOUGHT = "chain_of_thought"

@dataclass
class ScalingConfig:
    """缩放配置"""
    method: ScalingMethod
    temperature: float = 1.0
    top_p: float = 0.9
    top_k: int = 40
    num_samples: int = 5
    enable_cot: bool = True
    cot_steps: int = 3

class InferenceTimeScaling:
    """推理时缩放"""

    def __init__(self, config: ScalingConfig):
        self.config = config

    def scale_temperature(self, logits: np.ndarray) -> np.ndarray:
        """温度缩放"""
        if self.config.temperature == 1.0:
            return logits

        # 应用温度缩放
        scaled_logits = logits / self.config.temperature

        # 重新归一化
        scaled_logits = scaled_logits - np.max(scaled_logits, axis=-1, keepdims=True)
        exp_logits = np.exp(scaled_logits)
        scaled_probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)

        return scaled_probs

    def scale_top_p(self, probs: np.ndarray) -> np.ndarray:
        """Top-p（nucleus）缩放"""
        if self.config.top_p >= 1.0:
            return probs

        # 按概率降序排序
        sorted_probs = np.sort(probs)[::-1]
        cumulative_probs = np.cumsum(sorted_probs)

        # 找到累积概率超过top_p的索引
        cutoff_idx = np.searchsorted(cumulative_probs, self.config.top_p)

        # 创建掩码
        mask = np.zeros_like(probs)
        mask[:cutoff_idx + 1] = 1.0

        # 应用掩码并重新归一化
        masked_probs = probs * mask
        masked_probs = masked_probs / np.sum(masked_probs)

        return masked_probs

    def scale_top_k(self, probs: np.ndarray) -> np.ndarray:
        """Top-k缩放"""
        if self.config.top_k >= len(probs):
            return probs

        # 找到top-k的索引
        top_k_indices = np.argpartition(probs, -self.config.top_k)[-self.config.top_k:]

        # 创建掩码
        mask = np.zeros_like(probs)
        mask[top_k_indices] = 1.0

        # 应用掩码并重新归一化
        masked_probs = probs * mask
        masked_probs = masked_probs / np.sum(masked_probs)

        return masked_probs

    def self_consistency(self, query: str, generate_fn) -> List[str]:
        """自我一致性"""
        samples = []

        for _ in range(self.config.num_samples):
            # 生成多个样本
            sample = generate_fn(query)
            samples.append(sample)

        # 投票选择最一致的结果
        from collections import Counter
        counter = Counter(samples)
        most_common = counter.most_common(1)[0][0]

        return most_common

    def chain_of_thought(self, query: str, generate_fn) -> str:
        """思维链"""
        if not self.config.enable_cot:
            return generate_fn(query)

        # 生成思维链
        cot_prompt = f"Let's think step by step to answer: {query}\n\n"

        for step in range(self.config.cot_steps):
            step_prompt = f"{cot_prompt}Step {step + 1}:"
            step_response = generate_fn(step_prompt)
            cot_prompt += f"{step_response}\n\n"

        # 生成最终答案
        final_prompt = f"{cot_prompt}Based on the above reasoning, the answer is:"
        final_answer = generate_fn(final_prompt)

        return final_answer

    def apply_scaling(self, logits: np.ndarray) -> np.ndarray:
        """应用缩放"""
        probs = self.scale_temperature(logits)

        if self.config.method == ScalingMethod.TOP_P:
            probs = self.scale_top_p(probs)
        elif self.config.method == ScalingMethod.TOP_K:
            probs = self.scale_top_k(probs)

        return probs

    def generate_with_scaling(self, query: str, generate_fn) -> str:
        """使用缩放生成"""
        if self.config.method == ScalingMethod.SELF_CONSISTENCY:
            return self.self_consistency(query, generate_fn)
        elif self.config.method == ScalingMethod.CHAIN_OF_THOUGHT:
            return self.chain_of_thought(query, generate_fn)
        else:
            return generate_fn(query)


class AdaptiveScaling:
    """自适应缩放"""

    def __init__(self):
        self.history = []

    def select_temperature(self, query_complexity: float) -> float:
        """根据查询复杂度选择温度"""
        # 复杂度越高，温度越高
        base_temp = 0.7
        temp = base_temp + (query_complexity * 0.3)
        return min(temp, 1.5)

    def select_top_p(self, confidence: float) -> float:
        """根据置信度选择top_p"""
        # 置信度越低，top_p越高
        base_p = 0.9
        p = base_p - (confidence * 0.2)
        return max(p, 0.5)

    def select_top_k(self, diversity: float) -> int:
        """根据多样性选择top_k"""
        # 多样性越高，top_k越大
        base_k = 40
        k = int(base_k + (diversity * 20))
        return min(k, 100)

    def update_history(self, query: str, result: str, quality: float):
        """更新历史记录"""
        self.history.append({
            'query': query,
            'result': result,
            'quality': quality,
            'timestamp': datetime.now()
        })

    def get_best_config(self) -> ScalingConfig:
        """获取最佳配置"""
        if not self.history:
            return ScalingConfig(method=ScalingMethod.TEMPERATURE)

        # 分析历史记录，找到最佳配置
        best_quality = max(h['quality'] for h in self.history)

        # 这里可以添加更复杂的逻辑来选择最佳配置
        return ScalingConfig(method=ScalingMethod.TEMPERATURE)


if __name__ == "__main__":
    # 测试代码
    print("Testing Inference-Time Scaling...")

    # 测试温度缩放
    config = ScalingConfig(method=ScalingMethod.TEMPERATURE, temperature=0.7)
    scaling = InferenceTimeScaling(config)

    logits = np.array([2.0, 1.0, 0.5, -1.0, -2.0])
    scaled_probs = scaling.scale_temperature(logits)

    print(f"Original logits: {logits}")
    print(f"Scaled probs: {scaled_probs}")

    # 测试top-p缩放
    config = ScalingConfig(method=ScalingMethod.TOP_P, top_p=0.8)
    scaling = InferenceTimeScaling(config)

    probs = np.array([0.4, 0.3, 0.2, 0.05, 0.05])
    scaled_probs = scaling.scale_top_p(probs)

    print(f"Original probs: {probs}")
    print(f"Scaled probs: {scaled_probs}")

    # 测试top-k缩放
    config = ScalingConfig(method=ScalingMethod.TOP_K, top_k=3)
    scaling = InferenceTimeScaling(config)

    probs = np.array([0.4, 0.3, 0.2, 0.05, 0.05])
    scaled_probs = scaling.scale_top_k(probs)

    print(f"Original probs: {probs}")
    print(f"Scaled probs: {scaled_probs}")

    print("Inference-Time Scaling test complete!")

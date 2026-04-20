# -*- coding: utf-8 -*-
"""
优化版思维过程 - Optimized Thought Process
优化推理链，实现并行思考，优化决策过程，实现思维缓存
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class ThoughtType(Enum):
    """思维类型"""
    ANALYSIS = "analysis"  # 分析
    REASONING = "reasoning"  # 推理
    DECISION = "decision"  # 决策
    REFLECTION = "reflection"  # 反思
    IMAGINATION = "imagination"  # 想象
    PLANNING = "planning"  # 规划


@dataclass
class Thought:
    """思维"""
    id: str
    content: str
    thought_type: ThoughtType
    confidence: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class ReasoningStep:
    """推理步骤"""
    id: str
    premise: str
    conclusion: str
    confidence: float = 0.5
    evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Decision:
    """决策"""
    id: str
    options: List[str]
    selected_option: str
    reasoning: str
    confidence: float = 0.5
    alternatives: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class OptimizedThoughtProcess:
    """优化版思维过程"""

    def __init__(self, max_thoughts: int = 10000, cache_size: int = 1000):
        self.max_thoughts = max_thoughts
        self.cache_size = cache_size

        # 思维存储
        self.thoughts: Dict[str, Thought] = {}
        self.reasoning_chain: List[ReasoningStep] = []
        self.decision_history: List[Decision] = []

        # 思维缓存
        self.thought_cache: Dict[str, Thought] = {}
        self.reasoning_cache: Dict[str, List[ReasoningStep]] = {}
        self.decision_cache: Dict[str, Decision] = {}

        # 并行处理
        self.max_workers = 4
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

        # 性能优化
        self.batch_size = 100
        self.compression_threshold = 0.3

        logger.info(f"Optimized Thought Process initialized with {max_thoughts} max thoughts")

    def think(
        self,
        input_text: str,
        thought_type: ThoughtType = ThoughtType.ANALYSIS,
        context: Dict = None
    ) -> Thought:
        """思考"""
        # 检查缓存
        cache_key = f"{hash(input_text)}_{thought_type.value}"
        if cache_key in self.thought_cache:
            return self.thought_cache[cache_key]

        # 生成思维
        thought = self._generate_thought(input_text, thought_type, context)

        # 添加到思维存储
        self.thoughts[thought.id] = thought

        # 添加到缓存
        self._add_to_cache(cache_key, thought)

        # 清理缓存
        self._clear_cache()

        logger.debug(f"Thought generated: {thought.id}")

        return thought

    def _generate_thought(
        self,
        input_text: str,
        thought_type: ThoughtType,
        context: Dict = None
    ) -> Thought:
        """生成思维"""
        thought_id = f"thought-{len(self.thoughts)}"

        # 根据思维类型生成内容
        if thought_type == ThoughtType.ANALYSIS:
            content = f"分析: {input_text}"
        elif thought_type == ThoughtType.REASONING:
            content = f"推理: {input_text}"
        elif thought_type == ThoughtType.DECISION:
            content = f"决策: {input_text}"
        elif thought_type == ThoughtType.REFLECTION:
            content = f"反思: {input_text}"
        elif thought_type == ThoughtType.IMAGINATION:
            content = f"想象: {input_text}"
        elif thought_type == ThoughtType.PLANNING:
            content = f"规划: {input_text}"
        else:
            content = f"思考: {input_text}"

        # 计算置信度
        confidence = self._calculate_confidence(input_text, thought_type, context)

        # 创建思维
        thought = Thought(
            id=thought_id,
            content=content,
            thought_type=thought_type,
            confidence=confidence,
            metadata=context or {}
        )

        return thought

    def _calculate_confidence(
        self,
        input_text: str,
        thought_type: ThoughtType,
        context: Dict = None
    ) -> float:
        """计算置信度"""
        # 基础置信度
        base_confidence = 0.5

        # 根据输入长度调整
        length_factor = min(len(input_text) / 100, 1.0)
        base_confidence += length_factor * 0.2

        # 根据思维类型调整
        type_factors = {
            ThoughtType.ANALYSIS: 0.1,
            ThoughtType.REASONING: 0.15,
            ThoughtType.DECISION: 0.2,
            ThoughtType.REFLECTION: 0.1,
            ThoughtType.IMAGINATION: 0.05,
            ThoughtType.PLANNING: 0.15,
        }
        base_confidence += type_factors.get(thought_type, 0.0)

        # 根据上下文调整
        if context:
            if 'experience' in context:
                base_confidence += context['experience'] * 0.1
            if 'fitness' in context:
                base_confidence += context['fitness'] * 0.05

        return min(base_confidence, 1.0)

    def reason(
        self,
        premise: str,
        evidence: List[str] = None
    ) -> ReasoningStep:
        """推理"""
        # 检查缓存
        cache_key = f"{hash(premise)}_{hash(str(evidence))}"
        if cache_key in self.reasoning_cache:
            return self.reasoning_cache[cache_key][-1]

        # 生成推理步骤
        reasoning_step = self._generate_reasoning_step(premise, evidence)

        # 添加到推理链
        self.reasoning_chain.append(reasoning_step)

        # 添加到缓存
        self.reasoning_cache[cache_key] = self.reasoning_chain.copy()

        # 清理缓存
        self._clear_cache()

        logger.debug(f"Reasoning step generated: {reasoning_step.id}")

        return reasoning_step

    def _generate_reasoning_step(
        self,
        premise: str,
        evidence: List[str] = None
    ) -> ReasoningStep:
        """生成推理步骤"""
        reasoning_id = f"reasoning-{len(self.reasoning_chain)}"

        # 生成结论
        conclusion = self._derive_conclusion(premise, evidence)

        # 计算置信度
        confidence = self._calculate_reasoning_confidence(premise, evidence)

        # 创建推理步骤
        reasoning_step = ReasoningStep(
            id=reasoning_id,
            premise=premise,
            conclusion=conclusion,
            confidence=confidence,
            evidence=evidence or []
        )

        return reasoning_step

    def _derive_conclusion(self, premise: str, evidence: List[str] = None) -> str:
        """推导结论"""
        # 简单的结论推导
        if evidence:
            return f"基于证据，{premise} 的结论是: {evidence[0]}"
        else:
            return f"{premise} 的结论是: 基于前提的推理"

    def _calculate_reasoning_confidence(
        self,
        premise: str,
        evidence: List[str] = None
    ) -> float:
        """计算推理置信度"""
        # 基础置信度
        base_confidence = 0.5

        # 根据证据数量调整
        if evidence:
            base_confidence += min(len(evidence) * 0.1, 0.3)

        # 根据前提长度调整
        base_confidence += min(len(premise) / 100, 0.2)

        return min(base_confidence, 1.0)

    def decide(
        self,
        options: List[str],
        context: Dict = None
    ) -> Decision:
        """决策"""
        # 检查缓存
        cache_key = f"{hash(str(options))}_{hash(str(context))}"
        if cache_key in self.decision_cache:
            return self.decision_cache[cache_key]

        # 生成决策
        decision = self._generate_decision(options, context)

        # 添加到决策历史
        self.decision_history.append(decision)

        # 添加到缓存
        self.decision_cache[cache_key] = decision

        # 清理缓存
        self._clear_cache()

        logger.debug(f"Decision generated: {decision.id}")

        return decision

    def _generate_decision(
        self,
        options: List[str],
        context: Dict = None
    ) -> Decision:
        """生成决策"""
        decision_id = f"decision-{len(self.decision_history)}"

        # 选择最佳选项
        selected_option = self._select_best_option(options, context)

        # 生成推理
        reasoning = self._generate_decision_reasoning(selected_option, options, context)

        # 计算置信度
        confidence = self._calculate_decision_confidence(selected_option, options, context)

        # 创建决策
        decision = Decision(
            id=decision_id,
            options=options,
            selected_option=selected_option,
            reasoning=reasoning,
            confidence=confidence,
            alternatives=[opt for opt in options if opt != selected_option]
        )

        return decision

    def _select_best_option(
        self,
        options: List[str],
        context: Dict = None
    ) -> str:
        """选择最佳选项"""
        if not options:
            return "无选项"

        # 简单的选项选择
        if context and 'experience' in context:
            # 根据经验选择
            return options[int(context['experience'] * len(options)) % len(options)]
        else:
            # 随机选择
            return options[0]

    def _generate_decision_reasoning(
        self,
        selected_option: str,
        options: List[str],
        context: Dict = None
    ) -> str:
        """生成决策推理"""
        reasoning = f"选择 {selected_option} 的原因是: "

        if context:
            if 'experience' in context:
                reasoning += f"基于经验 {context['experience']:.2f}，"
            if 'fitness' in context:
                reasoning += f"适应度 {context['fitness']:.2f}，"

        reasoning += f"从 {len(options)} 个选项中选择"

        return reasoning

    def _calculate_decision_confidence(
        self,
        selected_option: str,
        options: List[str],
        context: Dict = None
    ) -> float:
        """计算决策置信度"""
        # 基础置信度
        base_confidence = 0.5

        # 根据选项数量调整
        base_confidence += min(len(options) * 0.05, 0.2)

        # 根据上下文调整
        if context:
            if 'experience' in context:
                base_confidence += context['experience'] * 0.2
            if 'fitness' in context:
                base_confidence += context['fitness'] * 0.1

        return min(base_confidence, 1.0)

    def think_parallel(
        self,
        inputs: List[str],
        thought_type: ThoughtType = ThoughtType.ANALYSIS
    ) -> List[Thought]:
        """并行思考"""
        # 使用线程池并行处理
        futures = []
        for input_text in inputs:
            future = self.executor.submit(
                self.think,
                input_text,
                thought_type
            )
            futures.append(future)

        # 收集结果
        results = []
        for future in as_completed(futures):
            try:
                thought = future.result()
                results.append(thought)
            except Exception as e:
                logger.error(f"Error in parallel thinking: {e}")

        return results

    def reason_parallel(
        self,
        premises: List[str],
        evidences: List[List[str]] = None
    ) -> List[ReasoningStep]:
        """并行推理"""
        if evidences is None:
            evidences = [[] for _ in premises]

        # 使用线程池并行处理
        futures = []
        for premise, evidence in zip(premises, evidences):
            future = self.executor.submit(
                self.reason,
                premise,
                evidence
            )
            futures.append(future)

        # 收集结果
        results = []
        for future in as_completed(futures):
            try:
                reasoning_step = future.result()
                results.append(reasoning_step)
            except Exception as e:
                logger.error(f"Error in parallel reasoning: {e}")

        return results

    def _add_to_cache(self, cache_key: str, thought: Thought):
        """添加到缓存"""
        self.thought_cache[cache_key] = thought

    def _clear_cache(self):
        """清理缓存"""
        # 清理思维缓存
        if len(self.thought_cache) > self.cache_size:
            oldest_key = next(iter(self.thought_cache))
            del self.thought_cache[oldest_key]

        # 清理推理缓存
        if len(self.reasoning_cache) > self.cache_size:
            oldest_key = next(iter(self.reasoning_cache))
            del self.reasoning_cache[oldest_key]

        # 清理决策缓存
        if len(self.decision_cache) > self.cache_size:
            oldest_key = next(iter(self.decision_cache))
            del self.decision_cache[oldest_key]

    def compress_thoughts(self):
        """压缩思维"""
        # 找到低置信度的思维
        low_confidence_thoughts = [
            t for t in self.thoughts.values()
            if t.confidence < self.compression_threshold
        ]

        # 压缩思维
        for thought in low_confidence_thoughts:
            # 减少置信度
            thought.confidence *= 0.5

            # 如果置信度太低，删除思维
            if thought.confidence < 0.1:
                del self.thoughts[thought.id]

        logger.info(f"Compressed {len(low_confidence_thoughts)} thoughts")

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            'total_thoughts': len(self.thoughts),
            'max_thoughts': self.max_thoughts,
            'reasoning_chain_length': len(self.reasoning_chain),
            'decision_history_length': len(self.decision_history),
            'cache_size': len(self.thought_cache),
            'max_workers': self.max_workers,
            'avg_confidence': np.mean([t.confidence for t in self.thoughts.values()]) if self.thoughts else 0.0,
        }


if __name__ == "__main__":
    # 测试优化版思维过程
    print("Testing Optimized Thought Process...")

    # 创建优化版思维过程
    thought_process = OptimizedThoughtProcess(max_thoughts=10000, cache_size=1000)

    print(f"\nThought Process Statistics:")
    stats = thought_process.get_statistics()
    print(f"  Total Thoughts: {stats['total_thoughts']}")
    print(f"  Max Thoughts: {stats['max_thoughts']}")
    print(f"  Reasoning Chain Length: {stats['reasoning_chain_length']}")
    print(f"  Decision History Length: {stats['decision_history_length']}")
    print(f"  Cache Size: {stats['cache_size']}")
    print(f"  Max Workers: {stats['max_workers']}")

    # 测试思考
    print(f"\nTesting Think...")
    thought = thought_process.think("I need to learn Python programming")
    print(f"  Thought ID: {thought.id}")
    print(f"  Content: {thought.content}")
    print(f"  Confidence: {thought.confidence:.2f}")

    # 测试推理
    print(f"\nTesting Reason...")
    reasoning_step = thought_process.reason(
        "Python is a good programming language",
        ["It is easy to learn", "It has many libraries"]
    )
    print(f"  Reasoning ID: {reasoning_step.id}")
    print(f"  Premise: {reasoning_step.premise}")
    print(f"  Conclusion: {reasoning_step.conclusion}")
    print(f"  Confidence: {reasoning_step.confidence:.2f}")

    # 测试决策
    print(f"\nTesting Decide...")
    decision = thought_process.decide(
        ["Option A", "Option B", "Option C"],
        {"experience": 0.7, "fitness": 0.8}
    )
    print(f"  Decision ID: {decision.id}")
    print(f"  Selected Option: {decision.selected_option}")
    print(f"  Reasoning: {decision.reasoning}")
    print(f"  Confidence: {decision.confidence:.2f}")

    # 测试并行思考
    print(f"\nTesting Parallel Think...")
    inputs = [
        "I need to learn Python",
        "I want to build a website",
        "I need to optimize my code"
    ]
    thoughts = thought_process.think_parallel(inputs)
    print(f"  Generated {len(thoughts)} thoughts")
    for thought in thoughts:
        print(f"    {thought.id}: {thought.content}")

    # 测试思维压缩
    print(f"\nTesting Thought Compression...")
    thought_process.compress_thoughts()
    stats = thought_process.get_statistics()
    print(f"  Total Thoughts: {stats['total_thoughts']}")
    print(f"  Avg Confidence: {stats['avg_confidence']:.3f}")

    print("\nOptimized Thought Process tested successfully!")
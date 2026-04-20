# -*- coding: utf-8 -*-
"""
心智模型 - Mental Models
实现 Mental Loop、Tree of Thoughts 和 Meta Controller
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class SimulationResult:
    """模拟结果"""
    outcome: str
    confidence: float
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)


class MentalLoop:
    """心智循环 - 内部模拟器"""

    def __init__(self):
        self.simulation_history: List[SimulationResult] = []
        self.current_simulation: Optional[SimulationResult] = None
        self.simulation_count = 0

    def simulate(self, action: str, context: Dict) -> SimulationResult:
        """模拟行动"""
        # 简单的模拟逻辑
        outcomes = ["成功", "失败", "部分成功"]
        outcome = random.choice(outcomes)

        confidence = random.uniform(0.5, 0.9)
        reasoning = f"模拟 {action}，预期结果: {outcome}"

        result = SimulationResult(
            outcome=outcome,
            confidence=confidence,
            reasoning=reasoning
        )

        self.simulation_history.append(result)
        self.current_simulation = result
        self.simulation_count += 1

        return result

    def learn(self, outcome: str, success: bool):
        """从结果中学习"""
        # 简单的学习逻辑
        if success:
            logger.info(f"Mental Loop learned: {outcome} was successful")
        else:
            logger.info(f"Mental Loop learned: {outcome} was not successful")


class TreeOfThoughts:
    """思维树 - 多路径思考"""

    def __init__(self):
        self.max_depth = 5
        self.current_depth = 0
        self.thought_paths: List[List[str]] = []
        self.best_path: Optional[List[str]] = None

    def explore(self, problem: str) -> List[str]:
        """探索问题"""
        # 简单的思维树探索
        paths = []

        for i in range(3):
            path = [f"思考路径 {i+1}: {problem}"]
            path.append(f"分析 {problem}")
            path.append(f"解决方案 {i+1}")
            paths.append(path)

        self.thought_paths = paths
        self.best_path = paths[0] if paths else None

        return self.best_path or []


class MetaController:
    """元控制器 - 高层决策"""

    def __init__(self):
        self.decision_history: List[Dict] = []
        self.performance_history: List[float] = []
        self.current_decision: Optional[Dict] = None

    def process(self, input_text: str, context: Dict) -> Dict:
        """处理输入"""
        # 简单的元控制器逻辑
        solutions = [
            "方案A: 直接执行",
            "方案B: 先分析再执行",
            "方案C: 寻求帮助",
        ]

        best_solution = random.choice(solutions)

        # 模拟结果
        simulation = {
            'outcome': '成功',
            'confidence': random.uniform(0.7, 0.9),
        }

        result = {
            'input': input_text,
            'context': context,
            'solutions': solutions,
            'best_solution': best_solution,
            'simulation': simulation,
            'timestamp': datetime.now(),
        }

        self.decision_history.append(result)
        self.current_decision = result

        return result

    def update_performance(self, success: bool, performance: float):
        """更新性能"""
        self.performance_history.append(performance)

        if len(self.performance_history) > 100:
            self.performance_history.pop(0)


if __name__ == "__main__":
    # 测试心智模型
    print("Testing Mental Models...")

    # 测试 Mental Loop
    print("\nMental Loop:")
    mental_loop = MentalLoop()
    result = mental_loop.simulate("执行任务", {})
    print(f"  Outcome: {result.outcome}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Reasoning: {result.reasoning}")

    # 测试 Tree of Thoughts
    print("\nTree of Thoughts:")
    tree = TreeOfThoughts()
    path = tree.explore("解决问题")
    print(f"  Best Path: {path}")

    # 测试 Meta Controller
    print("\nMeta Controller:")
    meta = MetaController()
    result = meta.process("处理输入", {})
    print(f"  Best Solution: {result['best_solution']}")
    print(f"  Simulation: {result['simulation']}")

    print("\nMental Models tested successfully!")
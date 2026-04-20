"""
自我调节模块
基于钱学森控制论理论，实现自适应参数和策略调节
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class AdjustmentType(Enum):
    """调节类型"""
    PARAMETER = "参数调节"
    STRATEGY = "策略调节"
    STRUCTURE = "结构调节"
    RESOURCE = "资源调节"


@dataclass
class Adjustment:
    """调节"""
    type: AdjustmentType
    target: str
    current_value: Any
    new_value: Any
    reason: str
    priority: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"


class SelfRegulator:
    """自我调节器"""

    def __init__(self):
        self.adjustments = []
        self.adjustment_history = []
        self.parameters = self.load_parameters()
        self.strategies = self.load_strategies()

    def load_parameters(self) -> Dict[str, Any]:
        """加载参数"""
        return {
            "learning_rate": 0.001,
            "batch_size": 32,
            "max_iterations": 1000,
            "tolerance": 0.0001,
            "timeout": 30,
            "cache_size": 1000,
            "parallel_workers": 4,
            "memory_limit": 1024
        }

    def load_strategies(self) -> Dict[str, Any]:
        """加载策略"""
        return {
            "optimization": "gradient_descent",
            "search": "beam_search",
            "planning": "hierarchical",
            "reasoning": "logical",
            "learning": "reinforcement"
        }

    def analyze_evaluation_results(self, evaluation_results: Dict[str, Any]) -> List[Adjustment]:
        """分析评估结果，生成调节方案"""
        adjustments = []

        # 分析准确性
        accuracy_result = evaluation_results.get("results", [{}])[0]
        if accuracy_result.get("score", 0) < accuracy_result.get("target", 0.95):
            adjustments.append(self.create_accuracy_adjustment(accuracy_result))

        # 分析效率
        efficiency_result = evaluation_results.get("results", [{}])[1]
        if efficiency_result.get("score", 0) < efficiency_result.get("target", 0.90):
            adjustments.append(self.create_efficiency_adjustment(efficiency_result))

        # 分析鲁棒性
        robustness_result = evaluation_results.get("results", [{}])[2]
        if robustness_result.get("score", 0) < robustness_result.get("target", 0.90):
            adjustments.append(self.create_robustness_adjustment(robustness_result))

        # 分析适应性
        adaptability_result = evaluation_results.get("results", [{}])[3]
        if adaptability_result.get("score", 0) < adaptability_result.get("target", 0.85):
            adjustments.append(self.create_adaptability_adjustment(adaptability_result))

        return adjustments

    def create_accuracy_adjustment(self, result: Dict[str, Any]) -> Adjustment:
        """创建准确性调节"""
        return Adjustment(
            type=AdjustmentType.PARAMETER,
            target="learning_rate",
            current_value=self.parameters["learning_rate"],
            new_value=self.parameters["learning_rate"] * 0.9,
            reason="提高准确性，降低学习率",
            priority="high"
        )

    def create_efficiency_adjustment(self, result: Dict[str, Any]) -> Adjustment:
        """创建效率调节"""
        return Adjustment(
            type=AdjustmentType.RESOURCE,
            target="parallel_workers",
            current_value=self.parameters["parallel_workers"],
            new_value=min(self.parameters["parallel_workers"] + 2, 8),
            reason="提高效率，增加并行工作线程",
            priority="medium"
        )

    def create_robustness_adjustment(self, result: Dict[str, Any]) -> Adjustment:
        """创建鲁棒性调节"""
        return Adjustment(
            type=AdjustmentType.STRATEGY,
            target="reasoning",
            current_value=self.strategies["reasoning"],
            new_value="probabilistic",
            reason="提高鲁棒性，使用概率推理",
            priority="medium"
        )

    def create_adaptability_adjustment(self, result: Dict[str, Any]) -> Adjustment:
        """创建适应性调节"""
        return Adjustment(
            type=AdjustmentType.STRATEGY,
            target="learning",
            current_value=self.strategies["learning"],
            new_value="meta_learning",
            reason="提高适应性，使用元学习",
            priority="high"
        )

    def apply_adjustment(self, adjustment: Adjustment) -> bool:
        """应用调节"""
        try:
            adjustment.status = "applying"

            if adjustment.type == AdjustmentType.PARAMETER:
                success = self.apply_parameter_adjustment(adjustment)
            elif adjustment.type == AdjustmentType.STRATEGY:
                success = self.apply_strategy_adjustment(adjustment)
            elif adjustment.type == AdjustmentType.STRUCTURE:
                success = self.apply_structure_adjustment(adjustment)
            elif adjustment.type == AdjustmentType.RESOURCE:
                success = self.apply_resource_adjustment(adjustment)
            else:
                success = False

            if success:
                adjustment.status = "completed"
                self.adjustment_history.append(adjustment)
            else:
                adjustment.status = "failed"

            return success

        except Exception as e:
            adjustment.status = "failed"
            adjustment.error = str(e)
            return False

    def apply_parameter_adjustment(self, adjustment: Adjustment) -> bool:
        """应用参数调节"""
        self.parameters[adjustment.target] = adjustment.new_value
        print(f"参数调节: {adjustment.target} = {adjustment.new_value}")
        return True

    def apply_strategy_adjustment(self, adjustment: Adjustment) -> bool:
        """应用策略调节"""
        self.strategies[adjustment.target] = adjustment.new_value
        print(f"策略调节: {adjustment.target} = {adjustment.new_value}")
        return True

    def apply_structure_adjustment(self, adjustment: Adjustment) -> bool:
        """应用结构调节"""
        print(f"结构调节: {adjustment.target}")
        return True

    def apply_resource_adjustment(self, adjustment: Adjustment) -> bool:
        """应用资源调节"""
        self.parameters[adjustment.target] = adjustment.new_value
        print(f"资源调节: {adjustment.target} = {adjustment.new_value}")
        return True

    def auto_regulate(self, evaluation_results: Dict[str, Any]) -> List[Adjustment]:
        """自动调节"""
        # 分析评估结果
        adjustments = self.analyze_evaluation_results(evaluation_results)

        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        adjustments.sort(key=lambda x: priority_order[x.priority])

        # 应用调节
        applied_adjustments = []
        for adjustment in adjustments:
            success = self.apply_adjustment(adjustment)
            if success:
                applied_adjustments.append(adjustment)

        return applied_adjustments

    def get_current_parameters(self) -> Dict[str, Any]:
        """获取当前参数"""
        return self.parameters.copy()

    def get_current_strategies(self) -> Dict[str, Any]:
        """获取当前策略"""
        return self.strategies.copy()

    def get_adjustment_history(self) -> List[Dict[str, Any]]:
        """获取调节历史"""
        return [adj.__dict__ for adj in self.adjustment_history]

    def save_state(self, filepath: str = "regulation_state.json"):
        """保存状态"""
        state = {
            "parameters": self.parameters,
            "strategies": self.strategies,
            "adjustment_history": self.get_adjustment_history()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def load_state(self, filepath: str = "regulation_state.json") -> bool:
        """加载状态"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state = json.load(f)

            self.parameters = state["parameters"]
            self.strategies = state["strategies"]
            self.adjustment_history = [
                Adjustment(**adj) for adj in state["adjustment_history"]
            ]

            return True

        except Exception as e:
            print(f"加载状态失败: {e}")
            return False


def main():
    """主函数"""
    # 创建自我调节器
    regulator = SelfRegulator()

    # 模拟评估结果
    evaluation_results = {
        "results": [
            {"dimension": "准确性", "score": 0.92, "target": 0.95},
            {"dimension": "效率", "score": 0.85, "target": 0.90},
            {"dimension": "鲁棒性", "score": 0.88, "target": 0.90},
            {"dimension": "适应性", "score": 0.78, "target": 0.85}
        ]
    }

    # 自动调节
    adjustments = regulator.auto_regulate(evaluation_results)

    print(f"应用了 {len(adjustments)} 个调节")

    # 保存状态
    regulator.save_state()

    return adjustments


if __name__ == "__main__":
    main()

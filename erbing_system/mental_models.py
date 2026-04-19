"""
二饼心智模型 - Mental Loop, Tree of Thoughts, Meta-Controller
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SimulationResult:
    """模拟结果"""
    action: str
    predicted_outcome: str
    confidence: float
    risk_level: float
    success_probability: float


@dataclass
class ThoughtNode:
    """思维节点"""
    id: str
    content: str
    depth: int
    confidence: float
    children: List['ThoughtNode'] = field(default_factory=list)
    parent: Optional['ThoughtNode'] = None
    value: float = 0.0


class MentalLoop:
    """心智循环 - 内部模拟器"""

    def __init__(self):
        self.simulation_history: List[SimulationResult] = []
        self.learning_rate = 0.1

    def simulate_action(
        self,
        action: str,
        context: Dict
    ) -> SimulationResult:
        """模拟行动"""
        # 1. 在心智模型中模拟
        predicted_outcome = self._predict_outcome(action, context)

        # 2. 预测后果
        consequences = self._predict_consequences(action, context)

        # 3. 评估风险
        risk = self._assess_risk(action, context, consequences)

        # 4. 计算成功概率
        success_prob = self._calculate_success_probability(action, context, risk)

        # 5. 计算置信度
        confidence = self._calculate_confidence(action, context, success_prob)

        result = SimulationResult(
            action=action,
            predicted_outcome=predicted_outcome,
            confidence=confidence,
            risk_level=risk,
            success_probability=success_prob
        )

        self.simulation_history.append(result)

        return result

    def _predict_outcome(self, action: str, context: Dict) -> str:
        """预测结果"""
        # 简化的预测逻辑
        if "分析" in action:
            return "获得洞察"
        elif "执行" in action:
            return "完成任务"
        elif "学习" in action:
            return "获得知识"
        else:
            return "产生结果"

    def _predict_consequences(self, action: str, context: Dict) -> List[str]:
        """预测后果"""
        consequences = []

        if "分析" in action:
            consequences.append("消耗时间")
            consequences.append("获得信息")
        elif "执行" in action:
            consequences.append("消耗资源")
            consequences.append("产生结果")
        elif "学习" in action:
            consequences.append("消耗精力")
            consequences.append("提升能力")

        return consequences

    def _assess_risk(self, action: str, context: Dict, consequences: List[str]) -> float:
        """评估风险"""
        # 基于后果评估风险
        risk = 0.0

        for consequence in consequences:
            if "消耗" in consequence:
                risk += 0.1
            if "失败" in consequence:
                risk += 0.3

        return min(risk, 1.0)

    def _calculate_success_probability(
        self,
        action: str,
        context: Dict,
        risk: float
    ) -> float:
        """计算成功概率"""
        # 基于风险和上下文计算
        base_prob = 0.7

        # 风险调整
        prob = base_prob * (1 - risk)

        # 上下文调整
        if context.get('experience', 0) > 0.5:
            prob += 0.1

        return min(prob, 1.0)

    def _calculate_confidence(
        self,
        action: str,
        context: Dict,
        success_prob: float
    ) -> float:
        """计算置信度"""
        # 基于成功概率和历史经验
        base_confidence = success_prob

        # 历史经验调整
        if self.simulation_history:
            avg_success = np.mean([r.success_probability for r in self.simulation_history])
            base_confidence = (base_confidence + avg_success) / 2

        return base_confidence

    def decide(
        self,
        action: str,
        context: Dict
    ) -> Tuple[bool, str]:
        """决策：执行或调整"""
        # 模拟行动
        result = self.simulate_action(action, context)

        # 决策
        if result.risk_level < 0.3 and result.success_probability > 0.7:
            return True, "执行"
        elif result.risk_level < 0.5:
            return True, "谨慎执行"
        else:
            return False, "调整行动"

    def learn(self, actual_outcome: str, success: bool):
        """学习"""
        # 更新模拟历史
        if self.simulation_history:
            last_sim = self.simulation_history[-1]

            # 调整预测准确性
            if success:
                # 成功增强信心
                last_sim.confidence = min(1.0, last_sim.confidence + self.learning_rate * 0.1)
            else:
                # 失败降低信心
                last_sim.confidence = max(0.0, last_sim.confidence - self.learning_rate * 0.2)

        logger.info(f"Mental Loop learned: {actual_outcome} (Success: {success})")


class TreeOfThoughts:
    """思维树 - 多路径思考"""

    def __init__(self, max_depth: int = 3, max_branches: int = 3):
        self.max_depth = max_depth
        self.max_branches = max_branches
        self.root: Optional[ThoughtNode] = None
        self.best_path: List[ThoughtNode] = []

    def generate_tree(self, problem: str) -> ThoughtNode:
        """生成思维树"""
        # 创建根节点
        self.root = ThoughtNode(
            id="root",
            content=problem,
            depth=0,
            confidence=0.5
        )

        # 递归生成子节点
        self._expand_node(self.root)

        # 评估所有路径
        self._evaluate_paths()

        return self.root

    def _expand_node(self, node: ThoughtNode):
        """扩展节点"""
        if node.depth >= self.max_depth:
            return

        # 生成子节点
        branches = self._generate_branches(node.content)

        for i, branch in enumerate(branches[:self.max_branches]):
            child = ThoughtNode(
                id=f"{node.id}-{i}",
                content=branch,
                depth=node.depth + 1,
                confidence=0.5,
                parent=node
            )

            node.children.append(child)

            # 递归扩展
            self._expand_node(child)

    def _generate_branches(self, content: str) -> List[str]:
        """生成分支"""
        # 简化的分支生成逻辑
        branches = []

        if "分析" in content:
            branches = [
                "深入分析",
                "快速分析",
                "全面分析"
            ]
        elif "执行" in content:
            branches = [
                "直接执行",
                "分步执行",
                "优化执行"
            ]
        elif "学习" in content:
            branches = [
                "理论学习",
                "实践学习",
                "混合学习"
            ]
        else:
            branches = [
                "方案A",
                "方案B",
                "方案C"
            ]

        return branches

    def _evaluate_paths(self):
        """评估所有路径"""
        if not self.root:
            return

        # 深度优先搜索评估
        self._dfs_evaluate(self.root, [])

        # 找到最佳路径
        self.best_path = self._find_best_path()

    def _dfs_evaluate(self, node: ThoughtNode, path: List[ThoughtNode]):
        """深度优先评估"""
        path.append(node)

        if not node.children:
            # 叶子节点，计算路径值
            path_value = self._calculate_path_value(path)
            node.value = path_value
        else:
            # 非叶子节点，递归评估子节点
            for child in node.children:
                self._dfs_evaluate(child, path.copy())

            # 节点值 = 子节点最大值
            node.value = max([child.value for child in node.children])

    def _calculate_path_value(self, path: List[ThoughtNode]) -> float:
        """计算路径值"""
        # 简化的路径值计算
        value = 0.0

        for i, node in enumerate(path):
            # 深度越深，权重越高
            weight = (i + 1) / len(path)
            value += node.confidence * weight

        return value / len(path)

    def _find_best_path(self) -> List[ThoughtNode]:
        """找到最佳路径"""
        if not self.root:
            return []

        # 深度优先搜索
        best_path = []
        best_value = 0.0

        self._dfs_find_best(self.root, [], best_path, best_value)

        return best_path

    def _dfs_find_best(
        self,
        node: ThoughtNode,
        current_path: List[ThoughtNode],
        best_path: List[ThoughtNode],
        best_value: float
    ):
        """深度优先搜索最佳路径"""
        current_path.append(node)

        if not node.children:
            # 叶子节点
            path_value = node.value
            if path_value > best_value:
                best_path.clear()
                best_path.extend(current_path)
                best_value = path_value
        else:
            # 非叶子节点
            for child in node.children:
                self._dfs_find_best(child, current_path.copy(), best_path, best_value)

    def get_best_solution(self) -> str:
        """获取最佳解决方案"""
        if not self.best_path:
            return "无解决方案"

        # 构建解决方案
        solution = " -> ".join([node.content for node in self.best_path])

        return solution

    def visualize(self) -> str:
        """可视化思维树"""
        if not self.root:
            return "空树"

        lines = []
        self._dfs_visualize(self.root, "", lines)

        return "\n".join(lines)

    def _dfs_visualize(self, node: ThoughtNode, prefix: str, lines: List[str]):
        """深度优先可视化"""
        lines.append(f"{prefix}{node.content} (conf={node.confidence:.2f}, val={node.value:.2f})")

        for i, child in enumerate(node.children):
            is_last = (i == len(node.children) - 1)
            new_prefix = prefix + ("    " if is_last else "│   ")
            self._dfs_visualize(child, new_prefix, lines)


class MetaController:
    """元控制器 - 高层决策"""

    def __init__(self):
        self.mental_loop = MentalLoop()
        self.tree_of_thoughts = TreeOfThoughts()
        self.decision_history: List[Dict] = []
        self.performance_metrics: Dict[str, float] = {
            'accuracy': 0.0,
            'efficiency': 0.0,
            'adaptability': 0.0,
        }

    def process(
        self,
        input_text: str,
        context: Dict
    ) -> Dict:
        """处理输入"""
        # 1. 生成思维树
        tree = self.tree_of_thoughts.generate_tree(input_text)

        # 2. 获取最佳解决方案
        best_solution = self.tree_of_thoughts.get_best_solution()

        # 3. 心智循环模拟
        action = best_solution.split(" -> ")[-1] if " -> " in best_solution else best_solution
        simulation = self.mental_loop.simulate_action(action, context)

        # 4. 决策
        should_execute, decision = self.mental_loop.decide(action, context)

        # 5. 生成最终决策
        result = {
            'input': input_text,
            'best_solution': best_solution,
            'simulation': {
                'action': simulation.action,
                'predicted_outcome': simulation.predicted_outcome,
                'confidence': simulation.confidence,
                'risk_level': simulation.risk_level,
                'success_probability': simulation.success_probability,
            },
            'decision': decision,
            'should_execute': should_execute,
            'tree_visualization': self.tree_of_thoughts.visualize(),
        }

        # 记录决策历史
        self.decision_history.append(result)

        return result

    def update_performance(self, success: bool, efficiency: float):
        """更新性能指标"""
        # 准确度
        if success:
            self.performance_metrics['accuracy'] = min(1.0, self.performance_metrics['accuracy'] + 0.1)
        else:
            self.performance_metrics['accuracy'] = max(0.0, self.performance_metrics['accuracy'] - 0.05)

        # 效率
        self.performance_metrics['efficiency'] = min(1.0, efficiency)

        # 适应性
        adaptability = (self.performance_metrics['accuracy'] + self.performance_metrics['efficiency']) / 2
        self.performance_metrics['adaptability'] = adaptability

        logger.info(f"Performance updated: {self.performance_metrics}")

    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'decision_count': len(self.decision_history),
            'performance_metrics': self.performance_metrics.copy(),
            'mental_loop_history': len(self.mental_loop.simulation_history),
            'tree_depth': self.tree_of_thoughts.max_depth,
        }


# 便捷函数
def create_meta_controller() -> MetaController:
    """创建元控制器"""
    return MetaController()


def simulate_decision(
    controller: MetaController,
    input_text: str,
    context: Dict
) -> Dict:
    """模拟决策"""
    return controller.process(input_text, context)
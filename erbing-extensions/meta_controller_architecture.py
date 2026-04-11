#!/usr/bin/env python3
"""
Erbing 扩展架构 - Meta-Controller（元控制器）
任务路由和多专家协调系统
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "memory" / "database"))
from hybrid_memory import get_memory


class ExpertAgent:
    """专家Agent基类"""

    def __init__(self, name: str, expertise: str, model_interface=None):
        self.name = name
        self.expertise = expertise
        self.model = model_interface

    def execute(self, task: str, context: str = "") -> Dict:
        """执行任务"""
        raise NotImplementedError


class ArchitectureExpert(ExpertAgent):
    """架构设计专家"""

    def __init__(self, model_interface=None):
        super().__init__(
            name="Architecture Expert",
            expertise="system architecture, design patterns, scalability",
            model_interface=model_interface
        )

    def execute(self, task: str, context: str = "") -> Dict:
        """执行架构设计任务"""
        prompt = f"作为架构设计专家，请设计：{task}\n\n上下文：{context}"

        if self.model:
            result = self.model.generate(prompt)
        else:
            result = f"[架构专家] 针对 '{task}' 的设计方案：\n1. 模块化架构\n2. 微服务设计\n3. 可扩展性考虑"

        return {
            "expert": self.name,
            "task": task,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }


class CodeExpert(ExpertAgent):
    """代码生成专家"""

    def __init__(self, model_interface=None):
        super().__init__(
            name="Code Expert",
            expertise="coding, implementation, debugging, optimization",
            model_interface=model_interface
        )

    def execute(self, task: str, context: str = "") -> Dict:
        """执行代码生成任务"""
        prompt = f"作为代码专家，请实现：{task}\n\n上下文：{context}"

        if self.model:
            result = self.model.generate(prompt)
        else:
            result = f"[代码专家] 针对 '{task}' 的代码实现：\n```python\n# 实现代码\n```"

        return {
            "expert": self.name,
            "task": task,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }


class MemoryExpert(ExpertAgent):
    """记忆系统专家"""

    def __init__(self, model_interface=None):
        super().__init__(
            name="Memory Expert",
            expertise="memory systems, retrieval, storage, optimization",
            model_interface=model_interface
        )

    def execute(self, task: str, context: str = "") -> Dict:
        """执行记忆系统任务"""
        # 使用数据库检索
        relevant = self.memory.search(task, limit=5)

        prompt = f"作为记忆系统专家，请设计：{task}\n\n相关记忆：{[m['title'] for m in relevant]}"

        if self.model:
            result = self.model.generate(prompt)
        else:
            result = f"[记忆专家] 针对 '{task}' 的记忆系统设计：\n使用四策略检索优化"

        return {
            "expert": self.name,
            "task": task,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }


class ErbingMetaController:
    """
    Meta-Controller 架构实现

    流程：
    1. 任务分类：分析任务类型
    2. 专家选择：路由到合适的专家
    3. 任务执行：专家执行任务
    4. 结果聚合：如果有多个专家，聚合结果
    """

    def __init__(self, model_interface=None):
        self.memory = get_memory()
        self.model = model_interface

        # 注册专家池
        self.experts = {
            "architecture": ArchitectureExpert(model_interface),
            "code": CodeExpert(model_interface),
            "memory": MemoryExpert(model_interface),
        }

        # 任务类型映射
        self.task_type_keywords = {
            "architecture": ["架构", "设计", "系统", "architecture", "design", "system"],
            "code": ["代码", "实现", "编程", "code", "implement", "python"],
            "memory": ["记忆", "检索", "存储", "memory", "retrieval", "storage"],
        }

    def route_task(self, task: str, context: str = "") -> Dict:
        """
        路由任务到合适的专家

        参数:
            task: 任务描述
            context: 上下文

        返回:
            {
                "task_type": 任务类型,
                "selected_expert": 选择的专家,
                "execution_result": 执行结果,
                "alternatives": 其他可选专家
            }
        """
        # 1. 分类任务
        task_type = self._classify_task(task)

        # 2. 选择专家
        expert = self._select_expert(task_type)
        alternatives = self._get_alternative_experts(task_type)

        # 3. 执行任务
        execution_result = expert.execute(task, context)

        # 4. 保存路由记录
        self._save_routing_to_memory(task, task_type, expert.name, execution_result)

        return {
            "task_type": task_type,
            "selected_expert": expert.name,
            "execution_result": execution_result,
            "alternatives": [e.name for e in alternatives]
        }

    def route_multi_expert(self, task: str, context: str = "") -> Dict:
        """
        多专家协作路由

        参数:
            task: 任务描述
            context: 上下文

        返回:
            {
                "task_types": 检测到的多种类型,
                "selected_experts": 选择的多个专家,
                "execution_results": 各专家执行结果,
                "aggregated_result": 聚合结果
            }
        """
        # 1. 检测多种任务类型
        task_types = self._detect_multiple_types(task)

        # 2. 选择多个专家
        experts = [self._select_expert(t) for t in task_types]

        # 3. 各专家执行
        execution_results = []
        for expert in experts:
            result = expert.execute(task, context)
            execution_results.append(result)

        # 4. 聚合结果
        aggregated = self._aggregate_expert_results(task, execution_results)

        return {
            "task_types": task_types,
            "selected_experts": [e.name for e in experts],
            "execution_results": execution_results,
            "aggregated_result": aggregated
        }

    def _classify_task(self, task: str) -> str:
        """分类任务类型"""
        task_lower = task.lower()

        # 计算每种类型的匹配度
        scores = {}
        for task_type, keywords in self.task_type_keywords.items():
            score = sum(1 for kw in keywords if kw in task_lower)
            scores[task_type] = score

        # 选择得分最高的类型
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        # 默认返回代码类型
        return "code"

    def _detect_multiple_types(self, task: str) -> List[str]:
        """检测多种任务类型"""
        task_lower = task.lower()

        detected = []
        for task_type, keywords in self.task_type_keywords.items():
            if any(kw in task_lower for kw in keywords):
                detected.append(task_type)

        # 如果没有检测到，返回默认
        return detected if detected else ["code"]

    def _select_expert(self, task_type: str) -> ExpertAgent:
        """选择专家"""
        return self.experts.get(task_type, self.experts["code"])

    def _get_alternative_experts(self, task_type: str) -> List[ExpertAgent]:
        """获取备选专家"""
        alternatives = []
        for t, expert in self.experts.items():
            if t != task_type:
                alternatives.append(expert)
        return alternatives

    def _aggregate_expert_results(self, task: str, results: List[Dict]) -> str:
        """聚合多专家结果"""
        # 如果有模型接口，让模型聚合
        if self.model:
            prompt = f"""
聚合以下专家意见：

任务: {task}

专家结果:
{json.dumps([r['result'][:300] for r in results], ensure_ascii=False, indent=2)}

请提供综合建议：
"""
            return self.model.generate(prompt)

        # 否则简单拼接
        aggregated = f"综合 {len(results)} 位专家的意见：\n\n"
        for i, result in enumerate(results, 1):
            aggregated += f"专家{i} ({result['expert']}):\n{result['result'][:200]}...\n\n"

        return aggregated

    def _save_routing_to_memory(self, task, task_type, expert_name, result):
        """保存路由记录到数据库"""
        conn = self.memory.sqlite_conn
        cursor = conn.cursor()

        content = f"""
任务: {task}

类型: {task_type}
选择专家: {expert_name}

执行结果:
{result['result'][:500]}
"""

        cursor.execute("""
            INSERT INTO memories (type, title, content, category, tags, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            'meta_routing',
            f'Meta: {task[:50]}',
            content,
            'meta-controller',
            'meta, routing, expert',
            7
        ))

        conn.commit()


# 示例使用
def example_usage():
    """示例：使用 Meta-Controller 架构"""
    print("="*60)
    print("Erbing Meta-Controller Architecture - Example")
    print("="*60)

    meta_controller = ErbingMetaController()

    # 测试1: 单专家路由
    print("\n[Test 1: Single Expert Routing]")
    task1 = "设计一个高效的记忆检索架构"
    result1 = meta_controller.route_task(task1)
    print(f"Task: {task1}")
    print(f"Type: {result1['task_type']}")
    print(f"Expert: {result1['selected_expert']}")
    print(f"Result: {result1['execution_result']['result'][:150]}...")

    # 测试2: 多专家协作
    print("\n[Test 2: Multi-Expert Collaboration]")
    task2 = "实现一个具有记忆系统的代码架构"
    result2 = meta_controller.route_multi_expert(task2)
    print(f"Task: {task2}")
    print(f"Types: {result2['task_types']}")
    print(f"Experts: {result2['selected_experts']}")
    print(f"Aggregated: {result2['aggregated_result'][:200]}...")


if __name__ == "__main__":
    example_usage()

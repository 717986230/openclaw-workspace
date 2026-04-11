#!/usr/bin/env python3
"""
Erbing 扩展架构 - 集成测试
整合 Reflection + PEV + Meta-Controller
"""
import sys
from pathlib import Path
from typing import Dict, Optional

sys.path.insert(0, str(Path(__file__).parent))
from reflection_architecture import ErbingReflection
from pev_architecture import ErbingPEV
from meta_controller_architecture import ErbingMetaController


class ErbingIntegratedArchitecture:
    """
    集成架构：Reflection + PEV + Meta-Controller

    组合使用三种架构：
    1. Meta-Controller 负责任务路由
    2. PEV 负责规划和验证
    3. Reflection 负责结果优化
    """

    def __init__(self, model_interface=None):
        self.reflection = ErbingReflection(model_interface)
        self.pev = ErbingPEV(model_interface)
        self.meta_controller = ErbingMetaController(model_interface)
        self.model = model_interface

    def process_task(
        self,
        task: str,
        context: str = "",
        use_reflection: bool = True,
        use_pev: bool = True,
        use_meta: bool = True
    ) -> Dict:
        """
        综合处理任务

        参数:
            task: 任务描述
            context: 上下文
            use_reflection: 是否使用反思
            use_pev: 是否使用PEV
            use_meta: 是否使用元控制器

        返回:
            {
                "task": 任务,
                "routing": 元控制器路由结果（如果启用）,
                "execution": PEV执行结果（如果启用）,
                "reflection": 反思结果（如果启用）,
                "final_output": 最终输出
            }
        """
        result = {"task": task}

        # 1. Meta-Controller 路由（如果启用）
        if use_meta:
            routing = self.meta_controller.route_task(task, context)
            result["routing"] = routing
            # 使用路由结果作为上下文
            context += f"\n专家建议: {routing['execution_result']['result'][:200]}"

        # 2. PEV 执行（如果启用）
        if use_pev:
            pev_result = self.pev.execute_with_pev(task, context)
            result["execution"] = pev_result
            current_output = pev_result["final_output"]
        else:
            # 直接生成输出
            current_output = self._simple_generate(task, context)
            result["execution"] = {"output": current_output}

        # 3. Reflection 优化（如果启用）
        if use_reflection:
            reflection_result = self.reflection.generate_with_reflection(
                query=task,
                context=context + "\n" + current_output,
                reflection_mode="balanced"
            )
            result["reflection"] = reflection_result
            result["final_output"] = reflection_result["final"]
        else:
            result["final_output"] = current_output

        return result

    def _simple_generate(self, task: str, context: str) -> str:
        """简单生成（不使用PEV）"""
        if self.model:
            return self.model.generate(f"Context: {context}\n\nTask: {task}")

        return f"[简单生成] 针对 '{task}' 的回答：基于当前上下文的直接回复。"


def run_integration_tests():
    """运行集成测试"""
    print("="*60)
    print("Erbing Integrated Architecture - Tests")
    print("="*60)

    integrated = ErbingIntegratedArchitecture()

    # 测试1: 全架构组合
    print("\n[Test 1: Full Architecture (Meta + PEV + Reflection)]")
    print("-" * 60)

    task1 = "设计并实现一个智能记忆检索系统"
    result1 = integrated.process_task(
        task1,
        use_reflection=True,
        use_pev=True,
        use_meta=True
    )

    print(f"Task: {task1}")
    print(f"\n[Routing]")
    print(f"  Type: {result1['routing']['task_type']}")
    print(f"  Expert: {result1['routing']['selected_expert']}")

    print(f"\n[PEV Execution]")
    print(f"  Steps: {len(result1['execution']['plan']['steps'])}")
    print(f"  Retries: {result1['execution']['retries']}")
    print(f"  Success: {result1['execution']['success']}")

    print(f"\n[Reflection]")
    print(f"  Iterations: {result1['reflection']['iterations']}")

    print(f"\n[Final Output]")
    print(f"  {result1['final_output'][:200]}...")

    # 测试2: 仅PEV + Reflection
    print("\n\n" + "="*60)
    print("[Test 2: PEV + Reflection (No Meta)]")
    print("-" * 60)

    task2 = "编写一个Python函数实现向量搜索"
    result2 = integrated.process_task(
        task2,
        use_reflection=True,
        use_pev=True,
        use_meta=False
    )

    print(f"Task: {task2}")
    print(f"\n[PEV Execution]")
    print(f"  Steps: {len(result2['execution']['plan']['steps'])}")

    print(f"\n[Reflection]")
    print(f"  Iterations: {result2['reflection']['iterations']}")

    print(f"\n[Final Output]")
    print(f"  {result2['final_output'][:200]}...")

    # 测试3: 仅Reflection
    print("\n\n" + "="*60)
    print("[Test 3: Reflection Only]")
    print("-" * 60)

    task3 = "解释什么是四策略检索"
    result3 = integrated.process_task(
        task3,
        use_reflection=True,
        use_pev=False,
        use_meta=False
    )

    print(f"Task: {task3}")
    print(f"\n[Reflection]")
    print(f"  Iterations: {result3['reflection']['iterations']}")

    print(f"\n[Final Output]")
    print(f"  {result3['final_output'][:200]}...")


def performance_comparison():
    """性能对比测试"""
    import time

    print("\n" + "="*60)
    print("Performance Comparison")
    print("="*60)

    integrated = ErbingIntegratedArchitecture()
    task = "优化记忆检索性能"

    # 测试不同配置的性能
    configs = [
        ("Simple", False, False, False),
        ("Reflection", True, False, False),
        ("PEV", False, True, False),
        ("Meta", False, False, True),
        ("PEV+Reflection", True, True, False),
        ("Full", True, True, True),
    ]

    results = []

    for name, use_ref, use_pev, use_meta in configs:
        start = time.time()

        result = integrated.process_task(
            task,
            use_reflection=use_ref,
            use_pev=use_pev,
            use_meta=use_meta
        )

        elapsed = time.time() - start

        results.append({
            "name": name,
            "time": elapsed,
            "output_length": len(result["final_output"])
        })

        print(f"{name:20s} | Time: {elapsed:.2f}s | Length: {len(result['final_output'])}")

    # 找出最优配置
    fastest = min(results, key=lambda x: x["time"])
    longest = max(results, key=lambda x: x["output_length"])

    print(f"\nFastest: {fastest['name']} ({fastest['time']:.2f}s)")
    print(f"Most detailed: {longest['name']} ({longest['output_length']} chars)")


if __name__ == "__main__":
    run_integration_tests()
    performance_comparison()

#!/usr/bin/env python3
"""
Erbing 扩展架构 - PEV（Plan-Execute-Verify）
规划-执行-验证循环，带自我校正能力
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "memory" / "database"))
from hybrid_memory import get_memory


class ErbingPEV:
    """
    PEV 架构实现

    流程：
    1. Plan（规划）：分解任务为步骤
    2. Execute（执行）：逐步执行计划
    3. Verify（验证）：检查执行结果
    4. 循环：如果验证失败，重新规划
    """

    def __init__(self, model_interface=None):
        self.memory = get_memory()
        self.model = model_interface
        self.max_retries = 2  # 最多重试2轮

    def execute_with_pev(
        self,
        task: str,
        context: str = "",
        auto_retry: bool = True
    ) -> Dict:
        """
        PEV 执行流程

        参数:
            task: 任务描述
            context: 上下文
            auto_retry: 是否自动重试

        返回:
            {
                "plan": 计划步骤列表,
                "execution_results": 执行结果,
                "verification": 验证结果,
                "final_output": 最终输出,
                "retries": 重试次数,
                "success": 是否成功
            }
        """
        # 检索相关记忆
        relevant_memories = self.memory.search(task, limit=5)
        memory_context = "\n".join([m["content"][:150] for m in relevant_memories[:3]])

        retries = 0
        all_plans = []
        all_executions = []

        while retries <= self.max_retries:
            # 1. Plan（规划）
            plan = self._create_plan(task, context + "\n" + memory_context, retries)
            all_plans.append(plan)

            # 2. Execute（执行）
            execution_results = []
            for i, step in enumerate(plan["steps"]):
                result = self._execute_step(step, i)
                execution_results.append(result)

            all_executions.append(execution_results)

            # 3. Verify（验证）
            verification = self._verify_results(task, plan, execution_results)

            # 如果验证通过，返回结果
            if verification["success"]:
                # 保存成功案例到数据库
                self._save_pev_to_memory(
                    task, plan, execution_results, verification, success=True
                )

                return {
                    "plan": plan,
                    "execution_results": execution_results,
                    "verification": verification,
                    "final_output": self._aggregate_results(execution_results),
                    "retries": retries,
                    "success": True
                }

            # 如果验证失败，决定是否重试
            if auto_retry and retries < self.max_retries:
                print(f"[Retry {retries + 1}] Verification failed: {verification['reason']}")
                retries += 1
                # 根据验证失败原因调整上下文
                context = self._adjust_context_from_failure(
                    context, verification, execution_results
                )
            else:
                # 不再重试，返回失败结果
                self._save_pev_to_memory(
                    task, plan, execution_results, verification, success=False
                )

                return {
                    "plan": plan,
                    "execution_results": execution_results,
                    "verification": verification,
                    "final_output": self._aggregate_results(execution_results),
                    "retries": retries,
                    "success": False,
                    "failure_reason": verification["reason"]
                }

    def _create_plan(self, task: str, context: str, retry_count: int) -> Dict:
        """创建执行计划"""
        plan_prompt = f"""
任务: {task}

上下文: {context}

{'这是第 ' + str(retry_count + 1) + ' 次尝试，之前尝试失败了。请调整计划。' if retry_count > 0 else ''}

请制定详细的执行计划，包含：
1. 步骤列表（每个步骤要具体、可执行）
2. 预期输出
3. 验证标准

格式：
Steps:
1. ...
2. ...
Expected Output: ...
Verification Criteria: ...
"""

        # 如果有模型接口
        if self.model:
            plan_text = self.model.generate(plan_prompt)
        else:
            # 模拟计划
            plan_text = f"""
Steps:
1. 分析任务需求
2. 检索相关资源
3. 生成解决方案
4. 验证结果完整性

Expected Output: 完整的任务解决方案
Verification Criteria: 包含所有必要信息，逻辑清晰，可执行
"""

        # 解析计划
        steps = self._parse_plan_steps(plan_text)

        return {
            "text": plan_text,
            "steps": steps,
            "retry_attempt": retry_count,
            "timestamp": datetime.now().isoformat()
        }

    def _parse_plan_steps(self, plan_text: str) -> List[Dict]:
        """解析计划步骤"""
        steps = []
        lines = plan_text.split('\n')

        for line in lines:
            # 匹配 "1. ..." 或 "- ..."
            if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-')):
                step_desc = line.strip()
                # 移除编号
                if step_desc[0].isdigit():
                    step_desc = '.'.join(step_desc.split('.')[1:]).strip()

                steps.append({
                    "description": step_desc,
                    "status": "pending"
                })

        # 如果没有解析到步骤，创建默认步骤
        if not steps:
            steps = [
                {"description": "分析任务", "status": "pending"},
                {"description": "执行任务", "status": "pending"},
                {"description": "验证结果", "status": "pending"}
            ]

        return steps

    def _execute_step(self, step: Dict, step_index: int) -> Dict:
        """执行单个步骤"""
        step_prompt = f"执行步骤 {step_index + 1}: {step['description']}"

        # 如果有模型接口
        if self.model:
            result = self.model.generate(step_prompt)
        else:
            # 模拟执行
            result = f"[执行结果] {step['description']} 完成"

        return {
            "step": step["description"],
            "result": result,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }

    def _verify_results(
        self,
        task: str,
        plan: Dict,
        execution_results: List[Dict]
    ) -> Dict:
        """验证执行结果"""
        verify_prompt = f"""
验证任务执行结果：

任务: {task}

计划步骤:
{json.dumps([s['description'] for s in plan['steps']], ensure_ascii=False, indent=2)}

执行结果:
{json.dumps([r['result'][:200] for r in execution_results], ensure_ascii=False, indent=2)}

请验证：
1. 是否所有步骤都执行完成？
2. 结果是否满足任务需求？
3. 是否存在逻辑错误或遗漏？

结论：通过/失败
原因：...
"""

        # 如果有模型接口
        if self.model:
            verification_text = self.model.generate(verify_prompt)
        else:
            # 模拟验证
            verification_text = """
验证分析：
1. 所有步骤已执行完成 ✓
2. 结果满足基本需求 ✓
3. 逻辑清晰，无明显遗漏 ✓

结论：通过
原因：所有步骤完成，结果符合预期
"""

        # 解析验证结果
        success = "通过" in verification_text or "成功" in verification_text
        reason = "验证通过" if success else "验证失败"

        return {
            "text": verification_text,
            "success": success,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }

    def _adjust_context_from_failure(
        self,
        context: str,
        verification: Dict,
        execution_results: List[Dict]
    ) -> str:
        """根据失败调整上下文"""
        failure_info = f"\n上次尝试失败原因: {verification['reason']}\n"
        failure_info += f"执行结果: {[r['result'][:100] for r in execution_results]}\n"
        return context + failure_info

    def _aggregate_results(self, execution_results: List[Dict]) -> str:
        """聚合执行结果"""
        results = [r["result"] for r in execution_results]
        return "\n\n".join(results)

    def _save_pev_to_memory(
        self,
        task,
        plan,
        execution_results,
        verification,
        success
    ):
        """保存 PEV 记录到数据库"""
        conn = self.memory.sqlite_conn
        cursor = conn.cursor()

        content = f"""
任务: {task}

计划:
{plan['text'][:500]}

执行步骤: {len(execution_results)}
执行结果:
{self._aggregate_results(execution_results)[:500]}

验证:
{verification['text'][:300]}

结果: {'成功' if success else '失败'}
"""

        cursor.execute("""
            INSERT INTO memories (type, title, content, category, tags, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            'pev_execution',
            f'PEV: {task[:50]}',
            content,
            'pev',
            'pev, plan, execute, verify',
            9 if success else 6
        ))

        conn.commit()


# 示例使用
def example_usage():
    """示例：使用 PEV 架构"""
    print("="*60)
    print("Erbing PEV Architecture - Example")
    print("="*60)

    pev = ErbingPEV()

    # 测试任务
    task = "设计并实现一个智能记忆检索系统"

    print(f"\n[Task] {task}")
    print("\n[Executing with PEV...]")

    result = pev.execute_with_pev(task, auto_retry=True)

    print(f"\n[Plan] {len(result['plan']['steps'])} steps")
    print(f"[Execution] {len(result['execution_results'])} results")
    print(f"[Verification] {'✓ Passed' if result['success'] else '✗ Failed'}")
    print(f"[Retries] {result['retries']}")
    print(f"\n[Final Output]\n{result['final_output'][:300]}...")


if __name__ == "__main__":
    example_usage()

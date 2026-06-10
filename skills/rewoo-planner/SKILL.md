---
name: rewoo-planner
description: ReWOO算法 — 将推理与观察解耦，通过DAG预规划和单次trace解析实现高效多步推理，token消耗与步数线性而非二次方增长
---

# ReWOO Planner Skill

## 核心问题：ReAct的Token二次方膨胀

**ReAct模式的问题**：每个tool observation都要重新注入Planner的prompt
- 8步任务：第8步的prompt包含1+2+3+...+7=28次历史重读
- Token成本 ≈ O(n²)，其中n=步数
- 大部分重读不产生新决策，却在烧钱

**ReWOO的解法**：把推理和观察完全解耦
- Planner**看不到任何tool observations**，只输出完整DAG（带占位变量）
- Worker执行DAG，替换占位变量
- Solver读取resolved trace（一次性），输出最终答案
- Token成本 → O(n)，线性！

## 三层架构

```
用户请求
    ↓
[Planner] ── 生成带占位变量的DAG ──→ 不看任何observation
    ↓
[DAG with #t1, #t2, #t3 vars]
    ↓
[Worker] ── 按拓扑顺序执行 ──→ 替换 #t1 → 实际结果
    ↓
[Resolved Trace: {t1: result1, t2: result2, ...}]
    ↓
[Solver] ── 一次性读取trace ──→ 最终答案
```

## DAG语法

每一步定义为：
```
StepID: tool_name
args: {param1: value1, param2: #upstream_step_output}
```

示例（研究任务）：
```
t1: web_search
args: {query: "2026 AI agent trends"}
t2: summarize
args: {text: #t1.output, max_length: 200}
t3: extract_insights
args: {summary: #t2.output, format: "bullet_points"}
```

## Erbing的ReWOO实现

### 适用场景
- ✅ 多步工具调用任务（搜索→总结→提取→格式化）
- ✅ 步数>3的复杂任务
- ✅ Token成本敏感的批量任务
- ❌ 探索性任务（每步依赖上一步的observation）

### 不适用场景
- ❌ 需要实时调整计划的任务
- ❌ 观察结果直接影响下一步决策的任务
- ❌ 简单单步任务（ReAct更简单）

## 代码实现框架

```python
class ReWOO:
    def __init__(self, planner_llm, solver_llm, tools):
        self.planner = planner_llm   # 强模型：规划判断
        self.solver = solver_llm       # 强模型：最终合成
        self.tools = tools             # 工具注册表

    def run(self, query: str, budget_ms: int = 30000) -> str:
        # 1. Planner生成DAG（不看任何observation）
        plan = self.planner.run(
            query,
            schema=REWOO_SCHEMA,
            tools=list(self.tools.keys())
        )
        
        # 2. Worker执行DAG
        results = {}
        for step in topological_sort(plan.steps):
            args = substitute(step.args, results)  # 替换 #t1 等占位符
            results[step.id] = self._run_tool(step.tool, args)
        
        # 3. Solver一次性读取trace，输出答案
        return self.solver.run(query, plan=plan, results=results)

    def _run_tool(self, tool_name, args):
        # 支持重试、超时、部分结果容错
        ...
```

## 与Erbing现有系统的整合

```
ReWOO Planner
    ↓ DAG输出
concept_graph.py → 查询相关概念节点
multi_signal_retrieval.py → 多信号检索
correction_capture.py → 记录执行中的错误
    ↓
Worker执行 → 共享记忆层
    ↓
Solver合成 → 返回Erbing的回答
```

## 进阶：ReWOO + LLMCompiler组合

- ReWOO生成DAG
- LLMCompiler并发调度独立步骤（如 t1 和 t2 无依赖则并行执行）
- 进一步加速执行

## 评估指标

| 指标 | ReWOO vs ReAct |
|------|---------------|
| Token消耗 | 线性 vs 二次方 |
| 8步任务Token节省 | ~60-70% |
| 答案质量 | 持平 |
| 计划正确性 | 关键（坏计划代价高）|

## 实施建议

1. 创建 `scripts/rewoo_engine.py`：实现Planner/Worker/Solver三层
2. 改造现有agent loop：当任务步数>3时切换到ReWOO模式
3. 与概念图结合：用concept_graph识别任务类型，决定用ReAct还是ReWOO
4. 添加重试和部分结果容错（critical_path失败才replan）
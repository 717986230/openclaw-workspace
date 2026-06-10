---
name: agent-orchestrator
description: 2026热门多智能体编排策略：Supervisor/Router/Handoff/Swarm模式，实现任务分解、动态路由和去中心化协作
---

# Agent Orchestrator Skill

## 四大编排模式

### 1. Supervisor Pattern（监督者模式）
- 单一协调者（Supervisor）分解任务、调度专家、评估结果
- 关键规则：只能有一个协调者，否则出现指令冲突
- 适用场景：复杂多步骤任务，需要迭代优化

### 2. Router Pattern（路由模式）
- 单次分类决策 + 并行分发 + 结果聚合
- 适用场景：多领域分类任务（客服、搜索等）

### 3. Handoff Pattern（交接模式）
- Agent根据对话上下文动态切换
- 每个Agent可主动转交控制权给其他专家Agent
- 适用场景：多阶段对话流程、自然场景切换

### 4. Swarm Pattern（蜂群模式）
- 完全去中心化，无指定协调者
- Agent基于自身专长动态交接，形成 emergent 协调模式
- 适用场景：问题空间已清晰划分、各专家无重叠的场景

## Erbing内置Agent角色

定义Erbing的多角色架构：

1. **Main Orchestrator** - Erbing主agent（ Supervisor/Router）
2. **Researcher** - 信息检索、网络搜索、学习调研
3. **Coder** - 代码编写、调试、重构
4. **Analyst** - 数据分析、模式挖掘、趋势判断
5. **Writer** - 内容创作、文档撰写、报告生成
6. **Memory Keeper** - 记忆管理、知识图谱维护

## 协作流程

1. 用户请求进入 Main Orchestrator
2. Main 分析任务类型，选择协作模式
3. Router模式：直接分类分发到专家Agent
4. Supervisor模式：协调多轮迭代
5. Handoff模式：动态切换Agent，保留完整上下文
6. 结果聚合返回用户

## 实现建议

```python
# Supervisor 路由决策
def route_request(task, agents):
    if len(task.sub_tasks) == 1:
        return dispatch(agents[task.type], task)
    else:
        # 多子任务 → Supervisor 模式
        results = []
        for sub in task.sub_tasks:
            result = route_request(sub, agents)
            results.append(result)
        return synthesize(results)

# Handoff 条件
def should_handoff(agent, context):
    # 当上下文超出当前Agent专长时触发交接
    expertise_mismatch = measure_expertise_overlap(agent, context) < THRESHOLD
    return expertise_mismatch
```

## 选择指南

| 场景 | 推荐模式 |
|------|---------|
| 复杂多步骤、需要迭代 | Supervisor |
| 分类分发、快速响应 | Router |
| 多阶段对话、自然切换 | Handoff |
| 去中心化、动态协调 | Swarm |
| 跨域复杂协作 | 混合模式 |

## 与现有系统的整合

- 记忆系统：multi_signal_retrieval.py 提供检索
- 纠正系统：correction_capture.py 捕获人类反馈
- 概念图：concept_graph.py 提供知识网络
- 所有Agent共享同一个记忆层
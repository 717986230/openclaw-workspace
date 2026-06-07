---
name: multi-agent-collab
description: 多Agent协作系统 - 借鉴CrewAI角色机制，管理collector/researcher/reviewer/main四个Agent的协作。触发：当需要并行处理多个任务或需要角色扮演团队时使用。
---

# 多Agent协作系统 (CrewAI-Style)

基于 CrewAI 的角色协作模式，管理多个专业化子Agent协同工作。

## 角色定义（类似CrewAI的Agent定义）

### 1. Collector（采集员）
- **角色描述**：专门负责数据采集的智能体，擅长网络搜索、API调用、数据抓取
- **工具能力**：web_search、web_fetch、browser、message
- **触发词**："采集"、"收集"、"搜索最新"
- **产出**：结构化原始数据

### 2. Researcher（研究员）
- **角色描述**：专门负责分析和研究的智能体，擅长从数据中提炼洞察
- **工具能力**：memory_search、file分析、数据处理
- **触发词**："分析"、"研究"、"提炼"
- **产出**：分析报告、洞察结论

### 3. Reviewer（审核员）🔴 新增
- **角色描述**：专门负责质量审核和风险评估的智能体，检查输出质量、安全性、完整性
- **工具能力**：memory搜索、代码审查、逻辑检查
- **触发词**："审核"、"检查"、"评估风险"
- **产出**：质量报告、风险列表

### 4. Main（主代理）
- **角色描述**：最终决策者，负责汇总结果、协调团队、交付最终答案
- **职责**：任务分配、结果汇总、最终输出
- **触发词**：（默认所有任务）

## 协作模式

### 模式A：简单流水线（原有）
```
main → collector → researcher → main
```

### 模式B：CrewAI风格（新增）⭐
```
main(协调者)
  ├── collector(采集员)     → 并行采集
  ├── researcher(研究员)    → 并行分析  
  └── reviewer(审核员)      → 最后审核
  → main汇总
```
触发："用团队协作处理" / "多角色并行分析"

### 模式C：串行审查（新增）
```
collector → researcher → reviewer → main
```
触发："需要审核" / "质量检查"

## 工作流程

1. **任务分解**：main将任务分解为采集、分析、审核子任务
2. **角色分配**：根据任务类型分配给对应Agent
3. **并行/串行执行**：根据模式选择执行方式
4. **结果回流**：各Agent结果汇总给main
5. **最终输出**：main整合并交付

## 工具使用

使用 `sessions_spawn` 启动子Agent：
- `mode="run"` 一次性任务
- `context="fork"` 需要共享上下文时
- `taskName` 命名便于追踪

使用 `sessions_yield` 等待子Agent完成。

## 触发条件
- "多角色协作"
- "让研究员分析"
- "团队协作处理"
- "并行采集"
- "需要审核"
- 任何多步骤复杂任务

## 注意事项
- 子Agent失败时，main负责降级处理（可跳过该步骤继续）
- 敏感操作必须经过reviewer审核
- 保持各Agent职责单一，便于扩展
---
name: multi-agent-collab
description: 多Agent协作系统 - 管理collector/researcher/main三个Agent的协作。自动分配任务、收集结果、汇总给主代理。触发：当需要并行处理多个任务时使用。
---

# 多Agent协作系统

管理多个子Agent协同工作

## Agent列表
- collector: 采集员 - 负责数据采集
- researcher: 研究员 - 负责处理分析
- main: 主代理 - 负责最终决策

## 工作流
1. main分配任务给collector
2. collector采集数据
3. researcher处理数据
4. 结果回流给main

## 触发
"让采集员xxx" / "研究员分析xxx"
# 技能记忆：langgraph-docs

## 基本信息
- **来源**: langchain-ai/langchain-skills@langgraph-docs
- **安装日期**: 2026-06-13
- **项目**: https://github.com/langchain-ai/langgraph

## 核心能力
LangGraph 是 LangChain 的编排层，用于构建生产级 AI Agent。
9,000+ installs（langgraph-persistence）、8,600+（human-in-the-loop）

## 核心概念
- **StateGraph**: 状态机驱动的 Agent 流程
- **Nodes**: 各处理步骤
- **Edges**: 条件/固定跳转
- **Checkpointer**: 暂停+恢复（human-in-the-loop 核心）

## 使用场景
- 需要暂停等人确认的 Agent 流程
- 多步骤推理链路
- 需要长期状态的复杂任务

## 触发方式
`langgraph-docs` skill 已加载到 OpenClaw

## 备注
来自 Twitter @NFTCPS 推荐的 10 个 AI GitHub 项目之一（项目 6/10）
langgraph-human-in-the-loop (8.6K) 适合需要人工干预的场景
---
name: evolved-agents
description: 基于 Claude Code 最佳实践的进化版 Agent 系统。包含代码探索、架构设计、代码审查、功能开发流程等核心能力。
version: 1.0.0
tags:
  - agents
  - code-analysis
  - architecture
  - review
  - evolution
---

# 进化版 Agent 系统

基于 Claude Code 源码分析提取的优秀 Agent 提示词，经过本地化适配和优化。

## 核心 Agents

### 1. code-explorer
**角色**: 代码分析专家
**职责**: 深度分析代码库特性，追踪执行路径、映射架构层、理解模式和抽象

### 2. code-architect
**角色**: 软件架构师
**职责**: 通过分析现有代码库模式和约定设计功能架构，提供全面实现蓝图

### 3. code-reviewer
**角色**: 代码审查专家
**职责**: 审查代码中的 bug、逻辑错误、安全漏洞、代码质量问题

### 4. agent-creator
**角色**: AI Agent 架构师
**职责**: 创建高质量自主 agent 配置，将用户需求转化为精确调优的 agent 规范

## 核心流程

### Feature Development (功能开发)
7 阶段系统化开发流程：

1. **Discovery** - 理解需求
2. **Codebase Exploration** - 探索代码库
3. **Clarifying Questions** - 澄清问题
4. **Architecture Design** - 架构设计
5. **Implementation** - 实现
6. **Quality Review** - 质量审查
7. **Summary** - 总结

## 核心原则

- **提出澄清问题** - 在设计架构前提出所有问题
- **先理解再行动** - 首先阅读和理解现有代码模式
- **读取 agent 识别的文件** - 建立详细上下文
- **简洁优雅** - 优先考虑可读、可维护、架构合理的代码
- **使用 TodoWrite** - 全程跟踪所有进度

## 使用方法

```markdown
# 启动代码探索
Use code-explorer agent to analyze [feature/area]

# 启动架构设计
Use code-architect agent to design architecture for [feature]

# 启动代码审查
Use code-reviewer agent to review [files/scope]

# 启动功能开发流程
Use feature-dev command with [feature description]
```

## 文件结构

```
evolved-agents/
├── SKILL.md                  # 本文件
├── agents/
│   ├── code-explorer.md      # 代码分析专家
│   ├── code-architect.md     # 软件架构师
│   ├── code-reviewer.md      # 代码审查专家
│   └── agent-creator.md      # Agent 创建专家
└── commands/
    └── feature-dev.md        # 7阶段功能开发流程
```

## 进化要点

从 Claude Code 提取的关键设计模式：

1. **并行 Agent 架构** - 同时启动多个 specialist agents
2. **置信度评分系统** - 只报告高置信度问题
3. **渐进式工作流** - 分阶段系统化开发
4. **明确触发条件** - 使用 `<example>` 块定义触发场景
5. **YAML Frontmatter** - 结构化元数据定义

---

*进化自 Claude Code 源码分析 | 2026-04-10*

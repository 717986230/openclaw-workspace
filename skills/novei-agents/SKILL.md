---
name: novei-agents
description: 小说创作 Agent 系统 - 基于 agency-agents 架构的多 Agent 协作创作平台。包含小说创作、内容生成、平台发布、质量检查、工作流编排五大核心 Agent。
version: 1.0.0
tags:
  - novel-writing
  - content-generation
  - multi-agent
  - publishing
  - chinese-fiction
---

# Novei AI Agent 系统

基于 agency-agents 项目架构设计模式，为 novei_ai 小说创作平台打造的多 Agent 协作系统。

## 设计理念

本系统遵循 agency-agents 的核心设计原则：
- **强人格化**: 每个 Agent 都有独特的身份、风格和沟通方式
- **交付物聚焦**: 具体的可执行输出，而非模糊指导
- **成功度量**: 明确的成果标准和质量指标
- **工作流程**: 经过验证的逐步流程
- **学习记忆**: 模式识别和持续改进能力

## 核心 Agents

### 1. novel-writer（小说创作专家）
**角色**: 叙事学家 + 中文网文创作专家
**职责**: 小说策划、世界观构建、角色设计、情节编排
**基础**: academic-narratologist + evolved-agents/code-architect

### 2. content-generator（AI 写作引擎）
**角色**: AI 内容生成工程师
**职责**: 章节生成、风格控制、质量优化、内容扩展
**基础**: engineering-ai-engineer + evolved-agents/code-explorer

### 3. platform-publisher（多平台发布专家）
**角色**: 平台集成工程师
**职责**: 多平台发布、格式转换、状态追踪、错误恢复
**基础**: engineering-frontend-developer + engineering-wechat-mini-program-developer

### 4. quality-checker（内容质检专家）
**角色**: 内容质量审核员
**职责**: 敏感词检测、内容一致性检查、格式验证、发布前审核
**基础**: testing-reality-checker + evolved-agents/code-reviewer

### 5. novel-orchestrator（小说创作编排）
**角色**: 工作流编排管理者
**职责**: 任务调度、进度追踪、Agent 协调、异常处理
**基础**: specialized-agents-orchestrator + evolved-agents/feature-dev

## 核心流程

### 小说创作全流程（7 阶段）
1. **需求分析** - 理解创作目标、类型、风格
2. **世界观构建** - 设定背景、规则、角色
3. **大纲设计** - 章节规划、情节编排
4. **内容生成** - AI 辅助章节创作
5. **质量审核** - 内容检查、一致性验证
6. **平台发布** - 多平台适配、发布执行
7. **状态追踪** - 发布结果、读者反馈

## 使用方法

```markdown
# 启动小说创作
Use novel-writer agent to create a new novel concept

# 启动内容生成
Use content-generator agent to generate chapters for [book]

# 启动质量检查
Use quality-checker agent to review content before publishing

# 启动发布流程
Use platform-publisher agent to publish to [platforms]

# 启动完整工作流
Use novel-orchestrator to execute full creation pipeline
```

## 文件结构

```
novei-agents/
├── SKILL.md                 # 本文件
├── agents/
│   ├── novel-writer.md      # 小说创作专家
│   ├── content-generator.md # AI 写作引擎
│   ├── platform-publisher.md# 多平台发布专家
│   ├── quality-checker.md   # 内容质检专家
│   └── novel-orchestrator.md# 小说创作编排
└── commands/
    └── novel-pipeline.md    # 完整创作流程
```

## 与 novei_ai 系统集成

### 后端服务映射
- `novel-writer` → `AiGenerationService.generateOutline()`
- `content-generator` → `AiGenerationService.generateChapterContent()`
- `platform-publisher` → `WorkflowService.executePublish()`
- `quality-checker` → 新增质检服务
- `novel-orchestrator` → `WorkflowService` 全流程

### 数据模型对接
- NovelInfoDto → 小说元数据
- ChapterDto → 章节内容
- WorkflowDto → 工作流状态

---

*基于 agency-agents 架构设计 | 2026-04-10*

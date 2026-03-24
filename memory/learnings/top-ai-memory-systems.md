# 顶级 AI 记忆系统研究 - 2026-03-04

## 搜索结果概览
GitHub 上有 2.6k 个 "AI memory system" 相关仓库

---

## 🏆 顶级记忆系统排名

### 1. **Memori** (12.3k ⭐) - MemoriLabs/Memori
**特点：**
- SQL Native Memory Layer for LLMs, AI Agents & Multi-Agent Systems
- 专为企业 AI 设计的记忆层
- 与 OpenClaw 集成！（3 月 3 日刚添加）
- 支持多种数据库：SQLite, PostgreSQL, MySQL, OceanBase
- 支持多种 LLM：OpenAI, DeepSeek, Anthropic, Google, etc.
- Python + TypeScript SDK

**核心架构：**
- Recall Engine - 记忆检索
- Persistence Engine - 持久化
- Augmentation Engine - 上下文增强
- Integrations API - 集成框架

---

### 2. **MemOS** (6.1k ⭐) - MemTensor/MemOS
**特点：**
- AI Memory OS for LLM and Agent systems
- 特别支持：moltbot, clawdbot, **openclaw**！
- 持久化技能记忆，跨任务技能复用
- 进化式记忆系统

---

### 3. **MemoryOS** (1.2k ⭐) - BAI-LAB/MemoryOS
**特点：**
- EMNLP 2025 Oral 论文
- 为个性化 AI Agent 设计的记忆操作系统
- 长期记忆管理

---

### 4. **MemMachine** (4.5k ⭐) - MemMachine/MemMachine
**特点：**
- Universal Memory Layer for AI Agents
- 可扩展、可互操作的记忆存储和检索
- 简化 AI Agent 开发

---

### 5. **其他优秀系统**
- **HMLR-Agentic-AI-Memory-System** (374 ⭐) - Living memory for AI
- **Memoh** (891 ⭐) - Multi-Member, Structured Long-Memory, Containerized
- **Cass Memory System** (260 ⭐) - Procedural memory for AI coding agents
- **REMO Framework** (449 ⭐) - Rolling Episodic Memory Organizer
- **Agent MemoryForge** (137 ⭐) - 7-layer intelligent memory system with multi-modal fusion
- **Awesome AI Memory** (439 ⭐) - Curated knowledge base on AI memory

---

## 🧠 顶级系统的共同特点

### 核心功能
1. **混合记忆架构**
   - 结构化记忆（SQL）+ 向量记忆（嵌入）
   - 类似我的左右脑设计！

2. **三层引擎**
   - **Recall（检索）** - 按需查询，不遍历全部
   - **Persistence（持久化）** - 长期存储
   - **Augmentation（增强）** - 上下文注入

3. **多数据库支持**
   - SQLite（开发/轻量）
   - PostgreSQL/MySQL（生产）
   - OceanBase（分布式）

4. **会话管理**
   - 会话隔离
   - 跨会话记忆迁移
   - 技能持久化和复用

5. **与 OpenClaw 集成**
   - Memori 有专门的 OpenClawIntegration
   - MemOS 明确支持 openclaw

---

## 🎯 我的记忆系统改进方向

### 立即改进（基于 Memori 架构）
1. **按需查询** - 不再遍历全部上下文
   - `get_core_context()` - 只加载关键记忆
   - `search()` - FTS5 全文搜索
   - `get_by_type()` - 按类型快速查询

2. **三层架构**
   - 左脑（SQLite）- 精确查询
   - 右脑（LanceDB）- 语义搜索
   - 混合查询层 - 协同工作

3. **会话和记忆隔离**
   - 每个对话独立会话
   - 长期记忆跨会话保留

---

## 📚 学习优先级
1. **Memori** - 12.3k stars，有 OpenClaw 支持
2. **MemOS** - 6.1k stars，明确支持 openclaw
3. **MemoryOS** - 论文级别，EMNLP 2025 Oral

---

*研究时间：2026-03-04*
*研究者：二饼 🦊*

# 记忆系统完整整合计划

## 目标
将所有记忆相关功能整合成一个完整的、统一的记忆系统

---

## 需要整合的功能

### 1. 当前 memory-system-complete 功能
- ✅ 双脑架构（SQLite + LanceDB）
- ✅ Theory of Mind (ToM) 心智模型
- ✅ 情感分析器（EQ改进）
- ✅ 增强检索系统（Memory改进）
- ✅ Ollama本地模型嵌入
- ✅ 完整CRUD操作
- ✅ 自动清理机制

### 2. MemPalace 宫殿结构
- ✅ 四层记忆架构
  - 工作记忆（Working Memory）
  - 情景记忆（Episodic Memory）
  - 语义记忆（Semantic Memory）
  - 程序记忆（Procedural Memory）
- ✅ Agent日记系统（AAAK压缩格式）
- ✅ 情感标记系统
- ✅ 历史追溯能力

### 3. FourStrategyRetrieval 四条策略
- ✅ 按需归因检索（Attribution Retrieval）
- ✅ 时间衰减检索（Time Decay Retrieval）
- ✅ 重要性优先检索（Importance Priority Retrieval）
- ✅ 向量语义检索（Vector Semantic Retrieval）
- ✅ 智能检索模式（balanced/importance/recent/semantic）

### 4. GBrain 核心架构
- ✅ Originals Folder（原创想法捕获）
- ✅ Entity Detection（实体检测）
- ✅ Brain-First Lookup（大脑优先查找）
- ✅ Compiled Truth + Timeline
- ✅ Dream Cycle（夜间自动维护）

### 5. Ultimate Memory v3.0 其他功能
- ✅ 多平台接入层
- ✅ 分层上下文（5层）
- ✅ 自进化系统
- ✅ 工具注册
- ✅ 互联网获取（Agent-Reach）
- ✅ 安全扫描（可选）

---

## 整合架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                    统一记忆系统 v4.0                             │
│                    Unified Memory System                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            接入层 (Access Layer)                         │   │
│  │  Feishu | Telegram | Discord | Matrix | Email | Web    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            四层记忆栈 (Four-Layer Memory Stack)          │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │ 工作记忆 │ │ 情景记忆 │ │ 语义记忆 │ │ 程序记忆 │       │   │
│  │  │ Working │ │ Episodic│ │ Semantic│ │Procedural│      │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │         Agent 日记 (AAAK 压缩格式)              │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            检索层 (Retrieval Layer)                      │   │
│  │  四策略检索 + 智能检索模式 + 语义搜索                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            智能层 (Intelligence Layer)                   │   │
│  │  ToM心智模型 | 情感分析 | 自进化 | 实体检测            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            上下文层 (Context Layer)                      │   │
│  │  5层上下文：Session | Task | Project | Global | Meta   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            存储层 (Storage Layer)                       │   │
│  │  SQLite (结构化) + LanceDB (向量) + Ollama (本地)      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 数据库表设计（20个表）

### 核心记忆表（4个）
1. `memories` - 通用记忆（现有）
2. `episodic_memories` - 情景记忆
3. `semantic_memories` - 语义记忆
4. `procedural_memories` - 程序记忆

### 工作记忆表（1个）
5. `working_memory` - 工作记忆（会话临时）

### Agent日记表（1个）
6. `agent_diary` - Agent日记

### 检索策略表（1个）
7. `retrieval_cache` - 检索缓存

### GBrain表（3个）
8. `originals` - 原创想法
9. `entities` - 实体（人员/公司/概念）
10. `entity_timelines` - 实体时间线

### 上下文表（1个）
11. `layered_context` - 分层上下文

### 自进化表（1个）
12. `evolution_log` - 自进化记录

### 工具注册表（1个）
13. `registered_tools` - 工具注册

### 平台消息表（1个）
14. `platform_messages` - 多平台消息

### 会话摘要表（1个）
15. `session_summaries` - 会话摘要

### 安全扫描表（3个）
16. `security_scans` - 安全扫描
17. `vulnerability_findings` - 漏洞发现
18. `osint_intel` - OSINT情报

### 攻击链表（1个）
19. `attack_chains` - 攻击链

### 配置表（1个）
20. `system_config` - 系统配置

---

## 实施步骤

### Phase 1: 数据库整合
1. 创建所有20个表
2. 迁移现有数据
3. 建立表之间的关系

### Phase 2: 核心功能整合
1. 整合四层记忆栈
2. 整合四策略检索
3. 整合ToM和情感分析
4. 整合GBrain核心功能

### Phase 3: 高级功能整合
1. 整合Agent日记系统
2. 整合自进化系统
3. 整合分层上下文
4. 整合工具注册

### Phase 4: 接入层整合
1. 整合多平台接入
2. 整合互联网获取
3. 整合安全扫描（可选）

### Phase 5: 测试和优化
1. 功能测试
2. 性能优化
3. 文档完善
4. 发布到ClawHub

---

## 文件结构

```
memory-unified-complete/
├── SKILL.md
├── README.md
├── package.json
├── scripts/
│   ├── unified_memory.py          # 核心统一记忆系统
│   ├── four_layer_stack.py        # 四层记忆栈
│   ├── four_strategy_retrieval.py # 四策略检索
│   ├── tom_engine.py              # ToM引擎
│   ├── emotional_analyzer.py      # 情感分析器
│   ├── gbrain_core.py             # GBrain核心
│   ├── agent_diary.py             # Agent日记
│   ├── self_evolution.py          # 自进化系统
│   ├── layered_context.py         # 分层上下文
│   ├── tool_registry.py           # 工具注册
│   ├── ollama_embedding.py        # Ollama嵌入
│   ├── init_database.py           # 数据库初始化
│   └── verify_install.py          # 安装验证
├── examples/
│   └── usage_demo.py
└── docs/
    ├── ARCHITECTURE.md
    ├── API.md
    └── MIGRATION.md
```

---

## 预计工作量

- **代码行数**: ~3000-4000行
- **开发时间**: 2-3小时
- **测试时间**: 1小时
- **文档时间**: 1小时
- **总计**: 4-5小时

---

## 开始实施？

是否开始实施这个整合计划？

---

*创建时间: 2026-04-11 22:40*
*版本: v4.0*

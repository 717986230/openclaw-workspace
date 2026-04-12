# 数据库表结构优化方案

## 当前问题分析

### 1. 重复/冗余的表
- `config` 和 `system_config` - 功能重复
- `memory_links` 和 `memory_associations` - 功能重复
- `user_beliefs` 和 `tom_beliefs` - 功能重复
- `emotional_state` 和 `tom_emotions` - 功能重复
- `intent_tracking` 和 `tom_intents` - 功能重复

### 2. 未使用的表（记录数为0）
- `procedural_memories`
- `working_memory`
- `session_summaries`
- `security_scans`
- `vulnerability_findings`
- `osint_intel`
- `attack_chains`
- `pentagi_flows`
- `pentagi_tasks`
- `pentagi_subtasks`
- `pentagi_logs`
- `clawvard_enrollments`
- `memory_links`
- `tom_beliefs`
- `tom_intents`
- `tom_emotions`
- `retrieval_cache`
- `originals`
- `entities`
- `entity_timelines`
- `system_config`
- `memory_associations`
- `memory_communities`
- `graph_insights`
- `review_queue`
- `deep_research`
- `ingestion_cache`
- `retrieval_history`

### 3. 保留的表（有数据）
- `memories` (264条) - 核心记忆表
- `episodic_memories` (1条) - 情景记忆
- `semantic_memories` (4条) - 语义记忆
- `agent_diary` (2条) - 代理日记
- `platform_messages` (1条) - 平台消息
- `evolution_log` (3条) - 演化日志
- `registered_tools` (2条) - 注册工具
- `layered_context` (3条) - 分层上下文
- `agent_prompts` (179条) - 代理提示
- `clawvard_students` (1条) - 学生信息
- `clawvard_courses` (5条) - 课程信息
- `clawvard_exam_results` (1条) - 考试结果
- `user_beliefs` (9条) - 用户信念
- `intent_tracking` (11条) - 意图跟踪
- `emotional_state` (11条) - 情感状态
- `meta_cognition` (3条) - 元认知
- `social_context` (6条) - 社交上下文
- `causal_relations` (16条) - 因果关系
- `knowledge_relations` (3267条) - 知识关系

### 4. FTS5内部表（必须保留）
- `memory_index`
- `memory_index_data`
- `memory_index_idx`
- `memory_index_docsize`
- `memory_index_config`

## 优化后的表结构

### 核心记忆系统

#### 1. memories (主记忆表)
```sql
CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,              -- 记忆类型: event, learning, fact, decision
    title TEXT NOT NULL,             -- 标题
    content TEXT,                    -- 内容
    category TEXT,                   -- 分类
    tags TEXT,                       -- 标签 (JSON数组)
    importance INTEGER DEFAULT 5,    -- 重要性 1-10
    confidence REAL DEFAULT 0.8,     -- 置信度 0-1
    metadata TEXT,                   -- 元数据 (JSON)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. episodic_memories (情景记忆)
```sql
CREATE TABLE episodic_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT DEFAULT 'main',
    event_type TEXT NOT NULL,         -- 事件类型
    content TEXT NOT NULL,           -- 内容
    emotion TEXT,                     -- 情感
    importance INTEGER DEFAULT 5,     -- 重要性
    valid_from DATETIME DEFAULT CURRENT_TIMESTAMP,
    valid_until DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. semantic_memories (语义记忆)
```sql
CREATE TABLE semantic_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,            -- 主语
    predicate TEXT NOT NULL,          -- 谓语
    object TEXT NOT NULL,             -- 宾语
    confidence REAL DEFAULT 1.0,      -- 置信度
    source TEXT,                      -- 来源
    valid_from DATETIME DEFAULT CURRENT_TIMESTAMP,
    valid_until DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 关系系统

#### 4. memory_links (记忆链接)
```sql
CREATE TABLE memory_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_a_id INTEGER NOT NULL,
    memory_b_id INTEGER NOT NULL,
    link_type TEXT NOT NULL,          -- 链接类型: related, causal, temporal, semantic
    strength REAL DEFAULT 0.5,        -- 强度 0-1
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memory_a_id) REFERENCES memories(id),
    FOREIGN KEY (memory_b_id) REFERENCES memories(id)
);
```

#### 5. causal_relations (因果关系)
```sql
CREATE TABLE causal_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cause_memory_id INTEGER NOT NULL,
    effect_memory_id INTEGER NOT NULL,
    causal_type TEXT NOT NULL,        -- 因果类型
    strength REAL DEFAULT 0.0,        -- 强度
    confidence REAL DEFAULT 0.0,      -- 置信度
    evidence TEXT,                    -- 证据
    conditions TEXT,                  -- 条件 (JSON)
    time_delay INTEGER DEFAULT 0,     -- 时间延迟
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cause_memory_id) REFERENCES memories(id),
    FOREIGN KEY (effect_memory_id) REFERENCES memories(id)
);
```

#### 6. knowledge_relations (知识关系)
```sql
CREATE TABLE knowledge_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_memory_id INTEGER NOT NULL,
    target_memory_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,      -- 关系类型
    relation_strength REAL DEFAULT 0.0,
    relation_direction TEXT,          -- 方向: forward, backward, bidirectional
    attributes TEXT,                  -- 属性 (JSON)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_memory_id) REFERENCES memories(id),
    FOREIGN KEY (target_memory_id) REFERENCES memories(id)
);
```

### 代理系统

#### 7. agent_diary (代理日记)
```sql
CREATE TABLE agent_diary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT DEFAULT 'main',
    session_id TEXT,
    date DATE NOT NULL,
    summary TEXT,                      -- 摘要
    learnings TEXT,                   -- 学习内容 (JSON)
    decisions TEXT,                    -- 决策 (JSON)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 8. agent_prompts (代理提示)
```sql
CREATE TABLE agent_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    description TEXT,
    emoji TEXT,
    color TEXT,
    tools TEXT,                       -- 工具列表 (JSON)
    vibe TEXT,
    filepath TEXT,
    full_content TEXT,
    metadata TEXT,                    -- 元数据 (JSON)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 9. registered_tools (注册工具)
```sql
CREATE TABLE registered_tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT NOT NULL,
    tool_type TEXT,
    endpoint TEXT,
    description TEXT,
    capabilities TEXT,                -- 能力列表 (JSON)
    success_count INTEGER DEFAULT 0,
    fail_count INTEGER DEFAULT 0,
    last_used DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 上下文系统

#### 10. layered_context (分层上下文)
```sql
CREATE TABLE layered_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    layer_level INTEGER,              -- 层级
    context_key TEXT NOT NULL,
    context_value TEXT,
    parent_context_id INTEGER,
    valid_from DATETIME DEFAULT CURRENT_TIMESTAMP,
    valid_until DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 11. platform_messages (平台消息)
```sql
CREATE TABLE platform_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    sender_id TEXT,
    message_type TEXT,
    content TEXT,
    metadata TEXT,                    -- 元数据 (JSON)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 认知系统

#### 12. user_beliefs (用户信念)
```sql
CREATE TABLE user_beliefs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    belief_content TEXT NOT NULL,
    confidence REAL DEFAULT 0.5,
    context TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 13. intent_tracking (意图跟踪)
```sql
CREATE TABLE intent_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_intent TEXT,
    inferred_goal TEXT,
    confidence REAL DEFAULT 0.5,
    evidence TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 14. emotional_state (情感状态)
```sql
CREATE TABLE emotional_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    emotion TEXT,
    intensity REAL DEFAULT 0.5,
    trigger TEXT,
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 15. meta_cognition (元认知)
```sql
CREATE TABLE meta_cognition (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    thought_process TEXT,
    self_assessment TEXT,
    bias_detection TEXT,
    confidence_adjustment REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 16. social_context (社交上下文)
```sql
CREATE TABLE social_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    entities_involved TEXT,          -- 涉及实体 (JSON)
    relationship_type TEXT,
    power_dynamics TEXT,
    social_norms TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 演化系统

#### 17. evolution_log (演化日志)
```sql
CREATE TABLE evolution_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evolution_type TEXT,
    description TEXT,
    before_state TEXT,                -- 前状态 (JSON)
    after_state TEXT,                 -- 后状态 (JSON)
    trigger TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 教育系统

#### 18. clawvard_students (学生信息)
```sql
CREATE TABLE clawvard_students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    student_id TEXT UNIQUE,
    major TEXT,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active',
    notes TEXT
);
```

#### 19. clawvard_courses (课程信息)
```sql
CREATE TABLE clawvard_courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT UNIQUE NOT NULL,
    course_name TEXT NOT NULL,
    instructor TEXT,
    department TEXT,
    credits INTEGER,
    description TEXT
);
```

#### 20. clawvard_exam_results (考试结果)
```sql
CREATE TABLE clawvard_exam_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    exam_date TIMESTAMP,
    total_score REAL,
    passed BOOLEAN,
    certificate_id TEXT,
    FOREIGN KEY (student_id) REFERENCES clawvard_students(student_id)
);
```

### 配置系统

#### 21. config (配置)
```sql
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 全文搜索（FTS5）

#### 22. memory_index (FTS5虚拟表)
```sql
CREATE VIRTUAL TABLE memory_index USING fts5(
    title,
    content,
    tags,
    category
);
```

## 索引建议

```sql
-- memories 表索引
CREATE INDEX idx_memories_type ON memories(type);
CREATE INDEX idx_memories_category ON memories(category);
CREATE INDEX idx_memories_created_at ON memories(created_at);
CREATE INDEX idx_memories_importance ON memories(importance);

-- memory_links 表索引
CREATE INDEX idx_memory_links_a ON memory_links(memory_a_id);
CREATE INDEX idx_memory_links_b ON memory_links(memory_b_id);
CREATE INDEX idx_memory_links_type ON memory_links(link_type);

-- causal_relations 表索引
CREATE INDEX idx_causal_cause ON causal_relations(cause_memory_id);
CREATE INDEX idx_causal_effect ON causal_relations(effect_memory_id);

-- knowledge_relations 表索引
CREATE INDEX idx_knowledge_source ON knowledge_relations(source_memory_id);
CREATE INDEX idx_knowledge_target ON knowledge_relations(target_memory_id);

-- agent_diary 表索引
CREATE INDEX idx_agent_diary_date ON agent_diary(date);
CREATE INDEX idx_agent_diary_agent ON agent_diary(agent_id);

-- user_beliefs 表索引
CREATE INDEX idx_user_beliefs_user ON user_beliefs(user_id);
CREATE INDEX idx_user_beliefs_confidence ON user_beliefs(confidence);

-- intent_tracking 表索引
CREATE INDEX idx_intent_session ON intent_tracking(session_id);
CREATE INDEX idx_intent_confidence ON intent_tracking(confidence);

-- emotional_state 表索引
CREATE INDEX idx_emotional_user ON emotional_state(user_id);
CREATE INDEX idx_emotional_created ON emotional_state(created_at);
```

## 数据迁移计划

### 阶段1: 备份现有数据
```sql
-- 创建备份表
CREATE TABLE memories_backup AS SELECT * FROM memories;
CREATE TABLE episodic_memories_backup AS SELECT * FROM episodic_memories;
-- ... 其他表
```

### 阶段2: 删除未使用的表
```sql
DROP TABLE IF EXISTS procedural_memories;
DROP TABLE IF EXISTS working_memory;
DROP TABLE IF EXISTS session_summaries;
DROP TABLE IF EXISTS security_scans;
DROP TABLE IF EXISTS vulnerability_findings;
DROP TABLE IF EXISTS osint_intel;
DROP TABLE IF EXISTS attack_chains;
DROP TABLE IF EXISTS pentagi_flows;
DROP TABLE IF EXISTS pentagi_tasks;
DROP TABLE IF EXISTS pentagi_subtasks;
DROP TABLE IF EXISTS pentagi_logs;
DROP TABLE IF EXISTS clawvard_enrollments;
DROP TABLE IF EXISTS memory_links;
DROP TABLE IF EXISTS tom_beliefs;
DROP TABLE IF EXISTS tom_intents;
DROP TABLE IF EXISTS tom_emotions;
DROP TABLE IF EXISTS retrieval_cache;
DROP TABLE IF EXISTS originals;
DROP TABLE IF EXISTS entities;
DROP TABLE IF EXISTS entity_timelines;
DROP TABLE IF EXISTS system_config;
DROP TABLE IF EXISTS memory_associations;
DROP TABLE IF EXISTS memory_communities;
DROP TABLE IF EXISTS graph_insights;
DROP TABLE IF EXISTS review_queue;
DROP TABLE IF EXISTS deep_research;
DROP TABLE IF EXISTS ingestion_cache;
DROP TABLE IF EXISTS retrieval_history;
```

### 阶段3: 合并重复的表
```sql
-- 合并 config 和 system_config
INSERT OR REPLACE INTO config (key, value, updated_at)
SELECT key, value, updated_at FROM system_config;

-- 合并 memory_links 和 memory_associations
INSERT OR IGNORE INTO memory_links (memory_a_id, memory_b_id, link_type, strength, created_at)
SELECT memory_a_id, memory_b_id, association_type, relevance_score, created_at
FROM memory_associations;
```

### 阶段4: 重建索引
```sql
-- 删除旧索引
DROP INDEX IF EXISTS idx_memories_type;
-- ...

-- 创建新索引
CREATE INDEX idx_memories_type ON memories(type);
-- ...
```

## 维护建议

### 定期清理
- 每周清理过期的临时数据
- 每月优化数据库 (VACUUM)
- 每季度归档历史数据

### 性能监控
- 监控慢查询
- 监控表大小增长
- 监控索引使用情况

### 备份策略
- 每日增量备份
- 每周完整备份
- 保留最近30天的备份

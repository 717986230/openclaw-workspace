# Hindsight 深度研究与记忆系统设计

## 核心发现：Hindsight 技术架构

### 1. 四大核心概念

```
┌─────────────────────────────────────────────────────────┐
│ Hindsight 记忆架构 │
├─────────────────────────────────────────────────────────┤
│ │
│ ┌─────────────┐ ┌─────────────┐ │
│ │ Retain │ │ Recall │ │
│ │ 存储记忆 │ │ 检索记忆 │ │
│ │ ↓ │ │ ↓ │ │
│ │ • 提取事实 │ │ • 4种并行搜索 │ │
│ │ • 识别实体 │ │ • RRF 融合 │ │
│ │ • 建立连接 │ │ • Cross-Encoder │ │
│ └─────────────┘ └─────────────┘ │
│ │
│ ┌─────────────┐ ┌─────────────┐ │
│ │ Observations│ │ Reflect │ │
│ │ 知识巩固 │ │ Agent推理 │ │
│ │ ↓ │ │ ↓ │ │
│ │ • 模式检测 │ │ • 层级检索 │ │
│ │ • 自动合成 │ │ • Disposition │ │
│ │ • 证据追踪 │ │ • Citations │ │
│ └─────────────┘ └─────────────┘ │
│ │
└─────────────────────────────────────────────────────────┘
```

---

## 核心机制详解

### 一、Retain（存储）

**核心理念**: 不只是存储"说了什么"，而是理解"为什么"、"怎么样"、"意味着什么"

```python
输入: "Alice joined Google last spring and was thrilled about the research opportunities"

提取:
├── 核心事实
│   ├── Alice joined Google
│   └── 时间: last spring
│
├── 情感与意义
│   ├── She was thrilled
│   └── 重要机会
│
└── 推理
    └── 选择了研究机会

实体识别:
├── Alice (Person)
├── Google (Organization)
└── research (Concept)

连接类型:
├── 实体连接 → 同一实体的所有事实
├── 时间连接 → 相近时间的事件
├── 语义连接 → 相似主题
└── 因果连接 → 原因和结果
```

### 二、Recall（检索）- TEMPR 四策略

```
Query: "What did Alice say about Python last spring?"

┌──────────────┐
│ Semantic │ → 理解语义: "Alice's views on programming"
└──────────────┘
┌──────────────┐
│ Keyword │ → 精确匹配: 确保 "Python" 出现
└──────────────┘
┌──────────────┐
│ Graph │ → 关系遍历: Alice → languages → related
└──────────────┘
┌──────────────┐
│ Temporal │ → 时间过滤: last spring
└──────────────┘
      ↓
┌──────────────┐
│ RRF Fusion │ → 融合排序
└──────────────┘
      ↓
┌──────────────┐
│ Cross-Encoder│ → 精细重排
└──────────────┘
```

**关键洞察**:
- 不同查询需要不同策略
- 单一策略无法处理所有场景
- 融合优于单一

### 三、Observations（知识巩固）

**核心价值**: 从碎片到模式，从事实到理解

```
时间线演化:

Day 1: "Redis is open source"
       → Observation: "Redis适合缓存，快速可靠，OSS友好"
       → 证据: 2个事实

Day 2: "Redis has great community"
       → Observation强化
       → 证据: 3个事实

Day 30: "Redis changed license to SSPL"
       → Observation修正: "Redis技术强，但有许可证风险"
       → 矛盾处理

Day 45: "Valkey forked Redis under BSD"
       → 新Observation: "新项目考虑Valkey"
       → 知识进化
```

**矛盾处理**:
```
Week 1: "User loves React"
        → "User prefers React for frontend"

Week 2: "User praises React's component model"
        → "User enthusiastic about React"

Week 3: "User switched to Vue"
        → "User was React enthusiast who switched to Vue"
        → 完整历程，不是简单覆盖
```

### 四、Reflect（Agent推理）

**核心突破**: 一致的推理风格 + 基于证据的回答

```
Agent Loop:
┌────────────────────────────────────┐
│ Query │
└────────────────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ Need more info? │
├────────────────────────────────────┤
│ Tools: │
│ • search_mental_models (最高优先)│
│ • search_observations │
│ • recall │
│ • expand │
└────────────────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ Apply Disposition │
├────────────────────────────────────┤
│ Skepticism: 1-5 │
│ Literalism: 1-5 │
│ Empathy: 1-5 │
└────────────────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ Generate with Citations │
└────────────────────────────────────┘
```

**Disposition 影响推理**:

相同事实，不同Disposition：

| Disposition | 对"远程工作"的回答 |
|-------------|---------------------|
| 低怀疑+高共情 | "远程工作带来灵活性和工作生活平衡..." |
| 高怀疑+低共情 | "远程工作的声明需要验证，实际生产力数据是什么？" |

---

## 关键设计理念

### 1. RAG vs Hindsight

| 维度 | RAG | Hindsight |
|------|-----|-----------|
| 搜索策略 | 仅语义相似 | 4种并行 |
| 多跳推理 | 限于检索块 | 图遍历实体关系 |
| 时间查询 | 关键词匹配 | 日期解析+范围过滤 |
| 实体理解 | 无 | 实体消解+共现追踪 |
| 知识巩固 | 无状态 | Mental Models进化 |
| 性格特质 | 无 | 3维度影响推理 |

### 2. 层级检索策略

```
优先级:
1. Mental Models → 用户预计算的摘要（最高）
2. Observations → 巩固的知识（高）
3. Raw Facts → 原始事实（基准）
```

### 3. 证据追踪

```json
{
  "response": "Based on Alice's ML expertise...",
  "based_on": {
    "memories": [{"id": "mem-123", "text": "..."}],
    "mental_models": [],
    "directives": [{"id": "dir-001", "rules": [...]}]
  },
  "trace": {...}
}
```

---

## 落地到现有记忆系统

### 架构对照

| Hindsight | 我们的系统 | 改进方向 |
|-----------|-----------|----------|
| Retain | SQLite存储 | ✅ 已有，需增强实体识别 |
| Recall | LanceDB检索 | ⚠️ 仅语义，需加3种策略 |
| Observations | 无 | ❌ 需新增 |
| Reflect | 无 | ❌ 需新增 |
| Disposition | 无 | ❌ 需新增 |

### 分阶段实现

#### Phase 1: 增强检索（2周）

```python
class EnhancedRecall:
    """四策略检索"""
    
    def recall(self, query, token_budget=4000):
        # 1. Semantic Search (现有)
        semantic = self.lancedb.search(query)
        
        # 2. Keyword Search (新增)
        keyword = self.keyword_search(query)
        
        # 3. Graph Traversal (新增)
        graph = self.graph_traverse(query)
        
        # 4. Temporal Search (新增)
        temporal = self.temporal_filter(query)
        
        # RRF Fusion
        fused = self.reciprocal_rank_fusion(
            semantic, keyword, graph, temporal
        )
        
        # Cross-Encoder Rerank
        reranked = self.cross_encoder_rerank(query, fused)
        
        # Token Budget
        return self.apply_token_budget(reranked, token_budget)
```

#### Phase 2: 知识巩固（2周）

```python
class ObservationEngine:
    """观察巩固引擎"""
    
    def consolidate(self, new_facts):
        """将新事实整合到观察中"""
        for fact in new_facts:
            # 检查是否与现有观察相关
            related = self.find_related_observations(fact)
            
            if related:
                # 更新现有观察
                self.refine_observation(related, fact)
            else:
                # 创建新观察
                self.create_observation(fact)
        
        # 检测矛盾并处理
        self.detect_and_resolve_contradictions()
```

#### Phase 3: Agent推理（3周）

```python
class ReflectAgent:
    """反思Agent"""
    
    def reflect(self, query, disposition):
        """带Disposition的推理"""
        evidence = []
        
        for _ in range(10):  # 最多10轮
            # 层级检索
            mental = self.search_mental_models(query)
            if mental:
                evidence.extend(mental)
                break
            
            obs = self.search_observations(query)
            if obs:
                evidence.extend(obs)
            
            facts = self.recall(query)
            if facts:
                evidence.extend(facts)
            
            # 检查是否足够
            if self.has_enough_evidence(evidence):
                break
            
            # 扩展查询
            query = self.expand_query(query)
        
        # 应用Disposition
        response = self.generate_with_disposition(
            query, evidence, disposition
        )
        
        # 添加引用
        return self.add_citations(response, evidence)
```

---

## 数据模型设计

### 增强的记忆表

```sql
-- 记忆表（增强）
CREATE TABLE memories (
    id INTEGER PRIMARY KEY,
    type TEXT,           -- world, experience
    title TEXT,
    content TEXT,
    
    -- 新增: 实体
    entities TEXT,       -- JSON: [{"name": "Alice", "type": "person"}]
    
    -- 新增: 时间
    temporal TEXT,       -- JSON: {"start": "2024-03", "end": null}
    
    -- 新增: 情感
    sentiment TEXT,      -- positive, negative, neutral
    
    -- 新增: 因果关系
    causes TEXT,         -- JSON array of memory IDs
    effects TEXT,        -- JSON array of memory IDs
    
    -- 原有
    category TEXT,
    tags TEXT,
    importance INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 观察表（新增）
CREATE TABLE observations (
    id INTEGER PRIMARY KEY,
    content TEXT,        -- 巩固的知识
    supporting_facts TEXT, -- JSON array of memory IDs
    freshness TIMESTAMP, -- 最后更新时间
    stale BOOLEAN,       -- 是否需要验证
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 实体关系图（新增）
CREATE TABLE entity_graph (
    id INTEGER PRIMARY KEY,
    entity1 TEXT,
    relation TEXT,
    entity2 TEXT,
    weight REAL,         -- 连接强度
    source_memory INTEGER,
    created_at TIMESTAMP
);

-- Disposition配置（新增）
CREATE TABLE dispositions (
    id INTEGER PRIMARY KEY,
    name TEXT,
    skepticism INTEGER,   -- 1-5
    literalism INTEGER,   -- 1-5
    empathy INTEGER,      -- 1-5
    mission TEXT,         -- 自然语言使命
    directives TEXT,      -- JSON array of rules
    created_at TIMESTAMP
);
```

---

## 技术实现要点

### 1. 实体识别

```python
import spacy

nlp = spacy.load("en_core_web_trf")

def extract_entities(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append({
            "name": ent.text,
            "type": ent.label_,  # PERSON, ORG, GPE, etc.
            "start": ent.start_char,
            "end": ent.end_char
        })
    return entities
```

### 2. 时间解析

```python
from dateparser import parse

def extract_temporal(text):
    # "last spring" → {"start": "2025-03", "end": "2025-05"}
    # "in 2023" → {"start": "2023-01", "end": "2023-12"}
    
    dates = parse(text, settings={'PREFER_DATES_FROM': 'past'})
    return dates
```

### 3. 关键词搜索

```python
from rank_bm25 import BM25Okapi

def keyword_search(query, documents, top_k=20):
    tokenized = [doc.split() for doc in documents]
    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(query.split())
    return sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)[:top_k]
```

### 4. RRF融合

```python
def reciprocal_rank_fusion(results_list, k=60):
    """
    多策略结果融合
    RRF score = sum(1 / (k + rank_i))
    """
    scores = defaultdict(float)
    
    for results in results_list:
        for rank, doc in enumerate(results, 1):
            scores[doc] += 1 / (k + rank)
    
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

---

## 与现有系统集成

### 改造现有数据库

```python
# 现有: SQLite + LanceDB
# 改造: 增强功能，不破坏现有数据

class EnhancedMemorySystem:
    def __init__(self):
        # 原有
        self.sqlite = sqlite3.connect('xiaozhi_memory.db')
        self.lancedb = lancedb.connect('lancedb')
        
        # 新增
        self.keyword_index = BM25Index()
        self.entity_graph = EntityGraph()
        self.observation_engine = ObservationEngine()
        self.reflect_agent = ReflectAgent()
    
    def retain(self, content):
        """增强的存储"""
        # 1. 原有: 存储到SQLite
        memory_id = self.store_to_sqlite(content)
        
        # 2. 原有: 向量化到LanceDB
        self.store_to_lancedb(content)
        
        # 3. 新增: 提取实体
        entities = self.extract_entities(content)
        self.store_entities(memory_id, entities)
        
        # 4. 新增: 提取时间
        temporal = self.extract_temporal(content)
        self.store_temporal(memory_id, temporal)
        
        # 5. 新增: 触发观察巩固
        self.observation_engine.consolidate([memory_id])
        
        return memory_id
    
    def recall(self, query, strategy="all"):
        """增强的检索"""
        if strategy == "semantic":
            return self.semantic_search(query)
        elif strategy == "keyword":
            return self.keyword_search(query)
        elif strategy == "graph":
            return self.graph_traverse(query)
        elif strategy == "temporal":
            return self.temporal_filter(query)
        else:
            # 四策略融合
            return self.four_strategy_recall(query)
    
    def reflect(self, query, disposition=None):
        """新增: Agent推理"""
        return self.reflect_agent.reflect(query, disposition)
```

---

## 预期效果

| 指标 | 现有系统 | 改进后 |
|------|----------|--------|
| 检索准确率 | 70% | 90%+ |
| 多跳推理 | ❌ | ✅ |
| 时间查询 | ❌ | ✅ |
| 知识进化 | ❌ | ✅ |
| 一致性性格 | ❌ | ✅ |
| 引用追踪 | ❌ | ✅ |

---

*研究时间: 2026-04-10*
*参考: vectorize-io/hindsight (8.7k stars)*

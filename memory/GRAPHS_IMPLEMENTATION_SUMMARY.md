# 因果关系图谱和知识点关系图谱实现总结

## 完成情况

✅ **已完成** - 因果关系图谱和知识点关系图谱已成功实现并测试

## 借鉴项目

### 1. causalgraph (59 stars)
- **GitHub**: https://github.com/causalgraph/causalgraph
- **特点**: 建模、持久化和可视化嵌入知识图谱中的因果图
- **借鉴点**:
  - 使用NetworkX MultiDiGraph作为基础图结构
  - 支持Add, Edit, Remove操作
  - 支持元数据和额外信息链接
  - 提供导出和加载功能

### 2. INDRA (206 stars)
- **GitHub**: https://github.com/gyorilab/indra
- **特点**: 自动化模型组装系统，产生因果图和动态模型
- **借鉴点**:
  - 与NLP系统和数据库接口
  - 自动化知识收集
  - 因果图和动态模型生成

## 实现内容

### 1. 数据库表（2个）

#### causal_relations（因果关系表）
```sql
CREATE TABLE causal_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cause_memory_id INTEGER NOT NULL,
    effect_memory_id INTEGER NOT NULL,
    causal_type TEXT NOT NULL,  -- 'direct', 'indirect', 'conditional', 'probabilistic'
    strength REAL DEFAULT 0.0,  -- 因果强度 0.0-1.0
    confidence REAL DEFAULT 0.0,  -- 置信度 0.0-1.0
    evidence TEXT,  -- 证据来源
    conditions TEXT,  -- 条件（JSON）
    time_delay INTEGER,  -- 时间延迟（秒）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cause_memory_id) REFERENCES memories(id),
    FOREIGN KEY (effect_memory_id) REFERENCES memories(id)
);
```

**因果类型**:
- `direct` - 直接因果
- `indirect` - 间接因果
- `conditional` - 条件因果
- `probabilistic` - 概率因果

#### knowledge_relations（知识点关系表）
```sql
CREATE TABLE knowledge_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_memory_id INTEGER NOT NULL,
    target_memory_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,  -- 关系类型
    relation_strength REAL DEFAULT 0.0,  -- 关系强度 0.0-1.0
    relation_direction TEXT,  -- 'bidirectional', 'unidirectional'
    attributes TEXT,  -- 额外属性（JSON）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_memory_id) REFERENCES memories(id),
    FOREIGN KEY (target_memory_id) REFERENCES memories(id)
);
```

**关系类型**:
- `is_a` - 是一种（继承）
- `part_of` - 是一部分（组成）
- `related_to` - 相关
- `similar_to` - 相似
- `opposite_of` - 相反
- `depends_on` - 依赖
- `precedes` - 先于
- `follows` - 跟随
- `causes` - 导致（因果关系）
- `caused_by` - 由...导致（因果关系）
- `contains` - 包含
- `contained_in` - 包含于
- `exemplifies` - 例证
- `exemplified_by` - 被例证
- `context_for` - 是...的上下文
- `context_of` - ...的上下文

### 2. 核心类（2个）

#### CausalGraph（因果关系图谱）
```python
class CausalGraph:
    def add_causal_relation(self, cause_id, effect_id, causal_type, strength=0.5, confidence=0.5, evidence="", conditions=None, time_delay=0)
    def get_causes(self, effect_id, causal_type=None, min_strength=0.0)
    def get_effects(self, cause_id, causal_type=None, min_strength=0.0)
    def get_causal_chain(self, start_id, max_depth=5)
    def detect_causal_cycles(self)
    def compute_causal_strength(self, cause_id, effect_id)
    def update_causal_strength(self, cause_id, effect_id, new_strength)
    def remove_causal_relation(self, cause_id, effect_id)
```

#### KnowledgeGraph（知识点关系图谱）
```python
class KnowledgeGraph:
    def add_relation(self, source_id, target_id, relation_type, strength=0.5, direction='bidirectional', attributes=None)
    def get_relations(self, memory_id, relation_type=None, min_strength=0.0)
    def get_related_memories(self, memory_id, relation_type, max_depth=2)
    def find_shortest_path(self, source_id, target_id)
    def compute_relation_strength(self, source_id, target_id, relation_type)
    def update_relation_strength(self, source_id, target_id, relation_type, new_strength)
    def remove_relation(self, source_id, target_id, relation_type)
    def get_subgraph(self, center_id, radius=2)
    def detect_communities(self)
```

### 3. 脚本（3个）

#### init_graph_tables.py
- 初始化因果关系表和知识点关系表
- 创建索引
- 验证表创建

#### causal_knowledge_graphs.py
- 实现CausalGraph类
- 实现KnowledgeGraph类
- 提供完整的图谱操作API

#### test_graphs.py
- 测试因果关系图谱功能
- 测试知识点关系图谱功能
- 验证所有功能正常工作

## 测试结果

### CausalGraph测试
✅ 添加因果关系
✅ 获取原因
✅ 获取结果
✅ 获取因果链
✅ 检测因果循环

### KnowledgeGraph测试
✅ 添加关系
✅ 获取关系
✅ 获取相关记忆
✅ 查找最短路径
✅ 检测社区

## 文件清单

1. `memory/GRAPH_DESIGN.md` - 图谱设计文档
2. `scripts/init_graph_tables.py` - 表初始化脚本
3. `scripts/causal_knowledge_graphs.py` - 图谱实现代码
4. `scripts/test_graphs.py` - 测试脚本

## 下一步

1. **自动检测** - 集成LLM自动检测因果关系和知识点关系
2. **可视化** - 添加图谱可视化功能
3. **智能检索** - 基于图谱的智能检索和推荐
4. **增量更新** - 自动更新图谱关系强度
5. **图谱分析** - 添加更多图谱分析功能

## 预期效果

- 因果关系图谱：自动检测和存储记忆之间的因果关系
- 知识点关系图谱：自动检测和存储知识点之间的各种关系
- 图谱可视化：直观展示记忆之间的关系网络
- 智能检索：基于图谱的智能检索和推荐
- 知识发现：自动发现新的知识关联

---

**实现完成！** ✅

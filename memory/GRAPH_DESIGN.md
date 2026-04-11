# 因果关系图谱和知识点关系图谱设计

## 借鉴项目分析

### 1. causalgraph (59 stars)
**核心特点**:
- 使用owlready2存储本体和知识图谱
- 基于NetworkX MultiDiGraph
- 支持因果发现和因果推理
- 支持元数据和额外信息链接
- 提供Add, Edit, Remove操作
- 支持导出和加载

**关键设计**:
```python
class Graph:
    def __init__(self, sql_db_filename=None, external_graph=None):
        self.store = self._init_store_backend_sqldb(sql_db_filename)
        self.add = Add(store=self.store)
        self.edit = Edit(store=self.store)
        self.remove = Remove(store=self.store)
        self.map = Mapping(graph=self)
        self.export = Export(graph=self)
        self.load = Load(graph=self)
        self.draw = Draw(graph=self)
```

### 2. INDRA (206 stars)
**核心特点**:
- 自动化模型组装系统
- 与NLP系统和数据库接口
- 产生因果图和动态模型
- 支持多种数据源

## 记忆系统图谱设计

### 1. 因果关系图谱 (Causal Graph)

**表结构**:
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

CREATE INDEX idx_causal_cause ON causal_relations(cause_memory_id);
CREATE INDEX idx_causal_effect ON causal_relations(effect_memory_id);
CREATE INDEX idx_causal_type ON causal_relations(causal_type);
CREATE INDEX idx_causal_strength ON causal_relations(strength);
```

**因果类型**:
- `direct` - 直接因果
- `indirect` - 间接因果
- `conditional` - 条件因果
- `probabilistic` - 概率因果

**核心功能**:
```python
class CausalGraph:
    def __init__(self, db_path):
        self.db_path = db_path

    def add_causal_relation(self, cause_id, effect_id, causal_type, strength=0.5, confidence=0.5, evidence="", conditions=None, time_delay=0):
        """添加因果关系"""

    def get_causes(self, effect_id, causal_type=None, min_strength=0.0):
        """获取某个记忆的所有原因"""

    def get_effects(self, cause_id, causal_type=None, min_strength=0.0):
        """获取某个记忆的所有结果"""

    def get_causal_chain(self, start_id, max_depth=5):
        """获取因果链"""

    def detect_causal_cycles(self):
        """检测因果循环"""

    def compute_causal_strength(self, cause_id, effect_id):
        """计算因果强度"""

    def update_causal_strength(self, cause_id, effect_id, new_strength):
        """更新因果强度"""

    def remove_causal_relation(self, cause_id, effect_id):
        """删除因果关系"""
```

### 2. 知识点关系图谱 (Knowledge Graph)

**表结构**:
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

CREATE INDEX idx_knowledge_source ON knowledge_relations(source_memory_id);
CREATE INDEX idx_knowledge_target ON knowledge_relations(target_memory_id);
CREATE INDEX idx_knowledge_type ON knowledge_relations(relation_type);
CREATE INDEX idx_knowledge_strength ON knowledge_relations(relation_strength);
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

**核心功能**:
```python
class KnowledgeGraph:
    def __init__(self, db_path):
        self.db_path = db_path

    def add_relation(self, source_id, target_id, relation_type, strength=0.5, direction='bidirectional', attributes=None):
        """添加知识点关系"""

    def get_relations(self, memory_id, relation_type=None, min_strength=0.0):
        """获取某个记忆的所有关系"""

    def get_related_memories(self, memory_id, relation_type, max_depth=2):
        """获取相关记忆（多跳）"""

    def find_shortest_path(self, source_id, target_id):
        """查找最短路径"""

    def compute_relation_strength(self, source_id, target_id, relation_type):
        """计算关系强度"""

    def update_relation_strength(self, source_id, target_id, relation_type, new_strength):
        """更新关系强度"""

    def remove_relation(self, source_id, target_id, relation_type):
        """删除关系"""

    def get_subgraph(self, center_id, radius=2):
        """获取子图"""

    def detect_communities(self):
        """检测社区"""
```

### 3. 图谱可视化

**可视化功能**:
```python
class GraphVisualizer:
    def __init__(self, causal_graph, knowledge_graph):
        self.causal_graph = causal_graph
        self.knowledge_graph = knowledge_graph

    def visualize_causal_graph(self, center_id, radius=2):
        """可视化因果关系图谱"""

    def visualize_knowledge_graph(self, center_id, radius=2):
        """可视化知识点关系图谱"""

    def visualize_combined_graph(self, center_id, radius=2):
        """可视化组合图谱"""

    def export_graph(self, graph_type, format='graphml'):
        """导出图谱"""
```

## 实现步骤

1. 创建数据库表
2. 实现CausalGraph类
3. 实现KnowledgeGraph类
4. 实现GraphVisualizer类
5. 集成到记忆系统
6. 添加自动检测功能
7. 添加可视化功能

## 预期效果

- 因果关系图谱：自动检测和存储记忆之间的因果关系
- 知识点关系图谱：自动检测和存储知识点之间的各种关系
- 图谱可视化：直观展示记忆之间的关系网络
- 智能检索：基于图谱的智能检索和推荐

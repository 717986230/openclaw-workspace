# 记忆系统进化配置 v2.0

## 配置概述

基于从3个项目学到的最佳实践，进化记忆系统：
- LLMs-from-Scratch (8个最佳实践)
- Reasoning-from-Scratch (3个核心技术)
- llm-wiki v0.2.0 (8个核心功能)

## 核心改进

### 1. 两步思维链摄入

```python
class TwoStepMemoryIngestion:
    def __init__(self, memory_system):
        self.memory_system = memory_system

    def add_memory(self, content):
        # 第一步：分析
        analysis = self._analyze_content(content)

        # 第二步：生成记忆
        memory = self._generate_memory(analysis, content)

        # 添加到记忆系统
        return self.memory_system.add_memory(memory)
```

### 2. 四信号关联度模型

```python
class MemoryGraphModel:
    def __init__(self):
        self.weights = {
            "direct_link": 3.0,
            "source_overlap": 4.0,
            "adamic_adar": 1.5,
            "type_affinity": 1.0
        }

    def compute_relevance(self, memory_a, memory_b, graph):
        relevance = 0.0

        # 1. 直接链接
        if self._has_direct_link(memory_a, memory_b):
            relevance += self.weights["direct_link"]

        # 2. 来源重叠
        if self._has_source_overlap(memory_a, memory_b):
            relevance += self.weights["source_overlap"]

        # 3. Adamic-Adar
        relevance += self.weights["adamic_adar"] * self._adamic_adar(memory_a, memory_b, graph)

        # 4. 类型亲和
        if self._has_type_affinity(memory_a, memory_b):
            relevance += self.weights["type_affinity"]

        return relevance
```

### 3. Louvain社区检测

```python
class MemoryCommunityDetection:
    def __init__(self, memory_graph):
        self.memory_graph = memory_graph
        self.communities = {}
        self.cohesion_scores = {}

    def detect_communities(self):
        communities = self._run_louvain(self.memory_graph)

        for community_id, members in communities.items():
            cohesion = self._compute_cohesion(community_id, members)
            self.cohesion_scores[community_id] = cohesion

        return communities

    def get_weak_memory_areas(self, threshold=0.15):
        weak_areas = []
        for community_id, cohesion in self.cohesion_scores.items():
            if cohesion < threshold and len(self.communities[community_id]) >= 3:
                weak_areas.append({
                    "area_id": community_id,
                    "cohesion": cohesion,
                    "memories": self.communities[community_id]
                })
        return weak_areas
```

### 4. 图谱洞察

```python
class MemoryInsights:
    def __init__(self, memory_graph, memory_communities):
        self.memory_graph = memory_graph
        self.memory_communities = memory_communities

    def detect_surprising_connections(self):
        surprising_connections = []

        # 1. 跨社区边
        cross_community_edges = self._find_cross_community_edges()
        for edge in cross_community_edges:
            surprising_connections.append({
                "type": "cross_community",
                "edge": edge,
                "score": self._compute_surprise_score(edge)
            })

        # 2. 跨类型链接
        cross_type_edges = self._find_cross_type_edges()
        for edge in cross_type_edges:
            surprising_connections.append({
                "type": "cross_type",
                "edge": edge,
                "score": self._compute_surprise_score(edge)
            })

        # 3. 边缘↔核心耦合
        periphery_core_edges = self._find_periphery_core_edges()
        for edge in periphery_core_edges:
            surprising_connections.append({
                "type": "periphery_core",
                "edge": edge,
                "score": self._compute_surprise_score(edge)
            })

        return surprising_connections

    def detect_memory_gaps(self):
        memory_gaps = []

        # 1. 孤立记忆（度 ≤ 1）
        isolated_memories = self._find_isolated_memories()
        for memory in isolated_memories:
            memory_gaps.append({
                "type": "isolated",
                "memory": memory,
                "degree": self._get_degree(memory)
            })

        # 2. 稀疏记忆领域（cohesion < 0.15, ≥ 3 个记忆）
        sparse_areas = self._find_sparse_areas(threshold=0.15)
        for area in sparse_areas:
            memory_gaps.append({
                "type": "sparse_area",
                "area": area
            })

        # 3. 桥接记忆（连接 3+ 个集群）
        bridge_memories = self._find_bridge_memories(min_clusters=3)
        for memory in bridge_memories:
            memory_gaps.append({
                "type": "bridge_memory",
                "memory": memory,
                "clusters": self._get_connected_clusters(memory)
            })

        return memory_gaps
```

### 5. 四阶段检索

```python
class FourStageMemoryRetrieval:
    def __init__(self, memory_system, memory_graph, context_window=4000):
        self.memory_system = memory_system
        self.memory_graph = memory_graph
        self.context_window = context_window
        self.budget_allocation = {
            "memories": 0.60,
            "chat_history": 0.20,
            "index": 0.05,
            "system_prompt": 0.15
        }

    def retrieve(self, query, chat_history=[]):
        # 阶段 1：分词搜索
        search_results = self._token_search(query)

        # 阶段 2：图谱扩展
        expanded_results = self._graph_expansion(search_results)

        # 阶段 3：预算控制
        selected_memories = self._budget_control(expanded_results)

        # 阶段 4：上下文组装
        context = self._assemble_context(selected_memories, chat_history)

        return context
```

### 6. 深度研究

```python
class MemoryDeepResearch:
    def __init__(self, memory_system, memory_graph):
        self.memory_system = memory_system
        self.memory_graph = memory_graph

    def research(self, topic, max_results=10):
        # 1. 生成搜索查询
        search_queries = self._generate_search_queries(topic)

        # 2. 网络搜索
        search_results = []
        for query in search_queries:
            results = self._web_search(query, max_results)
            search_results.extend(results)

        # 3. LLM 综合
        synthesis = self._synthesize_results(search_results, topic)

        # 4. 自动摄入
        memory_id = self.memory_system.add_memory({
            "type": "research",
            "title": f"Research: {topic}",
            "content": synthesis,
            "sources": [r["url"] for r in search_results],
            "importance": 8
        })

        return memory_id
```

### 7. 审核系统

```python
class MemoryReviewSystem:
    def __init__(self, memory_system):
        self.memory_system = memory_system
        self.review_queue = []

    def add_review_item(self, item):
        self.review_queue.append({
            "id": len(self.review_queue) + 1,
            "type": item["type"],
            "description": item["description"],
            "search_query": item.get("search_query", ""),
            "status": "pending"
        })

    def process_review_item(self, item_id, action):
        item = self.review_queue[item_id - 1]

        if action == "approve":
            if item["type"] == "create_memory":
                # 创建记忆
                pass
            elif item["type"] == "deep_research":
                # 深度研究
                pass
            item["status"] = "approved"
        elif action == "reject":
            item["status"] = "rejected"
```

### 8. Purpose.md

```python
class MemoryPurpose:
    def __init__(self, purpose_path="memory/purpose.md"):
        self.purpose_path = purpose_path
        self.purpose = self._load_purpose()

    def _load_purpose(self):
        if os.path.exists(self.purpose_path):
            with open(self.purpose_path, 'r', encoding='utf-8') as f:
                return f.read()
        return self._default_purpose()

    def _default_purpose(self):
        return """# Memory System Purpose

## Goals
- 持续学习和进化
- 记录重要决策和经验
- 建立知识网络

## Key Questions
- 如何更好地服务用户？
- 如何提升系统性能？
- 如何发现新的机会？

## Research Scope
- AI 系统优化
- 记忆系统改进
- 多Agent协作

## Evolving Arguments
- 记忆系统应该更智能
- 检索应该更精准
- 进化应该更主动
"""

    def get_context(self):
        return self.purpose

    def suggest_update(self, usage_patterns):
        # 根据使用模式建议更新
        pass
```

## 配置参数

```python
MEMORY_EVOLUTION_CONFIG = {
    # 两步思维链
    "two_step_ingestion": {
        "enabled": True,
        "sha256_cache": True,
        "source_tracing": True,
        "language_aware": True
    },

    # 四信号关联度
    "four_signal_graph": {
        "enabled": True,
        "weights": {
            "direct_link": 3.0,
            "source_overlap": 4.0,
            "adamic_adar": 1.5,
            "type_affinity": 1.0
        }
    },

    # Louvain社区检测
    "louvain_detection": {
        "enabled": True,
        "cohesion_threshold": 0.15,
        "min_community_size": 3
    },

    # 图谱洞察
    "graph_insights": {
        "enabled": True,
        "surprising_connections": True,
        "memory_gaps": True,
        "bridge_nodes": True
    },

    # 四阶段检索
    "four_stage_retrieval": {
        "enabled": True,
        "context_window": 4000,
        "budget_allocation": {
            "memories": 0.60,
            "chat_history": 0.20,
            "index": 0.05,
            "system_prompt": 0.15
        }
    },

    # 深度研究
    "deep_research": {
        "enabled": True,
        "max_results": 10,
        "max_concurrent_tasks": 3
    },

    # 审核系统
    "review_system": {
        "enabled": True,
        "async_processing": True,
        "predefined_actions": True
    },

    # Purpose.md
    "purpose": {
        "enabled": True,
        "path": "memory/purpose.md",
        "auto_update": True
    }
}
```

## 启动步骤

1. 创建Purpose.md
2. 初始化两步思维链摄入
3. 初始化四信号关联度模型
4. 初始化Louvain社区检测
5. 初始化图谱洞察
6. 初始化四阶段检索
7. 初始化深度研究
8. 初始化审核系统
9. 验证所有功能
10. 开始运行

## 预期效果

- 记忆质量提升 50%
- 检索精度提升 40%
- 知识发现能力提升 60%
- 自动化程度提升 70%

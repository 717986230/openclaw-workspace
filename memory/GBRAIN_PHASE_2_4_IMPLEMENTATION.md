# GBrain Phase 2-4 实施计划

**开始时间**: 2026-04-11
**目标**: 完成 GBrain 核心功能的完整实现

---

## Phase 2: 增强功能

### 2.1 Dream Cycle（夜间维护）

**目标**: 实现夜间自动维护任务

**实现步骤**:
1. 创建 `scripts/dream_cycle.py`
2. 实现以下功能：
   - 扫描今天的所有对话
   - 丰富缺失的实体
   - 修复损坏的引用
   - 巩固记忆
   - 生成 DREAMS.md

**代码结构**:
```python
class ErbingDreamCycle:
    """梦境循环 - 夜间自动维护"""

    def run_dream_cycle(self):
        """夜间运行"""
        # 1. 扫描今天的所有对话
        today_conversations = self.get_today_conversations()

        # 2. 丰富缺失的实体
        for conv in today_conversations:
            entities = self.detect_entities(conv)
            for entity in entities:
                if not self.memory.has_rich_page(entity):
                    self.enrich_in_background(entity)

        # 3. 修复损坏的引用
        self.fix_broken_citations()

        # 4. 巩固记忆
        self.consolidate_memories()

        # 5. 生成 DREAMS.md
        self.generate_dream_report()
```

### 2.2 Cross-Reference Back-Links（交叉引用）

**目标**: 实现铁律 - 每个实体页面必须链接到所有引用它的其他页面

**实现步骤**:
1. 创建 `memory/database/cross_reference.py`
2. 实现反向链接功能
3. 在每次更新实体页面时自动添加反向链接

**代码结构**:
```python
def update_entity_page(entity, new_info):
    """更新实体页面"""

    # 更新页面
    page = erbing.get(entity)
    page.timeline.append(new_info)

    # 找到所有提及此实体的其他页面
    mentions = erbing.find_mentions(entity)

    # 添加反向链接
    for mention in mentions:
        mention.add_backlink(
            f"- Referenced in [{mention.title}]({mention.path}) -- {new_info.summary}"
        )
```

### 2.3 Enrichment Tier（丰富化分级）

**目标**: 实现3级丰富化系统

**实现步骤**:
1. 创建 `memory/database/enrichment_tier.py`
2. 实现Tier分级系统：
   - Tier 1: 关键人员和公司（10-15 API调用）
   - Tier 2: 值得注意的人员（3-5 API调用）
   - Tier 3: 次要提及（1-2 API调用）

**代码结构**:
```python
class EnrichmentTier:
    """丰富化分级系统"""

    def classify_tier(self, entity):
        """分类实体层级"""
        # Tier 1: 关键人员和公司
        if entity in self.core_circle:
            return 1
        # Tier 2: 值得注意的人员
        elif entity in self.notable_contacts:
            return 2
        # Tier 3: 次要提及
        else:
            return 3

    def enrich(self, entity, tier):
        """按层级丰富"""
        if tier == 1:
            return self.full_enrichment(entity)
        elif tier == 2:
            return self.standard_enrichment(entity)
        else:
            return self.minimal_enrichment(entity)
```

---

## Phase 3: 查询优化

### 3.1 Brain-First Lookup Protocol（大脑优先查找）

**目标**: 在调用任何外部API之前，先检查大脑

**实现步骤**:
1. 创建 `memory/database/brain_first_lookup.py`
2. 实现大脑优先查找协议

**代码结构**:
```python
def research_entity(name):
    """研究实体 - 大脑优先"""

    # 1. gbrain search（关键词匹配）
    results = erbing.search(name, strategy="keyword")

    # 2. gbrain query（混合搜索）
    results = erbing.search(f"what do we know about {name}", strategy="balanced")

    # 3. gbrain get（直接读取）
    if results:
        page = erbing.get(slug)

    # 4. 外部API仅作为后备
    if not results or page.is_thin():
        results = external_api_search(name)

    return results
```

### 3.2 混合搜索优化

**目标**: 优化四策略检索系统

**实现步骤**:
1. 优化 `memory/database/retrieval_strategies.py`
2. 实现RRF融合
3. 实现Cross-Encoder重排序

### 3.3 性能优化

**目标**: 优化查询性能

**实现步骤**:
1. 添加缓存层
2. 优化数据库查询
3. 实现批量操作

---

## Phase 4: 高级功能

### 4.1 完整的Enrichment Pipeline（7步协议）

**目标**: 实现完整的7步丰富化流程

**实现步骤**:
1. 创建 `memory/database/enrichment_pipeline.py`
2. 实现以下步骤：
   - Step 1: 识别实体
   - Step 2: 检查大脑状态
   - Step 3: 从来源提取信号
   - Step 4: 数据源查询
   - Step 5: 保存原始数据
   - Step 6: 写入大脑
   - Step 7: 交叉引用

**代码结构**:
```python
class EnrichmentPipeline:
    """7步丰富化流程"""

    def run(self, entity):
        """运行完整流程"""

        # Step 1: 识别实体
        entity_info = self.identify_entity(entity)

        # Step 2: 检查大脑状态
        page = self.check_brain_state(entity)

        # Step 3: 从来源提取信号
        signals = self.extract_signals(entity_info)

        # Step 4: 数据源查询
        data = self.query_data_sources(entity, signals)

        # Step 5: 保存原始数据
        self.save_raw_data(entity, data)

        # Step 6: 写入大脑
        self.write_to_brain(entity, data, page)

        # Step 7: 交叉引用
        self.cross_reference(entity, data)
```

### 4.2 高级功能

**目标**: 实现高级功能

**实现步骤**:
1. 实体关系图
2. 概念聚类
3. 原创想法索引

### 4.3 生产部署

**目标**: 生产环境部署

**实现步骤**:
1. 配置管理
2. 监控和日志
3. 错误处理
4. 性能监控

---

## 实施时间表

| Phase | 任务 | 预计时间 | 状态 |
|-------|------|---------|------|
| Phase 1 | 核心模式 | 已完成 | ✅ |
| Phase 2 | 增强功能 | 2-3天 | 🚧 |
| Phase 3 | 查询优化 | 2-3天 | 📋 |
| Phase 4 | 高级功能 | 3-5天 | 📋 |

---

## 下一步行动

1. ✅ 创建 Phase 2-4 实施计划文档
2. 🚧 开始实施 Phase 2.1 Dream Cycle
3. 📋 实施 Phase 2.2 Cross-Reference
4. 📋 实施 Phase 2.3 Enrichment Tier

---

*创建时间: 2026-04-11*
*版本: v1.0*

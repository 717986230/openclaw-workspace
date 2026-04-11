# GBrain 深度分析与进化提炼

**项目**: garrytan/gbrain ⭐ 2,464
**核心价值**: Memex 理念的现代实现，让知识自动复合增长

---

## 🎯 核心理念

### Memex 愿景（1945）→ GBrain 实现（2026）

Vannevar Bush 在 "As We May Think" 中描述的 Memex：
- 存储所有书籍、记录、通信
- 机械化的快速检索
- 关联线索链接知识

**GBrain 的突破**：Memex 是被动的（你需要构建线索），GBrain 是主动的（Agent 自动维护）。

> **关键洞察**："You don't build the memex. The memex builds itself."

---

## 🏗️ 架构设计

### 三层架构

```
┌─────────────────┐
│  AI Agent       │ ← Skills 定义如何使用
│  (read/write)   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  GBrain         │ ← 检索层（混合搜索）
│  (retrieval)    │   - Postgres + pgvector
└────────┬────────┘   - 关键词 + 向量 + RRF融合
         │
         ↓
┌─────────────────┐
│  Brain Repo     │ ← 真理之源（Git版本控制）
│  (markdown)     │   - 每页一人/公司/概念
└─────────────────┘   - Compiled Truth + Timeline
```

### 关键原则

**Repo 是真理之源**：
- Markdown 文件是 system of record
- Human always wins - 可以直接编辑
- Git 版本控制 - 完整的历史追踪

---

## 📊 实际数据规模

Garry Tan 的生产环境（真实数据）：

| 类型 | 数量 | 时间跨度 |
|------|------|---------|
| **Markdown 文件** | 10,000+ | - |
| **人员档案** | 3,000+ | 关系历史 |
| **日历事件** | 21,000+ | 13年 |
| **Apple Notes** | 5,800+ | 2009至今 |
| **会议转录** | 280+ | AI分析 |
| **原创想法** | 300+ | 按论题组织 |
| **媒体页面** | 500+ | 视频/书籍/文章 |

**关键洞察**：当文件超过 1,000 时，`grep` 失效，需要真正的检索系统。

---

## 🔄 Brain-Agent Loop（核心循环）

这是让知识复合增长的秘诀：

```
信号到达（会议/邮件/推文/链接）
    ↓
实体检测（人员/公司/原创想法）
    ↓
READ: 先检查大脑（gbrain search/get）
    ↓
携带完整上下文响应
    ↓
WRITE: 更新大脑页面（新信息编译到现有页面）
    ↓
Sync: gbrain 索引变更（下次查询可用）
    ↓
（下一个信号到达时 - Agent 已经更聪明了）
```

### 两个不变量

1. **每次 READ 改进响应** - 如果不检查大脑就回答关于某人的问题，你就给出了比可能的更差的答案。

2. **每次 WRITE 改进未来的 READ** - 如果会议转录提到公司的新信息而你没有更新公司页面，你就创造了一个以后会咬你的缺口。

---

## 🧠 Compiled Truth + Timeline 模式

这是最重要的设计模式！

### 页面结构

```markdown
## Executive Summary
一段话。你怎么认识他们的，为什么重要。

## State
角色、公司、关键数字、关系状态。

## What They Believe
世界观、第一性原理、立场。

## What They're Building
当前项目、最近发布、下一步。

## Assessment
优势、劣势、对这个人的总体判断。

## Trajectory
走向何方。上升、平台期、转型？

## Relationship
与你的历史。最后互动。开放线索。

## Contact
邮箱、电话、X handle、LinkedIn。

---

## Timeline
- **2026-04-07** | 在团队同步会议见面。讨论了新产品发布。看起来对转型很兴奋。[来源：会议笔记 "Team Sync" #12345]
- **2026-03-15** | 邮件讨论投资条款。对估值条款有顾虑。[来源：邮件线程]
- **2025-12-01** | 在 Demo Day 初次见面。介绍了他们的创业公司。[来源：活动笔记]
```

### 设计哲学

**水平线上：Compiled Truth**
- 当前状态的综合
- 新证据到达时重写
- 30秒内了解关键信息

**水平线下：Timeline**
- 每个信号的追加式日志
- 永不重写，永不删除
- 可追溯到来源的证据库

**关键原则**：每个 Compiled Truth 的声明应该可追溯到一个或多个 Timeline 条目。

---

## 🎯 Entity Detection - 每条消息都运行

### 实体检测优先级

#### PRIMARY: Original Thinking（原创想法）

**最高价值信号！**

用户的想法、观察、论题、框架、哲学性思考。

**捕获原则**：
- **保留用户的原始措辞** - 语言本身就是洞察
- "ambition-to-lifespan ratio has never been more broken" 比 "tension between ambition and mortality" 捕获了更多
- 不要清理，不要改写

**路由规则**：

| 信号类型 | 目的地 |
|---------|--------|
| 用户生成的想法 | `brain/originals/{slug}.md` |
| 引用的世界概念 | `brain/concepts/{slug}.md` |
| 产品或商业想法 | `brain/ideas/{slug}.md` |
| 个人反思或模式 | `brain/personal/reflections/` |

**什么算原创想法**：
- 关于世界如何运作的原创观察
- 不同事物之间的新颖联系
- 框架和心智模型
- 模式识别时刻
- 带推理的热门观点
- 揭示新角度的隐喻

#### SECONDARY: Entity Mentions（实体提及）

人员、公司、媒体引用。

**处理流程**：
1. 检查大脑页面是否存在
2. 如果不存在且实体值得注意：创建、丰富
3. 如果页面薄弱：生成后台丰富任务
4. 如果页面丰富：静默加载上下文
5. 对于现有实体的新事实：追加到 Timeline

**铁律**：从实体页面反向链接到提及它们的来源。未链接的提及是损坏的大脑。

---

## 🚀 Enrichment Pipeline（7步协议）

### Tier 分级系统

| 层级 | 对象 | 投入 | API调用数 |
|------|------|------|----------|
| **Tier 1** | 关键人员和公司：核心圈子、商业伙伴、投资组合公司 | 完整流程，所有数据源 | 10-15 |
| **Tier 2** | 值得注意：偶尔互动的人 | 网页搜索 + 社交 + 大脑交叉引用 | 3-5 |
| **Tier 3** | 次要提及：其他值得追踪的人 | 大脑交叉引用 + 已知 handle 的社交查询 | 1-2 |

### 7步流程

**Step 1: 识别实体**
从输入信号中提取人员名称、公司名称、它们的关联信息。

**Step 2: 检查大脑状态**
页面存在吗？如果存在，读取它 → UPDATE 路径。如果不存在 → CREATE 路径。

**Step 3: 从来源提取信号**
不仅提取事实 - 提取质感：
- 他们表达了什么观点？→ What They Believe
- 他们在构建或发布什么？→ What They're Building
- 他们表达了情感吗？→ What Makes Them Tick
- 他们与谁互动？→ Network / Relationship
- 这是反复出现的话题吗？→ Hobby Horses
- 他们承诺了什么？→ Open Threads
- 他们的能量如何？→ Trajectory

**Step 4: 数据源查询**
按优先顺序：

1. **Brain cross-reference**（免费，最高价值 - 总是第一）
2. **Web search**（Brave/Exa）：背景、新闻、演讲、融资
3. **X/Twitter 深度查询**：观点、构建、hobby horses、网络、轨迹
4. **People enrichment**（Crustdata/Happenstance）：LinkedIn数据、职业轨迹
5. **Company/funding data**（Captain API）：Pitchbook级别的数据
6. **Meeting history**（Circleback）：转录搜索、参会者查询
7. **Contact data**（Google Contacts, CRM sync）

**关键洞察**：X/Twitter 是被低估的来源。当你有某人的 handle 时，他们的推文是最好的来源：
- 他们相信什么（未提示表达的观点）
- 他们在构建什么（发布公告）
- Hobby horses（反复出现的话题）
- 他们与谁互动（回复模式、放大）
- 轨迹（发布频率、语气变化）

**Step 5: 保存原始数据**
每个 API 响应保存到 `.raw/` sidecar。JSON 格式，包含 `sources.{provider}.fetched_at` 和 `.data`。

**Step 6: 写入大脑**
- CREATE 路径：使用页面模板，填充编译的真相，添加第一个 Timeline 条目
- UPDATE 路径：追加 Timeline，如果新信号显著改变图景则更新编译的真相。标记矛盾 - 不要静默解决。

**Step 7: 交叉引用**
更新人员页面后：
- 更新他们的公司页面
- 更新交易页面
- 添加反向链接

**关键原则**：每个实体页面应该链接到所有引用它的其他实体页面。

---

## 💡 The Compounding Thesis（复合论题）

> "Most tools help you find things. GBrain makes you smarter over time."

### 核心循环

```
信号到达（会议、邮件、推文、链接）
    ↓
Agent 检测实体（人员、公司、想法）
    ↓
READ: 先检查大脑（gbrain search, gbrain get）
    ↓
携带完整上下文响应
    ↓
WRITE: 用新信息更新大脑页面
    ↓
Sync: gbrain 索引变更供下次查询
```

### 复合效应

每次通过这个循环都增加知识。

- Agent 在会议后丰富人员页面
- 下次这个人出现时，Agent 已经有上下文 - 他们的角色、你们的历史、他们在意什么、上次讨论的内容
- 你永远不会从零开始

**时间维度**：
- 每天复合
- 6个月后，Agent 对你的世界的了解比你工作记忆能容纳的更多
- 因为它永远不会忘记，永远不会停止索引

---

## 🌙 The Dream Cycle（梦境循环）

这是最强大的概念！

### 夜间自动维护

```
你睡觉时...
    ↓
Agent 扫描白天的所有对话
    ↓
丰富缺失的实体
    ↓
修复损坏的引用
    ↓
巩固记忆
    ↓
你醒来时，大脑比睡觉时更聪明
```

**OpenClaw 实现**：通过 `DREAMS.md`
**Hermes Agent 实现**：通过 nightly cron job

### 20+ 重复任务

让大脑保持活力的后台任务：
- 实体丰富队列
- 引用修复扫描
- 关系网络更新
- Timeline 压缩
- 交叉引用生成
- 概念聚类
- 原创想法索引
- ...

---

## 🎯 与 Erbing 的关系

### 三层记忆对比

| 层级 | GBrain | Erbing | 存储内容 |
|------|--------|--------|---------|
| **世界知识** | gbrain | 左脑（SQLite）| 人员、公司、概念、原创想法 |
| **Agent记忆** | Agent memory | 左脑（SQLite）| 偏好、决策、会话上下文、配置 |
| **会话上下文** | Session | 右脑（LanceDB）| 当前对话 |

**关键洞察**：三层都应该被检查！

- GBrain/左脑：关于世界的事实
- Agent Memory：Agent 配置
- Session：即时上下文

---

## 🚀 Erbing 可以学习的关键进化

### 1. **Originals Folder（原创文件夹）**

**这是最高价值的概念！**

```python
# Erbing 应该添加
class OriginalsCapture:
    """捕获用户的原创想法"""

    def capture_original_thinking(self, user_message):
        # 识别原创想法
        if self.is_original_idea(user_message):
            # 保留原始措辞！
            original = self.extract_original(user_message)

            # 保存到 originals/
            self.save_to(f"originals/{self.slug(original)}.md", {
                "content": original,  # 原始措辞
                "timestamp": datetime.now(),
                "context": self.get_context(),
                "cross_links": self.find_related_originals(original)
            })
```

**路由规则**：
- 用户生成的想法 → `originals/{slug}.md`
- 引用的世界概念 → `concepts/{slug}.md`
- 产品想法 → `ideas/{slug}.md`

---

### 2. **Compiled Truth + Timeline 模式**

Erbing 的每条记忆应该采用这种结构：

```python
# 当前 Erbing 记忆结构
{
    "type": "learning",
    "title": "...",
    "content": "...",
    "importance": 8,
    "created_at": "..."
}

# 应该进化为
{
    "type": "person",  # 或 company, concept
    "title": "某人",
    "compiled_truth": {
        "executive_summary": "...",
        "state": "...",
        "what_they_believe": "...",
        "what_they_building": "...",
        "assessment": "...",
        "trajectory": "...",
        "relationship": "...",
        "contact": "..."
    },
    "timeline": [
        {
            "date": "2026-04-11",
            "event": "...",
            "source": "...",
            "links": ["..."]
        }
    ],
    "importance": 8,
    "updated_at": "...",
    "created_at": "..."
}
```

---

### 3. **Entity Detection on Every Message**

每条消息都运行实体检测：

```python
class ErbingEntityDetector:
    """每条消息运行"""

    def process_message(self, message):
        # 生成轻量级子Agent
        entities = self.detect_entities(message)

        for entity in entities:
            # 检查是否存在
            if not self.memory.exists(entity):
                # Tier 1/2/3 分级
                tier = self.classify_tier(entity)

                # 按Tier处理
                if tier == 1:
                    self.full_enrichment(entity)
                elif tier == 2:
                    self.standard_enrichment(entity)
                else:
                    self.minimal_enrichment(entity)
```

---

### 4. **Dream Cycle**

夜间自动维护：

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

---

### 5. **Brain-First Lookup Protocol**

在调用任何外部API之前：

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

---

### 6. **Cross-Reference Back-Links**

**铁律**：每个实体页面必须链接到所有引用它的其他页面。

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

---

## 📊 对比总结

| 特性 | GBrain | Erbing 当前 | Erbing 进化 |
|------|--------|------------|------------|
| **存储结构** | Markdown + Git | SQLite + LanceDB | ✅ 保持（更好） |
| **混合搜索** | Postgres + pgvector | 四策略检索 | ✅ 更先进 |
| **Compiled Truth** | ✅ | ❌ | 📋 需添加 |
| **Timeline** | ✅ | 部分（created_at） | 📋 需增强 |
| **Originals Folder** | ✅ | ❌ | 📋 需添加 |
| **Entity Detection** | ✅ 每条消息 | ❌ | 📋 需添加 |
| **Dream Cycle** | ✅ 夜间维护 | ❌ | 📋 需添加 |
| **Cross-Reference** | ✅ 铁律 | 部分 | 📋 需加强 |
| **Enrichment Tier** | ✅ 3级 | ❌ | 📋 需添加 |

---

## 🎯 实施优先级

### Phase 1: 核心模式（本周）
1. ✅ **Compiled Truth + Timeline** 结构
2. ✅ **Originals Folder** 捕获原创想法
3. ✅ **Entity Detection** 每条消息运行

### Phase 2:
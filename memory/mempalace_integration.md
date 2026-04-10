# MemPalace 整合设计

## 核心概念学习

MemPalace 是一个优秀的AI记忆系统，有以下值得借鉴的设计：

### 1. 四层记忆架构
- **工作记忆 (Working Memory)** - 当前会话的短期记忆
- **情景记忆 (Episodic Memory)** - 事件和经历
- **语义记忆 (Semantic Memory)** - 知识和概念
- **程序记忆 (Procedural Memory)** - 技能和流程

### 2. AAAK 压缩方言
- 实体编码：ALC=Alice, JOR=Jordan
- 情感标记：*warm*=喜悦, *fierce*=坚定, *raw*=脆弱
- 高效存储，人类和LLM都可读

### 3. 知识图谱
- 实体关系三元组：subject → predicate → object
- 时间有效性：valid_from, ended_at
- 自动失效机制

### 4. Agent日记系统
- 每个Agent独立的日记
- 记录会话摘要、学习内容、重要决策
- AAAK格式压缩

### 5. 记忆协议 (PALACE_PROTOCOL)
```
1. ON WAKE-UP: 加载宫殿概览 + AAAK规范
2. BEFORE RESPONDING: 先查询知识图谱或搜索记忆
3. IF UNSURE: 说"让我查一下"然后查询，不要猜测
4. AFTER EACH SESSION: 写日记记录发生的事
5. WHEN FACTS CHANGE: 失效旧事实，添加新事实
```

## 与现有系统集成

### 已有的记忆系统
- SQLite (左脑) - 结构化记忆
- LanceDB (右脑) - 向量记忆

### 建议整合
1. 借鉴四层架构设计
2. 引入AAAK压缩方言用于日记
3. 增强知识图谱功能
4. 实现Agent日记系统

## 下一步
- 评估是否需要安装MemPalace作为MCP服务
- 或者将其设计理念融入现有系统

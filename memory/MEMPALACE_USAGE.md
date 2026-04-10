# MemPalace 混合记忆系统

整合了 MemPalace 的四层架构设计，保留原有的 SQLite+LanceDB 基础。

## 架构

```
┌─────────────────────────────────────────────────────┐
│              MemPalace 混合记忆系统                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐  ┌─────────────┐                  │
│  │ 工作记忆    │  │ 情景记忆    │                  │
│  │ Working     │  │ Episodic    │                  │
│  │ 会话临时    │  │ 事件经历    │                  │
│  └─────────────┘  └─────────────┘                  │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐                  │
│  │ 语义记忆    │  │ 程序记忆    │                  │
│  │ Semantic    │  │ Procedural  │                  │
│  │ 知识图谱    │  │ 技能流程    │                  │
│  └─────────────┘  └─────────────┘                  │
│                                                     │
│  ┌─────────────────────────────────────┐           │
│  │         Agent 日记系统              │           │
│  │    AAAK 压缩格式 · 历史追溯         │           │
│  └─────────────────────────────────────┘           │
│                                                     │
├─────────────────────────────────────────────────────┤
│  底层：SQLite (左脑) + LanceDB (右脑)               │
└─────────────────────────────────────────────────────┘
```

## 使用方法

```python
from memory_palace import get_palace

palace = get_palace()

# 1. 情景记忆 - 记录事件
palace.add_episodic(
    event_type='learning',
    content='学习了新技能',
    emotion='curiosity',  # joy, determination, vulnerability, curiosity, concern
    importance=7
)

# 2. 语义记忆 - 知识图谱
palace.add_knowledge('用户', '偏好', '简洁回复')
palace.add_knowledge('项目', '位于', 'D:\\CODE')

# 查询知识
facts = palace.query_knowledge(subject='用户')

# 3. 程序记忆 - 技能流程
palace.add_skill(
    skill_name='daily_report',
    skill_type='automation',
    description='每日报告生成',
    steps=['收集数据', '分析汇总', '生成报告']
)

# 记录技能使用
palace.record_skill_usage('daily_report', success=True)

# 4. Agent 日记
palace.write_diary(
    summary='完成系统整合',
    learnings=['四层架构', 'AAAK压缩'],
    decisions=['保留SQLite', '引入新表']
)

# 5. 工作记忆 - 会话临时存储
palace.set_working('session-123', 'current_task', '配置系统', ttl_seconds=3600)
task = palace.get_working('session-123', 'current_task')
```

## AAAK 压缩方言

Agent 日记使用 AAAK 格式压缩：

```
[12:17] 完成系统整合
 > 四层架构 | AAAK压缩
 ! 保留SQLite | 引入新表
```

- `[时间]` - 时间戳
- `>` - 学习内容
- `!` - 决策记录

## 情感标记

```python
EMOTION_MARKERS = {
    'joy': '*warm*',        # 喜悦
    'determination': '*fierce*',  # 坚定
    'vulnerability': '*raw*',     # 脆弱
    'curiosity': '*spark*',       # 好奇
    'concern': '*dim*',          # 担忧
    'satisfaction': '*bright*',   # 满足
}
```

## 与 Agent-Reach 联动

Agent-Reach 可以获取互联网数据，存入 MemPalace：

```python
# 使用 Agent-Reach 获取网页
# agent-reach read https://example.com

# 将学习结果存入情景记忆
palace.add_episodic(
    event_type='web_learning',
    content='从网页学习了新知识',
    source='https://example.com'
)

# 将知识点存入语义记忆
palace.add_knowledge('主题', '来源', '网页URL', source='agent-reach')
```

## 数据库表

- `episodic_memories` - 情景记忆（事件经历）
- `semantic_memories` - 语义记忆（知识图谱）
- `procedural_memories` - 程序记忆（技能流程）
- `working_memory` - 工作记忆（会话临时）
- `agent_diary` - Agent 日记

---

整合时间：2026-04-08

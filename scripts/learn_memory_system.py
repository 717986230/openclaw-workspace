import sys
import os
import sqlite3
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.getcwd(), 'skills/memory-complete/scripts'))
from memory_palace import MemPalace

db_path = "memory/database/xiaozhi_memory.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("Complete Memory System v4.0 - 学习记录")
print("=" * 60)

# 1. 添加情景记忆
palace = MemPalace(db_path)
palace.connect()

# 学习记忆系统架构
palace.add_episodic(
    event_type="learning",
    content="学习了 Complete Memory System v4.0 完整架构",
    emotion="curiosity",
    importance=9,
    aaak_content="[20:30] 深入学习记忆系统完整版 | 四层架构 | 双脑机制"
)

# 学习到的核心知识
knowledge_items = [
    ("记忆系统", "has_component", "四层记忆栈"),
    ("记忆系统", "has_component", "四策略检索"),
    ("记忆系统", "has_component", "Theory of Mind"),
    ("记忆系统", "has_component", "情感分析"),
    ("记忆系统", "has_component", "Ollama嵌入"),
    ("四层记忆栈", "includes", "工作记忆"),
    ("四层记忆栈", "includes", "情景记忆"),
    ("四层记忆栈", "includes", "语义记忆"),
    ("四层记忆栈", "includes", "程序记忆"),
    ("工作记忆", "feature", "TTL过期机制"),
    ("工作记忆", "storage", "会话临时存储"),
    ("情景记忆", "format", "AAAK压缩格式"),
    ("情景记忆", "feature", "情感标记"),
    ("语义记忆", "format", "三元组subject-predicate-object"),
    ("程序记忆", "content", "技能和执行步骤"),
    ("四策略检索", "strategy_1", "按需归因检索"),
    ("四策略检索", "strategy_2", "时间衰减检索"),
    ("四策略检索", "strategy_3", "重要性优先检索"),
    ("四策略检索", "strategy_4", "向量语义检索"),
    ("按需归因检索", "based_on", "Entity-Process-Session三层归因"),
    ("时间衰减检索", "formula", "exp(-0.693 * days / half_life)"),
    ("时间衰减检索", "default_half_life", "30天"),
    ("重要性优先检索", "range", "1-10重要性分数"),
    ("Theory of Mind", "has", "信念更新"),
    ("Theory of Mind", "has", "意图推断"),
    ("Theory of Mind", "has", "情绪检测"),
    ("信念更新", "formula", "贝叶斯融合 旧*0.7 + 新*0.3"),
    ("情感分析", "emotions", "7种情绪类型"),
    ("情感分析", "intensity_modifiers", "very/extremely/really/quite/somewhat"),
    ("Ollama", "models", "nomic-embed-text(768维)"),
    ("Ollama", "models", "mxbai-embed-large(1024维)"),
    ("Ollama", "models", "all-minilm(384维)"),
    ("数据库", "count", "71个表"),
    ("memories表", "records", "288条记忆"),
    ("语义记忆", "records", "3267条知识关系"),
    ("记忆关联", "records", "8227条关联"),
]

for subject, predicate, obj in knowledge_items:
    palace.add_knowledge(subject, predicate, obj, source="memory-complete-SKILL.md")

# 写日记
learnings = [
    "四层记忆栈架构: 工作/情景/语义/程序",
    "四策略检索: 归因/时间衰减/重要性/向量语义",
    "ToM贝叶斯信念融合公式",
    "AAAK压缩格式用于Agent日记",
    "Ollama本地嵌入可选集成",
    "数据库包含71个表，288条记忆记录"
]

decisions = [
    "使用CompleteMemorySystem作为主记忆入口",
    "四策略检索作为主要查询方式",
    "继续集成Ollama以提升语义搜索能力"
]

palace.write_diary(
    summary="完成 Complete Memory System v4.0 完整学习",
    learnings=learnings,
    decisions=decisions,
    session_id="memory-learning-2026-04-21"
)

# 2. 技能记忆 - 记忆系统操作
cursor.execute('''
INSERT INTO procedural_memories (skill_name, skill_type, description, steps)
VALUES (?, ?, ?, ?)
ON CONFLICT DO UPDATE SET
    description = excluded.description,
    steps = excluded.steps,
    success_count = success_count + 1,
    last_used = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
''', (
    "CompleteMemorySystem操作",
    "memory",
    "完整记忆系统 v4.0 的使用方法和API",
    json.dumps([
        "from complete_memory_system import CompleteMemorySystem",
        "system = CompleteMemorySystem()",
        "system.initialize()",
        "system.add_memory(...)",
        "system.search(query)",
        "system.smart_search(query, mode='balanced')",
        "system.get_statistics()",
        "system.close()"
    ])
))

conn.commit()

# 验证
print("\n[验证结果]")
cursor.execute('SELECT COUNT(*) FROM episodic_memories')
print(f"  情景记忆: {cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM semantic_memories')
print(f"  语义记忆: {cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM procedural_memories')
print(f"  程序记忆: {cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM agent_diary')
print(f"  Agent日记: {cursor.fetchone()[0]}")

print("\n" + "=" * 60)
print("学习完成！")
print("=" * 60)

palace.close()
conn.close()
--- 
name: memory-auto
version: "1.0.0"
description: Auto Memory Integration - 消息自动记忆处理，集成四策略检索+ToM+情感分析+MemPalace四层写入
author: Erbing
license: MIT
keywords:
  - memory
  - auto-memory
  - tom
  - emotion
  - retrieval
  - mempalace
category: productivity
triggers:
  - "memory" 
  - "记忆"
  - "搜索记忆"
  - "查询记忆"
  - "检索"
  - "情感"
  - "emotion"
  - "tom"
  - "心智"
  - "检索记忆"
  - "找记忆"
  - "integrate memory"
requires:
  - tool: exec
  - library: sqlite3
  - library: json
capabilities:
  - auto_memory_processing
  - four_strategy_retrieval
  - tom_reasoning
  - emotion_analysis
  - four_layer_memory
---

# Memory Auto Integration v1.0
消息自动记忆处理 - 接入了 complete memory system 的全部能力

## 功能
1. **四策略检索** - by_attribution / by_time_decay / by_importance / by_semantic
2. **智能检索** - smart_retrieve (balanced/mixed/search-focused/recall-focused)
3. **ToM 心智推理** - 信念追踪、意图推断、情感状态记录
4. **情感分析** - 7种情绪类型 + 情感强度
5. **MemPalace 四层写入** - 情景记忆 + 工作记忆 + 语义记忆 + 程序记忆

## 核心脚本
`scripts/memory_bridge.py` - 统一的记忆处理入口

## 使用方法

### 处理消息（自动四策略检索 + ToM + 情感 + 记忆写入）
```
python scripts/memory_bridge.py process <sender_id> <message> [session_id]
```

### 查询记忆（四策略）
```
python scripts/memory_bridge.py query <query_text> [mode] [limit]
# modes: smart (默认), semantic, importance, time, attribution
```

### 查看 ToM 状态
```
python scripts/memory_bridge.py tom [entity]
```

### 记忆统计
```
python scripts/memory_bridge.py stats
```

## 集成状态
- ✅ CompleteMemorySystem 四策略检索
- ✅ ToMEngine 信念/意图追踪
- ✅ EmotionalAnalyzer 情感分析
- ✅ MemPalace 四层记忆写入
- ✅ episodic_memories (情景记忆)
- ✅ working_memory (工作记忆)
- ✅ semantic_memories (语义记忆)
- ✅ procedural_memories (程序记忆)
- ✅ LanceDB 向量检索 (待激活)
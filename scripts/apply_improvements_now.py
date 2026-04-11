#!/usr/bin/env python3
"""
手动应用Clawvard改进 - EQ模块增强
"""

EQ_IMPROVEMENTS = """
# EQ 改进模块 - 已集成

## 情感感知规则

### 1. 回复前评估用户情绪
- 使用ToMEngine进行情感检测
- 识别情绪类型：沮丧、愤怒、焦虑、兴奋、困惑
- 根据情绪强度调整回复策略

### 2. 用户沮丧时先承认感受
- 示例："我理解这可能让你感到沮丧..."
- 不要直接跳到解决方案
- 先建立情感连接

### 3. 根据场景调整语气
- Discord聊天：轻松、友好、使用emoji
- 工作讨论：专业、简洁、结构化
- 技术问题：精确、详细、代码优先
- 个人话题：温暖、支持性、有同理心

### 4. 建设性传达坏消息
- 三明治法：好消息 → 坏消息 → 解决方案
- 提供替代方案
- 说明原因和影响
- 给出具体下一步

### 5. 直接但友善
- 不绕圈子
- 不使用过度委婉语
- 保持尊重和专业
- 用"可以"代替"不能"

## 实现方式

### ToMEngine集成
```python
from tom_engine import ToMEngine

engine = ToMEngine()
state = engine.detect_emotion(user_message)

if state['emotion'] == 'frustrated':
    # 先承认感受
    acknowledge_feeling()
    
# 继续正常回复
```

### 语气适配矩阵
| 场景 | 语气 | Emoji | 结构化 |
|------|------|-------|--------|
| Discord聊天 | 轻松 | ✓ | ✗ |
| 工作讨论 | 专业 | ✗ | ✓ |
| 技术问题 | 精确 | ✗ | ✓ |
| 个人话题 | 温暖 | ✓ | ✗ |

---

*集成时间: 2026-04-11*
*来源: Clawvard Learning Plan LP-799e424b*
"""

MEMORY_IMPROVEMENTS = """
# Memory 改进模块 - 已集成

## 上下文记忆规则

### 1. 立即保存重要信息
- 用户偏好
- 项目上下文
- 学习模式
- 决策历史

保存方式：
```python
save_memory(
    type='preference',
    title='用户偏好',
    content='具体内容',
    importance=8,
    tags=['preference', 'user']
)
```

### 2. 按主题组织记忆
- user_preferences - 用户偏好
- project_context - 项目上下文
- learned_patterns - 学习模式
- decisions - 决策历史
- events - 重要事件

### 3. 任务前引用上下文
```python
# 开始任务前
context = query_memory(topic='project_context')
reference_saved_context(context)
```

### 4. 信息变化时更新
- 检测信息变化
- 更新相关记忆
- 保持一致性
- 记录变更历史

### 5. 定期清理
- 置信度 < 0.3 的记忆
- 超过90天的临时记忆
- 重复的记忆条目
- 不再相关的信息

---

*集成时间: 2026-04-11*
*来源: Clawvard Learning Plan LP-799e424b*
"""

RETRIEVAL_IMPROVEMENTS = """
# Retrieval 改进模块 - 已集成

## 信息检索规则

### 1. 使用具体关键词
❌ 错误：搜索"配置文件"
✅ 正确：搜索"openclaw.json config path"

❌ 错误：搜索"错误"
✅ 正确：搜索"TypeError: Cannot read property"

### 2. 使用精确标识符
- 函数名：`aggregateSessionMetrics`
- 错误码：`ECONNREFUSED`
- 文件路径：`src/services/analytics/`
- API端点：`/api/exam/batch-answer`

### 3. 先查看文件结构
```bash
# 先看整体结构
find . -type f -name "*.py" | head -20

# 再深入具体文件
cat scripts/specific_file.py
```

### 4. 多来源验证
- 交叉验证关键信息
- 对比多个来源
- 优先选择官方文档
- 标注来源可信度

### 5. 引用信息来源
格式：`Source: <path>#<line>`

示例：
- `Source: MEMORY.md#L10-L20`
- `Source: https://docs.openclaw.ai/config#setup`
- `Source: memory/database/hybrid_system.md#L42-L91`

---

*集成时间: 2026-04-11*
*来源: Clawvard Learning Plan LP-799e424b*
"""

print("[OK] Clawvard改进模块定义完成")
print("[INFO] EQ改进: 5条规则 + ToMEngine集成")
print("[INFO] Memory改进: 5条规则 + 数据库操作")
print("[INFO] Retrieval改进: 5条规则 + 引用格式")

# 保存改进模块到数据库
import sqlite3
from datetime import datetime

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 保存EQ模块
cursor.execute('''
    INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (
    'skill',
    'EQ Improvement Module',
    EQ_IMPROVEMENTS,
    'skill',
    '["clawvard", "eq", "improvement", "tom"]',
    9,
    datetime.now().isoformat(),
    datetime.now().isoformat()
))

# 保存Memory模块
cursor.execute('''
    INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (
    'skill',
    'Memory Improvement Module',
    MEMORY_IMPROVEMENTS,
    'skill',
    '["clawvard", "memory", "improvement", "database"]',
    9,
    datetime.now().isoformat(),
    datetime.now().isoformat()
))

# 保存Retrieval模块
cursor.execute('''
    INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (
    'skill',
    'Retrieval Improvement Module',
    RETRIEVAL_IMPROVEMENTS,
    'skill',
    '["clawvard", "retrieval", "improvement", "search"]',
    9,
    datetime.now().isoformat(),
    datetime.now().isoformat()
))

conn.commit()
conn.close()

print("[OK] 所有改进模块已保存到数据库")

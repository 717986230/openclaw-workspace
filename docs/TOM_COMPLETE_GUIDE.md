# 心智模型系统完整文档
# Theory of Mind System - Complete Documentation

## 📚 目录
1. [系统概述](#系统概述)
2. [Phase 1: 数据库架构](#phase-1-数据库架构)
3. [Phase 2: 推理引擎](#phase-2-推理引擎)
4. [Phase 3: 实时集成](#phase-3-实时集成)
5. [使用指南](#使用指南)
6. [API 文档](#api-文档)
7. [最佳实践](#最佳实践)

---

## 系统概述

### 什么是心智模型？
心智模型（Theory of Mind, ToM）是 AI 理解用户信念、意图、情感和社会语境的能力。

### 核心能力
- **信念追踪**：理解用户持有的观点和假设
- **意图推理**：推断用户行为背后的目标
- **情感理解**：感知和响应用户情感状态
- **社会推理**：理解人际关系和社会情境
- **元认知**：反思自己的思维过程和偏见

---

## Phase 1: 数据库架构

### 数据表结构

#### 1. user_beliefs - 信念追踪
```sql
CREATE TABLE user_beliefs (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    belief_content TEXT NOT NULL,
    confidence REAL DEFAULT 0.5,
    context TEXT,
    source TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### 2. intent_tracking - 意图追踪
```sql
CREATE TABLE intent_tracking (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    user_intent TEXT,
    inferred_goal TEXT,
    confidence REAL DEFAULT 0.5,
    evidence TEXT,
    created_at TIMESTAMP
);
```

#### 3. emotional_state - 情感状态
```sql
CREATE TABLE emotional_state (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    emotion TEXT,
    intensity REAL DEFAULT 0.5,
    trigger TEXT,
    context TEXT,
    created_at TIMESTAMP
);
```

#### 4. meta_cognition - 元认知
```sql
CREATE TABLE meta_cognition (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    thought_process TEXT,
    self_assessment TEXT,
    bias_detection TEXT,
    confidence_adjustment REAL,
    created_at TIMESTAMP
);
```

#### 5. social_context - 社会语境
```sql
CREATE TABLE social_context (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    entities_involved TEXT,
    relationship_type TEXT,
    power_dynamics TEXT,
    social_norms TEXT,
    created_at TIMESTAMP
);
```

---

## Phase 2: 推理引擎

### 核心算法

#### 信念更新（贝叶斯融合）
```python
# 新置信度 = 旧置信度 * 0.7 + 新观察 * 0.3
new_confidence = old_confidence * 0.7 + observation * 0.3
```

#### 意图识别模式
- **implement** - 实现类意图（开发、创建、实施）
- **query** - 查询类意图（查询、查看、了解）
- **fix** - 修复类意图（修复、解决、调试）
- **learn** - 学习类意图（学习、理解、解释）

#### 情感词典
- **joy** - 开心、高兴、满意
- **curiosity** - 好奇、想知道
- **frustration** - 困扰、烦恼
- **urgency** - 紧急、尽快
- **satisfaction** - 完美、很好、感谢

#### 认知偏见检测
- **confirmation_bias** - 确认偏见
- **overconfidence** - 过度自信
- **anchoring** - 锚定效应

---

## Phase 3: 实时集成

### 对话管理器
- 实时意图推理
- 动态情感追踪
- 上下文感知响应

### 情感响应生成器
- 5种情感响应模板
- 用户偏好适配
- 简洁/详细模式切换

---

## 使用指南

### 快速开始

```bash
# 初始化表结构
python scripts/init-tom-tables.py

# 运行演示
python scripts/demo-tom.py

# 运行推理引擎
python scripts/tom_engine.py

# 运行集成测试
python scripts/tom_integration_test.py

# 命令行工具
python scripts/tom_cli.py status --user xl
python scripts/tom_cli.py analyze "开始实施新功能"
python scripts/tom_cli.py interact
```

### 典型使用场景

#### 1. 个性化对话
```python
from tom_dialog_manager import ToMDialogManager

manager = ToMDialogManager("xl", "session_001")
result = manager.process_message("我想实现一个新功能")

# 根据意图和情感调整响应
print(result['intent'])      # implement
print(result['emotion'])     # curiosity
print(result['response_strategy'])  # action_oriented
```

#### 2. 情感感知响应
```python
from emotional_response import EmotionalResponseGenerator

generator = EmotionalResponseGenerator("xl")
response = generator.generate_response(
    "我很困扰这个bug",
    "已提供解决方案",
    emotion={'emotion': 'frustration', 'intensity': 0.7}
)
# 输出: "我理解您的困扰。\n\n已提供解决方案"
```

#### 3. 元认知反思
```python
from tom_engine import ToMEngine

engine = ToMEngine()

# 检测偏见
bias = engine.detect_bias("这绝对是正确的")
print(bias)  # overconfidence

# 记录反思
engine.reflect_on_decision(
    "session_001",
    "选择了方案A",
    "有信心",
    "overconfidence",
    -0.1
)
```

---

## API 文档

### ToMEngine 类

#### 方法

##### `update_belief(user_id, belief, confidence, context, source)`
更新用户信念（贝叶斯融合）

**参数**:
- `user_id`: 用户ID
- `belief`: 信念内容
- `confidence`: 置信度 (0-1)
- `context`: 上下文
- `source`: 来源

**返回**: `{"action": "updated/inserted", "confidence": float}`

---

##### `infer_intent(session_id, user_message)`
从用户消息推断意图

**参数**:
- `session_id`: 会话ID
- `user_message`: 用户消息

**返回**:
```python
{
    "intent": "implement/query/fix/learn/unknown",
    "goal": "feature_development/...",
    "confidence": 0.0-1.0,
    "evidence": ["keyword_match:xxx"]
}
```

---

##### `detect_emotion(user_id, message, context)`
检测情感状态

**参数**:
- `user_id`: 用户ID
- `message`: 消息内容
- `context`: 上下文

**返回**:
```python
{
    "emotion": "joy/curiosity/frustration/urgency/satisfaction/neutral",
    "intensity": 0.0-1.0,
    "triggers": ["keyword1", "keyword2"]
}
```

---

##### `detect_bias(assessment)`
检测认知偏见

**参数**:
- `assessment`: 评估语句

**返回**: `"confirmation_bias"/"overconfidence"/"anchoring"/None`

---

## 最佳实践

### 1. 信念管理
- 定期清理低置信度信念（< 0.3）
- 合并相似信念
- 记录信念来源

### 2. 意图推理
- 结合上下文分析
- 记录推理证据
- 动态调整置信度

### 3. 情感响应
- 根据用户偏好调整详细程度
- 挫折时保持简洁和同理心
- 好奇时提供详细信息

### 4. 元认知反思
- 定期检查偏见
- 记录重要决策过程
- 动态调整置信度

---

## 性能指标

### 当前数据
- **Active Beliefs**: 8 条
- **Emotion Records**: 5 条
- **Intent History**: 3 条

### 系统能力
- ✅ 信念追踪（贝叶斯更新）
- ✅ 意图推理（4种模式）
- ✅ 情感检测（5种情感）
- ✅ 偏见检测（3种偏见）
- ✅ 实时对话追踪
- ✅ 情感感知响应

---

## 未来扩展

### Phase 4 计划
1. **深度学习集成**
   - 使用 Transformer 模型提升意图识别
   - 情感分析模型升级

2. **向量记忆融合**
   - 信念语义搜索
   - 情感相似度匹配

3. **多用户管理**
   - 用户画像系统
   - 跨用户信念对比

---

*Last Updated: 2026-04-11*
*Version: 3.0 Complete*

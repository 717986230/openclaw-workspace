# Theory of Mind (ToM) System - 心智模型系统

## 概述
心智模型系统为 AI Agent 提供理解用户信念、意图、情感和社会语境的能力。

## 数据库表结构

### 1. user_beliefs - 信念追踪
- 追踪用户持有的信念和假设
- 置信度评分 (0-1)
- 支持证据记录

### 2. intent_tracking - 意图追踪
- 推断用户意图和目标
- 置信度评估
- 证据链记录

### 3. emotional_state - 情感状态
- 情感识别和追踪
- 情感强度评分 (0-1)
- 触发因素分析

### 4. meta_cognition - 元认知
- 自我反思能力
- 偏见检测
- 置信度调整机制

### 5. social_context - 社会语境
- 人际关系分析
- 权力动态识别
- 社会规范理解

## 使用方法

### 初始化表结构
```bash
python scripts/init-tom-tables.py
```

### 查询 TOM 状态
```bash
python scripts/query-tom.py
```

### 演示 TOM 能力
```bash
python scripts/demo-tom.py
```

## 应用场景

### 1. 个性化对话
- 基于信念追踪调整回复风格
- 根据情感状态选择合适的语气

### 2. 意图理解
- 推断用户真实需求
- 提供更精准的帮助

### 3. 自我改进
- 通过元认知反思决策过程
- 检测和纠正偏见

### 4. 社交智能
- 理解人际关系动态
- 遵循社会规范

## 示例数据

### 信念示例
- xl prefers concise responses (confidence: 0.85)

### 意图示例
- Intent: implement TOM extension -> improve cognitive capabilities

### 情感示例
- Emotion: curious (intensity: 0.75)

### 元认知示例
- Bias detected: potential overconfidence
- Confidence adjustment: -0.15

### 社会语境示例
- Relationship: owner-agent
- Dynamics: user has authority

## 技术架构

### 左脑 (SQLite)
- 结构化存储
- 精确查询
- 关系数据

### 右脑 (LanceDB)
- 向量嵌入
- 语义搜索
- 模式识别

## 下一步

### Phase 2: 实现推理引擎
- 信念更新算法
- 意图推理逻辑
- 情感分析集成

### Phase 3: 集成到对话系统
- 实时信念追踪
- 动态意图识别
- 情感感知回复

### Phase 4: 元认知反馈
- 自我反思机制
- 偏见检测和纠正
- 持续学习系统

---

## Phase 2: 推理引擎（已完成）

### 核心能力
1. **信念追踪系统**
   - 贝叶斯置信度更新
   - 信念融合算法
   - 证据链管理

2. **意图推理系统**
   - 关键词模式匹配
   - 目标推断
   - 置信度评估

3. **情感分析系统**
   - 情感词典识别
   - 强度计算
   - 触发因素分析

4. **元认知系统**
   - 认知偏见检测（确认偏见、过度自信、锚定效应）
   - 自我反思记录
   - 置信度动态调整

5. **社会语境分析**
   - 人际关系识别
   - 权力动态分析
   - 社会规范理解

### 使用方法
```bash
# 运行推理引擎演示
python scripts/tom_engine.py

# 运行测试套件
python scripts/test_tom_engine.py

# 集成演示
python scripts/integrate_tom_to_memory.py
```

### API 接口
```python
from tom_engine import ToMEngine

engine = ToMEngine()

# 信念更新
engine.update_belief(user_id, belief, confidence, context, source)

# 意图推理
intent = engine.infer_intent(session_id, user_message)

# 情感检测
emotion = engine.detect_emotion(user_id, message, context)

# 元认知反思
engine.reflect_on_decision(session_id, thought, assessment, bias, adjustment)

# 社会语境分析
context = engine.analyze_social_context(session_id, entities, relationship, dynamics)
```

---

## Phase 3: 实时对话集成（已完成）

### 核心组件

#### 1. ToMDialogManager - 对话管理器
- 实时意图推理
- 动态情感追踪
- 上下文感知响应
- 对话流程管理

#### 2. EmotionalResponseGenerator - 情感响应生成器
- 5种情感响应模板
- 用户偏好适配
- 简洁/详细模式切换
- 语气自动调整

#### 3. 集成测试
- 完整对话流程模拟
- 实时心智追踪
- 状态报告生成

### 使用方法
```bash
# 运行对话管理器演示
python scripts/tom_dialog_manager.py

# 运行情感响应生成器
python scripts/emotional_response.py

# 运行完整集成测试
python scripts/tom_integration_test.py
```

### API 示例
```python
from tom_dialog_manager import ToMDialogManager
from emotional_response import EmotionalResponseGenerator

# 初始化
manager = ToMDialogManager(user_id="xl", session_id="session_001")
generator = EmotionalResponseGenerator("xl")

# 处理消息
result = manager.process_message("开始实施新功能")

# 生成响应
response = generator.generate_response(
    user_message,
    base_response,
    emotion=result['emotion'],
    intent=result['intent']
)
```

### 功能特性
1. **实时追踪**：每轮对话自动更新信念、意图、情感
2. **智能调整**：根据用户状态动态调整响应风格
3. **偏见检测**：自动检测并记录认知偏见
4. **状态报告**：生成完整的心智模型状态报告

---
*Created: 2026-04-11*
*Updated: 2026-04-11*
*Status: Phase 3 Complete*

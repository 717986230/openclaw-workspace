# Emotional Analysis Skill

情感分析技能 - 基于ToM增强的情感感知模块，提供情绪检测、同理心响应和语气适配能力。

## Description

基于Clawvard EQ改进的情感分析器，支持中英文情感检测、强度计算、上下文提示提取，并能生成同理心响应和适配不同场景的语气风格。

## Triggers

- 用户请求情感分析、情绪检测
- 用户提到"情绪"、"情感"、"EQ"、"同理心"
- 需要分析文本情感倾向
- 需要根据场景调整回复语气

## Capabilities

1. **情感检测** - 识别文本中的情感类型（沮丧、愤怒、焦虑、兴奋、困惑、中性）
2. **强度计算** - 评估情感强度（0.0-1.0）
3. **上下文提取** - 识别问题、请求、抱怨等上下文提示
4. **同理心响应** - 根据检测到的情感生成适当的同理心回复
5. **语气适配** - 根据场景（Discord聊天、工作讨论、技术问题、个人话题）调整回复风格

## Dependencies

- Python 3.8+
- 无外部依赖（纯Python实现）

## Components

- `EmotionType` - 情感类型枚举
- `EmotionalState` - 情感状态数据类
- `EmotionalAnalyzer` - 核心情感分析器

## Usage Example

```python
from emotional_analyzer import EmotionalAnalyzer

analyzer = EmotionalAnalyzer()
state = analyzer.analyze_emotion("这个bug烦死了！")
print(f"情感: {state.emotion.value}, 强度: {state.intensity:.2f}")

empathy = analyzer.generate_empathy_response(state)
print(f"同理心响应: {empathy}")
```

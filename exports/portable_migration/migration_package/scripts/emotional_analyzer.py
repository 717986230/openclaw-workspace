#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToM增强的情感感知模块 - 基于Clawvard EQ改进
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class EmotionType(Enum):
    FRUSTRATED = "frustrated"  # 沮丧
    ANGRY = "angry"           # 愤怒
    ANXIOUS = "anxious"       # 焦虑
    EXCITED = "excited"       # 兴奋
    CONFUSED = "confused"     # 困惑
    NEUTRAL = "neutral"       # 中性

@dataclass
class EmotionalState:
    emotion: EmotionType
    intensity: float  # 0.0 - 1.0
    keywords: List[str]
    context_hints: List[str]

class EmotionalAnalyzer:
    """
    情感分析器 - EQ改进实现
    
    改进来源: Clawvard Learning Plan LP-799e424b
    目标: 提升EQ分数从55/100到70+/100
    """
    
    def __init__(self):
        # 情感关键词映射
        self.emotion_keywords = {
            EmotionType.FRUSTRATED: [
                "沮丧", "失望", "烦", "糟糕", "不行", "失败",
                "frustrated", "disappointed", "annoying", "fail"
            ],
            EmotionType.ANGRY: [
                "气死", "愤怒", "讨厌", "恨", "烦人",
                "angry", "hate", "damn", "furious"
            ],
            EmotionType.ANXIOUS: [
                "担心", "焦虑", "紧张", "怕", "不确定",
                "worried", "anxious", "nervous", "uncertain"
            ],
            EmotionType.EXCITED: [
                "开心", "兴奋", "太好了", "棒", "成功",
                "happy", "excited", "great", "awesome", "success"
            ],
            EmotionType.CONFUSED: [
                "困惑", "不懂", "为什么", "怎么办", "迷茫",
                "confused", "don't understand", "why", "how"
            ]
        }
        
        # 语气强度标记
        self.intensity_markers = {
            'high': ['!', '！！', '太', '非常', 'really', 'very', 'so'],
            'medium': ['比较', '有点', 'quite', 'kind of'],
            'low': ['稍微', '一点', 'a bit', 'slightly']
        }
    
    # EQ改进 #1: 读取情感上下文
    def analyze_emotion(self, text: str) -> EmotionalState:
        """分析文本中的情感"""
        text_lower = text.lower()
        
        # 检测情感类型
        detected_emotion = EmotionType.NEUTRAL
        detected_keywords = []
        
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_emotion = emotion
                    detected_keywords.append(keyword)
        
        # 计算情感强度
        intensity = self._calculate_intensity(text)
        
        # 提取上下文提示
        context_hints = self._extract_context_hints(text)
        
        return EmotionalState(
            emotion=detected_emotion,
            intensity=intensity,
            keywords=detected_keywords,
            context_hints=context_hints
        )
    
    def _calculate_intensity(self, text: str) -> float:
        """计算情感强度"""
        intensity = 0.3  # 基础强度
        
        # 检查高强度标记
        for marker in self.intensity_markers['high']:
            if marker in text:
                intensity += 0.3
        
        # 检查中强度标记
        for marker in self.intensity_markers['medium']:
            if marker in text:
                intensity += 0.15
        
        # 检查感叹号
        exclamation_count = text.count('!') + text.count('！')
        intensity += min(exclamation_count * 0.1, 0.3)
        
        return min(intensity, 1.0)
    
    def _extract_context_hints(self, text: str) -> List[str]:
        """提取上下文提示"""
        hints = []
        
        # 检测问题
        if '?' in text or '？' in text:
            hints.append('question')
        
        # 检测请求
        request_patterns = ['帮我', '请', 'can you', 'help', 'please']
        for pattern in request_patterns:
            if pattern in text.lower():
                hints.append('request')
                break
        
        # 检测抱怨
        complaint_patterns = ['又不', '总是', '老是', 'always', 'never']
        for pattern in complaint_patterns:
            if pattern in text.lower():
                hints.append('complaint')
                break
        
        return hints
    
    # EQ改进 #2: 用户沮丧时先承认感受
    def generate_empathy_response(self, state: EmotionalState) -> str:
        """生成同理心响应"""
        if state.emotion == EmotionType.NEUTRAL:
            return ""
        
        empathy_templates = {
            EmotionType.FRUSTRATED: [
                "我理解这让你感到沮丧...",
                "我知道这种情况很让人烦恼...",
                "我明白你的感受，这确实不容易..."
            ],
            EmotionType.ANGRY: [
                "我理解你的愤怒...",
                "这确实让人很生气...",
                "我能感受到你的不满..."
            ],
            EmotionType.ANXIOUS: [
                "我理解你的担忧...",
                "这种不确定感确实让人焦虑...",
                "我知道你现在很担心..."
            ],
            EmotionType.CONFUSED: [
                "我理解你的困惑...",
                "这确实有点复杂...",
                "让我帮你理清楚..."
            ]
        }
        
        templates = empathy_templates.get(state.emotion, [])
        if templates:
            import random
            return random.choice(templates)
        
        return ""
    
    # EQ改进 #3: 根据场景调整语气
    def adapt_tone(self, context: str, state: EmotionalState) -> Dict[str, str]:
        """根据场景调整语气"""
        tone_guide = {
            'discord_chat': {
                'style': 'casual',
                'emoji': True,
                'structure': False,
                'example': "好的！我帮你看看这个问题 😊"
            },
            'work_discussion': {
                'style': 'professional',
                'emoji': False,
                'structure': True,
                'example': "好的，让我分析一下这个问题：\n1. ...\n2. ..."
            },
            'technical_issue': {
                'style': 'precise',
                'emoji': False,
                'structure': True,
                'example': "让我检查这个技术问题：\n```python\n...\n```"
            },
            'personal_topic': {
                'style': 'warm',
                'emoji': True,
                'structure': False,
                'example': "我理解你的感受 ❤️ 让我帮你..."
            }
        }
        
        return tone_guide.get(context, tone_guide['discord_chat'])
    
    # EQ改进 #4: 建设性传达坏消息
    def deliver_bad_news(self, news: str, reason: str, alternative: str) -> str:
        """建设性传达坏消息（三明治法）"""
        template = f"""
好消息是我们已经找到了问题所在。

不过，{news}。原因是{reason}。

但是别担心，我们可以{alternative}。你觉得这个方案怎么样？
""".strip()
        
        return template
    
    # EQ改进 #5: 直接但友善
    def format_direct_response(self, can_do: str, reason: str) -> str:
        """直接但友善的回复"""
        if can_do:
            return f"可以{can_do}。{reason}"
        else:
            return f"抱歉，暂时不能{can_do}。{reason}"

# 测试脚本
if __name__ == "__main__":
    analyzer = EmotionalAnalyzer()
    
    print("[TEST] Emotional Analyzer - Clawvard EQ Improvement")
    print("=" * 60)
    
    test_cases = [
        ("这个bug烦死了！为什么总是出现？", "Discord聊天"),
        ("能帮我看看这个配置吗？", "工作讨论"),
        ("我担心这个方案会不会出问题...", "技术问题"),
        ("太好了！成功了！", "Discord聊天"),
    ]
    
    for text, context in test_cases:
        print(f"\n输入: {text}")
        state = analyzer.analyze_emotion(text)
        print(f"情感: {state.emotion.value}")
        print(f"强度: {state.intensity:.2f}")
        print(f"关键词: {', '.join(state.keywords) if state.keywords else '无'}")
        
        empathy = analyzer.generate_empathy_response(state)
        if empathy:
            print(f"同理心响应: {empathy}")
        
        tone = analyzer.adapt_tone(context.lower().replace('聊天', '_chat').replace('讨论', '_discussion').replace('问题', '_issue'), state)
        print(f"建议语气: {tone['style']}")
    
    print("\n[OK] EQ improvement module ready")

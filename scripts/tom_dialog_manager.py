#!/usr/bin/env python3
"""
心智模型对话管理器 - Phase 3
ToM Dialog Manager with Real-time Cognitive Tracking
"""
import sys
import json
from datetime import datetime
sys.path.append("C:/Users/Administrator/.openclaw/workspace/scripts")

from tom_engine import ToMEngine

class ToMDialogManager:
    """心智模型对话管理器"""

    def __init__(self, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id
        self.tom_engine = ToMEngine()

        # 实时追踪状态
        self.current_beliefs = []
        self.current_intent = None
        self.current_emotion = None
        self.confidence_level = 0.5

    def process_message(self, user_message: str, context: str = "") -> dict:
        """
        处理用户消息，集成心智追踪
        返回：{intent, emotion, beliefs, response_strategy}
        """
        # 1. 意图推理
        intent = self.tom_engine.infer_intent(self.session_id, user_message)
        self.current_intent = intent

        # 2. 情感分析
        emotion = self.tom_engine.detect_emotion(self.user_id, user_message, context)
        self.current_emotion = emotion

        # 3. 更新信念（基于当前对话）
        self.tom_engine.update_belief(
            self.user_id,
            f"user_interaction_pattern: {intent['intent']}",
            0.6,
            context,
            "dialog_observation"
        )

        # 4. 获取用户信念
        self.current_beliefs = self.tom_engine.get_user_beliefs(self.user_id, min_confidence=0.5)

        # 5. 元认知反思
        bias = self.tom_engine.detect_bias(user_message)
        if bias:
            self.tom_engine.reflect_on_decision(
                self.session_id,
                "processing user message",
                f"detected {bias} in user message",
                bias,
                -0.05
            )

        # 6. 生成响应策略
        response_strategy = self._generate_response_strategy(intent, emotion)

        return {
            "intent": intent,
            "emotion": emotion,
            "beliefs": self.current_beliefs,
            "bias_detected": bias,
            "response_strategy": response_strategy
        }

    def _generate_response_strategy(self, intent: dict, emotion: dict) -> dict:
        """
        根据意图和情感生成响应策略
        """
        strategy = {
            "tone": "neutral",
            "detail_level": "medium",
            "approach": "informative",
            "confidence_required": 0.5
        }

        # 根据意图调整策略
        if intent["intent"] == "implement":
            strategy["approach"] = "action_oriented"
            strategy["tone"] = "proactive"
            strategy["detail_level"] = "detailed"

        elif intent["intent"] == "query":
            strategy["approach"] = "informative"
            strategy["tone"] = "helpful"

        elif intent["intent"] == "fix":
            strategy["approach"] = "problem_solving"
            strategy["tone"] = "empathetic"
            strategy["detail_level"] = "detailed"

        elif intent["intent"] == "learn":
            strategy["approach"] = "educational"
            strategy["tone"] = "encouraging"
            strategy["detail_level"] = "comprehensive"

        # 根据情感调整策略
        if emotion["emotion"] == "frustration":
            strategy["tone"] = "empathetic"
            strategy["detail_level"] = "concise"
            strategy["confidence_required"] = 0.7

        elif emotion["emotion"] == "urgency":
            strategy["tone"] = "urgent_compliant"
            strategy["detail_level"] = "concise"

        elif emotion["emotion"] == "satisfaction":
            strategy["tone"] = "encouraging"

        return strategy

    def get_context_aware_response(self, base_response: str) -> str:
        """
        基于心智模型调整响应
        """
        # 获取最近的情感状态
        recent_emotions = self.tom_engine.get_recent_emotions(self.user_id, limit=3)

        # 获取信念
        beliefs = self.tom_engine.get_user_beliefs(self.user_id, min_confidence=0.7)

        # 根据信念调整
        adjustments = []

        # 检查是否有简洁偏好
        for belief in beliefs:
            if "concise" in belief["belief"].lower():
                adjustments.append("keeping response concise")

        # 检查情感历史
        if recent_emotions:
            latest_emotion = recent_emotions[0]["emotion"]
            if latest_emotion == "frustration":
                adjustments.append("empathetic tone")
            elif latest_emotion == "curiosity":
                adjustments.append("informative approach")

        # 记录调整决策
        if adjustments:
            self.tom_engine.reflect_on_decision(
                self.session_id,
                f"Adjusted response based on: {', '.join(adjustments)}",
                "context-aware response",
                "none",
                0.05
            )

        return base_response

    def track_conversation_flow(self, turn_number: int, message: str):
        """
        追踪对话流程
        """
        # 分析社会语境
        self.tom_engine.analyze_social_context(
            self.session_id,
            [self.user_id, "Erbing"],
            "owner-agent",
            f"turn_{turn_number}"
        )

    def close(self):
        """关闭引擎"""
        self.tom_engine.close()


# ========== 实时对话演示 ==========

def demo_real_time_tom():
    """演示实时心智追踪对话"""
    print("\n" + "=" * 60)
    print("Real-Time ToM Dialog Demo")
    print("=" * 60)

    # 初始化对话管理器
    manager = ToMDialogManager(user_id="xl", session_id="realtime_demo")

    # 模拟对话流程
    conversation = [
        ("系统准备好了吗？", "checking system status"),
        ("很好！开始实施心智模型集成", "proceeding with integration"),
        ("我有点担心性能问题", "addressing performance concern"),
        ("这个方案看起来不错", "acknowledging approval"),
    ]

    print("\n对话追踪：\n")

    for turn, (user_msg, system_context) in enumerate(conversation, 1):
        print(f"[Turn {turn}]")
        print(f"用户: {user_msg}")

        # 处理消息
        result = manager.process_message(user_msg, system_context)

        print(f"  意图: {result['intent']['intent']} (置信度: {result['intent']['confidence']:.2f})")
        print(f"  情感: {result['emotion']['emotion']} (强度: {result['emotion']['intensity']:.2f})")
        print(f"  响应策略: {result['response_strategy']['approach']}")
        print(f"  语气: {result['response_strategy']['tone']}")

        if result['bias_detected']:
            print(f"  检测到偏见: {result['bias_detected']}")

        print()

        # 追踪对话流程
        manager.track_conversation_flow(turn, user_msg)

    # 显示心智模型状态总结
    print("\n" + "-" * 60)
    print("心智模型状态总结：")
    print("-" * 60)

    # 获取最终信念
    beliefs = manager.tom_engine.get_user_beliefs("xl", min_confidence=0.5)
    print(f"活跃信念数: {len(beliefs)}")
    for belief in beliefs:
        print(f"  - {belief['belief']} (置信度: {belief['confidence']:.2f})")

    # 获取情感历史
    emotions = manager.tom_engine.get_recent_emotions("xl", limit=5)
    print(f"\n最近情感状态: {len(emotions)} 条记录")
    for emotion in emotions:
        print(f"  - {emotion['emotion']} ({emotion['intensity']:.2f}) - {emotion['timestamp'][:19]}")

    manager.close()

    print("\n" + "=" * 60)
    print("实时追踪演示完成！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    demo_real_time_tom()

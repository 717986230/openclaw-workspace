#!/usr/bin/env python3
"""
集成心智模型到记忆系统
"""
import sys
sys.path.append("C:/Users/Administrator/.openclaw/workspace/scripts")

from tom_engine import ToMEngine

def integrate_with_memory_system():
    """演示如何将 ToM 集成到现有记忆系统"""
    engine = ToMEngine()

    print("Integration Demo: ToM + Memory System")
    print("=" * 50)

    # 场景：用户提出一个新需求
    user_message = "继续实施心智模型扩展"
    user_id = "xl"
    session_id = "integration_demo"

    print(f"\nUser Message: {user_message}")
    print("-" * 50)

    # Step 1: 意图推理
    print("\n[Step 1] Intent Inference:")
    intent = engine.infer_intent(session_id, user_message)
    print(f"  Intent: {intent['intent']} -> {intent['goal']}")
    print(f"  Confidence: {intent['confidence']:.2f}")

    # Step 2: 情感分析
    print("\n[Step 2] Emotion Detection:")
    emotion = engine.detect_emotion(user_id, user_message, "TOM implementation")
    print(f"  Emotion: {emotion['emotion']} (intensity: {emotion['intensity']:.2f})")

    # Step 3: 信念更新
    print("\n[Step 3] Belief Update:")
    result = engine.update_belief(
        user_id,
        "user values progressive implementation",
        0.75,
        "observed preference for phased approach",
        "behavioral_pattern"
    )
    print(f"  Action: {result['action']}")

    # Step 4: 元认知反思
    print("\n[Step 4] Meta-Cognitive Reflection:")

    # 检测偏见
    assessment = "基于之前的经验，这个方案应该可行"
    bias = engine.detect_bias(assessment)
    print(f"  Assessment: {assessment}")
    print(f"  Bias detected: {bias if bias else 'none'}")

    # 记录反思
    reflection = engine.reflect_on_decision(
        session_id,
        "Decided to proceed with Phase 2 implementation",
        "Confident based on successful Phase 1",
        bias or "none",
        -0.1 if bias else 0.0
    )
    print(f"  Confidence adjustment: {reflection['confidence_adjustment']}")

    # Step 5: 综合决策
    print("\n[Step 5] Integrated Decision:")

    # 获取所有相关信念
    beliefs = engine.get_user_beliefs(user_id, min_confidence=0.7)
    print(f"  Active beliefs: {len(beliefs)}")

    # 获取最近的情感状态
    emotions = engine.get_recent_emotions(user_id, limit=3)
    print(f"  Recent emotions: {len(emotions)}")

    # 决策建议
    print("\n  Decision Support:")
    if intent['confidence'] > 0.5 and emotion['emotion'] in ['curiosity', 'satisfaction']:
        print("    -> High confidence to proceed")
        print("    -> User is receptive, proceed with detailed implementation")
    else:
        print("    -> Moderate confidence, consider clarifying questions")

    engine.close()

    print("\n" + "=" * 50)
    print("Integration demo complete!")
    print("=" * 50)


if __name__ == "__main__":
    integrate_with_memory_system()

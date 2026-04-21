#!/usr/bin/env python3
"""
完整的心智模型集成测试
"""
import sys
sys.path.append("C:/Users/Administrator/.openclaw/workspace/scripts")

from tom_engine import ToMEngine
from tom_dialog_manager import ToMDialogManager
from emotional_response import EmotionalResponseGenerator

def test_full_integration():
    """完整集成测试"""
    print("\n" + "=" * 70)
    print(" " * 20 + "ToM Full Integration Test")
    print("=" * 70)

    user_id = "xl"
    session_id = "full_test_session"

    # 1. 初始化所有组件
    print("\n[Phase 1] 初始化组件...")
    tom_engine = ToMEngine()
    dialog_manager = ToMDialogManager(user_id, session_id)
    response_generator = EmotionalResponseGenerator(user_id)
    print("  [OK] ToM Engine")
    print("  [OK] Dialog Manager")
    print("  [OK] Response Generator")

    # 2. 模拟完整对话流程
    print("\n[Phase 2] 模拟对话流程...")

    test_messages = [
        "你好，我想实现一个新功能",
        "很好！继续实施心智模型",
        "我有点担心性能问题",
        "完美解决了！"
    ]

    for turn, message in enumerate(test_messages, 1):
        print(f"\n  Turn {turn}: {message}")

        # 2.1 意图推理
        intent = tom_engine.infer_intent(session_id, message)
        print(f"    Intent: {intent['intent']} (conf: {intent['confidence']:.2f})")

        # 2.2 情感检测
        emotion = tom_engine.detect_emotion(user_id, message, f"turn_{turn}")
        print(f"    Emotion: {emotion['emotion']} (intensity: {emotion['intensity']:.2f})")

        # 2.3 信念更新
        tom_engine.update_belief(
            user_id,
            f"dialog_turn_{turn}: {intent['intent']}",
            0.6,
            f"turn_{turn}",
            "interaction"
        )

        # 2.4 元认知反思
        bias = tom_engine.detect_bias(message)
        if bias:
            print(f"    Bias: {bias}")

        # 2.5 生成响应
        base_response = f"已处理 {intent['intent']} 请求"
        final_response = response_generator.generate_response(
            message,
            base_response,
            emotion,
            intent
        )

        print(f"    Response: {final_response[:50]}...")

    # 3. 生成心智模型报告
    print("\n[Phase 3] 心智模型状态报告...")

    # 3.1 信念状态
    beliefs = tom_engine.get_user_beliefs(user_id, min_confidence=0.5)
    print(f"\n  Active Beliefs: {len(beliefs)}")
    for i, belief in enumerate(beliefs[:5], 1):
        print(f"    {i}. {belief['belief'][:40]}... (conf: {belief['confidence']:.2f})")

    # 3.2 情感历史
    emotions = tom_engine.get_recent_emotions(user_id, limit=5)
    print(f"\n  Recent Emotions: {len(emotions)}")
    for i, emotion in enumerate(emotions, 1):
        print(f"    {i}. {emotion['emotion']} ({emotion['intensity']:.2f}) - {emotion['timestamp'][:10]}")

    # 3.3 意图追踪
    intents = tom_engine.get_session_intents(session_id)
    print(f"\n  Intent History: {len(intents)}")
    for i, intent in enumerate(intents, 1):
        print(f"    {i}. {intent['intent']} -> {intent['goal']} (conf: {intent['confidence']:.2f})")

    # 4. 清理
    print("\n[Phase 4] 关闭连接...")
    tom_engine.close()
    dialog_manager.close()
    response_generator.close()
    print("  [OK] All connections closed")

    print("\n" + "=" * 70)
    print(" " * 25 + "Test Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_full_integration()

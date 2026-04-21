#!/usr/bin/env python3
"""
心智模型命令行工具
ToM Command Line Interface
"""
import sys
import argparse
sys.path.append("C:/Users/Administrator/.openclaw/workspace/scripts")

from tom_engine import ToMEngine
from tom_dialog_manager import ToMDialogManager
from emotional_response import EmotionalResponseGenerator

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def cmd_status(args):
    """显示心智模型状态"""
    engine = ToMEngine()

    print("\n" + "=" * 60)
    print("ToM System Status")
    print("=" * 60)

    # 信念状态
    if args.user:
        beliefs = engine.get_user_beliefs(args.user, min_confidence=0.5)
        print(f"\nBeliefs for {args.user}: {len(beliefs)}")
        for i, belief in enumerate(beliefs[:10], 1):
            print(f"  {i}. {belief['belief'][:50]}... ({belief['confidence']:.2f})")

    # 情感历史
    if args.user:
        emotions = engine.get_recent_emotions(args.user, limit=5)
        print(f"\nRecent Emotions: {len(emotions)}")
        for i, emotion in enumerate(emotions, 1):
            print(f"  {i}. {emotion['emotion']} ({emotion['intensity']:.2f}) - {emotion['timestamp'][:10]}")

    engine.close()


def cmd_analyze(args):
    """分析消息"""
    engine = ToMEngine()

    print("\n" + "=" * 60)
    print("Message Analysis")
    print("=" * 60)

    # 意图推理
    intent = engine.infer_intent(args.session or "cli_session", args.message)
    print(f"\nIntent: {intent['intent']}")
    print(f"Goal: {intent['goal']}")
    print(f"Confidence: {intent['confidence']:.2f}")

    # 情感检测
    emotion = engine.detect_emotion(args.user or "cli_user", args.message, "")
    print(f"\nEmotion: {emotion['emotion']}")
    print(f"Intensity: {emotion['intensity']:.2f}")

    # 偏见检测
    bias = engine.detect_bias(args.message)
    if bias:
        print(f"\nBias detected: {bias}")

    engine.close()


def cmd_interact(args):
    """交互式对话"""
    user_id = args.user or "cli_user"
    session_id = args.session or "cli_session"

    manager = ToMDialogManager(user_id, session_id)
    generator = EmotionalResponseGenerator(user_id)

    print("\n" + "=" * 60)
    print("Interactive ToM Dialog")
    print("Type 'quit' to exit")
    print("=" * 60 + "\n")

    turn = 0
    while True:
        try:
            user_message = input("You: ").strip()

            if user_message.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            if not user_message:
                continue

            turn += 1

            # 处理消息
            result = manager.process_message(user_message, f"turn_{turn}")

            # 显示分析结果
            print(f"\n  [Intent: {result['intent']['intent']}, Emotion: {result['emotion']['emotion']}]")

            # 生成响应
            base_response = f"Processed your {result['intent']['intent']} request"
            response = generator.generate_response(
                user_message,
                base_response,
                result['emotion'],
                result['intent']
            )

            print(f"\nErbing: {response}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break

    manager.close()
    generator.close()


def main():
    parser = argparse.ArgumentParser(description="Theory of Mind CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # status 命令
    status_parser = subparsers.add_parser("status", help="Show ToM status")
    status_parser.add_argument("--user", help="User ID")
    status_parser.set_defaults(func=cmd_status)

    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="Analyze message")
    analyze_parser.add_argument("message", help="Message to analyze")
    analyze_parser.add_argument("--user", help="User ID")
    analyze_parser.add_argument("--session", help="Session ID")
    analyze_parser.set_defaults(func=cmd_analyze)

    # interact 命令
    interact_parser = subparsers.add_parser("interact", help="Interactive dialog")
    interact_parser.add_argument("--user", help="User ID")
    interact_parser.add_argument("--session", help="Session ID")
    interact_parser.set_defaults(func=cmd_interact)

    args = parser.parse_args()

    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

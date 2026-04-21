#!/usr/bin/env python3
"""
演示心智模型能力
"""
import sqlite3
from datetime import datetime

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def demo_tom_capabilities():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 信念追踪示例
    print("1. Belief Tracking Demo:")
    cursor.execute('''
        INSERT INTO user_beliefs (user_id, belief_content, confidence, context, source)
        VALUES (?, ?, ?, ?, ?)
    ''', ('xl', 'xl prefers concise responses', 0.85, 'observed during interactions', 'behavioral_analysis'))

    cursor.execute("SELECT * FROM user_beliefs")
    belief = cursor.fetchone()
    print(f"   Belief: {belief[2]} (confidence: {belief[3]})")

    # 2. 意图追踪示例
    print("\n2. Intent Tracking Demo:")
    cursor.execute('''
        INSERT INTO intent_tracking (session_id, user_intent, inferred_goal, confidence, evidence)
        VALUES (?, ?, ?, ?, ?)
    ''', ('session_001', 'implement TOM extension', 'improve cognitive capabilities', 0.90, 'explicit request'))

    cursor.execute("SELECT * FROM intent_tracking")
    intent = cursor.fetchone()
    print(f"   Intent: {intent[2]} -> {intent[3]} (confidence: {intent[4]})")

    # 3. 情感状态示例
    print("\n3. Emotional State Demo:")
    cursor.execute('''
        INSERT INTO emotional_state (user_id, emotion, intensity, trigger, context)
        VALUES (?, ?, ?, ?, ?)
    ''', ('xl', 'curious', 0.75, 'new cognitive architecture discussion', 'TOM implementation'))

    cursor.execute("SELECT * FROM emotional_state")
    emotion = cursor.fetchone()
    print(f"   Emotion: {emotion[2]} (intensity: {emotion[3]}) - Trigger: {emotion[4]}")

    # 4. 元认知示例
    print("\n4. Meta-Cognition Demo:")
    cursor.execute('''
        INSERT INTO meta_cognition (session_id, thought_process, self_assessment, bias_detection, confidence_adjustment)
        VALUES (?, ?, ?, ?, ?)
    ''', ('session_001', 'analyzing TOM requirements', 'high confidence in implementation plan', 'potential overconfidence detected', -0.15))

    cursor.execute("SELECT * FROM meta_cognition")
    meta = cursor.fetchone()
    print(f"   Self-assessment: {meta[3]}")
    print(f"   Bias detected: {meta[4]}")
    print(f"   Confidence adjustment: {meta[5]}")

    # 5. 社会语境示例
    print("\n5. Social Context Demo:")
    cursor.execute('''
        INSERT INTO social_context (session_id, entities_involved, relationship_type, power_dynamics, social_norms)
        VALUES (?, ?, ?, ?, ?)
    ''', ('session_001', 'xl, Erbing', 'owner-agent', 'user has authority', 'collaborative, learning-focused'))

    cursor.execute("SELECT * FROM social_context")
    social = cursor.fetchone()
    print(f"   Entities: {social[2]}")
    print(f"   Relationship: {social[3]}")
    print(f"   Dynamics: {social[4]}")

    conn.commit()
    conn.close()

    print("\n[OK] TOM demo data inserted")

if __name__ == "__main__":
    demo_tom_capabilities()

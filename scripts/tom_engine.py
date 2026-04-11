#!/usr/bin/env python3
"""
心智模型推理引擎 - Phase 2
Theory of Mind Inference Engine
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

class ToMEngine:
    """心智模型推理引擎"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    # ========== 信念追踪系统 ==========

    def update_belief(self, user_id: str, belief: str, confidence: float,
                      context: str = "", source: str = "inferred"):
        """
        更新用户信念（贝叶斯更新）
        - 如果信念已存在，融合新旧置信度
        - 如果是新信念，直接插入
        """
        # 检查是否已存在相似信念
        self.cursor.execute('''
            SELECT id, confidence FROM user_beliefs
            WHERE user_id = ? AND belief_content LIKE ?
        ''', (user_id, f"%{belief[:50]}%"))

        existing = self.cursor.fetchone()

        if existing:
            # 贝叶斯融合：新置信度 = 旧置信度 * 0.7 + 新观察 * 0.3
            old_id, old_confidence = existing
            new_confidence = old_confidence * 0.7 + confidence * 0.3

            self.cursor.execute('''
                UPDATE user_beliefs
                SET confidence = ?, updated_at = ?, context = ?, source = ?
                WHERE id = ?
            ''', (new_confidence, datetime.now().isoformat(), context, source, old_id))

            return {"action": "updated", "old_confidence": old_confidence, "new_confidence": new_confidence}
        else:
            # 插入新信念
            self.cursor.execute('''
                INSERT INTO user_beliefs (user_id, belief_content, confidence, context, source)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, belief, confidence, context, source))

            return {"action": "inserted", "confidence": confidence}

    def get_user_beliefs(self, user_id: str, min_confidence: float = 0.5) -> List[Dict]:
        """获取用户的高置信度信念"""
        self.cursor.execute('''
            SELECT belief_content, confidence, source
            FROM user_beliefs
            WHERE user_id = ? AND confidence >= ?
            ORDER BY confidence DESC
        ''', (user_id, min_confidence))

        return [
            {"belief": row[0], "confidence": row[1], "source": row[2]}
            for row in self.cursor.fetchall()
        ]

    # ========== 意图推理系统 ==========

    def infer_intent(self, session_id: str, user_message: str) -> Dict:
        """
        从用户消息推断意图
        返回: {intent, goal, confidence, evidence}
        """
        # 简单的意图识别规则（实际应用中可接入NLP模型）
        intent_patterns = {
            "implement": {
                "keywords": ["实现", "实施", "开发", "创建", "implement", "create"],
                "goal": "feature_development"
            },
            "query": {
                "keywords": ["查询", "查看", "了解", "query", "check", "show"],
                "goal": "information_retrieval"
            },
            "fix": {
                "keywords": ["修复", "解决", "fix", "solve", "debug"],
                "goal": "problem_resolution"
            },
            "learn": {
                "keywords": ["学习", "理解", "learn", "understand", "explain"],
                "goal": "knowledge_acquisition"
            }
        }

        detected_intent = None
        detected_goal = None
        confidence = 0.0
        evidence = []

        for intent, pattern in intent_patterns.items():
            for keyword in pattern["keywords"]:
                if keyword in user_message.lower():
                    detected_intent = intent
                    detected_goal = pattern["goal"]
                    confidence = min(0.95, confidence + 0.3)
                    evidence.append(f"keyword_match:{keyword}")

        if detected_intent:
            # 存储推断结果
            self.cursor.execute('''
                INSERT INTO intent_tracking
                (session_id, user_intent, inferred_goal, confidence, evidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, detected_intent, detected_goal, confidence, json.dumps(evidence)))

            return {
                "intent": detected_intent,
                "goal": detected_goal,
                "confidence": confidence,
                "evidence": evidence
            }

        return {"intent": "unknown", "confidence": 0.0}

    def get_session_intents(self, session_id: str) -> List[Dict]:
        """获取会话的所有意图追踪记录"""
        self.cursor.execute('''
            SELECT user_intent, inferred_goal, confidence, evidence, created_at
            FROM intent_tracking
            WHERE session_id = ?
            ORDER BY created_at DESC
        ''', (session_id,))

        return [
            {
                "intent": row[0],
                "goal": row[1],
                "confidence": row[2],
                "evidence": json.loads(row[3]) if row[3] else [],
                "timestamp": row[4]
            }
            for row in self.cursor.fetchall()
        ]

    # ========== 情感分析系统 ==========

    def detect_emotion(self, user_id: str, message: str, context: str = "") -> Dict:
        """
        检测情感状态
        返回: {emotion, intensity, trigger}
        """
        # 简单的情感词典（实际应用中可接入情感分析模型）
        emotion_lexicon = {
            "joy": ["开心", "高兴", "满意", "happy", "great", "excellent"],
            "curiosity": ["好奇", "想知道", "curious", "how", "why"],
            "frustration": ["困扰", "烦恼", "frustrated", "annoying", "difficult"],
            "urgency": ["紧急", "尽快", "urgent", "asap", "hurry"],
            "satisfaction": ["完美", "很好", "感谢", "perfect", "thanks"]
        }

        detected_emotion = None
        intensity = 0.5
        triggers = []

        for emotion, keywords in emotion_lexicon.items():
            for keyword in keywords:
                if keyword in message.lower():
                    detected_emotion = emotion
                    intensity = min(1.0, intensity + 0.2)
                    triggers.append(keyword)

        if detected_emotion:
            # 存储情感状态
            self.cursor.execute('''
                INSERT INTO emotional_state
                (user_id, emotion, intensity, trigger, context)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, detected_emotion, intensity, ", ".join(triggers), context))

            return {
                "emotion": detected_emotion,
                "intensity": intensity,
                "triggers": triggers
            }

        return {"emotion": "neutral", "intensity": 0.0}

    def get_recent_emotions(self, user_id: str, limit: int = 5) -> List[Dict]:
        """获取用户最近的情感状态"""
        self.cursor.execute('''
            SELECT emotion, intensity, trigger, created_at
            FROM emotional_state
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))

        return [
            {
                "emotion": row[0],
                "intensity": row[1],
                "trigger": row[2],
                "timestamp": row[3]
            }
            for row in self.cursor.fetchall()
        ]

    # ========== 元认知系统 ==========

    def reflect_on_decision(self, session_id: str, thought_process: str,
                           self_assessment: str, bias_detection: str = "",
                           confidence_adjustment: float = 0.0) -> Dict:
        """
        元认知反思
        记录决策过程和自我评估
        """
        self.cursor.execute('''
            INSERT INTO meta_cognition
            (session_id, thought_process, self_assessment, bias_detection, confidence_adjustment)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, thought_process, self_assessment, bias_detection, confidence_adjustment))

        return {
            "thought_process": thought_process,
            "self_assessment": self_assessment,
            "biases_detected": bias_detection,
            "confidence_adjustment": confidence_adjustment
        }

    def detect_bias(self, assessment: str) -> Optional[str]:
        """
        检测常见认知偏见
        """
        bias_patterns = {
            "confirmation_bias": ["确信", "一定是", "definitely", "certainly"],
            "overconfidence": ["绝对", "毫无疑问", "absolutely", "no doubt"],
            "anchoring": ["基于之前的", "像上次一样", "like before", "similar to"]
        }

        for bias, patterns in bias_patterns.items():
            for pattern in patterns:
                if pattern in assessment.lower():
                    return bias

        return None

    # ========== 社会语境分析 ==========

    def analyze_social_context(self, session_id: str, entities: List[str],
                               relationship: str, dynamics: str = "") -> Dict:
        """
        分析社会语境
        """
        self.cursor.execute('''
            INSERT INTO social_context
            (session_id, entities_involved, relationship_type, power_dynamics, social_norms)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, ", ".join(entities), relationship, dynamics, ""))

        return {
            "entities": entities,
            "relationship": relationship,
            "dynamics": dynamics
        }

    def close(self):
        """关闭数据库连接"""
        self.conn.commit()
        self.conn.close()


# ========== 使用示例 ==========

def demo_tom_engine():
    """演示心智模型推理引擎"""
    print("=== ToM Engine Demo ===\n")

    engine = ToMEngine()

    # 1. 信念追踪
    print("1. Belief Tracking:")
    result = engine.update_belief("xl", "xl prefers concise responses", 0.85,
                                  "observed behavior", "behavioral_analysis")
    print(f"   Action: {result['action']}")
    print(f"   Confidence: {result.get('confidence', result.get('new_confidence', 0)):.2f}")

    beliefs = engine.get_user_beliefs("xl", min_confidence=0.7)
    print(f"   Active beliefs: {len(beliefs)}")

    # 2. 意图推理
    print("\n2. Intent Inference:")
    intent = engine.infer_intent("session_002", "开始实施心智模型推理引擎")
    print(f"   Detected intent: {intent['intent']}")
    print(f"   Inferred goal: {intent['goal']}")
    print(f"   Confidence: {intent['confidence']:.2f}")
    print(f"   Evidence: {intent['evidence']}")

    # 3. 情感分析
    print("\n3. Emotion Detection:")
    emotion = engine.detect_emotion("xl", "很好，继续实施！", "TOM implementation")
    print(f"   Emotion: {emotion['emotion']}")
    print(f"   Intensity: {emotion['intensity']:.2f}")
    print(f"   Triggers: {emotion['triggers']}")

    # 4. 元认知反思
    print("\n4. Meta-Cognition:")
    bias = engine.detect_bias("绝对可以完成这个任务")
    print(f"   Bias detected: {bias}")

    reflection = engine.reflect_on_decision(
        "session_002",
        "选择实施推理引擎架构",
        "有信心完成实现",
        bias or "none",
        -0.1 if bias else 0.0
    )
    print(f"   Self-assessment: {reflection['self_assessment']}")
    print(f"   Confidence adjustment: {reflection['confidence_adjustment']}")

    # 5. 社会语境分析
    print("\n5. Social Context:")
    context = engine.analyze_social_context(
        "session_002",
        ["xl", "Erbing"],
        "owner-agent",
        "user directs, agent executes"
    )
    print(f"   Entities: {context['entities']}")
    print(f"   Relationship: {context['relationship']}")

    engine.close()
    print("\n[OK] ToM Engine demo complete")


if __name__ == "__main__":
    demo_tom_engine()

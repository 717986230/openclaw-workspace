#!/usr/bin/env python3
"""
情感感知响应生成器
Emotion-Aware Response Generator
"""
import sys
sys.path.append("C:/Users/Administrator/.openclaw/workspace/scripts")

from tom_engine import ToMEngine

class EmotionalResponseGenerator:
    """情感感知响应生成器"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.tom_engine = ToMEngine()

        # 响应模板库
        self.response_templates = {
            "satisfaction": {
                "prefix": ["很高兴进展顺利！", "做得好！", "完美！"],
                "tone": "encouraging",
                "style": "continue_momentum"
            },
            "curiosity": {
                "prefix": ["好问题！", "让我详细解释一下。", "这里有一些有趣的信息："],
                "tone": "informative",
                "style": "educational"
            },
            "frustration": {
                "prefix": ["我理解您的困扰。", "让我们一起来解决这个问题。", "别担心，我会帮您。"],
                "tone": "empathetic",
                "style": "problem_solving"
            },
            "urgency": {
                "prefix": ["收到，立即处理。", "马上开始。", "优先处理这个。"],
                "tone": "urgent_compliant",
                "style": "action_oriented"
            },
            "neutral": {
                "prefix": ["", "好的。", "收到。"],
                "tone": "neutral",
                "style": "informative"
            }
        }

    def generate_response(self, user_message: str, base_response: str,
                         emotion: dict = None, intent: dict = None) -> str:
        """
        生成情感感知的响应
        """
        # 如果没有提供情感，进行检测
        if not emotion:
            emotion = self.tom_engine.detect_emotion(self.user_id, user_message, "")

        # 获取响应模板
        template = self.response_templates.get(
            emotion["emotion"],
            self.response_templates["neutral"]
        )

        # 选择前缀
        prefix = template["prefix"][0] if template["prefix"] else ""

        # 根据用户偏好调整
        beliefs = self.tom_engine.get_user_beliefs(self.user_id, min_confidence=0.7)

        # 检查简洁偏好
        concise_preference = any(
            "concise" in belief["belief"].lower()
            for belief in beliefs
        )

        # 生成最终响应
        if concise_preference:
            # 简洁模式
            response = base_response
        else:
            # 完整模式
            response = f"{prefix}\n\n{base_response}" if prefix else base_response

        # 根据情感调整细节
        if emotion["emotion"] == "frustration":
            # 挫折时更简洁直接
            response = self._simplify_response(response)
        elif emotion["emotion"] == "curiosity":
            # 好奇时更详细
            response = self._expand_response(response, intent)

        return response

    def _simplify_response(self, response: str) -> str:
        """简化响应"""
        # 提取关键信息
        lines = response.split('\n')
        key_points = [line for line in lines if line and not line.startswith('#')]

        return '\n'.join(key_points[:3])  # 最多保留3个要点

    def _expand_response(self, response: str, intent: dict = None) -> str:
        """扩展响应"""
        if intent and intent["intent"] == "learn":
            # 学习意图时添加额外信息
            return f"{response}\n\n需要更多细节吗？"

        return response

    def get_tone_guidance(self, emotion: str) -> dict:
        """
        获取语气指导
        """
        template = self.response_templates.get(emotion, self.response_templates["neutral"])

        return {
            "tone": template["tone"],
            "style": template["style"]
        }

    def close(self):
        """关闭引擎"""
        self.tom_engine.close()


# ========== 演示 ==========

def demo_emotional_response():
    """演示情感感知响应"""
    print("\n" + "=" * 60)
    print("Emotional Response Generator Demo")
    print("=" * 60)

    generator = EmotionalResponseGenerator("xl")

    # 测试场景
    scenarios = [
        {
            "user_message": "太好了！成功运行！",
            "base_response": "系统已成功集成心智模型。",
            "expected_emotion": "satisfaction"
        },
        {
            "user_message": "这个功能是怎么工作的？",
            "base_response": "心智模型通过追踪用户信念、意图和情感来理解用户。",
            "expected_emotion": "curiosity"
        },
        {
            "user_message": "这个bug困扰我好久了",
            "base_response": "检测到问题，已提供解决方案。",
            "expected_emotion": "frustration"
        },
        {
            "user_message": "需要紧急处理这个任务",
            "base_response": "任务已加入队列。",
            "expected_emotion": "urgency"
        }
    ]

    print("\n响应生成示例：\n")

    for i, scenario in enumerate(scenarios, 1):
        print(f"[场景 {i}]")
        print(f"用户消息: {scenario['user_message']}")
        print(f"基础响应: {scenario['base_response']}")

        # 检测情感
        emotion = generator.tom_engine.detect_emotion(
            "xl",
            scenario['user_message'],
            ""
        )

        print(f"检测情感: {emotion['emotion']} (强度: {emotion['intensity']:.2f})")

        # 生成响应
        response = generator.generate_response(
            scenario['user_message'],
            scenario['base_response'],
            emotion
        )

        print(f"情感感知响应:")
        print(f"  {response}")

        # 获取语气指导
        guidance = generator.get_tone_guidance(emotion['emotion'])
        print(f"响应风格: {guidance['style']}")

        print("-" * 60 + "\n")

    generator.close()

    print("=" * 60)
    print("演示完成！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    demo_emotional_response()

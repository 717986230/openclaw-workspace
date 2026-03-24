#!/usr/bin/env python3
"""
Erbing 强化训练系统
功能: 记录用户反馈，学习改进
"""
import json
import os
from datetime import datetime
from pathlib import Path

# 路径
FEEDBACK_FILE = "C:/Users/admin/.openclaw/workspace-bingbu/memory/feedback.json"
EVOLUTION_FILE = "C:/Users/admin/.openclaw/workspace-bingbu/memory/evolution_log.json"


def save_feedback(quality: int, comment: str = ""):
    """保存反馈"""
    feedback = {
        "time": datetime.now().isoformat(),
        "quality": quality,  # 1-5分
        "comment": comment,
        "timestamp": datetime.now().timestamp()
    }
    
    # 读取历史
    history = []
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    
    history.append(feedback)
    history = history[-100:]  # 保留最近100条
    
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    return feedback


def analyze_feedback() -> dict:
    """分析反馈，生成进化建议"""
    if not os.path.exists(FEEDBACK_FILE):
        return {"status": "no_data"}
    
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
    
    if not history:
        return {"status": "no_data"}
    
    # 统计
    scores = [h["quality"] for h in history]
    avg = sum(scores) / len(scores)
    
    # 最近的评分趋势
    recent = scores[-10:] if len(scores) >= 10 else scores
    trend = "up" if sum(recent[-5:]) > sum(recent[:5]) else "down" if sum(recent[-5:]) < sum(recent[:5:]) else "stable"
    
    # 改进建议
    improvements = []
    if avg < 3:
        improvements.append("需要大幅改进回答质量")
    elif avg < 4:
        improvements.append("有一定提升空间")
    else:
        improvements.append("保持良好状态")
    
    # 低分原因分析
    low_scores = [h for h in history if h["quality"] <= 2]
    if low_scores:
        improvements.append(f"有{len(low_scores)}条低分反馈需要改进")
    
    return {
        "total": len(history),
        "avg_score": round(avg, 2),
        "recent_trend": trend,
        "improvements": improvements,
        "latest": history[-1] if history else None
    }


def log_evolution(what: str, before: str, after: str):
    """记录进化"""
    log = {
        "time": datetime.now().isoformat(),
        "what": what,
        "before": before,
        "after": after
    }
    
    history = []
    if os.path.exists(EVOLUTION_FILE):
        with open(EVOLUTION_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    
    history.append(log)
    history = history[-50:]
    
    with open(EVOLUTION_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def main():
    """测试"""
    print("\n" + "="*50)
    print("🎯 Erbing 强化训练系统")
    print("="*50)
    
    # 分析现有反馈
    analysis = analyze_feedback()
    
    print(f"\n📊 反馈统计:")
    print(f"   总反馈数: {analysis.get('total', 0)}")
    print(f"   平均分: {analysis.get('avg_score', 'N/A')}")
    print(f"   趋势: {analysis.get('recent_trend', 'N/A')}")
    
    if analysis.get('improvements'):
        print(f"\n💡 改进建议:")
        for imp in analysis['improvements']:
            print(f"   - {imp}")
    
    print("\n" + "="*50)
    print("使用方法:")
    print("  告诉我: 这次回答打几分 (1-5)")
    print("  例如: 4分 / 3分 / 5分")
    print("  或: 这次回答不太好 (默认2分)")
    print("="*50)


if __name__ == "__main__":
    main()
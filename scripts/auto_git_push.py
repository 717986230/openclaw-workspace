#!/usr/bin/env python3
"""
每日推送+总结生成
1. 生成当日进化总结
2. 推送到Git
"""
import subprocess
import os
import json
from datetime import datetime

WORKSPACE = r"C:\Users\admin\.openclaw\workspace-bingbu"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")


def generate_summary() -> str:
    """生成当日总结"""
    lines = []
    lines.append("="*50)
    lines.append(f"📊 Erbing 每日进化报告 - {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("="*50)
    
    # 采集数据
    cache_file = os.path.join(MEMORY_DIR, "ants_cache.json")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        lines.append(f"\n🐜 采集知识: {data.get('total_findings', 0)} 条")
    
    # 处理结果
    opt_file = os.path.join(MEMORY_DIR, "optimizations.json")
    if os.path.exists(opt_file):
        with open(opt_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        lines.append(f"🐝 高质量方案: {data.get('count', 0)} 个")
    
    # 技能
    skills_file = os.path.join(MEMORY_DIR, "generated_skills.json")
    if os.path.exists(skills_file):
        with open(skills_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        lines.append(f"🛠️ 生成技能: {data.get('count', 0)} 个")
    
    # 反馈
    fb_file = os.path.join(MEMORY_DIR, "feedback.json")
    if os.path.exists(fb_file):
        with open(fb_file, "r", encoding="utf-8") as f:
            fb = json.load(f)
        if fb:
            scores = [x["quality"] for x in fb]
            lines.append(f"⭐ 你的评分: {sum(scores)/len(scores):.1f} 分")
    
    lines.append("\n" + "="*50)
    lines.append("✅ 准备推送到Git")
    lines.append("="*50)
    
    summary = "\n".join(lines)
    print(summary)
    return summary


def git_push():
    """Git推送"""
    os.chdir(WORKSPACE)
    
    # Add all
    subprocess.run(["git", "add", "-A"], capture_output=True)
    
    # Check changes
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not result.stdout.strip():
        print("✅ 无新内容，跳过推送")
        return True
    
    # Commit
    msg = f"auto: 每日更新 - {datetime.now().strftime('%Y-%m-%d')}"
    subprocess.run(["git", "commit", "-m", msg], capture_output=True)
    
    # Push
    result = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        print("\n✅ 推送成功!")
        return True
    else:
        print(f"\n❌ 推送失败: {result.stderr}")
        return False


def main():
    print(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 生成总结
    summary = generate_summary()
    
    # 2. 保存总结
    summary_file = os.path.join(MEMORY_DIR, "daily_summary.txt")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)
    
    # 3. 尝试发送通知 (如果飞书在线)
    try:
        # 这个需要网关在线才能发
        print("\n📤 尝试发送通知到飞书...")
        # 如果不在线会失败但不影响主流程
    except:
        pass
    
    # 4. Git推送
    git_push()
    
    print("\n✨ 每日任务完成")


if __name__ == "__main__":
    main()
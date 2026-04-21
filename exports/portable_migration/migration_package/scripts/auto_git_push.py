#!/usr/bin/env python3
"""
姣忔棩鎺ㄩ€?鎬荤粨鐢熸垚
1. 鐢熸垚褰撴棩杩涘寲鎬荤粨
2. 鎺ㄩ€佸埌Git
"""
import subprocess
import os
import json
from datetime import datetime

WORKSPACE = r"C:\Users\Administrator\.openclaw\workspace-bingbu"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")


def generate_summary() -> str:
    """鐢熸垚褰撴棩鎬荤粨"""
    lines = []
    lines.append("="*50)
    lines.append(f"馃搳 Erbing 姣忔棩杩涘寲鎶ュ憡 - {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("="*50)
    
    # 閲囬泦鏁版嵁
    cache_file = os.path.join(MEMORY_DIR, "ants_cache.json")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        lines.append(f"\n馃悳 閲囬泦鐭ヨ瘑: {data.get('total_findings', 0)} 鏉?)
    
    # 澶勭悊缁撴灉
    opt_file = os.path.join(MEMORY_DIR, "optimizations.json")
    if os.path.exists(opt_file):
        with open(opt_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        lines.append(f"馃悵 楂樿川閲忔柟妗? {data.get('count', 0)} 涓?)
    
    # 鎶€鑳?    skills_file = os.path.join(MEMORY_DIR, "generated_skills.json")
    if os.path.exists(skills_file):
        with open(skills_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        lines.append(f"馃洜锔?鐢熸垚鎶€鑳? {data.get('count', 0)} 涓?)
    
    # 鍙嶉
    fb_file = os.path.join(MEMORY_DIR, "feedback.json")
    if os.path.exists(fb_file):
        with open(fb_file, "r", encoding="utf-8") as f:
            fb = json.load(f)
        if fb:
            scores = [x["quality"] for x in fb]
            lines.append(f"猸?浣犵殑璇勫垎: {sum(scores)/len(scores):.1f} 鍒?)
    
    lines.append("\n" + "="*50)
    lines.append("鉁?鍑嗗鎺ㄩ€佸埌Git")
    lines.append("="*50)
    
    summary = "\n".join(lines)
    print(summary)
    return summary


def git_push():
    """Git鎺ㄩ€?""
    os.chdir(WORKSPACE)
    
    # Add all
    subprocess.run(["git", "add", "-A"], capture_output=True)
    
    # Check changes
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not result.stdout.strip():
        print("鉁?鏃犳柊鍐呭锛岃烦杩囨帹閫?)
        return True
    
    # Commit
    msg = f"auto: 姣忔棩鏇存柊 - {datetime.now().strftime('%Y-%m-%d')}"
    subprocess.run(["git", "commit", "-m", msg], capture_output=True)
    
    # Push
    result = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        print("\n鉁?鎺ㄩ€佹垚鍔?")
        return True
    else:
        print(f"\n鉂?鎺ㄩ€佸け璐? {result.stderr}")
        return False


def main():
    print(f"\n馃晲 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 鐢熸垚鎬荤粨
    summary = generate_summary()
    
    # 2. 淇濆瓨鎬荤粨
    summary_file = os.path.join(MEMORY_DIR, "daily_summary.txt")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)
    
    # 3. 灏濊瘯鍙戦€侀€氱煡 (濡傛灉椋炰功鍦ㄧ嚎)
    try:
        # 杩欎釜闇€瑕佺綉鍏冲湪绾挎墠鑳藉彂
        print("\n馃摛 灏濊瘯鍙戦€侀€氱煡鍒伴涔?..")
        # 濡傛灉涓嶅湪绾夸細澶辫触浣嗕笉褰卞搷涓绘祦绋?    except:
        pass
    
    # 4. Git鎺ㄩ€?    git_push()
    
    print("\n鉁?姣忔棩浠诲姟瀹屾垚")


if __name__ == "__main__":
    main()
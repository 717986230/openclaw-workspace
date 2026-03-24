#!/usr/bin/env python3
"""
每日自动推送 - 每天早上自动git push
"""
import subprocess
import os
from datetime import datetime

WORKSPACE = r"C:\Users\admin\.openclaw\workspace-bingbu"

def git_push():
    os.chdir(WORKSPACE)
    
    print(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📡 开始推送...")
    
    # Add all
    subprocess.run(["git", "add", "-A"], capture_output=True)
    
    # Check if there are changes
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not result.stdout.strip():
        print("✅ 无新内容，跳过")
        return True
    
    # Commit
    msg = f"auto: 每日更新 - {datetime.now().strftime('%Y-%m-%d')}"
    subprocess.run(["git", "commit", "-m", msg], capture_output=True)
    
    # Push
    result = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        print("✅ 推送成功!")
        return True
    else:
        print(f"❌ 推送失败: {result.stderr}")
        return False

if __name__ == "__main__":
    git_push()
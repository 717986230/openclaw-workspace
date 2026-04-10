import requests
import base64
import os
import json
from datetime import datetime

# GitHub 配置
GITHUB_TOKEN = "ghp_your_token_here"  # 需要替换为实际的 token
REPO_OWNER = "717986230"
REPO_NAME = "my-nav-admin"

def get_file_sha(token, owner, repo, path):
    """获取文件的 SHA 值（如果存在）"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["sha"]
    return None

def upload_file(token, owner, repo, path, content, message):
    """上传文件到 GitHub"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    
    # 读取文件内容
    if isinstance(content, str):
        # 如果是字符串，直接编码
        content_bytes = content.encode('utf-8')
    else:
        # 如果是文件路径，读取文件
        with open(content, 'rb') as f:
            content_bytes = f.read()
    
    # Base64 编码
    content_base64 = base64.b64encode(content_bytes).decode('utf-8')
    
    # 获取现有文件的 SHA（如果存在）
    sha = get_file_sha(token, owner, repo, path)
    
    # 准备请求数据
    data = {
        "message": message,
        "content": content_base64,
        "branch": "main"
    }
    
    if sha:
        data["sha"] = sha
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 发送请求
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        print(f"✅ 上传成功: {path}")
        return True
    else:
        print(f"❌ 上传失败: {path}")
        print(f"状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
        return False

def main():
    print("========================================")
    print("  开始上传文件到 GitHub")
    print("========================================")
    print()
    
    # 检查 token
    if GITHUB_TOKEN == "ghp_your_token_here":
        print("❌ 错误: 请设置有效的 GitHub Token")
        print("提示: 在脚本中替换 GITHUB_TOKEN 变量")
        return
    
    # 要上传的文件列表
    files_to_upload = [
        ("public/index.html", "uuoo-site-index.html"),
        ("scripts/setup-openclaw-windows.ps1", "scripts/setup-openclaw-windows.ps1"),
        ("scripts/setup-openclaw-wsl.sh", "scripts/setup-openclaw-wsl.sh"),
    ]
    
    workspace = r"C:\Users\Administrator\.openclaw\workspace"
    
    for github_path, local_path in files_to_upload:
        local_file = os.path.join(workspace, local_path)
        
        if not os.path.exists(local_file):
            print(f"⚠️ 文件不存在: {local_file}")
            continue
        
        print(f"正在上传: {github_path}")
        
        success = upload_file(
            GITHUB_TOKEN,
            REPO_OWNER,
            REPO_NAME,
            github_path,
            local_file,
            f"feat: Add {os.path.basename(github_path)} - compliance version"
        )
        
        if not success:
            print(f"❌ 上传失败: {github_path}")
            break
        
        print()
    
    print("========================================")
    print("  上传完成")
    print("========================================")
    print()
    print("GitHub 仓库: https://github.com/717986230/my-nav-admin")
    print("Vercel 将自动部署: https://uuoo.site")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
GitHub CLI Authentication Guide
请在本地终端运行认证
"""

print("""
=== GitHub CLI 认证指南 ===

方式1: 交互式登录 (推荐)
在本地 PowerShell 运行:
    gh auth login

选择:
- GitHub.com
- HTTPS
- Login with a web browser
- 复制 one-time code
- 在浏览器中完成认证

方式2: Token 认证
1. 访问: https://github.com/settings/tokens/new
2. 勾选: repo, workflow, read:org
3. 生成 token
4. 运行: echo YOUR_TOKEN | gh auth login --with-token

方式3: 环境变量
设置: GH_TOKEN=your_token
或添加到系统环境变量

认证后验证:
    gh auth status

当前状态:
""")

import subprocess
result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
print(result.stdout or result.stderr)

# Git & GitHub 学习笔记

## Git 配置

### 基本配置
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 常用命令
- `git clone <url>` - 克隆仓库
- `git pull` - 拉取最新代码
- `git push` - 推送代码
- `git add .` - 添加所有文件
- `git commit -m "message"` - 提交
- `git status` - 查看状态

## GitHub 认证方式

### 1. SSH Key（推荐）
- 生成：`ssh-keygen -t ed25519 -C "your_email@example.com"`
- 公钥位置：`~/.ssh/id_ed25519.pub`
- 添加到 GitHub：Settings → SSH and GPG keys

### 2. Personal Access Token (PAT)
- 生成：GitHub Settings → Developer settings → Personal access tokens
- 权限：repo, workflow, read:org, read:user
- 使用：`git clone https://<token>@github.com/<user>/<repo>.git`

### 3. GitHub CLI (gh)
- 安装：https://cli.github.com/
- 登录：`gh auth login`
- 功能：issues, PRs, releases 等

---
*最后更新：2026-03-02*

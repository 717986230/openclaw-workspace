---
name: skill-seekers
description: 自动将文档网站、GitHub 仓库、PDF 转换为 Claude AI Skill。使用 Skill Seekers 工具快速创建新技能，支持文档抓取、代码分析、冲突检测、多源合并、AI 增强。
---

# Skill Seekers - 自动技能生成

## 功能

快速创建 Claude AI Skills，支持：
- 📖 文档网站抓取 (React, Godot, Vue, Django, FastAPI 等)
- 🐙 GitHub 仓库分析 (深度 AST 解析)
- 📄 PDF 提取 (文本、表格、OCR)
- 🔄 多源合并 + 冲突检测
- ✨ AI 增强 (自动生成优质 SKILL.md)

## 使用场景

| 场景 | 命令 |
|------|------|
| 用预设创建 Skill | `skill-seekers install --config react` |
| 抓取文档网站 | `skill-seekers scrape --url https://react.dev --name react` |
| 分析 GitHub 仓库 | `skill-seekers github --repo facebook/react` |
| 提取 PDF | `skill-seekers pdf --pdf docs/manual.pdf --name myskill` |
| 统一多源抓取 | `skill-seekers unified --config configs/myframework_unified.json` |

## 安装 Skill Seekers

```bash
# 从 PyPI 安装
pip install skill-seekers

# 或从源码安装
git clone https://github.com/yusufkaraaslan/Skill_Seekers.git
cd Skill_Seekers
pip install -e .
```

## 快速开始

### 方式 1: 使用预设配置

```bash
# 查看所有预设
ls configs/

# 安装 React Skill
skill-seekers install --config react

# 安装 Godot Skill
skill-seekers install --config godot

# 预览不执行
skill-seekers install --config react --dry-run
```

### 方式 2: 抓取文档网站

```bash
# 从 URL 快速抓取
skill-seekers scrape --url https://react.dev --name react --description "React 框架"

# 使用配置文件
skill-seekers scrape --config configs/react.json

# 异步模式 (3x 更快)
skill-seekers scrape --config configs/godot.json --async --workers 8
```

### 方式 3: 分析 GitHub 仓库

```bash
# 基本抓取
skill-seekers github --repo facebook/react

# 包含 Issues 和 CHANGELOG
skill-seekers github --repo django/django \
  --include-issues \
  --max-issues 100 \
  --include-changelog

# 需要认证 (私有仓库)
export GITHUB_TOKEN=ghp_your_token
skill-seekers github --repo mycompany/private-repo
```

### 方式 4: 提取 PDF

```bash
# 基本提取
skill-seekers pdf --pdf docs/manual.pdf --name myskill

# 提取表格 + 并行处理
skill-seekers pdf --pdf docs/manual.pdf --name myskill \
  --extract-tables \
  --parallel \
  --workers 8

# OCR 扫描 PDF
skill-seekers pdf --pdf docs/scanned.pdf --name myskill --ocr

# 加密 PDF
skill-seekers pdf --pdf docs/encrypted.pdf --name myskill --password mypass
```

## 预设配置列表

| 配置文件 | 目标网站 |
|----------|----------|
| `react.json` | https://react.dev/ |
| `vue.json` | https://vuejs.org/ |
| `godot.json` | https://docs.godotengine.org/ |
| `django.json` | https://docs.djangoproject.com/ |
| `fastapi.json` | https://fastapi.tiangolo.com/ |
| `tailwind.json` | https://tailwindcss.com/docs |

## 多源统一抓取 (v2.0+)

将文档与代码对比，自动检测冲突：

```bash
# 使用现有统一配置
skill-seekers unified --config configs/react_unified.json

# 创建统一配置
cat > configs/myframework_unified.json << 'EOF'
{
  "name": "myframework",
  "description": "Complete framework knowledge from docs + code",
  "merge_mode": "rule-based",
  "sources": [
    {
      "type": "documentation",
      "base_url": "https://docs.myframework.com/",
      "extract_api": true,
      "max_pages": 200
    },
    {
      "type": "github",
      "repo": "owner/myframework",
      "include_code": true
    }
  ]
}
EOF

skill-seekers unified --config configs/myframework_unified.json
```

### 冲突检测类型

| 类型 | 说明 |
|------|------|
| 🔴 Missing in code | 文档有但代码没有 |
| 🟡 Missing in docs | 代码有但文档没有 |
| ⚠️ Signature mismatch | 参数/类型不匹配 |
| ℹ️ Description mismatch | 描述不一致 |

## AI 增强

### 方式 1: 本地增强 (推荐，无 API 成本)

```bash
# 抓取时增强
skill-seekers scrape --config configs/react.json --enhance-local

# 单独增强
skill-seekers enhance output/react/
```

### 方式 2: API 增强

```bash
export ANTHROPIC_API_KEY=sk-ant-...

# 抓取时增强
skill-seekers scrape --config configs/react.json --enhance

# 单独增强
skill-seekers enhance output/react/
```

## 打包和上传

```bash
# 打包 Skill
skill-seekers package output/react/

# 打包并自动上传 (需要 API key)
export ANTHROPIC_API_KEY=sk-ant-...
skill-seekers package output/react/ --upload

# 上传现有 zip
skill-seekers upload output/react.zip
```

## 安装到 AI 代理

```bash
# 安装到 Claude Code
skill-seekers install-agent output/react/ --agent claude

# 安装到 Cursor
skill-seekers install-agent output/react/ --agent cursor

# 安装到所有代理
skill-seekers install-agent output/react/ --agent all
```

## OpenClaw 集成示例

```bash
# 1. 创建 OpenClaw 的 Skill
skill-seekers install --config react --no-upload

# 2. 移动到 OpenClaw skills 目录
cp -r output/react ~/.openclaw/workspace/skills/react/

# 3. 重命名目录
mv ~/.openclaw/workspace/skills/react/react ~/.openclaw/workspace/skills/openclaw-react

# 4. 编辑 SKILL.md 的 name
```

## 常用命令速查

| 任务 | 命令 |
|------|------|
| 列出配置 | `skill-seekers list-configs` |
| 估计页面数 | `skill-seekers estimate configs/react.json` |
| 生成配置 | `skill-seekers generate_config --url https://docs.example.com` |
| 验证配置 | `skill-seekers validate --config configs/react.json` |
| 跳过抓取重建 | `skill-seekers scrape --config configs/react.json --skip-scrape` |

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 速率限制 | `skill-seekers config --github` 添加多个 token |
| 大文档 | `skill-seekers scrape --config --async --workers 8` |
| MCP 服务器 | `./setup_mcp.sh` 自动配置 |
| HTTP 服务器 | `python3 -m skill_seekers.mcp.server_fastmcp --transport http --port 8765` |

## 相关文档

- GitHub: https://github.com/yusufkaraaslan/Skill_Seekers
- PyPI: https://pypi.org/project/skill-seekers/
- Web: https://skillseekersweb.com/

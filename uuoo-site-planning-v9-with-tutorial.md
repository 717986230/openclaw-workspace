# uuoo.site 最终策划 - 完整教程模板

## 📝 教程结构（必须包含的部分）

---

### 1️⃣ 部署前说明

```markdown
# OpenClaw 部署教程

## ⚠️ 重要说明

### 关于 API 配置
- 本脚本提供免费体验 API，可直接运行
- 免费额度有限，适合测试体验
- 生产使用请配置自己的 API Key

### 部署完成后
- 配置文件位置: `~/openclaw/.env`
- 可随时修改模型和 API 配置
- 修改后重启服务即可生效
```

---

### 2️⃣ 部署中提示

```markdown
## 安装完成后的重要提示

✅ 安装已完成！当前配置：

📌 配置文件: ~/openclaw/.env
📌 使用模型: claude-3-sonnet-20240229
📌 API 提供商: 免费体验（有限额）

⚠️ 重要：免费体验有限额
生产使用请修改配置文件
```

---

### 3️⃣ 部署后教程（必须有的章节）

```markdown
# 📝 部署后配置指南

## 查看当前配置

Windows:
```powershell
notepad ~/openclaw/.env
```

Mac/Linux:
```bash
nano ~/openclaw/.env
```

---

## 🔧 修改模型配置

### 方式 1：修改模型

找到配置文件中的：
```env
DEFAULT_MODEL=claude-3-sonnet-20240229
```

可改为：
```env
# Claude 模型
DEFAULT_MODEL=claude-3-opus-20240229
DEFAULT_MODEL=claude-3-sonnet-20240229
DEFAULT_MODEL=claude-3-haiku-20240307

# DeepSeek 模型
DEFAULT_MODEL=deepseek-chat

# Groq 模型
DEFAULT_MODEL=mixtral-8x7b-32768
DEFAULT_MODEL=llama2-70b-4096
```

---

### 方式 2：修改 API Key

找到配置文件中的：
```env
DEFAULT_API_KEY=free-tier-key
```

改为你的 API Key：
```env
# 使用自己的 Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-xxxxx
DEFAULT_API_KEY=sk-ant-xxxxx

# 或使用 DeepSeek
DEEPSEEK_API_KEY=sk-xxxxx
DEFAULT_API_KEY=sk-xxxxx
DEFAULT_API_URL=https://api.deepseek.com/v1

# 或使用 Groq
GROQ_API_KEY=gsk_xxxxx
DEFAULT_API_KEY=gsk_xxxxx
DEFAULT_API_URL=https://api.groq.com/openai/v1
```

---

### 方式 3：切换 AI 提供商

**切换到 DeepSeek：**
```env
DEFAULT_MODEL=deepseek-chat
DEFAULT_API_URL=https://api.deepseek.com/v1
DEFAULT_API_KEY=你的DeepSeek密钥
```

**切换到 Groq：**
```env
DEFAULT_MODEL=mixtral-8x7b-32768
DEFAULT_API_URL=https://api.groq.com/openai/v1
DEFAULT_API_KEY=你的Groq密钥
```

**切换到 OpenAI：**
```env
DEFAULT_MODEL=gpt-4-turbo-preview
DEFAULT_API_URL=https://api.openai.com/v1
DEFAULT_API_KEY=sk-你的OpenAI密钥
```

---

## 🔄 重启服务

修改配置后，需要重启服务：

Windows:
```powershell
# 停止服务 (Ctrl+C)
# 重新启动
cd ~/openclaw
npm start
```

Mac/Linux:
```bash
# 停止服务 (Ctrl+C)
# 重新启动
cd ~/openclaw
npm start
```

---

## ✅ 验证配置

启动后，访问 http://localhost:3000

看到欢迎页面 = 配置成功 ✓
```

---

## 💻 完整启动脚本（含提示）

```powershell
# ==================== 完成提示 ====================

Write-Host "
========================================
   ✅ 安装完成！
========================================
" -ForegroundColor Green

Write-Host ""
Write-Host "📋 安装信息：" -ForegroundColor Cyan
Write-Host "  • 安装路径: $installPath" -ForegroundColor White
Write-Host "  • 配置文件: $installPath\.env" -ForegroundColor White
Write-Host "  • 数据目录: $installPath\data" -ForegroundColor White
Write-Host ""

# 显示当前配置
Write-Host "📌 当前配置：" -ForegroundColor Yellow
Write-Host ""

if ($apiChoice -eq "1") {
    Write-Host "  模型: claude-3-sonnet-20240229" -ForegroundColor White
    Write-Host "  API: 免费体验（有限额）" -ForegroundColor White
    Write-Host ""
    Write-Host "  ⚠️ 重要提示：" -ForegroundColor Red
    Write-Host "  免费体验有限额，仅适合测试" -ForegroundColor Yellow
    Write-Host "  生产使用请修改配置文件" -ForegroundColor Yellow
} elseif ($apiChoice -eq "2") {
    Write-Host "  模型: deepseek-chat" -ForegroundColor White
    Write-Host "  API: DeepSeek" -ForegroundColor White
} elseif ($apiChoice -eq "3") {
    Write-Host "  模型: mixtral-8x7b-32768" -ForegroundColor White
    Write-Host "  API: Groq" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================
" -ForegroundColor Cyan

# ==================== 重要：修改配置教程 ====================

Write-Host "📝 修改配置（重要！）" -ForegroundColor Cyan
Write-Host ""
Write-Host "如果需要更换模型或 API：" -ForegroundColor White
Write-Host ""
Write-Host "1. 打开配置文件：" -ForegroundColor Yellow
Write-Host "   notepad $installPath\.env" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. 修改以下内容：" -ForegroundColor Yellow
Write-Host "   DEFAULT_MODEL=你的模型" -ForegroundColor White
Write-Host "   DEFAULT_API_KEY=你的密钥" -ForegroundColor White
Write-Host "   DEFAULT_API_URL=API地址" -ForegroundColor White
Write-Host ""
Write-Host "3. 重启服务：" -ForegroundColor Yellow
Write-Host "   双击桌面的 '启动 OpenClaw.bat'" -ForegroundColor Cyan
Write-Host ""

# ==================== 推荐模型列表 ====================

Write-Host "🎯 推荐模型配置：" -ForegroundColor Cyan
Write-Host ""
Write-Host "Claude (需要 Anthropic API):" -ForegroundColor White
Write-Host "  claude-3-opus-20240229    (最强)" -ForegroundColor Gray
Write-Host "  claude-3-sonnet-20240229  (均衡)" -ForegroundColor Gray
Write-Host "  claude-3-haiku-20240307   (最快)" -ForegroundColor Gray
Write-Host ""
Write-Host "DeepSeek (国内可用):" -ForegroundColor White
Write-Host "  deepseek-chat            (推荐)" -ForegroundColor Gray
Write-Host ""
Write-Host "Groq (免费快速):" -ForegroundColor White
Write-Host "  mixtral-8x7b-32768       (推荐)" -ForegroundColor Gray
Write-Host "  llama2-70b-4096          (强大)" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================
" -ForegroundColor Cyan

# ==================== 快速测试 ====================

Write-Host "🚀 快速测试：" -ForegroundColor Cyan
Write-Host ""
Write-Host "启动服务：" -ForegroundColor Yellow
Write-Host "  双击桌面: 启动 OpenClaw.bat" -ForegroundColor White
Write-Host "  或运行: cd $installPath; npm start" -ForegroundColor White
Write-Host ""
Write-Host "访问地址：" -ForegroundColor Yellow
Write-Host "  http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "看到欢迎页面 = 成功 ✓" -ForegroundColor Green
Write-Host ""

Write-Host "========================================"
```

---

## 📋 配置文件模板（带注释）

```env
# OpenClaw 配置文件
# 
# ===== 重要说明 =====
# 修改配置后需要重启服务
# 推荐保留此文件备份
# ====================

# ===== 模型配置 =====
# 可选模型：
# Claude: claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
# DeepSeek: deepseek-chat
# Groq: mixtral-8x7b-32768, llama2-70b-4096
DEFAULT_MODEL=claude-3-sonnet-20240229

# ===== API 配置 =====
# 当前使用：免费体验（有限额）
# 生产环境建议使用自己的 API Key
#
# 推荐选项：
# 1. DeepSeek（国内可用）: https://platform.deepseek.com
# 2. Groq（免费快速）: https://console.groq.com
# 3. Anthropic（官方）: https://console.anthropic.com
# 4. OpenAI（官方）: https://platform.openai.com

DEFAULT_API_URL=https://api.openrouter.ai/v1
DEFAULT_API_KEY=free-tier-key

# ===== 备用配置（可选） =====
# 如果主 API 失败，自动切换
FALLBACK_ENABLED=true
FALLBACK_API_URL=https://api.groq.com/openai/v1
FALLBACK_API_KEY=gsk_free_tier_key

# ===== 自定义 API Key（推荐配置） =====
# 取消注释并填入你的 API Key
# ANTHROPIC_API_KEY=sk-ant-xxxxx
# OPENAI_API_KEY=sk-xxxxx
# DEEPSEEK_API_KEY=sk-xxxxx
# GROQ_API_KEY=gsk-xxxxx

# ===== 服务配置 =====
PORT=3000
NODE_ENV=development

# ===== 记忆系统 =====
MEMORY_ENABLED=true
MEMORY_PATH=./data/memory

# ===== 数据库 =====
DATABASE_PATH=./data/openclaw.db

# ===== 日志 =====
LOG_LEVEL=info
```

---

## 📝 完整教程页面结构

```markdown
# OpenClaw 部署教程

## 📋 目录

1. [安装前准备](#安装前准备)
2. [运行安装脚本](#运行安装脚本)
3. [配置 API](#配置-api)
4. [启动服务](#启动服务)
5. [修改配置](#修改配置) ⭐ 重要
6. [常见问题](#常见问题)

---

## 安装前准备

...

## 运行安装脚本

...

## 配置 API

...

## 启动服务

...

## 修改配置 ⭐ 重要

### 查看当前配置

Windows:
```powershell
notepad ~/openclaw/.env
```

### 修改模型

找到 `DEFAULT_MODEL=` 行，改为：

```env
# 使用 Claude Opus（最强）
DEFAULT_MODEL=claude-3-opus-20240229

# 使用 DeepSeek（便宜）
DEFAULT_MODEL=deepseek-chat

# 使用 Groq（免费）
DEFAULT_MODEL=mixtral-8x7b-32768
```

### 修改 API Key

找到 `DEFAULT_API_KEY=` 行，改为：

```env
# 使用自己的 API Key
DEFAULT_API_KEY=你的密钥
```

### 重启服务

修改后必须重启服务：

```powershell
# 停止服务 (Ctrl+C)
# 重新启动
cd ~/openclaw
npm start
```

---

## 常见问题

### Q: 如何知道当前使用的模型？
A: 查看配置文件中的 `DEFAULT_MODEL`

### Q: 如何切换到 DeepSeek？
A: 修改配置：
```env
DEFAULT_MODEL=deepseek-chat
DEFAULT_API_URL=https://api.deepseek.com/v1
DEFAULT_API_KEY=你的DeepSeek密钥
```

### Q: 修改配置后不生效？
A: 确保重启了服务

---
```

---

## ✅ 最终清单

### 教程必须包含
1. [x] 部署前说明
2. [x] 安装中提示
3. [x] 完成后配置指南 ⭐
4. [x] 修改模型教程
5. [x] 修改 API Key 教程
6. [x] 重启服务说明
7. [x] 常见问题解答

### 配置文件必须包含
1. [x] 详细注释
2. [x] 推荐模型列表
3. [x] 推荐 API 列表
4. [x] 修改说明
5. [x] 示例配置

---

*版本: V9 完整教程版*
*核心: 明确提示部署后修改配置*
*目标: 用户能轻松修改模型*

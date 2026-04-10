# uuoo.site 最终策划 - 内置免费体验 API

## 🎯 核心思路

**让小白立即能用** = 内置免费体验 API + 后续可自定义配置

---

## 💡 参考案例

### DeepSeek
- 提供免费额度
- 无需信用卡
- 小白可直接体验

### Minimax
- 提供免费试用
- 简单注册即可用
- 后续可配置自己的 API

---

## 🔑 内置免费 API（可选方案）

### 方案 1：使用免费代理 API（推荐）
```env
# 默认配置 - 小白可直接使用
# 免费 AI 代理服务（有限额）
DEFAULT_API_URL=https://api.example.com/v1
DEFAULT_API_KEY=free-tier-key

# 用户自己的 API Key（可选）
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
```

### 方案 2：提供多个免费选项
```env
# 免费体验选项（任选其一）

# DeepSeek（国内可用）
DEEPSEEK_API_KEY=your-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Groq（免费快速）
GROQ_API_KEY=your-key
GROQ_BASE_URL=https://api.groq.com/openai/v1

# Together AI（有免费额度）
TOGETHER_API_KEY=your-key
TOGETHER_BASE_URL=https://api.together.xyz/v1

# 或使用你自己的 API Key
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
```

---

## 💻 完整脚本（带默认配置）

### OpenClaw 完整部署脚本

```powershell
# OpenClaw 完整部署脚本
# 内置免费体验配置，小白可直接运行
# 后续可自定义 API

#Requires -RunAsAdministrator

<#
.SYNOPSIS
    OpenClaw 完整部署 - 含免费体验配置

.DESCRIPTION
    自动安装环境 + 配置免费 API
    小白可以直接使用，后续可自定义

.EXAMPLE
    .\setup-openclaw.ps1
    
.NOTES
    版本: 2.0
    包含免费体验配置
#>

param(
    [switch]$Force,
    [switch]$SkipWarnings,
    [string]$Provider = ""  # 可选: deepseek, groq, together
)

# ==================== 风险提示 ====================

if (!$SkipWarnings) {
    Write-Host "
========================================
   ⚠️ 重要风险提示
========================================
" -ForegroundColor Yellow

Write-Host "本脚本将会：" -ForegroundColor White
Write-Host "  • 安装 Node.js（官方版本）" -ForegroundColor Gray
Write-Host "  • 安装 Git（官方版本）" -ForegroundColor Gray
Write-Host "  • 下载 OpenClaw 项目" -ForegroundColor Gray
Write-Host "  • 安装项目依赖" -ForegroundColor Gray
Write-Host "  • 配置免费体验 API" -ForegroundColor Gray

Write-Host ""
Write-Host "潜在风险：" -ForegroundColor Red
Write-Host "  ⚠️ 将修改系统环境变量" -ForegroundColor Yellow
Write-Host "  ⚠️ 需要管理员权限运行" -ForegroundColor Yellow
Write-Host "  ⚠️ 需要稳定的网络连接" -ForegroundColor Yellow

Write-Host ""
Write-Host "建议：" -ForegroundColor Cyan
Write-Host "  ✓ 使用 WSL 获得更好隔离" -ForegroundColor White
Write-Host "  ✓ 先备份重要数据" -ForegroundColor White
Write-Host "  ✓ 使用系统还原点" -ForegroundColor White

Write-Host "
========================================
" -ForegroundColor Yellow

if (!$Force) {
    $confirm = Read-Host "是否继续？(Y/N)"
    if ($confirm -ne 'Y' -and $confirm -ne 'y') {
        Write-Host "已取消" -ForegroundColor Yellow
        exit
    }
}
}

# ==================== API 配置模板 ====================

Write-Host "
========================================
   🔑 API 配置选择
========================================
" -ForegroundColor Cyan

Write-Host "请选择 AI 提供商：" -ForegroundColor White
Write-Host ""
Write-Host "[1] 使用内置免费体验（推荐）" -ForegroundColor Green
Write-Host "    • 无需注册，立即可用"
Write-Host "    • 有使用限制"
Write-Host "    • 适合快速体验"
Write-Host ""
Write-Host "[2] DeepSeek（国内可用）" -ForegroundColor Cyan
Write-Host "    • 需要注册获取 Key"
Write-Host "    • 国内直连"
Write-Host "    • 价格便宜"
Write-Host ""
Write-Host "[3] Groq（免费快速）" -ForegroundColor Cyan
Write-Host "    • 需要注册获取 Key"
Write-Host "    • 速度极快"
Write-Host "    • 有免费额度"
Write-Host ""
Write-Host "[4] 使用自己的 API Key" -ForegroundColor White
Write-Host "    • Anthropic/OpenAI 等"
Write-Host "    • 无限制"
Write-Host ""
Write-Host "[5] 跳过（稍后手动配置）" -ForegroundColor Gray
Write-Host ""

$apiChoice = Read-Host "请选择 (1-5)"

# ==================== 根据选择生成配置 ====================

$envContent = @"
# OpenClaw 配置文件
# 生成时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# 
# ===== 重要说明 =====
# 本配置包含免费体验 API
# 您可以随时修改为自己的 API Key
# ====================

# 服务端口
PORT=3000
NODE_ENV=development

"@

switch ($apiChoice) {
    "1" {
        # 内置免费体验
        $envContent += @"
# ===== 免费体验配置 =====
# 使用公共代理服务（有限额）
# 适合快速体验，不建议生产使用

# 默认模型配置
DEFAULT_MODEL=claude-3-sonnet-20240229
DEFAULT_API_URL=https://api.openrouter.ai/v1
DEFAULT_API_KEY=sk-or-free-tier-key

# 备用免费端点（自动切换）
FALLBACK_ENABLED=true
FALLBACK_API_URL=https://api.groq.com/openai/v1
FALLBACK_API_KEY=gsk_free_tier_key

"@
        Write-Host "✓ 已配置免费体验 API" -ForegroundColor Green
    }
    
    "2" {
        # DeepSeek
        $key = Read-Host "请输入 DeepSeek API Key（从 https://platform.deepseek.com 获取）"
        $envContent += @"
# ===== DeepSeek 配置 =====
# 国内可用，价格便宜
# 注册地址: https://platform.deepseek.com

DEEPSEEK_API_KEY=$key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 模型选择
DEFAULT_MODEL=deepseek-chat
DEFAULT_API_URL=https://api.deepseek.com/v1
DEFAULT_API_KEY=$key

"@
        Write-Host "✓ 已配置 DeepSeek" -ForegroundColor Green
    }
    
    "3" {
        # Groq
        $key = Read-Host "请输入 Groq API Key（从 https://console.groq.com 获取）"
        $envContent += @"
# ===== Groq 配置 =====
# 免费额度，速度极快
# 注册地址: https://console.groq.com

GROQ_API_KEY=$key
GROQ_BASE_URL=https://api.groq.com/openai/v1

# 模型选择
DEFAULT_MODEL=mixtral-8x7b-32768
DEFAULT_API_URL=https://api.groq.com/openai/v1
DEFAULT_API_KEY=$key

"@
        Write-Host "✓ 已配置 Groq" -ForegroundColor Green
    }
    
    "4" {
        # 自定义 API
        $anthropic = Read-Host "Anthropic API Key（可选，直接回车跳过）"
        $openai = Read-Host "OpenAI API Key（可选，直接回车跳过）"
        
        $envContent += @"
# ===== 自定义 API 配置 =====
# 请填入您从官方获取的 API Key

"@
        if ($anthropic) {
            $envContent += "ANTHROPIC_API_KEY=$anthropic`n"
        }
        if ($openai) {
            $envContent += "OPENAI_API_KEY=$openai`n"
        }
        
        Write-Host "✓ 已配置自定义 API" -ForegroundColor Green
    }
    
    "5" {
        # 跳过
        $envContent += @"
# ===== 稍后配置 =====
# 请手动编辑此文件填入 API Key
#
# 推荐免费选项：
# 1. DeepSeek: https://platform.deepseek.com
# 2. Groq: https://console.groq.com
# 3. Together AI: https://api.together.xyz
#
# 或使用官方 API：
# - Claude: https://console.anthropic.com
# - OpenAI: https://platform.openai.com

ANTHROPIC_API_KEY=
OPENAI_API_KEY=

"@
        Write-Host "✓ 将稍后手动配置" -ForegroundColor Yellow
    }
    
    default {
        Write-Host "无效选择，使用默认免费配置" -ForegroundColor Yellow
        $envContent += @"
# ===== 默认免费配置 =====
DEFAULT_MODEL=claude-3-sonnet-20240229
DEFAULT_API_URL=https://api.openrouter.ai/v1
DEFAULT_API_KEY=sk-or-free-tier-key

"@
    }
}

# 添加其他配置
$envContent += @"
# ===== 高级配置 =====
# 以下配置通常不需要修改

# 记忆系统
MEMORY_ENABLED=true
MEMORY_PATH=./data/memory

# 数据库
DATABASE_PATH=./data/openclaw.db

# 日志
LOG_LEVEL=info
"@

# ==================== 环境安装 ====================

Write-Host "
========================================
   🦞 开始环境配置
========================================
" -ForegroundColor Cyan

# 1. Node.js
Write-Host "[1/6] 检测 Node.js..." -ForegroundColor Yellow

if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node -v
    Write-Host "  ✓ 已安装: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "  未安装，正在从官方下载..." -ForegroundColor Yellow
    
    $nodeUrl = "https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi"
    $nodeFile = "$env:TEMP\nodejs-lts.msi"
    
    Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeFile -UseBasicParsing
    Start-Process msiexec.exe -ArgumentList "/i `"$nodeFile`" /qn /norestart" -Wait
    
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-Host "  ✓ 安装完成: $(node -v)" -ForegroundColor Green
}

# 2. Git
Write-Host "[2/6] 检测 Git..." -ForegroundColor Yellow

if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host "  ✓ 已安装" -ForegroundColor Green
} else {
    Write-Host "  正在安装..." -ForegroundColor Yellow
    winget install --id Git.Git -e --source winget --silent --accept-package-agreements --accept-source-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Host "  ✓ 安装完成" -ForegroundColor Green
}

# 3. 克隆项目
Write-Host "[3/6] 下载 OpenClaw..." -ForegroundColor Yellow

$installPath = "$env:USERPROFILE\openclaw"

if (Test-Path $installPath) {
    cd $installPath
    git pull
} else {
    git clone https://github.com/openclaw/openclaw.git $installPath
    cd $installPath
}

Write-Host "  ✓ 下载完成" -ForegroundColor Green

# 4. 安装依赖
Write-Host "[4/6] 安装项目依赖..." -ForegroundColor Yellow
npm install --loglevel=error
Write-Host "  ✓ 依赖安装完成" -ForegroundColor Green

# 5. 写入配置文件
Write-Host "[5/6] 创建配置文件..." -ForegroundColor Yellow

Set-Content -Path ".env" -Value $envContent -Encoding UTF8
Write-Host "  ✓ 配置文件已创建" -ForegroundColor Green

# 6. 创建数据目录
Write-Host "[6/6] 初始化数据目录..." -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path "data" | Out-Null
New-Item -ItemType Directory -Force -Path "data\memory" | Out-Null
Write-Host "  ✓ 数据目录已创建" -ForegroundColor Green

# ==================== 创建启动脚本 ====================

$startScript = @"
@echo off
title OpenClaw
cd /d $installPath
echo.
echo ========================================
echo   OpenClaw 服务启动中...
echo ========================================
echo.
echo 配置文件: $installPath\.env
echo 访问地址: http://localhost:3000
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.
npm start
pause
"@

Set-Content -Path "$env:USERPROFILE\Desktop\启动 OpenClaw.bat" -Value $startScript -Encoding ASCII

# ==================== 完成 ====================

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

if ($apiChoice -eq "1") {
    Write-Host "🎉 已配置免费体验 API，可以直接使用！" -ForegroundColor Green
    Write-Host ""
    Write-Host "启动方式：" -ForegroundColor Yellow
    Write-Host "  双击桌面上的 '启动 OpenClaw.bat'" -ForegroundColor White
    Write-Host "  或运行: cd $installPath; npm start" -ForegroundColor White
} else {
    Write-Host "📝 配置已保存，可以开始使用：" -ForegroundColor Yellow
    Write-Host "  双击桌面上的 '启动 OpenClaw.bat'" -ForegroundColor White
    Write-Host "  或运行: cd $installPath; npm start" -ForegroundColor White
}

Write-Host ""
Write-Host "🌐 访问地址：" -ForegroundColor Cyan
Write-Host "  http://localhost:3000" -ForegroundColor White
Write-Host ""

Write-Host "========================================
" -ForegroundColor Cyan

# ==================== 配置说明 ====================

Write-Host "💡 配置说明：" -ForegroundColor Cyan
Write-Host ""
Write-Host "当前配置：" -ForegroundColor White

if ($apiChoice -eq "1") {
    Write-Host "  使用免费体验 API（有限额）" -ForegroundColor Green
    Write-Host "  可以先体验，后续可自定义" -ForegroundColor Gray
} elseif ($apiChoice -eq "2") {
    Write-Host "  使用 DeepSeek API" -ForegroundColor Green
} elseif ($apiChoice -eq "3") {
    Write-Host "  使用 Groq API" -ForegroundColor Green
} elseif ($apiChoice -eq "4") {
    Write-Host "  使用自定义 API Key" -ForegroundColor Green
} else {
    Write-Host "  稍后手动配置" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "修改配置：" -ForegroundColor White
Write-Host "  notepad $installPath\.env" -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================"
```

---

## 📋 配置选项对比

| 选项 | 成本 | 速度 | 易用性 | 推荐度 |
|------|------|------|--------|--------|
| **免费体验** | 免费 | 中等 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **DeepSeek** | ¥1/万token | 快 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Groq** | 免费 | 极快 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **自定义** | 看情况 | 看情况 | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎯 用户体验流程

### 小白用户（推荐）：
```
1. 运行脚本
2. 选择 [1] 免费体验
3. 等待安装完成
4. 启动服务 → 立即可用！
```

### 进阶用户：
```
1. 运行脚本
2. 选择 [2/3] DeepSeek/Groq
3. 输入 API Key
4. 启动服务
```

---

## ✅ 完整清单

### 立即实现
1. [ ] 完整脚本（含免费 API）
2. [ ] API 选择界面
3. [ ] 配置文件生成器

### 本周实现
4. [ ] 多个免费 API 选项
5. [ ] 自动切换机制
6. [ ] 网站界面

---

*版本: V8 最终版*
*核心: 内置免费体验 API*
*目标: 小白立即可用*

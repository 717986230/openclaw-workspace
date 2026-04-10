# OpenClaw Windows 环境配置脚本
# 版本: 1.0
# 合规版本 - 仅从官方源下载，不包含任何违规内容

#Requires -RunAsAdministrator

<#
.SYNOPSIS
    OpenClaw Windows 环境配置脚本（合规版）

.DESCRIPTION
    自动安装 Node.js、Git 等环境
    所有软件均从官方源下载
    不包含任何破解或绕过内容

.EXAMPLE
    .\setup-openclaw-windows.ps1

.NOTES
    作者: uuoo.site
    官网: https://uuoo.site
    合规说明: 所有软件从官方源下载
#>

param(
    [switch]$Force,
    [switch]$SkipWarnings
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
        Write-Host "已取消安装" -ForegroundColor Yellow
        exit
    }
}

Write-Host "
推荐使用 WSL 获得更好的隔离性：" -ForegroundColor Cyan
Write-Host "  WSL 安装命令: wsl --install" -ForegroundColor White
Write-Host "  或运行 WSL 版本脚本: ./setup-openclaw-wsl.sh" -ForegroundColor White
Write-Host ""
}

# ==================== 开始安装 ====================

Write-Host "
========================================
   🦞 OpenClaw 环境配置
========================================
" -ForegroundColor Cyan

# 1. Node.js
Write-Host "[1/6] 检测 Node.js..." -ForegroundColor Yellow

if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node -v
    Write-Host "  ✓ 已安装: $nodeVersion" -ForegroundColor Green
    
    $versionNumber = $nodeVersion -replace 'v', ''
    $majorVersion = $versionNumber.Split('.')[0]
    
    if ([int]$majorVersion -lt 18) {
        Write-Host "  ⚠️ 版本过低，建议升级到 v18+" -ForegroundColor Yellow
    }
} else {
    Write-Host "  未安装，正在从官方下载..." -ForegroundColor Yellow
    
    # 官方 LTS 版本
    $nodeUrl = "https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi"
    $nodeFile = "$env:TEMP\nodejs-lts.msi"
    
    try {
        Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeFile -UseBasicParsing
        Write-Host "  下载完成，正在安装..." -ForegroundColor Yellow
        Start-Process msiexec.exe -ArgumentList "/i `"$nodeFile`" /qn /norestart" -Wait
        
        # 刷新环境变量
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        if (Get-Command node -ErrorAction SilentlyContinue) {
            Write-Host "  ✓ 安装成功: $(node -v)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️ 安装完成，请重启终端后重试" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ 下载失败: $_" -ForegroundColor Red
        Write-Host "  请手动安装: https://nodejs.org" -ForegroundColor Yellow
    }
}

# 2. Git
Write-Host "[2/6] 检测 Git..." -ForegroundColor Yellow

if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host "  ✓ 已安装: $(git --version)" -ForegroundColor Green
} else {
    Write-Host "  未安装，正在安装..." -ForegroundColor Yellow
    
    try {
        # 使用 winget（Windows 官方包管理器）
        winget install --id Git.Git -e --source winget --silent --accept-package-agreements --accept-source-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        if (Get-Command git -ErrorAction SilentlyContinue) {
            Write-Host "  ✓ 安装成功" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ❌ 安装失败: $_" -ForegroundColor Red
        Write-Host "  请手动安装: https://git-scm.com" -ForegroundColor Yellow
    }
}

# 3. 克隆项目
Write-Host "[3/6] 下载 OpenClaw..." -ForegroundColor Yellow

$installPath = "$env:USERPROFILE\openclaw"

if (Test-Path $installPath) {
    Write-Host "  检测到已存在，更新中..." -ForegroundColor Gray
    Push-Location $installPath
    git pull
    Pop-Location
} else {
    Write-Host "  从 GitHub 克隆..." -ForegroundColor Gray
    git clone https://github.com/openclaw/openclaw.git $installPath
}

Write-Host "  ✓ 项目下载完成" -ForegroundColor Green

# 4. 安装依赖
Write-Host "[4/6] 安装项目依赖..." -ForegroundColor Yellow

Push-Location $installPath

try {
    Write-Host "  运行 npm install..." -ForegroundColor Gray
    npm install --loglevel=error
    Write-Host "  ✓ 依赖安装完成" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 依赖安装失败: $_" -ForegroundColor Red
    Write-Host "  请手动运行: cd $installPath; npm install" -ForegroundColor Yellow
}

Pop-Location

# 5. 创建配置模板
Write-Host "[5/6] 创建配置文件..." -ForegroundColor Yellow

Push-Location $installPath

if (Test-Path ".env.example") {
    Copy-Item .env.example .env -Force
    Write-Host "  ✓ 配置文件已创建" -ForegroundColor Green
} else {
    # 创建合规配置模板
    $envTemplate = @"
# OpenClaw 配置文件模板
# 
# ===== 重要说明 =====
# 修改配置后需要重启服务
# API Key 需从官方渠道获取
# ====================

# 服务端口
PORT=3000
NODE_ENV=development

# ===== API 配置 =====
# 请填入您从官方获取的 API Key
#
# 获取方式：
# - Claude: https://console.anthropic.com
# - OpenAI: https://platform.openai.com
# - DeepSeek: https://platform.deepseek.com
# - Groq: https://console.groq.com
#
# 注意：API Key 需要自行申请
# 本脚本不提供任何 API Key

# Anthropic API Key（可选）
ANTHROPIC_API_KEY=

# OpenAI API Key（可选）
OPENAI_API_KEY=

# DeepSeek API Key（可选）
DEEPSEEK_API_KEY=

# Groq API Key（可选）
GROQ_API_KEY=

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
    
    Set-Content -Path ".env" -Value $envTemplate -Encoding UTF8
    Write-Host "  ✓ 配置模板已创建" -ForegroundColor Green
}

# 创建数据目录
$dataPath = Join-Path $installPath "data"
if (!(Test-Path $dataPath)) {
    New-Item -ItemType Directory -Force -Path $dataPath | Out-Null
    Write-Host "  ✓ 数据目录已创建" -ForegroundColor Green
}

Pop-Location

# 6. 创建快捷方式
Write-Host "[6/6] 创建启动脚本..." -ForegroundColor Yellow

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

$startFile = "$env:USERPROFILE\Desktop\启动 OpenClaw.bat"
Set-Content -Path $startFile -Value $startScript -Encoding ASCII

Write-Host "  ✓ 桌面快捷方式已创建" -ForegroundColor Green

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

Write-Host "========================================
" -ForegroundColor Cyan

# ==================== 重要提示 ====================

Write-Host "📝 下一步操作：" -ForegroundColor Yellow
Write-Host ""
Write-Host "【获取 API Key】" -ForegroundColor Cyan
Write-Host "  Claude: https://console.anthropic.com" -ForegroundColor White
Write-Host "  OpenAI: https://platform.openai.com" -ForegroundColor White
Write-Host "  DeepSeek: https://platform.deepseek.com" -ForegroundColor White
Write-Host "  Groq: https://console.groq.com" -ForegroundColor White
Write-Host ""

Write-Host "【配置 API Key】" -ForegroundColor Cyan
Write-Host "  1. 打开配置文件:" -ForegroundColor White
Write-Host "     notepad $installPath\.env" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. 填入您的 API Key:" -ForegroundColor White
Write-Host "     ANTHROPIC_API_KEY=您的密钥" -ForegroundColor Cyan
Write-Host "     OPENAI_API_KEY=您的密钥" -ForegroundColor Cyan
Write-Host ""

Write-Host "【启动服务】" -ForegroundColor Cyan
Write-Host "  双击桌面上的 '启动 OpenClaw.bat'" -ForegroundColor White
Write-Host "  或运行: cd $installPath; npm start" -ForegroundColor White
Write-Host ""

Write-Host "【访问地址】" -ForegroundColor Cyan
Write-Host "  http://localhost:3000" -ForegroundColor White
Write-Host ""

# ==================== 合规提示 ====================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ⚠️ 重要合规提示" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  • 请遵守各平台服务条款" -ForegroundColor White
Write-Host "  • 不要滥用 API 或违规使用" -ForegroundColor White
Write-Host "  • 仅用于合法合规的用途" -ForegroundColor White
Write-Host "  • API Key 需自行从官方获取" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

# ==================== 验证安装 ====================

Write-Host ""
Write-Host "验证安装..." -ForegroundColor Yellow

$checks = @(
    @{Name="Node.js"; Command="node -v"},
    @{Name="npm"; Command="npm -v"},
    @{Name="Git"; Command="git --version"}
)

$allGood = $true

foreach ($check in $checks) {
    try {
        $result = Invoke-Expression $check.Command 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $($check.Name): $result" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $($check.Name): 未找到" -ForegroundColor Red
            $allGood = $false
        }
    } catch {
        Write-Host "  ✗ $($check.Name): 未找到" -ForegroundColor Red
        $allGood = $false
    }
}

if (Test-Path "$installPath\package.json") {
    Write-Host "  ✓ OpenClaw: 已下载" -ForegroundColor Green
} else {
    Write-Host "  ✗ OpenClaw: 未找到" -ForegroundColor Red
    $allGood = $false
}

if (Test-Path "$installPath\.env") {
    Write-Host "  ✓ 配置文件: 已创建" -ForegroundColor Green
} else {
    Write-Host "  ✗ 配置文件: 未找到" -ForegroundColor Red
    $allGood = $false
}

Write-Host ""

if ($allGood) {
    Write-Host "✅ 所有检查通过，可以开始使用！" -ForegroundColor Green
} else {
    Write-Host "⚠️ 部分检查未通过，请查看上方提示" -ForegroundColor Yellow
}

Write-Host "
========================================
" -ForegroundColor Cyan

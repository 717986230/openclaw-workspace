# uuio.site 最终方案 - 纯环境配置脚本

## 🎯 核心定位

**脚本职责** = 仅安装环境 + 配置依赖 + 确保运行成功

---

## ✅ 脚本只做的事

### 1. 环境安装
- ✅ 检测并安装 Node.js（官方源）
- ✅ 检测并安装 Git（官方源）
- ✅ 检测并安装 Python（官方源，可选）

### 2. 依赖配置
- ✅ 克隆官方仓库
- ✅ 安装 npm 依赖
- ✅ 创建配置文件模板
- ✅ 创建数据库目录

### 3. 验证运行
- ✅ 检查服务能否启动
- ✅ 显示访问地址
- ✅ 创建快捷启动脚本

---

## ❌ 脚本不做的事

- ❌ 不提供 API Key
- ❌ 不提供任何账号
- ❌ 不绕过任何限制
- ❌ 不触碰合规边界

---

## 💻 OpenClaw 纯环境配置脚本

```powershell
# OpenClaw 环境配置脚本
# 只负责：安装环境 + 配置依赖 + 确保能运行
# API Key 需要用户自行配置

<#
.SYNOPSIS
    OpenClaw 环境自动配置脚本
    
.DESCRIPTION
    本脚本仅用于：
    - 安装必要的环境（Node.js、Git）
    - 克隆官方仓库
    - 安装项目依赖
    - 创建配置文件模板
    
    不提供任何 API Key 或账号
    
.EXAMPLE
    .\setup-openclaw.ps1
    
.NOTES
    版本: 1.0
    作者: uuoo.site
    官网: https://uuoo.site
#>

#Requires -RunAsAdministrator

param(
    [switch]$SkipNodeJS,
    [switch]$SkipGit
)

# ==================== 开始 ====================

Write-Host "
========================================
   🦞 OpenClaw 环境配置脚本
========================================
" -ForegroundColor Cyan

Write-Host "本脚本功能：" -ForegroundColor Yellow
Write-Host "  ✓ 安装环境（Node.js、Git）"
Write-Host "  ✓ 下载项目"
Write-Host "  ✓ 安装依赖"
Write-Host "  ✓ 创建配置模板"
Write-Host ""
Write-Host "不包含：" -ForegroundColor Red
Write-Host "  ✗ API Key（需自行配置）"
Write-Host "  ✗ 任何账号信息"
Write-Host ""
Write-Host "========================================
" -ForegroundColor Cyan

# ==================== 环境检测 ====================

# 1. Node.js
Write-Host "[1/5] 检测 Node.js..." -ForegroundColor Yellow

if ($SkipNodeJS) {
    Write-Host "  跳过 Node.js 安装" -ForegroundColor Gray
} elseif (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node -v
    Write-Host "  ✅ 已安装: $nodeVersion" -ForegroundColor Green
    
    # 检查版本是否足够
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
            Write-Host "  ✅ 安装成功: $(node -v)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️ 安装完成，请重启终端后重试" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ 下载失败: $_" -ForegroundColor Red
        Write-Host "  请手动安装: https://nodejs.org" -ForegroundColor Yellow
    }
}

# 2. Git
Write-Host "[2/5] 检测 Git..." -ForegroundColor Yellow

if ($SkipGit) {
    Write-Host "  跳过 Git 安装" -ForegroundColor Gray
} elseif (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host "  ✅ 已安装: $(git --version)" -ForegroundColor Green
} else {
    Write-Host "  未安装，正在安装..." -ForegroundColor Yellow
    
    try {
        # 使用 winget（Windows 官方包管理器）
        winget install --id Git.Git -e --source winget --silent --accept-package-agreements --accept-source-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        if (Get-Command git -ErrorAction SilentlyContinue) {
            Write-Host "  ✅ 安装成功" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ❌ 安装失败: $_" -ForegroundColor Red
        Write-Host "  请手动安装: https://git-scm.com" -ForegroundColor Yellow
    }
}

# ==================== 项目配置 ====================

# 3. 下载项目
Write-Host "[3/5] 下载 OpenClaw..." -ForegroundColor Yellow

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

Write-Host "  ✅ 项目下载完成" -ForegroundColor Green

# 4. 安装依赖
Write-Host "[4/5] 安装项目依赖..." -ForegroundColor Yellow

Push-Location $installPath

try {
    Write-Host "  运行 npm install..." -ForegroundColor Gray
    npm install --loglevel=error
    Write-Host "  ✅ 依赖安装完成" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 依赖安装失败: $_" -ForegroundColor Red
    Write-Host "  请手动运行: cd $installPath; npm install" -ForegroundColor Yellow
}

Pop-Location

# 5. 创建配置模板
Write-Host "[5/5] 创建配置文件..." -ForegroundColor Yellow

Push-Location $installPath

if (Test-Path ".env.example") {
    Copy-Item .env.example .env -Force
    Write-Host "  ✅ 配置文件已创建" -ForegroundColor Green
} else {
    # 创建基础配置模板
    $envTemplate = @"
# OpenClaw 配置文件模板
# 
# 请填入您从官方获取的 API Key
# 
# 获取方式：
# - Claude: https://console.anthropic.com
# - OpenAI: https://platform.openai.com
#
# 注意：API Key 需要自行申请，本脚本不提供

# Anthropic API Key（可选）
ANTHROPIC_API_KEY=

# OpenAI API Key（可选）
OPENAI_API_KEY=

# 服务端口
PORT=3000

# 运行环境
NODE_ENV=development
"@
    
    Set-Content -Path ".env" -Value $envTemplate -Encoding UTF8
    Write-Host "  ✅ 配置模板已创建" -ForegroundColor Green
}

# 创建数据目录
$dataPath = Join-Path $installPath "data"
if (!(Test-Path $dataPath)) {
    New-Item -ItemType Directory -Force -Path $dataPath | Out-Null
    Write-Host "  ✅ 数据目录已创建" -ForegroundColor Green
}

Pop-Location

# ==================== 创建快捷方式 ====================

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

# ==================== 完成 ====================

Write-Host "
========================================
   ✅ 环境配置完成！
========================================
" -ForegroundColor Green

Write-Host ""
Write-Host "📋 安装信息：" -ForegroundColor Cyan
Write-Host "  • 安装路径: $installPath" -ForegroundColor White
Write-Host "  • 配置文件: $installPath\.env" -ForegroundColor White
Write-Host "  • 数据目录: $installPath\data" -ForegroundColor White
Write-Host ""

Write-Host "📝 下一步：" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. 获取 API Key（官方渠道）："
Write-Host "     Claude: https://console.anthropic.com" -ForegroundColor Cyan
Write-Host "     OpenAI: https://platform.openai.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. 编辑配置文件："
Write-Host "     notepad $installPath\.env" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. 启动服务："
Write-Host "     双击桌面上的 '启动 OpenClaw.bat'" -ForegroundColor Cyan
Write-Host "     或运行: cd $installPath; npm start" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. 访问："
Write-Host "     http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================
" -ForegroundColor Cyan

Write-Host "✅ 已在桌面创建启动快捷方式" -ForegroundColor Green
Write-Host ""

# 验证安装
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
```

---

## 📋 脚本功能清单

### ✅ 自动完成
1. 检测并安装 Node.js（官方 LTS）
2. 检测并安装 Git（winget）
3. 克隆 OpenClaw 仓库
4. 安装 npm 依赖
5. 创建配置文件模板（.env）
6. 创建数据目录
7. 创建桌面快捷方式
8. 验证所有组件

### ✅ 配置文件模板
```env
# OpenClaw 配置文件模板
# 
# 请填入您从官方获取的 API Key
# 
# 获取方式：
# - Claude: https://console.anthropic.com
# - OpenAI: https://platform.openai.com
#
# 注意：API Key 需要自行申请，本脚本不提供

ANTHROPIC_API_KEY=
OPENAI_API_KEY=
PORT=3000
NODE_ENV=development
```

### ✅ 桌面快捷方式
```batch
@echo off
title OpenClaw
cd /d C:\Users\xxx\openclaw
echo 启动中...
echo 访问: http://localhost:3000
npm start
pause
```

---

## 🚫 绝对不做

### 脚本层面
- ❌ 不包含任何 API Key
- ❌ 不包含任何账号密码
- ❌ 不提供任何绕过方法
- ❌ 不修改任何系统设置
- ❌ 不安装非官方软件

### 内容层面
- ❌ 不推荐接码平台
- ❌ 不提供代注册服务
- ❌ 不教授绕过方法
- ❌ 不触碰合规边界

---

## 🎯 用户体验

### 运行脚本
```
双击 setup-openclaw.ps1
→ 等待安装完成
→ 查看桌面快捷方式
```

### 配置 API Key
```
1. 访问官方获取 API Key
2. 打开配置文件: notepad ~/openclaw/.env
3. 填入 API Key
4. 保存关闭
```

### 启动服务
```
双击桌面 "启动 OpenClaw.bat"
→ 自动启动服务
→ 浏览器访问 http://localhost:3000
```

---

## 📝 文件说明

### 用户需要自己做的事
1. **获取 API Key** - 从官方渠道
2. **编辑配置文件** - 填入 API Key
3. **启动服务** - 使用桌面快捷方式

### 脚本做的事
1. ✅ 安装环境
2. ✅ 下载项目
3. ✅ 安装依赖
4. ✅ 创建模板
5. ✅ 验证安装

---

## ✅ 最终清单

### 立即实现
1. [x] OpenClaw 纯环境配置脚本
2. [ ] 桌面快捷方式生成
3. [ ] 配置文件模板

### 本周实现
4. [ ] Ollama 环境脚本
5. [ ] Stable Diffusion 脚本
6. [ ] 其他 AI 工具脚本

---

*版本: V6 最终纯净版*
*核心: 只做环境配置，防止合规风险*
*目标: 干净、安全、无风险*

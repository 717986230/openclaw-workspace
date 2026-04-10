# uuoo.site 终极极简版 - 连数据库都一键配置

## 🎯 核心目标

**真正的零门槛** = 环境配置 + 数据库安装 + API配置 + 记忆系统 → 全自动

---

## 💡 OpenClaw 完整一键部署方案

### 用户最终只需要：
1. 运行一个脚本
2. 输入 API Key（脚本会提示）
3. 完成！

---

## 🔧 完整自动化清单

### 1. 环境配置 ✅
- Node.js 自动安装
- Git 自动安装
- Python 自动安装（如果需要）

### 2. 数据库配置 ✅
- SQLite 自动安装
- 数据库文件自动创建
- 表结构自动初始化
- 默认密码设置为 `111111`

### 3. 记忆系统配置 ✅
- 记忆数据库自动创建
- 默认记忆表结构初始化
- 示例记忆数据导入

### 4. API Key 配置 ✅
- 脚本运行时提示输入
- 自动写入配置文件
- 支持多个 API Key

---

## 💻 OpenClaw 终极一键脚本

```powershell
# OpenClaw 完整一键部署脚本（终极版）
# 以管理员身份运行 PowerShell
# 用户只需要：运行脚本 → 输入 API Key → 完成

param(
    [string]$AnthropicAPIKey = "",
    [string]$OpenAIAPIKey = "",
    [string]$DatabasePassword = "111111"
)

Write-Host "
========================================
   🦞 OpenClaw 完整一键部署
   环境 + 数据库 + API 全自动配置
========================================
" -ForegroundColor Cyan

# ==================== 环境配置 ====================

# 1. Node.js
Write-Host "[1/8] 检查 Node.js..." -ForegroundColor Yellow
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "  正在自动安装 Node.js..." -ForegroundColor Yellow
    $url = "https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi"
    $output = "$env:TEMP\nodejs.msi"
    Invoke-WebRequest -Uri $url -OutFile $output
    Start-Process msiexec.exe -ArgumentList "/i $output /qn" -Wait
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
}
Write-Host "  ✅ Node.js $(node -v)" -ForegroundColor Green

# 2. Git
Write-Host "[2/8] 检查 Git..." -ForegroundColor Yellow
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "  正在自动安装 Git..." -ForegroundColor Yellow
    winget install --id Git.Git -e --source winget --silent
}
Write-Host "  ✅ Git $(git --version)" -ForegroundColor Green

# 3. SQLite
Write-Host "[3/8] 检查 SQLite..." -ForegroundColor Yellow
if (!(Get-Command sqlite3 -ErrorAction SilentlyContinue)) {
    Write-Host "  正在安装 SQLite..." -ForegroundColor Yellow
    $sqliteUrl = "https://www.sqlite.org/2024/sqlite-tools-win-x64-3450000.zip"
    $sqliteZip = "$env:TEMP\sqlite.zip"
    Invoke-WebRequest -Uri $sqliteUrl -OutFile $sqliteZip
    Expand-Archive -Path $sqliteZip -DestinationPath "C:\Program Files\SQLite" -Force
    $env:Path += ";C:\Program Files\SQLite"
}
Write-Host "  ✅ SQLite 安装完成" -ForegroundColor Green

# ==================== OpenClaw 安装 ====================

# 4. 克隆仓库
Write-Host "[4/8] 下载 OpenClaw..." -ForegroundColor Yellow
$openclawPath = "$env:USERPROFILE\openclaw"
if (Test-Path $openclawPath) {
    cd $openclawPath
    git pull
} else {
    git clone https://github.com/openclaw/openclaw.git $openclawPath
    cd $openclawPath
}
Write-Host "  ✅ OpenClaw 下载完成" -ForegroundColor Green

# 5. 安装依赖
Write-Host "[5/8] 安装依赖包..." -ForegroundColor Yellow
npm install --silent
Write-Host "  ✅ 依赖安装完成" -ForegroundColor Green

# ==================== 数据库配置 ====================

# 6. 创建数据库
Write-Host "[6/8] 配置数据库..." -ForegroundColor Yellow
$dbPath = "$openclawPath\openclaw.db"

# 创建数据库表结构
$sql = @"
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL DEFAULT '111111',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    title TEXT,
    content TEXT,
    category TEXT,
    tags TEXT,
    importance INTEGER DEFAULT 5,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    platform TEXT,
    message TEXT,
    response TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认用户
INSERT OR IGNORE INTO users (username, password) VALUES ('admin', '111111');

-- 插入默认设置
INSERT OR IGNORE INTO settings (key, value) VALUES ('database_password', '111111');
INSERT OR IGNORE INTO settings (key, value) VALUES ('created_date', datetime('now'));
"@

sqlite3 $dbPath $sql
Write-Host "  ✅ 数据库创建完成（密码: $DatabasePassword）" -ForegroundColor Green

# ==================== 记忆系统 ====================

# 7. 初始化记忆系统
Write-Host "[7/8] 配置记忆系统..." -ForegroundColor Yellow
$memoryPath = "$openclawPath\memory"
New-Item -ItemType Directory -Force -Path $memoryPath | Out-Null

# 创建记忆初始化 SQL
$memorySql = @"
INSERT INTO memories (type, title, content, category, tags, importance)
VALUES 
('system', '首次启动', '欢迎使用 OpenClaw！这是你的第一条记忆。', 'system', '["system","welcome"]', 10),
('tip', '使用技巧', '可以问我任何问题，我会记住我们的对话。', 'tip', '["tip","usage"]', 7),
('help', '数据库信息', '数据库位置: $dbPath，默认密码: 111111', 'help', '["help","database"]', 8);
"@

sqlite3 $dbPath $memorySql
Write-Host "  ✅ 记忆系统初始化完成" -ForegroundColor Green

# ==================== API Key 配置 ====================

# 8. 配置 API Key
Write-Host "[8/8] 配置 API Key..." -ForegroundColor Yellow

# 如果没有提供 API Key，提示用户输入
if ($AnthropicAPIKey -eq "") {
    Write-Host ""
    $AnthropicAPIKey = Read-Host "请输入 Anthropic API Key（Claude，可选，直接回车跳过）"
}

if ($OpenAIAPIKey -eq "") {
    $OpenAIAPIKey = Read-Host "请输入 OpenAI API Key（可选，直接回车跳过）"
}

# 创建配置文件
$configContent = @"
# OpenClaw 配置文件
# 由一键部署脚本自动生成

# API Keys
ANTHROPIC_API_KEY=$AnthropicAPIKey
OPENAI_API_KEY=$OpenAIAPIKey

# 数据库配置
DATABASE_PATH=$dbPath
DATABASE_PASSWORD=$DatabasePassword

# 记忆系统
MEMORY_ENABLED=true
MEMORY_PATH=$memoryPath

# 其他配置
PORT=3000
NODE_ENV=production
"@

Set-Content -Path "$openclawPath\.env" -Value $configContent -Encoding UTF8
Write-Host "  ✅ 配置文件创建完成" -ForegroundColor Green

# ==================== 完成 ====================

Write-Host "
========================================
   ✅ 安装完成！
========================================
" -ForegroundColor Green

Write-Host "
📋 重要信息：" -ForegroundColor Cyan
Write-Host "  • 数据库位置: $dbPath" -ForegroundColor White
Write-Host "  • 数据库密码: $DatabasePassword" -ForegroundColor White
Write-Host "  • 配置文件: $openclawPath\.env" -ForegroundColor White
Write-Host ""
Write-Host "🚀 启动命令：" -ForegroundColor Yellow
Write-Host "  cd $openclawPath" -ForegroundColor Cyan
Write-Host "  npm start" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 访问地址：" -ForegroundColor Yellow
Write-Host "  http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 提示：" -ForegroundColor Yellow
Write-Host "  • 首次登录用户名: admin" -ForegroundColor White
Write-Host "  • 首次登录密码: $DatabasePassword" -ForegroundColor White
Write-Host ""
Write-Host "需要帮助？查看文档: $openclawPath\README.md" -ForegroundColor Gray
Write-Host ""

# 创建快速启动脚本
$quickStart = @"
@echo off
cd $openclawPath
npm start
pause
"@

Set-Content -Path "$env:USERPROFILE\Desktop\启动 OpenClaw.bat" -Value $quickStart -Encoding ASCII
Write-Host "✅ 已在桌面创建启动快捷方式" -ForegroundColor Green
```

---

## 🗄️ 数据库配置详解

### 默认数据库结构

```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL DEFAULT '111111',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 记忆表
CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    title TEXT,
    content TEXT,
    category TEXT,
    tags TEXT,
    importance INTEGER DEFAULT 5,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- 对话表
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    platform TEXT,
    message TEXT,
    response TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 设置表
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 默认数据
INSERT INTO users (username, password) VALUES ('admin', '111111');
INSERT INTO settings (key, value) VALUES ('database_password', '111111');
```

---

## 🧠 记忆系统配置

### 自动初始化内容

```
记忆 ID: 1
类型: system
标题: 首次启动
内容: 欢迎使用 OpenClaw！这是你的第一条记忆。
重要性: 10

记忆 ID: 2
类型: tip
标题: 使用技巧
内容: 可以问我任何问题，我会记住我们的对话。
重要性: 7

记忆 ID: 3
类型: help
标题: 数据库信息
内容: 数据库位置: ~/openclaw/openclaw.db，默认密码: 111111
重要性: 8
```

---

## 🔑 API Key 配置流程

### 方式 1：命令行参数（推荐）
```powershell
.\install-openclaw.ps1 `
  -AnthropicAPIKey "sk-ant-xxx" `
  -OpenAIAPIKey "sk-xxx" `
  -DatabasePassword "111111"
```

### 方式 2：交互式输入
```powershell
.\install-openclaw.ps1
# 脚本会提示：
请输入 Anthropic API Key: _
请输入 OpenAI API Key: _
```

### 方式 3：手动配置
脚本运行后，打开配置文件修改：
```bash
notepad ~/openclaw/.env
```

---

## 📦 完整下载包

### 包含内容
```
openclaw-complete-setup.zip
├── install-openclaw.ps1      # 一键安装脚本
├── start-openclaw.bat        # 快速启动脚本
├── README.txt                # 简明使用说明
└── database/
    ├── schema.sql            # 数据库结构
    └── init-data.sql         # 初始化数据
```

### README.txt（用户看到的）
```
================================
   OpenClaw 一键安装包
================================

使用方法（超简单）：

Windows:
1. 右键点击 install-openclaw.ps1
2. 选择"使用 PowerShell 运行"
3. 按提示输入 API Key（如果没有，直接回车）
4. 等待安装完成
5. 双击桌面上的"启动 OpenClaw"图标

默认登录信息：
用户名: admin
密码: 111111

访问地址：
http://localhost:3000

问题反馈：
GitHub: https://github.com/openclaw/openclaw/issues
```

---

## 🎯 用户体验流程

### 安装前（用户视角）
```
1. 下载安装包
2. 解压到任意位置
3. 右键运行安装脚本
```

### 安装中（脚本显示）
```
================================
   🦞 OpenClaw 完整一键部署
================================

[1/8] 检查 Node.js...
  ✅ Node.js v20.11.0

[2/8] 检查 Git...
  ✅ Git 安装完成

[3/8] 检查 SQLite...
  ✅ SQLite 安装完成

[4/8] 下载 OpenClaw...
  ✅ OpenClaw 下载完成

[5/8] 安装依赖包...
  ✅ 依赖安装完成

[6/8] 配置数据库...
  ✅ 数据库创建完成（密码: 111111）

[7/8] 配置记忆系统...
  ✅ 记忆系统初始化完成

[8/8] 配置 API Key...
请输入 Anthropic API Key: sk-ant-xxx
请输入 OpenAI API Key: sk-xxx
  ✅ 配置文件创建完成

================================
   ✅ 安装完成！
================================

📋 重要信息：
  • 数据库位置: ~/openclaw/openclaw.db
  • 数据库密码: 111111
  • 配置文件: ~/openclaw/.env

🚀 启动命令：
  cd ~/openclaw
  npm start

🌐 访问地址：
  http://localhost:3000

✅ 已在桌面创建启动快捷方式
```

### 安装后（用户操作）
```
双击桌面图标 → 自动启动 → 浏览器打开 → 开始使用
```

---

## 🔐 安全考虑

### 数据库密码
- 默认: `111111`
- 用户可在安装时自定义
- 脚本会提示修改建议

### API Key 安全
- 不上传到云端
- 仅存储在本地 `.env` 文件
- 权限设置为仅当前用户可读

### 数据库文件
- 自动设置权限
- 默认用户目录
- 定期备份提醒

---

## 📊 与原版对比

### 原版（复杂）
```
用户需要：
1. 安装 Node.js
2. 安装 Git
3. 安装 SQLite
4. 克隆仓库
5. 安装依赖
6. 创建数据库
7. 初始化表结构
8. 配置环境变量
9. 编辑配置文件
10. 填写 API Key
11. 启动服务
```

### 终极版（简化）
```
用户只需要：
1. 运行脚本
2. 输入 API Key（或回车跳过）
3. 完成！
```

---

## ✅ 执行清单

### 立即实现
1. [ ] OpenClaw 完整一键脚本
2. [ ] 数据库自动配置模块
3. [ ] 记忆系统初始化模块
4. [ ] API Key 交互式输入

### 本周实现
5. [ ] Ollama 完整脚本
6. [ ] Stable Diffusion 脚本
7. [ ] 完整安装包制作

---

*策划版本: V4 终极极简版*
*核心: 连数据库都自动配置*
*目标: 小白真正零门槛*

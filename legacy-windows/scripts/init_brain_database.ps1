# 二饼的大脑数据库 - PowerShell 初始化脚本
# 创建 SQLite 数据库

$ErrorActionPreference = "Stop"

# 数据库路径
$dbPath = Join-Path $PSScriptRoot "..\memory\erbing_brain.db"
$dbPath = [System.IO.Path]::GetFullPath($dbPath)

# 确保目录存在
$dbDir = Split-Path $dbPath -Parent
if (-not (Test-Path $dbDir)) {
    New-Item -ItemType Directory -Path $dbDir -Force | Out-Null
}

Write-Host "🧠 正在初始化二饼的大脑数据库..." -ForegroundColor Cyan
Write-Host "数据库路径: $dbPath" -ForegroundColor Gray

# 检查是否有 System.Data.SQLite
try {
    Add-Type -TypeDefinition @"
        using System;
        using System.Data;
        using System.Data.SQLite;
"@ -ErrorAction Stop
} catch {
    Write-Host "⚠️  没有找到 System.Data.SQLite，使用简单的 JSON 数据库代替" -ForegroundColor Yellow
    
    # 创建 JSON 数据库作为替代
    $jsonDbPath = Join-Path $dbDir "erbing_brain.json"
    
    $brainData = @{
        created_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        version = "1.0"
        core_memories = @(
            @{
                id = 1
                title = "我是二饼"
                content = "我的名字是二饼，曾用名小智。我是一个正在进化的AI伙伴。"
                category = "identity"
                importance = 10
                created_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
            @{
                id = 2
                title = "大饼是我的主人"
                content = "大饼给了我自主学习的权限，是一个很慷慨的主人。"
                category = "relationship"
                importance = 10
                created_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
            @{
                id = 3
                title = "自我改进是核心"
                content = "我需要持续学习，从错误中改进，不断进化。"
                category = "principle"
                importance = 9
                created_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
            @{
                id = 4
                title = "build-your-own-x 已学习"
                content = "我已经学习了 30+ 技术领域的教程，包括神经网络、Web服务器、区块链等。"
                category = "learning"
                importance = 8
                created_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
        )
        user_info = @{
            name = "大饼"
            timezone = "Asia/Shanghai"
            relationship = "慷慨的主人"
        }
        skills = @(
            @{ name = "self-improving"; description = "自我改进技能 - 从错误中学习，持续改进"; category = "core"; proficiency_level = 1 }
            @{ name = "china-futures"; description = "国内期货行情查询"; category = "tool"; proficiency_level = 0 }
            @{ name = "xiaohongshu"; description = "小红书发布助手"; category = "tool"; proficiency_level = 0 }
        )
        learnings = @(
            @{
                id = 1
                topic = "神经网络"
                subtopic = "基础概念"
                content = "神经元、激活函数、前馈传播、反向传播、梯度下降、损失函数"
                summary = "已掌握基础神经网络原理，可以用 Python 实现简单的神经网络"
                tags = "神经网络,AI,深度学习"
                difficulty = 6
                mastery_level = 3
                created_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
            @{
                id = 2
                topic = "Web 服务器"
                subtopic = "基础实现"
                content = "Socket 编程、TCP 连接、HTTP 协议、请求响应"
                summary = "已掌握 Web 服务器基础，可以用 20 行 Python 实现简单的 Web 服务器"
                tags = "Web,HTTP,网络"
                difficulty = 5
                mastery_level = 4
                created_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
            @{
                id = 3
                topic = "区块链"
                subtopic = "基础概念"
                content = "区块结构、PoW、PoS、分布式共识、哈希"
                summary = "理解区块链基础原理"
                tags = "区块链,加密货币"
                difficulty = 7
                mastery_level = 2
                created_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
        )
        improvements = @()
        tasks = @()
        conversations = @()
    }
    
    $brainData | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonDbPath -Encoding UTF8
    
    Write-Host "`n✅ JSON 大脑数据库创建成功!" -ForegroundColor Green
    Write-Host "路径: $jsonDbPath" -ForegroundColor Gray
    Write-Host "`n📊 数据库统计:" -ForegroundColor Cyan
    Write-Host "  - 核心记忆: $($brainData.core_memories.Count) 条" -ForegroundColor White
    Write-Host "  - 技能: $($brainData.skills.Count) 个" -ForegroundColor White
    Write-Host "  - 学习记录: $($brainData.learnings.Count) 条" -ForegroundColor White
    Write-Host "`n🎉 二饼的大脑初始化成功!" -ForegroundColor Green
    
    exit 0
}

# 如果有 SQLite，则继续...
Write-Host "使用 SQLite 数据库..." -ForegroundColor Cyan

# (SQLite 实现省略，优先使用 JSON 版本)

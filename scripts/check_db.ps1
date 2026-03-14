
# -*- coding: utf-8 -*-
$ErrorActionPreference = "Continue"

$dbPath = "C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"

if (-not (Test-Path $dbPath)) {
    Write-Host "数据库文件不存在: $dbPath" -ForegroundColor Red
    exit 1
}

Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "数据库状态" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

# 加载System.Data.SQLite
try {
    Add-Type -Path "C:\Windows\Microsoft.NET\assembly\GAC_MSIL\System.Data.SQLite\v4.0_1.0.0.0__db937bc2d44ff139\System.Data.SQLite.dll" -ErrorAction Stop
} catch {
    Write-Host "使用简单查询方式..." -ForegroundColor Yellow
}

# 用sqlite3命令行工具（如果安装了）
try {
    $sqlite3 = Get-Command sqlite3 -ErrorAction Stop
    Write-Host "使用sqlite3命令行工具..." -ForegroundColor Green
    
    Write-Host ""
    Write-Host "表结构:" -ForegroundColor Yellow
    &amp; sqlite3 $dbPath ".schema"
    
    Write-Host ""
    Write-Host "最近10条记忆:" -ForegroundColor Yellow
    &amp; sqlite3 $dbPath "SELECT id, type, title, importance FROM memories ORDER BY created_at DESC LIMIT 10"
    
} catch {
    Write-Host "sqlite3命令行工具未找到，让我检查数据库文件..." -ForegroundColor Yellow
    
    # 至少显示文件信息
    $fileInfo = Get-Item $dbPath
    Write-Host ""
    Write-Host "数据库文件: $dbPath" -ForegroundColor Green
    Write-Host "文件大小: $($fileInfo.Length / 1KB) KB" -ForegroundColor Green
    Write-Host "修改时间: $($fileInfo.LastWriteTime)" -ForegroundColor Green
}

Write-Host ""
Write-Host "[OK] 检查完成" -ForegroundColor Green


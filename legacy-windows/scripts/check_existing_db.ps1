# 检查已有的数据库
$ErrorActionPreference = "Stop"

$memoryDbPath = "C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"
$secureDbPath = "C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_secure.db"

Write-Host "🧠 检查小智的记忆数据库..." -ForegroundColor Cyan
Write-Host "记忆库: $memoryDbPath" -ForegroundColor Gray
Write-Host "安全库: $secureDbPath" -ForegroundColor Gray
Write-Host ""

# 检查文件是否存在
if (-not (Test-Path $memoryDbPath)) {
    Write-Host "❌ 记忆库不存在!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $secureDbPath)) {
    Write-Host "❌ 安全库不存在!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 数据库文件存在!" -ForegroundColor Green
Write-Host ""

# 尝试用 ODBC 或简单的方式检查
# 这里只是简单显示文件信息
$memoryDb = Get-Item $memoryDbPath
$secureDb = Get-Item $secureDbPath

Write-Host "📊 文件信息:" -ForegroundColor Cyan
Write-Host "  记忆库大小: $([math]::Round($memoryDb.Length/1KB, 2)) KB" -ForegroundColor White
Write-Host "  安全库大小: $([math]::Round($secureDb.Length/1KB, 2)) KB" -ForegroundColor White
Write-Host "  记忆库修改时间: $($memoryDb.LastWriteTime)" -ForegroundColor White
Write-Host "  安全库修改时间: $($secureDb.LastWriteTime)" -ForegroundColor White
Write-Host ""

Write-Host "🎉 找到小智的真大脑了!" -ForegroundColor Green
Write-Host "位置: memory/database/" -ForegroundColor Gray

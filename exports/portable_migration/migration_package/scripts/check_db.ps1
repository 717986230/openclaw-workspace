
# -*- coding: utf-8 -*-
$ErrorActionPreference = "Continue"

$dbPath = "C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"

if (-not (Test-Path $dbPath)) {
    Write-Host "鏁版嵁搴撴枃浠朵笉瀛樺湪: $dbPath" -ForegroundColor Red
    exit 1
}

Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "鏁版嵁搴撶姸鎬? -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

# 鍔犺浇System.Data.SQLite
try {
    Add-Type -Path "C:\Windows\Microsoft.NET\assembly\GAC_MSIL\System.Data.SQLite\v4.0_1.0.0.0__db937bc2d44ff139\System.Data.SQLite.dll" -ErrorAction Stop
} catch {
    Write-Host "浣跨敤绠€鍗曟煡璇㈡柟寮?.." -ForegroundColor Yellow
}

# 鐢╯qlite3鍛戒护琛屽伐鍏凤紙濡傛灉瀹夎浜嗭級
try {
    $sqlite3 = Get-Command sqlite3 -ErrorAction Stop
    Write-Host "浣跨敤sqlite3鍛戒护琛屽伐鍏?.." -ForegroundColor Green
    
    Write-Host ""
    Write-Host "琛ㄧ粨鏋?" -ForegroundColor Yellow
    &amp; sqlite3 $dbPath ".schema"
    
    Write-Host ""
    Write-Host "鏈€杩?0鏉¤蹇?" -ForegroundColor Yellow
    &amp; sqlite3 $dbPath "SELECT id, type, title, importance FROM memories ORDER BY created_at DESC LIMIT 10"
    
} catch {
    Write-Host "sqlite3鍛戒护琛屽伐鍏锋湭鎵惧埌锛岃鎴戞鏌ユ暟鎹簱鏂囦欢..." -ForegroundColor Yellow
    
    # 鑷冲皯鏄剧ず鏂囦欢淇℃伅
    $fileInfo = Get-Item $dbPath
    Write-Host ""
    Write-Host "鏁版嵁搴撴枃浠? $dbPath" -ForegroundColor Green
    Write-Host "鏂囦欢澶у皬: $($fileInfo.Length / 1KB) KB" -ForegroundColor Green
    Write-Host "淇敼鏃堕棿: $($fileInfo.LastWriteTime)" -ForegroundColor Green
}

Write-Host ""
Write-Host "[OK] 妫€鏌ュ畬鎴? -ForegroundColor Green


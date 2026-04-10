# 妫€鏌ュ凡鏈夌殑鏁版嵁搴?$ErrorActionPreference = "Stop"

$memoryDbPath = "C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"
$secureDbPath = "C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_secure.db"

Write-Host "馃 妫€鏌ュ皬鏅虹殑璁板繂鏁版嵁搴?.." -ForegroundColor Cyan
Write-Host "璁板繂搴? $memoryDbPath" -ForegroundColor Gray
Write-Host "瀹夊叏搴? $secureDbPath" -ForegroundColor Gray
Write-Host ""

# 妫€鏌ユ枃浠舵槸鍚﹀瓨鍦?if (-not (Test-Path $memoryDbPath)) {
    Write-Host "鉂?璁板繂搴撲笉瀛樺湪!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $secureDbPath)) {
    Write-Host "鉂?瀹夊叏搴撲笉瀛樺湪!" -ForegroundColor Red
    exit 1
}

Write-Host "鉁?鏁版嵁搴撴枃浠跺瓨鍦?" -ForegroundColor Green
Write-Host ""

# 灏濊瘯鐢?ODBC 鎴栫畝鍗曠殑鏂瑰紡妫€鏌?# 杩欓噷鍙槸绠€鍗曟樉绀烘枃浠朵俊鎭?$memoryDb = Get-Item $memoryDbPath
$secureDb = Get-Item $secureDbPath

Write-Host "馃搳 鏂囦欢淇℃伅:" -ForegroundColor Cyan
Write-Host "  璁板繂搴撳ぇ灏? $([math]::Round($memoryDb.Length/1KB, 2)) KB" -ForegroundColor White
Write-Host "  瀹夊叏搴撳ぇ灏? $([math]::Round($secureDb.Length/1KB, 2)) KB" -ForegroundColor White
Write-Host "  璁板繂搴撲慨鏀规椂闂? $($memoryDb.LastWriteTime)" -ForegroundColor White
Write-Host "  瀹夊叏搴撲慨鏀规椂闂? $($secureDb.LastWriteTime)" -ForegroundColor White
Write-Host ""

Write-Host "馃帀 鎵惧埌灏忔櫤鐨勭湡澶ц剳浜?" -ForegroundColor Green
Write-Host "浣嶇疆: memory/database/" -ForegroundColor Gray

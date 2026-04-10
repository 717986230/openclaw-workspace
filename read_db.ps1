
$ErrorActionPreference = "Stop"
$dbPath = "C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DATABASE STATUS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Load SQLite assembly
Add-Type -AssemblyName System.Data.SQLite

$conn = New-Object System.Data.SQLite.SQLiteConnection
$conn.ConnectionString = "Data Source=$dbPath"
$conn.Open()

# Get total count
$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT COUNT(*) FROM memories"
$total = $cmd.ExecuteScalar()
Write-Host "Total memories: $total" -ForegroundColor Green

# Get by type
Write-Host ""
Write-Host "By type:" -ForegroundColor Yellow
$cmd.CommandText = "SELECT type, COUNT(*) as cnt FROM memories GROUP BY type ORDER BY cnt DESC"
$reader = $cmd.ExecuteReader()
while ($reader.Read()) {
    Write-Host "  $($reader[0]): $($reader[1])"
}
$reader.Close()

# Get latest 5
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Latest 5 memories:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
$cmd.CommandText = "SELECT id, type, title, importance FROM memories ORDER BY created_at DESC LIMIT 5"
$reader = $cmd.ExecuteReader()
while ($reader.Read()) {
    Write-Host "[$($reader[0])] $($reader[1]) - $($reader[2]) (imp: $($reader[3]))" -ForegroundColor White
}
$reader.Close()

$conn.Close()
Write-Host ""
Write-Host "[OK] Database is working!" -ForegroundColor Green


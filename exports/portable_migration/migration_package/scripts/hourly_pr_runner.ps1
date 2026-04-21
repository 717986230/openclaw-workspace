# hourly_pr_runner.ps1
# Run GitHub Auto PR every hour

$ScriptPath = "C:\Users\Administrator\.openclaw\workspace\scripts\auto_pr_missing_files.py"
$LogFile = "C:\Users\Administrator\.openclaw\workspace\logs\auto-pr-$(Get-Date -Format 'yyyyMMdd').log"

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Output "[$timestamp] Running Auto PR..." | Out-File -Append $LogFile

    python $ScriptPath 2>&1 | Out-File -Append $LogFile

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Output "[$timestamp] Sleeping for 1 hour..." | Out-File -Append $LogFile

    Start-Sleep -Seconds 3600
}

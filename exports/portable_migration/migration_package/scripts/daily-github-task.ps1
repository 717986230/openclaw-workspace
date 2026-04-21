# daily-github-task.ps1
# Daily GitHub Trending PR Automation with Feishu Notification

$ErrorActionPreference = "Stop"
$workspace = "C:\Users\Administrator\.openclaw\workspace"
$logFile = "$workspace\logs\github-trending-$(Get-Date -Format 'yyyyMMdd').log"

# Ensure log directory exists
$logDir = Split-Path $logFile -Parent
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path $logFile -Value $logMessage
}

function Send-FeishuNotification {
    param($Title, $Content)

    # Save notification to file for OpenClaw to pick up
    $notificationFile = "$workspace\logs\notification-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"

    $notification = @{
        title = $Title
        content = $Content
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        status = "pending"
    }

    $notification | ConvertTo-Json -Depth 10 | Set-Content $notificationFile
    Write-Log "Notification saved to: $notificationFile"

    # Also write to a status file that OpenClaw can check
    $statusFile = "$workspace\logs\last-notification.json"
    $notification | ConvertTo-Json -Depth 10 | Set-Content $statusFile
}

# Main execution
Write-Log "=== Starting Daily GitHub Trending PR Automation ==="

try {
    # Run the Python script
    $pythonScript = "$workspace\scripts\github-trending-pr.py"
    $result = python $pythonScript 2>&1
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-Log "GitHub trending analysis completed successfully"
        Write-Log $result

        # Get today's memories from database
        $dbScript = @"
import sqlite3
conn = sqlite3.connect(r'$workspace\memory\database\xiaozhi_memory.db')
c = conn.cursor()
c.execute('SELECT title FROM memories WHERE type=\"event\" ORDER BY created_at DESC LIMIT 5')
for row in c.fetchall():
    print('- ' + row[0])
conn.close()
"@

        $todayMemories = python -c $dbScript 2>&1

        # Send success notification
        $notificationContent = @"
**Daily GitHub Trending PR Automation**

Status: Completed

Today's analysis:
$todayMemories

Check logs: $logFile
"@

        Send-FeishuNotification -Title "GitHub Trending Daily Report" -Content $notificationContent

        Write-Log "=== Daily run completed successfully ==="
    } else {
        Write-Log "Error: GitHub trending analysis failed with exit code $exitCode"
        Write-Log $result

        # Send error notification
        Send-FeishuNotification -Title "GitHub Trending Error" -Content "Error occurred during daily run. Check logs: $logFile"
    }
} catch {
    Write-Log "Exception: $_"
    Send-FeishuNotification -Title "GitHub Trending Exception" -Content "Exception: $_"
}

# Sync database to LanceDB
Write-Log "Syncing database to LanceDB..."
python "$workspace\memory\database\sync_to_lancedb.py" 2>&1 | Add-Content $logFile

Write-Log "=== Task completed ==="

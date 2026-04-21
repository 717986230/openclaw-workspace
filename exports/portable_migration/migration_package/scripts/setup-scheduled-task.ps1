# setup-scheduled-task.ps1
# Setup Windows Task Scheduler for daily GitHub trending analysis

$TaskName = "OpenClaw-GitHub-Trending-Daily"
$TaskDescription = "Daily GitHub trending repository analysis and PR automation"
$ScriptPath = "C:\Users\Administrator\.openclaw\workspace\scripts\daily-github-task.ps1"

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task '$TaskName' already exists. Updating..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create action
$action = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""

# Create trigger (daily at 8:00 AM)
$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At "8:00 AM"

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

# Register task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $TaskDescription `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal

Write-Host "Task '$TaskName' created successfully!" -ForegroundColor Green
Write-Host "Schedule: Daily at 8:00 AM" -ForegroundColor Cyan
Write-Host "Script: $ScriptPath" -ForegroundColor Cyan

# Test run
Write-Host "`nTesting task..." -ForegroundColor Yellow
Start-ScheduledTask -TaskName $TaskName
Write-Host "Task started. Check logs in 30 seconds." -ForegroundColor Green

# Show task info
Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, Description, State, LastRunTime, NextRunTime

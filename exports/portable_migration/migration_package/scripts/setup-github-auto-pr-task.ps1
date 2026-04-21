# setup-github-auto-pr-task.ps1
# Setup hourly task for GitHub Auto PR

$TaskName = "OpenClaw-GitHub-Auto-PR-Hourly"
$TaskDescription = "Hourly GitHub trending scan and PR automation"
$ScriptPath = "C:\Users\Administrator\.openclaw\workspace\scripts\github_trending_auto_pr.py"

# Remove existing task if exists
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing task" -ForegroundColor Yellow
}

# Create action
$action = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "`"$ScriptPath`" --run" `
    -WorkingDirectory "C:\Users\Administrator\.openclaw\workspace"

# Create trigger (hourly, starting now)
$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Hours 1)

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# Create principal
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

Write-Host "`nTask '$TaskName' created!" -ForegroundColor Green
Write-Host "Schedule: Every hour" -ForegroundColor Cyan

# Show task info
Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, Description, State

# Run now to test
Write-Host "`nStarting first run..." -ForegroundColor Yellow
Start-ScheduledTask -TaskName $TaskName

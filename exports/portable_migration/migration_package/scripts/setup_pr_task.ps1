# setup_pr_task.ps1
$TaskName = 'OpenClaw-Auto-PR-Hourly'

# Remove existing task
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing task"
}

# Create new task
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Users\Administrator\.openclaw\workspace\scripts\auto_pr_missing_files.py"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Description "Hourly GitHub Auto PR" -Action $action -Trigger $trigger -Settings $settings -Principal $principal

Write-Host "Task created: $TaskName"
Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, State, LastRunTime

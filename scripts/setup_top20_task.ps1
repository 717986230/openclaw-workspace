# Setup Top 20 PR Task
$TaskName = 'OpenClaw-Auto-PR-Top20'

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Users\Administrator\.openclaw\workspace\scripts\auto_pr_top20.py"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Description "Top 20 Deep Analysis PR" -Action $action -Trigger $trigger -Settings $settings -Principal $principal

Write-Host "Task created: $TaskName"
Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, State

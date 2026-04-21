# 设置Windows定时任务 - 每小时执行AI学习
# 需要管理员权限运行

$TaskName = "OpenClaw-HourlyAILearning"
$ScriptPath = "C:\Users\Administrator\.openclaw\workspace\scripts\hourly_ai_learning.ps1"

# 检查任务是否已存在
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "定时任务已存在，更新配置..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# 创建任务
$Action = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""

$Trigger = New-ScheduledTaskTrigger `
    -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Hours 1) `
    -RepetitionDuration ([TimeSpan]::MaxValue)

$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdle `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

$Principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "OpenClaw每小时自动搜索AI文章学习进化"

Write-Host "✅ 定时任务已创建: $TaskName"
Write-Host "⏰ 执行频率: 每小时一次"
Write-Host "📝 脚本路径: $ScriptPath"

# 显示任务详情
Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, State, LastRunTime, NextRunTime

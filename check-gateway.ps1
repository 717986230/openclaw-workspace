# OpenClaw Gateway Health Check
# 检查网关状态，只在崩溃时重启 - SILENT MODE

$ErrorActionPreference = "SilentlyContinue"
$port = 18789
$logFile = "$env:USERPROFILE\.openclaw\logs\gateway-health.log"
$gatewayCmd = "$env:USERPROFILE\.openclaw\gateway.cmd"

function Log {
    param($message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $message"
    Add-Content -Path $logFile -Value $logMessage
}

# 检查端口是否在监听
try {
    $tcpConnection = New-Object System.Net.Sockets.TcpClient
    $tcpConnection.Connect("127.0.0.1", $port)
    $tcpConnection.Close()
    # 端口正常，静默退出
    exit 0
} catch {
    # 端口不通，需要重启
    Log "Gateway port $port is NOT responding. Restarting..."
    
    # 先杀掉可能占用端口的进程
    $processes = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
    if ($processes) {
        foreach ($pid in $processes) {
            if ($pid -ne 0) {
                try {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    Log "Killed process $pid"
                } catch {}
            }
        }
        Start-Sleep -Seconds 2
    }
    
    # 启动网关
    Log "Starting gateway..."
    Start-Process -FilePath $gatewayCmd -WindowStyle Hidden
    Log "Gateway restarted"
    exit 1
}

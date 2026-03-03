
$ErrorActionPreference = "SilentlyContinue"
try {
    $t = New-Object System.Net.Sockets.TcpClient
    $t.Connect("127.0.0.1", 18789)
    $t.Close()
    exit 0
} catch {
    Get-NetTCPConnection -LocalPort 18789 -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.OwningProcess -ne 0) {
            Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 2
    Start-Process -FilePath "C:\Users\admin\.openclaw\gateway.cmd" -WindowStyle Hidden
}

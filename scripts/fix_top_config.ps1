$configPath = "C:\Users\Administrator\.openclaw\config.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json

# Show current agents.defaults
Write-Host "=== Current agents.defaults ==="
$config.agents.defaults | ConvertTo-Json -Depth 5

Write-Host "`n=== Current models ==="
$config.models.providers | ConvertTo-Json -Depth 5

Write-Host "`n=== Current tools ==="
$config.tools | ConvertTo-Json -Depth 5

Write-Host "`n=== Current plugins ==="
$config.plugins | ConvertTo-Json -Depth 5

Write-Host "`n=== Current channels.feishu ==="
$config.channels.feishu | ConvertTo-Json -Depth 5
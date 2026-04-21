$configPath = "C:\Users\Administrator\.openclaw\openclaw.json"
$backupPath = "C:\Users\Administrator\.openclaw\openclaw.json.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Copy-Item $configPath $backupPath -Force
Write-Host "[OK] Backup: $backupPath"

$c = Get-Content $configPath -Raw | ConvertFrom-Json

# 1. FIX CRITICAL: sandbox.mode=all (protects small models + multi-user)
$c.agents.defaults.sandbox = @{ mode = "all" }
Write-Host "[OK] sandbox.mode=all"

# 2. FIX WARN: gateway.trustedProxies
$c.gateway | Add-Member -NotePropertyName "trustedProxies" -NotePropertyValue @("127.0.0.1", "::1") -Force -ErrorAction SilentlyContinue
if ($c.gateway.PSObject.Properties.Name.Contains('trustedProxies')) {
    $c.gateway.trustedProxies = @("127.0.0.1", "::1")
} else {
    $c.gateway | Add-Member -NotePropertyName "trustedProxies" -NotePropertyValue @("127.0.0.1", "::1") -Force
}
Write-Host "[OK] gateway.trustedProxies=[127.0.0.1, ::1]"

# 3. FIX WARN: Feishu doc tool
if ($c.channels.feishu.PSObject.Properties.Name.Contains('tools')) {
    $c.channels.feishu.tools | Add-Member -NotePropertyName "doc" -NotePropertyValue $false -Force
} else {
    $c.channels.feishu | Add-Member -NotePropertyName "tools" -NotePropertyValue @{ doc = $false } -Force
}
Write-Host "[OK] channels.feishu.tools.doc=false"

# 4. FIX: tools.fs.workspaceOnly
if ($c.tools.PSObject.Properties.Name.Contains('fs')) {
    $c.tools.fs | Add-Member -NotePropertyName "workspaceOnly" -NotePropertyValue $true -Force
} else {
    $c.tools | Add-Member -NotePropertyName "fs" -NotePropertyValue @{ workspaceOnly = $true } -Force
}
Write-Host "[OK] tools.fs.workspaceOnly=true"

# 5. FIX: tools.deny
if ($c.tools.PSObject.Properties.Name.Contains('deny')) {
    $c.tools.deny = @("group:web", "browser")
} else {
    $c.tools | Add-Member -NotePropertyName "deny" -NotePropertyValue @("group:web", "browser") -Force
}
Write-Host "[OK] tools.deny=[group:web, browser]"

# 6. FIX: Disable openclaw-agent-reach plugin
if ($c.plugins -and $c.plugins.entries -and $c.plugins.entries.PSObject.Properties.Name.Contains('openclaw-agent-reach')) {
    $c.plugins.entries.'openclaw-agent-reach'.enabled = $false
    Write-Host "[OK] openclaw-agent-reach disabled"
}

# 7. Add model constraints
if (-not $c.agents.defaults.model.PSObject.Properties.Name.Contains('constraints')) {
    $c.agents.defaults.model | Add-Member -NotePropertyName "constraints" -NotePropertyValue @{ requireSandbox = $true } -Force
}
Write-Host "[OK] agents.defaults.model.constraints.requireSandbox=true"

# Save
$c | ConvertTo-Json -Depth 20 | Set-Content $configPath -Encoding UTF8
Write-Host "`n[SUCCESS] Top-tier config applied to openclaw.json!"
$configPath = "C:\Users\Administrator\.openclaw\openclaw.json"
$c = Get-Content $configPath -Raw | ConvertFrom-Json

# 1. FIX CRITICAL: sandbox.mode=all
$c.agents.defaults.sandbox = @{ mode = "all" }
Write-Host "[OK] sandbox.mode=all"

# 2. Remove gemma4:26b from fallbacks (small model needs sandbox - remove from un-sandboxed use)
$currentFallbacks = @($c.agents.defaults.model.fallbacks)
$safeFallbacks = $currentFallbacks | Where-Object { $_ -notmatch "gemma4" }
$c.agents.defaults.model.fallbacks = $safeFallbacks
Write-Host "[OK] Removed gemma4:26b from fallbacks. New fallbacks: $($safeFallbacks -join ', ')"

# 3. gateway.trustedProxies
$c.gateway | Add-Member -NotePropertyName "trustedProxies" -NotePropertyValue @("127.0.0.1", "::1") -Force
Write-Host "[OK] gateway.trustedProxies"

# 4. Feishu doc tool = false
if ($c.channels.feishu.PSObject.Properties.Name.Contains('tools')) {
    $c.channels.feishu.tools | Add-Member -NotePropertyName "doc" -NotePropertyValue $false -Force
} else {
    $c.channels.feishu | Add-Member -NotePropertyName "tools" -NotePropertyValue @{ doc = $false } -Force
}
Write-Host "[OK] channels.feishu.tools.doc=false"

# 5. tools.fs.workspaceOnly
if ($c.tools.PSObject.Properties.Name.Contains('fs')) {
    $c.tools.fs | Add-Member -NotePropertyName "workspaceOnly" -NotePropertyValue $true -Force
} else {
    $c.tools | Add-Member -NotePropertyName "fs" -NotePropertyValue @{ workspaceOnly = $true } -Force
}
Write-Host "[OK] tools.fs.workspaceOnly=true"

# 6. tools.deny
if ($c.tools.PSObject.Properties.Name.Contains('deny')) {
    $c.tools.deny = @("group:web", "browser")
} else {
    $c.tools | Add-Member -NotePropertyName "deny" -NotePropertyValue @("group:web", "browser") -Force
}
Write-Host "[OK] tools.deny"

# 7. Disable Agent Reach plugin
if ($c.plugins -and $c.plugins.entries) {
    $ep = $c.plugins.entries.PSObject.Properties.Name
    if ($ep.Contains('openclaw-agent-reach')) {
        $c.plugins.entries.'openclaw-agent-reach'.enabled = $false
        Write-Host "[OK] openclaw-agent-reach disabled"
    }
}

# Save
$c | ConvertTo-Json -Depth 20 | Set-Content $configPath -Encoding UTF8
Write-Host "`n[SUCCESS] All fixes applied to openclaw.json!"
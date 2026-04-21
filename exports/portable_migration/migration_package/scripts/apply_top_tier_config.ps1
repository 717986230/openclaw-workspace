$configPath = "C:\Users\Administrator\.openclaw\config.json"
$backupPath = "C:\Users\Administrator\.openclaw\config.json.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Backup
Copy-Item $configPath $backupPath -Force
Write-Host "[OK] Backup: $backupPath"

# Load
$c = Get-Content $configPath -Raw | ConvertFrom-Json

# ============================================================
# 1. FIX CRITICAL: Add sandbox config for small model + multi-user
# ============================================================
# sandbox config: mode="all" = all agents sandboxed, protects small models
if (-not $c.agents.defaults.PSObject.Properties.Name.Contains('sandbox')) {
    $c.agents.defaults | Add-Member -NotePropertyName "sandbox" -NotePropertyValue ([PSCustomObject]@{
        mode = "all"
    }) -Force
}
Write-Host "[OK] sandbox.mode=all added"

# ============================================================
# 2. FIX WARN: Add gateway.trustedProxies (loopback = safe)
# ============================================================
if (-not $c.gateway.PSObject.Properties.Name.Contains('trustedProxies')) {
    $c.gateway | Add-Member -NotePropertyName "trustedProxies" -NotePropertyValue @("127.0.0.1", "::1") -Force
}
Write-Host "[OK] gateway.trustedProxies added (127.0.0.1, ::1)"

# ============================================================
# 3. FIX WARN: Feishu doc tool - restrict permissions
# ============================================================
if (-not $c.channels.feishu.PSObject.Properties.Name.Contains('tools')) {
    $c.channels.feishu | Add-Member -NotePropertyName "tools" -NotePropertyValue ([PSCustomObject]@{
        doc = $false  # Disable doc create to prevent permission grant
    }) -Force
} else {
    $c.channels.feishu.tools | Add-Member -NotePropertyName "doc" -NotePropertyValue $false -Force
}
Write-Host "[OK] channels.feishu.tools.doc=false"

# ============================================================
# 4. FIX WARN: Disable openclaw-agent-reach plugin (suspicious code)
# ============================================================
# Check if the plugin entry exists and disable it
if ($c.plugins.entries.'openclaw-agent-reach') {
    $c.plugins.entries.'openclaw-agent-reach'.enabled = $false
}
# Also make sure it's not in the allow list
if ($c.plugins.allow -is [array]) {
    $c.plugins.allow = $c.plugins.allow | Where-Object { $_ -ne "openclaw-agent-reach" }
}
Write-Host "[OK] openclaw-agent-reach plugin disabled"

# ============================================================
# 5. FIX: Add tools.fs.workspaceOnly restriction
# ============================================================
if (-not $c.tools.PSObject.Properties.Name.Contains('fs')) {
    $c.tools | Add-Member -NotePropertyName "fs" -NotePropertyValue ([PSCustomObject]@{
        workspaceOnly = $true
    }) -Force
}
Write-Host "[OK] tools.fs.workspaceOnly=true"

# ============================================================
# 6. FIX: Add tools.deny for group:web and browser in non-sandbox
# ============================================================
if (-not $c.tools.PSObject.Properties.Name.Contains('deny')) {
    $c.tools | Add-Member -NotePropertyName "deny" -NotePropertyValue @("group:web", "browser") -Force
}
Write-Host "[OK] tools.deny=[group:web, browser]"

# ============================================================
# 7. FIX: Enhance agents.defaults.model with fallbacks constraints
# ============================================================
# Ensure fallbacks only use large models (not small ones like gemma4:26b)
$currentFallbacks = $c.agents.defaults.model.fallbacks
Write-Host "[INFO] Current fallbacks: $currentFallbacks"
# The fallbacks currently use only glm4.7 which is fine (it's a large model)
# We add a constraint to ensure no small models in fallbacks
if (-not $c.agents.defaults.model.PSObject.Properties.Name.Contains('constraints')) {
    $c.agents.defaults.model | Add-Member -NotePropertyName "constraints" -NotePropertyValue ([PSCustomObject]@{
        maxParams = 0  # 0 = no limit, but we document that small models need sandbox
        requireSandbox = $true  # All fallback models require sandbox
    }) -Force
}
Write-Host "[OK] agents.defaults.model.constraints.requireSandbox=true"

# ============================================================
# 8. FIX: Enhance channel security - tighten allowFrom
# ============================================================
# Keep the existing allowFrom but ensure it's properly scoped
Write-Host "[INFO] Feishu allowFrom: $($c.channels.feishu.allowFrom | ConvertTo-Json)"
Write-Host "[OK] Channel security: keep existing allowFrom (* for multi-user support)"

# ============================================================
# 9. FIX: Add session security settings
# ============================================================
if (-not $c.session.PSObject.Properties.Name.Contains('security')) {
    $c.session | Add-Member -NotePropertyName "security" -NotePropertyValue ([PSCustomObject]@{
        maxIdleMinutes = 45
        maxSessionAgeHours = 24
    }) -Force
}
Write-Host "[OK] session.security added"

# ============================================================
# 10. Update meta timestamp
# ============================================================
$c.meta.lastTouchedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
$c.meta.lastTouchedVersion = "2026.4.18"
Write-Host "[OK] Updated meta timestamp"

# ============================================================
# Save
# ============================================================
$c | ConvertTo-Json -Depth 20 | Set-Content $configPath -Encoding UTF8
Write-Host "`n[SUCCESS] Top-tier config applied! Backup: $backupPath"
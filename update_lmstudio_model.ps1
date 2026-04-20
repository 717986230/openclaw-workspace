# Update LM Studio model configuration with correct model name

# Read config file
$configPath = "$env:USERPROFILE\.openclaw\config.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json

# Update fallbacks with correct model name
$config.agents.defaults.model.fallbacks = @(
    "nvidia-backup2/z-ai/glm4.7",
    "nvidia-backup1/z-ai/glm4.7",
    "lmstudio/gemma-4-26b-a4b-it-uncensored-max-i1"
)

# Save config file
$config | ConvertTo-Json -Depth 20 | Set-Content $configPath

Write-Host "Config file updated"
Write-Host "Final fallback model changed to: lmstudio/gemma-4-26b-a4b-it-uncensored-max-i1"
Write-Host ""
Write-Host "Available LM Studio models:"
Write-Host "  - gemma-2-2b-it (2B)"
Write-Host "  - gemma-4-26b-a4b-it-uncensored-max-i1 (26B) - LOADED"
Write-Host "  - text-embedding-nomic-embed-text-v1.5 (embedding)"
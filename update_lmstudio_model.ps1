# Update LM Studio model configuration

# Read config file
$configPath = "$env:USERPROFILE\.openclaw\config.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json

# Update fallbacks
$config.agents.defaults.model.fallbacks = @(
    "nvidia-backup2/z-ai/glm4.7",
    "nvidia-backup1/z-ai/glm4.7",
    "lmstudio/gemma-4-26b-it"
)

# Save config file
$config | ConvertTo-Json -Depth 20 | Set-Content $configPath

Write-Host "Config file updated"
Write-Host "Final fallback model changed to: lmstudio/gemma-4-26b-it"
Write-Host ""
Write-Host "Please ensure LM Studio has loaded gemma-4-26b-it model"
Write-Host "LM Studio should be running at http://127.0.0.1:1234"
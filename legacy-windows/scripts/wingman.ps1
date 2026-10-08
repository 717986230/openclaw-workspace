param(
    [string]$SessionName = "",
    [string]$Workdir = "",
    [string]$Prompt = "",
    [switch]$Auto
)

$GitBash = "C:\Program Files\Git\git-bash.exe"
$SkillDir = "$env:USERPROFILE\.agents\skills\claude-code-wingman"

if (-not $Prompt) {
    Write-Host "Usage: wingman.ps1 -SessionName <name> -Workdir <path> -Prompt '<task>' [-Auto]"
    exit 1
}

if (-not $SessionName) {
    $SessionName = "claude-$(Get-Date -Format 'yyyyMMddHHmmss')"
}

# Build the command
$cmd = "bash `"$SkillDir/claude-wingman.sh`" --session $SessionName"
if ($Workdir) {
    $cmd += " --workdir `"$Workdir`""
}
$cmd += " --prompt `"$Prompt`""
if ($Auto) {
    $cmd += " --auto"
}

Write-Host "[Wingman] Running: $cmd"
& $GitBash -c $cmd
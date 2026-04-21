# create-pr-flow.ps1
# Create PR for system-design-primer

$ErrorActionPreference = "Stop"

# Check if fork exists
$forkExists = gh repo view 717986230/system-design-primer 2>&1
if ($forkExists -match "does not exist") {
    Write-Host "Creating fork..."
    gh repo fork donnemartin/system-design-primer --clone=true --remote=true D:\CODE\system-design-primer-fork
} else {
    Write-Host "Fork already exists"
}

# Clone fork
$workDir = "D:\CODE\system-design-primer-fork"
if (-not (Test-Path $workDir)) {
    Write-Host "Cloning fork..."
    gh repo clone 717986230/system-design-primer $workDir
}

Set-Location $workDir

# Ensure we're up to date
Write-Host "Updating from upstream..."
git fetch origin
git checkout master
git pull origin master

# Create branch for PR
$branchName = "add-georgian-translation"
Write-Host "Creating branch: $branchName"
git checkout -b $branchName

# Get README content for translation reference
Write-Host "`n=== Creating Georgian Translation ==="
Write-Host "This PR will add Georgian language translation to README"
Write-Host "Branch: $branchName"
Write-Host "Target: donnemartin/system-design-primer"
Write-Host "Issue: #1193"

# Commit placeholder
Write-Host "`nReady to create commit and PR"
Write-Host "Next steps:"
Write-Host "1. Add Georgian translation content"
Write-Host "2. git add ."
Write-Host "3. git commit -m 'Add Georgian translation (fixes #1193)'"
Write-Host "4. git push -u origin $branchName"
Write-Host "5. gh pr create --repo donnemartin/system-design-primer --title 'Add Georgian translation' --body 'Fixes #1193'"

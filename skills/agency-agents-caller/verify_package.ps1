# 验证技能包完整性

$skillDir = "C:\Users\Administrator\.openclaw\workspace\skills\agency-agents-caller"

Write-Host "=" * 70
Write-Host "Agency Agents Caller - Skill Package Verification"
Write-Host "=" * 70

$requiredFiles = @(
    "SKILL.md",
    "README.md",
    "package.json",
    "scripts\agent_caller.py",
    "examples\usage_demo.py"
)

Write-Host "`nChecking required files:" -ForegroundColor Yellow

$allPresent = $true
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $skillDir $file
    if (Test-Path $filePath) {
        $size = (Get-Item $filePath).Length
        Write-Host "  [OK] $file ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
        $allPresent = $false
    }
}

Write-Host "`nOptional files:" -ForegroundColor Yellow

$optionalFiles = @(
    "publish.py",
    "create_package.ps1",
    "PACKAGE_INFO.md"
)

foreach ($file in $optionalFiles) {
    $filePath = Join-Path $skillDir $file
    if (Test-Path $filePath) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    }
}

if ($allPresent) {
    Write-Host "`n" + ("=" * 70)
    Write-Host "All required files present!" -ForegroundColor Green
    Write-Host "Skill package is ready for publishing." -ForegroundColor Cyan
    Write-Host "=" * 70
    
    Write-Host @"

Next Steps:

1. Publish to ClawHub:
   cd $skillDir
   clawhub publish

2. Or use Web UI:
   Visit: https://clawhub.com/publish
   Upload all files

3. After publishing:
   Users can install: clawhub install agency-agents-caller

"@
} else {
    Write-Host "`nSome required files are missing!" -ForegroundColor Red
}

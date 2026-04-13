cd C:\Users\Administrator\.openclaw\workspace\skills

Write-Host "Checking SKILL.md format..." -ForegroundColor Yellow
Get-Content agency-agents-caller\SKILL.md -First 15

Write-Host "`nAttempting to publish..." -ForegroundColor Yellow
Set-Location agency-agents-caller

# Try different publish methods
Write-Host "`nMethod 1: Direct publish" -ForegroundColor Cyan
clawhub publish . --version "1.0.0"

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nMethod 2: With explicit path" -ForegroundColor Cyan
    clawhub publish C:\Users\Administrator\.openclaw\workspace\skills\agency-agents-caller --version "1.0.0"
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nMethod 3: Sync method" -ForegroundColor Cyan
    cd C:\Users\Administrator\.openclaw\workspace
    clawhub sync
}

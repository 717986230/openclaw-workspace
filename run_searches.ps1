
# Run multiple searches
$ErrorActionPreference = "Stop"

. "C:\Users\admin\.openclaw\workspace\search_hn.ps1"

Write-Host "========================================"
Write-Host "  Multi-Topic Search"
Write-Host "========================================"
Write-Host ""

$topics = @("deployment", "devops", "programming tools", "CI/CD")
$allResults = @{}

foreach ($topic in $topics) {
    Write-Host "`n--- Searching: $topic ---`n"
    $results = & "C:\Users\admin\.openclaw\workspace\search_hn.ps1" -Query $topic -Limit 5
    if ($results) {
        $allResults[$topic] = $results
    }
    Start-Sleep -Milliseconds 500
}

Write-Host "`n`n========================================"
Write-Host "  All searches complete!"
Write-Host "========================================"
Write-Host "Saving results..."

$allResults | ConvertTo-Json -Depth 10 | Out-File -FilePath "C:\Users\admin\.openclaw\workspace\search_results.json" -Encoding UTF8

Write-Host "Results saved to search_results.json"

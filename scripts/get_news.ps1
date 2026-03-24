
$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LATEST WORLD NEWS - Hacker News" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get top stories from Hacker News
$url = "https://hn.algolia.com/api/v1/search?tags=story,front_page&amp;hitsPerPage=15"
$response = Invoke-RestMethod -Uri $url -UseBasicParsing

$stories = $response.hits

for ($i = 0; $i -lt $stories.Count; $i++) {
    $story = $stories[$i]
    $num = $i + 1
    
    Write-Host "$num. $($story.title)" -ForegroundColor White
    
    $info = @()
    if ($story.points) { $info += "$($story.points) points" }
    if ($story.num_comments) { $info += "$($story.num_comments) comments" }
    if ($story.author) { $info += "by $($story.author)" }
    
    if ($info.Count -gt 0) {
        Write-Host "   $($info -join ' | ')" -ForegroundColor Gray
    }
    
    if ($story.url) {
        Write-Host "   $($story.url)" -ForegroundColor DarkGray
    }
    
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[OK] News fetched successfully!" -ForegroundColor Green


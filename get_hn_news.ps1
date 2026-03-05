
# Simple Hacker News Fetcher
# Avoids encoding issues by using simple URLs

$ErrorActionPreference = "Stop"

# Build URL manually to avoid encoding issues
$baseUrl = "https://hn.algolia.com/api/v1/search"
$query = "ai"
$tags = "story"
$hitsPerPage = 10

# Use WebClient instead of Invoke-RestMethod for better control
$webClient = New-Object System.Net.WebClient
$webClient.Encoding = [System.Text.Encoding]::UTF8

# Construct URL carefully
$url = $baseUrl + "?query=" + $query + "&tags=" + $tags + "&hitsPerPage=" + $hitsPerPage

Write-Host "Fetching from: $url"
Write-Host ""

try {
    $json = $webClient.DownloadString($url)
    $data = $json | ConvertFrom-Json
    
    $news = $data.hits | Select-Object -First 8
    
    Write-Host "========================================"
    Write-Host "  Hacker News AI Top Stories"
    Write-Host "========================================"
    Write-Host ""
    
    $index = 1
    foreach ($item in $news) {
        Write-Host "$index. $($item.title)"
        Write-Host "   Points: $($item.points) | Comments: $($item.num_comments)"
        if ($item.url) {
            Write-Host "   URL: $($item.url)"
        }
        Write-Host ""
        $index++
    }
    
    Write-Host "========================================"
    Write-Host "  Done! Fetched $($news.Count) stories"
    Write-Host "========================================"
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

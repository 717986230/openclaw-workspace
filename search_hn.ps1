
# Hacker News Search Tool
# Supports multiple search queries

param(
    [string]$Query = "ai",
    [int]$Limit = 8
)

$ErrorActionPreference = "Stop"

$baseUrl = "https://hn.algolia.com/api/v1/search"
$tags = "story"

$webClient = New-Object System.Net.WebClient
$webClient.Encoding = [System.Text.Encoding]::UTF8

# Build URL step by step
$url = $baseUrl + "?query=" + $Query + "&tags=" + $tags + "&hitsPerPage=" + $Limit

Write-Host "Searching for: $Query"
Write-Host "Fetching from: $url"
Write-Host ""

try {
    $json = $webClient.DownloadString($url)
    $data = $json | ConvertFrom-Json
    
    $news = $data.hits | Select-Object -First $Limit
    
    Write-Host "========================================"
    Write-Host "  Hacker News: $Query"
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
    
    # Return data for further processing
    return $news
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    return $null
}

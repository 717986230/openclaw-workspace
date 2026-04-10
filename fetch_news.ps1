
$baseUrl = "https://hn.algolia.com/api/v1/search"
$query = "ai"
$tags = "story"
$hitsPerPage = 15

$url = "$baseUrl`?query=$query&amp;tags=$tags&amp;hitsPerPage=$hitsPerPage"

Write-Host "Fetching news from: $url"

$response = Invoke-RestMethod -Uri $url -UseBasicParsing

$news = $response.hits | Select-Object -First 10

Write-Host "`n馃摪 Hacker News AI 鐑棬鏂伴椈`n" -ForegroundColor Cyan

$index = 1
foreach ($item in $news) {
    $date = [DateTime]$item.created_at
    Write-Host "$index. `"$($item.title)`"" -ForegroundColor White
    Write-Host "   馃搮 $($date.ToString('yyyy-MM-dd')) | 馃憤 $($item.points) 鐐?| 馃挰 $($item.num_comments) 鏉¤瘎璁? -ForegroundColor Gray
    if ($item.url) {
        Write-Host "   馃敆 $($item.url)" -ForegroundColor Blue
    }
    Write-Host ""
    $index++
}

# 淇濆瓨鍒版枃浠?$news | ConvertTo-Json -Depth 10 | Out-File -FilePath "C:\Users\Administrator\.openclaw\workspace\news_data.json" -Encoding UTF8

Write-Host "鉁?鏂伴椈宸蹭繚瀛樺埌 news_data.json" -ForegroundColor Green

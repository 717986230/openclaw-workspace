
$baseUrl = "https://hn.algolia.com/api/v1/search"
$query = "ai"
$tags = "story"
$hitsPerPage = 15

$url = "$baseUrl`?query=$query&amp;tags=$tags&amp;hitsPerPage=$hitsPerPage"

Write-Host "Fetching news from: $url"

$response = Invoke-RestMethod -Uri $url -UseBasicParsing

$news = $response.hits | Select-Object -First 10

Write-Host "`n📰 Hacker News AI 热门新闻`n" -ForegroundColor Cyan

$index = 1
foreach ($item in $news) {
    $date = [DateTime]$item.created_at
    Write-Host "$index. `"$($item.title)`"" -ForegroundColor White
    Write-Host "   📅 $($date.ToString('yyyy-MM-dd')) | 👍 $($item.points) 点 | 💬 $($item.num_comments) 条评论" -ForegroundColor Gray
    if ($item.url) {
        Write-Host "   🔗 $($item.url)" -ForegroundColor Blue
    }
    Write-Host ""
    $index++
}

# 保存到文件
$news | ConvertTo-Json -Depth 10 | Out-File -FilePath "C:\Users\admin\.openclaw\workspace\news_data.json" -Encoding UTF8

Write-Host "✅ 新闻已保存到 news_data.json" -ForegroundColor Green

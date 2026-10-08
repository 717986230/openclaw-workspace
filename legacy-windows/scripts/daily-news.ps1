# 每日新闻推送脚本
Write-Host "📰 开始获取今日新闻..." -ForegroundColor Green

# 获取 Hacker News AI 热门新闻
try {
    $news = Invoke-RestMethod -Uri "https://hn.algolia.com/api/v1/search?query=china&tags=story&hitsPerPage=5" -UseBasicParsing
    
    $output = "`n📰 今日新闻简报`n`n"
    
    $index = 1
    foreach ($item in $news.hits) {
        $output += "$index. `"$($item.title)`"`n"
        $output += "   - $($item.points) 点，$($item.num_comments) 条评论`n"
        if ($item.url) {
            $output += "   - $($item.url)`n"
        }
        $output += "`n"
        $index++
    }
    
    Write-Host $output
    return $output
}
catch {
    Write-Host "❌ 获取新闻失败: $_" -ForegroundColor Red
    return "❌ 今日新闻获取失败，请稍后再试。"
}

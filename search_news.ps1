
# 搜索全球新闻脚本

function Get-GlobalNews {
    param(
        [string]$Query = "world news",
        [int]$Limit = 10
    )
    
    $url = "https://hn.algolia.com/api/v1/search?query=$([Uri]::EscapeDataString($Query))&tags=story&hitsPerPage=$Limit"
    try {
        $response = Invoke-RestMethod -Uri $url -UseBasicParsing
        return $response.hits
    } catch {
        Write-Error "搜索失败: $_"
        return @()
    }
}

function Format-NewsResults {
    param($News, [string]$Title = "🌍 全球新闻")
    
    $output = "`n$Title`n"
    $output += "=" * 60 + "`n`n"
    
    if ($News -and $News.Count -gt 0) {
        $index = 1
        foreach ($item in $News) {
            if ($item.title) {
                $output += "$index. `"$($item.title)`"`n"
                if ($item.points -or $item.num_comments) {
                    $output += "   热度: $($item.points) 点 · $($item.num_comments) 评论`n"
                }
                if ($item.url) {
                    $output += "   链接: $($item.url)`n"
                }
                if ($item.created_at) {
                    $output += "   时间: $($item.created_at)`n"
                }
                $output += "`n"
                $index++
            }
        }
    } else {
        $output += "❌ 没有找到相关新闻`n`n"
    }
    
    $output += "=" * 60 + "`n"
    return $output
}

Write-Host "🔍 正在搜索战火消息..." -ForegroundColor Yellow
$warNews = Get-GlobalNews -Query "war conflict military attack tension" -Limit 15
Format-NewsResults -News $warNews -Title "🔥 战火消息"

Write-Host "`n🔍 正在搜索原油市场动态..." -ForegroundColor Yellow
$oilNews = Get-GlobalNews -Query "oil crude prices market OPEC energy" -Limit 15
Format-NewsResults -News $oilNews -Title "🛢️ 原油市场动态"

Write-Host "`n✅ 搜索完成！" -ForegroundColor Green


# 使用代理搜索新闻

# 设置代理
$proxyUri = [System.Uri]"http://127.0.0.1:7891"
$proxy = New-Object System.Net.WebProxy($proxyUri)
$proxy.BypassProxyOnLocal = $false
[System.Net.WebRequest]::DefaultWebProxy = $proxy

function Get-GlobalNews {
    param(
        [string]$Query = "world news",
        [int]$Limit = 10
    )
    
    $url = "https://hn.algolia.com/api/v1/search?query=$([Uri]::EscapeDataString($Query))&amp;tags=story&amp;hitsPerPage=$Limit"
    
    try {
        $wc = New-Object System.Net.WebClient
        $wc.Proxy = $proxy
        $wc.Encoding = [System.Text.Encoding]::UTF8
        $json = $wc.DownloadString($url)
        $data = $json | ConvertFrom-Json
        return $data.hits
    } catch {
        Write-Error "搜索失败: $_"
        return @()
    }
}

function Format-NewsResults {
    param($News, [string]$Title = "🌍 全球新闻")
    
    $output = "`n" + "="*60 + "`n"
    $output += "  $Title`n"
    $output += "="*60 + "`n`n"
    
    if ($News -and $News.Count -gt 0) {
        $index = 1
        foreach ($item in $News) {
            if ($item.title) {
                $output += "$index. `"$($item.title)`"`n"
                
                $parts = @()
                if ($item.author) { $parts += "作者: $($item.author)" }
                if ($item.points -ne $null) { $parts += "热度: $($item.points) 点" }
                if ($item.num_comments -ne $null) { $parts += "评论: $($item.num_comments)" }
                if ($parts) { $output += "   $($parts -join ' · ')`n" }
                
                if ($item.url) { $output += "   链接: $($item.url)`n" }
                if ($item.created_at) { $output += "   时间: $($item.created_at)`n" }
                
                $output += "`n"
                $index++
            }
        }
    } else {
        $output += "❌ 没有找到相关新闻`n`n"
    }
    
    $output += "="*60 + "`n"
    return $output
}

Write-Host "🔍 正在搜索战火消息..." -ForegroundColor Yellow
$warNews = Get-GlobalNews -Query "war conflict military attack tension" -Limit 15
Format-NewsResults -News $warNews -Title "🔥 战火消息"

Write-Host "`n🔍 正在搜索原油市场动态..." -ForegroundColor Yellow
$oilNews = Get-GlobalNews -Query "oil crude prices market OPEC energy" -Limit 15
Format-NewsResults -News $oilNews -Title "🛢️ 原油市场动态"

Write-Host "`n✅ 搜索完成！" -ForegroundColor Green

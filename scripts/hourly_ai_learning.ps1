# 每小时AI学习脚本 - 双源版（Hacker News + Twitter/X）
# 功能：多源搜索AI内容、提炼学习、写入记忆系统

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$memoryDir = "C:\Users\Administrator\.openclaw\workspace\memory\learnings"
$eventsDir = "C:\Users\Administrator\.openclaw\workspace\memory\events"

# 确保目录存在
@($memoryDir, $eventsDir) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

Write-Host "[$timestamp] 🚀 开始每小时AI学习任务（双源模式）..."

$dateStr = Get-Date -Format "yyyy-MM-dd"
$learningFile = Join-Path $memoryDir "ai-learnings-$dateStr.md"

# ========== 源1：Hacker News AI热门 ==========
Write-Host "`n📊 [1/2] 获取 Hacker News AI热门文章..."

$hnContent = @"
## Hacker News AI热门

"@

try {
    $hnUrl = "https://hn.algolia.com/api/v1/search?query=ai artificial intelligence&tags=story&hitsPerPage=5"
    $hnResponse = Invoke-RestMethod -Uri $hnUrl -UseBasicParsing -TimeoutSec 30
    $articles = $hnResponse.hits
    
    Write-Host "  ✅ 获取到 $($articles.Count) 篇文章"
    
    foreach ($article in $articles) {
        $title = $article.title
        $url = $article.url
        $points = $article.points
        $comments = $article.num_comments
        
        $hnContent += @"
### 📰 $title
- **热度**: $points 点 | **评论**: $comments 条
- **链接**: $url
- **时间**: $($article.created_at)

"@
        Write-Host "  - $title"
    }
} catch {
    $hnContent += "❌ 获取失败: $($_.Exception.Message)`n"
    Write-Host "  ❌ HN获取失败: $($_.Exception.Message)"
}

# ========== 源2：Twitter/X AI大V推文 ==========
Write-Host "`n🐦 [2/2] 获取 Twitter/X AI领域内容..."

$twitterContent = @"
## Twitter/X AI内容

"@

# 检查是否有TWITTER_TOKEN
$twitterToken = $env:TWITTER_TOKEN
if (-not $twitterToken) {
    # 尝试从环境变量文件读取
    $envFile = "C:\Users\Administrator\.openclaw\config\twitter_token.txt"
    if (Test-Path $envFile) {
        $twitterToken = Get-Content $envFile -Raw | ForEach-Object { $_.Trim() }
    }
}

if ($twitterToken) {
    try {
        # AI领域KOL账号列表
        $aiKOLs = @("karpathy", "sama", "ylecun", "AndrewYNg", "jeffdean")
        $tweetsPerUser = 3
        
        foreach ($username in $aiKOLs) {
            $body = @{
                username = $username
                maxResults = $tweetsPerUser
                product = "Top"
                excludeReplies = $true
                excludeRetweets = $true
            } | ConvertTo-Json
            
            $headers = @{
                "Authorization" = "Bearer $twitterToken"
                "Content-Type" = "application/json"
            }
            
            $response = Invoke-RestMethod -Uri "https://ai.6551.io/open/twitter_user_tweets" -Method POST -Headers $headers -Body $body -UseBasicParsing -TimeoutSec 30
            
            if ($response.data) {
                $twitterContent += "### 🎯 @$username`n`n"
                foreach ($tweet in $response.data) {
                    $text = $tweet.text -replace "`n", " " -replace "`r", ""
                    if ($text.Length -gt 200) { $text = $text.Substring(0, 200) + "..." }
                    
                    $twitterContent += "- **推文**: $text`n"
                    $twitterContent += "  - ❤️ $($tweet.favoriteCount) | 🔄 $($tweet.retweetCount) | 💬 $($tweet.replyCount)`n"
                    $twitterContent += "  - 链接: https://x.com/$username/status/$($tweet.id)`n`n"
                }
                Write-Host "  ✅ @$username - $($response.data.Count) 条推文"
            }
        }
        
        # 搜索热门AI话题
        $searchBody = @{
            keywords = "AI artificial intelligence"
            minLikes = 500
            product = "Top"
            maxResults = 5
            lang = "en"
        } | ConvertTo-Json
        
        $searchResponse = Invoke-RestMethod -Uri "https://ai.6551.io/open/twitter_search" -Method POST -Headers $headers -Body $searchBody -UseBasicParsing -TimeoutSec 30
        
        if ($searchResponse.data) {
            $twitterContent += "### 🔥 热门AI推文`n`n"
            foreach ($tweet in $searchResponse.data) {
                $text = $tweet.text -replace "`n", " " -replace "`r", ""
                if ($text.Length -gt 200) { $text = $text.Substring(0, 200) + "..." }
                $author = $tweet.userScreenName
                
                $twitterContent += "- **@$author**: $text`n"
                $twitterContent += "  - ❤️ $($tweet.favoriteCount) | 🔄 $($tweet.retweetCount)`n`n"
            }
            Write-Host "  ✅ 热门AI搜索 - $($searchResponse.data.Count) 条推文"
        }
        
    } catch {
        $twitterContent += "❌ Twitter获取失败: $($_.Exception.Message)`n"
        Write-Host "  ❌ Twitter获取失败: $($_.Exception.Message)"
    }
} else {
    $twitterContent += "⚠️ 未配置TWITTER_TOKEN，跳过Twitter源`n"
    $twitterContent += "获取Token: https://6551.io/mcp`n"
    $twitterContent += "设置: 环境变量 TWITTER_TOKEN 或保存到 config/twitter_token.txt`n"
    Write-Host "  ⚠️ 未配置TWITTER_TOKEN，跳过Twitter源"
}

# ========== 汇总写入 ==========
$fullContent = @"
# AI学习记录 - $timestamp

$hnContent
$twitterContent
---

*双源采集 | Hacker News + Twitter/X | $timestamp*
"@

$fullContent | Out-File -FilePath $learningFile -Encoding UTF8 -Append
Write-Host "`n✅ 学习记录已保存: $learningFile"

# 记录执行事件
$eventFile = Join-Path $eventsDir "hourly-learning-$(Get-Date -Format 'yyyy-MM').log"
"[$timestamp] ✅ 执行完成 (HN + Twitter)" | Out-File -FilePath $eventFile -Encoding UTF8 -Append

Write-Host "[$timestamp] 🎉 任务完成"

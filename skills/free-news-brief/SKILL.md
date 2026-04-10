---
name: free-news-brief
description: Fetch free AI and tech news from Hacker News, TechCrunch, and other free sources. No API key required, no payment needed. Use when user asks for news, AI news, tech news, or news briefings.
version: 1.0.0
tags:
  - news
  - ai
  - tech
  - free
  - hacker-news
---

# Free News Brief

免费获取AI和科技新闻的技能，无需API密钥，无需付费。

## 功能

- 📰 Hacker News - 从Hacker News获取热门AI/科技新闻
- 🔍 免费搜索 - 使用DuckDuckGo等免费API
- 📊 新闻摘要 - 提供标题、点数、评论数和链接

## 使用场景

"给我新闻" / "AI新闻" / "科技新闻" / "新闻简报"

## 免费新闻源

### 1. Hacker News (推荐)

**API端点**: `https://hn.algolia.com/api/v1/search`

**参数**:
- `query`: 搜索关键词（如 "ai", "artificial intelligence"）
- `tags`: 过滤类型（如 "story"）
- `hitsPerPage`: 结果数量（1-100）

**示例**:
```powershell
# 获取AI相关热门故事
Invoke-RestMethod "https://hn.algolia.com/api/v1/search?query=ai&tags=story&hitsPerPage=10"
```

**返回字段**:
- `title`: 新闻标题
- `url`: 原文链接
- `author`: 作者
- `points`: 点数（赞）
- `num_comments`: 评论数
- `created_at`: 创建时间

### 2. DuckDuckGo Instant Answer

**API端点**: `https://api.duckduckgo.com/`

**参数**:
- `q`: 搜索查询
- `format`: 输出格式（json）
- `no_html`: 1（不包含HTML）

**示例**:
```powershell
Invoke-RestMethod "https://api.duckduckgo.com/?q=AI+news&format=json&no_html=1"
```

## 使用流程

1. **用户请求新闻** → 优先使用Hacker News
2. **搜索关键词** → 根据用户需求选择（"ai", "tech", "startup"等）
3. **返回结果** → 展示标题、点数、评论数、链接
4. **详细查看** → 用户可以选择某条新闻查看详情

## 示例输出

```
📰 Hacker News AI 热门新闻

1. "Open source AI is the path forward" (2024-07-23)
   - 2360 点，887 条评论
   - https://about.fb.com/news/2024/07/open-source-ai-is-the-path-forward/

2. "An AI agent published a hit piece on me" (2026-02-12)
   - 2346 点，951 条评论
   - https://theshamblog.com/an-ai-agent-published-a-hit-piece-on-me/
```

## PowerShell 辅助函数

```powershell
function Get-HackerNews {
    param(
        [string]$Query = "ai",
        [int]$Limit = 10
    )
    
    $url = "https://hn.algolia.com/api/v1/search?query=$([Uri]::EscapeDataString($Query))&tags=story&hitsPerPage=$Limit"
    $response = Invoke-RestMethod -Uri $url -UseBasicParsing
    return $response.hits
}

function Format-News {
    param($News)
    
    $output = "📰 Hacker News 热门新闻`n`n"
    $index = 1
    
    foreach ($item in $News) {
        $output += "$index. `"$($item.title)`"`n"
        $output += "   - $($item.points) 点，$($item.num_comments) 条评论`n"
        $output += "   - $($item.url)`n`n"
        $index++
    }
    
    return $output
}
```

## 注意事项

- 所有API都是免费的，无需认证
- 尊重Rate Limits，不要频繁请求
- 优先使用Hacker News，质量较高
- 如果需要更具体的新闻，让用户提供关键词

---

*免费新闻，无隐藏费用*

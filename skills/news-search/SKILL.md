---
name: news-search
description: Search and fetch news using various free APIs and sources.
---

# News Search Skill

获取新闻的技能。

## Free News Sources

1. **DuckDuckGo API** - https://api.duckduckgo.com/
2. **NewsAPI** - https://newsapi.org/ (needs key)
3. **GNews** - https://gnews.io/ (needs key)
4. **RSS feeds** - Various news sites

## Simple Search Function

```powershell
function Get-News {
    param([string]$Query = "today's news")
    
    try {
        $response = Invoke-RestMethod -Uri "https://api.duckduckgo.com/?q=$([Uri]::EscapeDataString($Query))&format=json&no_html=1" -UseBasicParsing
        return $response
    } catch {
        Write-Error "Failed to fetch news: $_"
    }
}
```

---

*Search for news.*

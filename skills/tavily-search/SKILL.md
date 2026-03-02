---
name: tavily-search
description: Web search using Tavily AI Search API. Use when: user asks to search the web, look up current events, find information online, research topics, fact-check, or get up-to-date information from the internet. Requires Tavily API key (set in TAVILY_API_KEY environment variable).
---

# Tavily Search Skill

AI-optimized web search using Tavily Search API.

## When to Use

✅ **USE this skill when:**
- "Search the web for..."
- "Find information about..."
- "What's the latest news on..."
- "Research..."
- "Fact-check..."
- Any query that requires up-to-date internet information

❌ **DON'T use this skill when:**
- Information is already in context or memory
- Static knowledge that doesn't change over time
- Simple calculations or reasoning tasks

## Setup

Set your Tavily API key:
```powershell
$env:TAVILY_API_KEY = "tvly-xxxxxxxxxxxxxxxxx"
```

Or set permanently in your environment variables.

## API Usage

### Basic Search

```powershell
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $env:TAVILY_API_KEY"
}

$body = @{
    query = "your search query"
    search_depth = "basic"  # or "advanced"
    include_answer = $true
    max_results = 5
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "https://api.tavily.com/search" -Method Post -Headers $headers -Body $body
$response
```

### Search with Raw Content

```powershell
$body = @{
    query = "your search query"
    search_depth = "advanced"
    include_answer = $true
    include_raw_content = $true
    max_results = 10
} | ConvertTo-Json
```

### Quick Search Function

Create a helper function for easy searching:

```powershell
function Search-Tavily {
    param(
        [Parameter(Mandatory)]
        [string]$Query,
        [int]$MaxResults = 5,
        [switch]$Advanced
    )
    
    if (-not $env:TAVILY_API_KEY) {
        Write-Error "TAVILY_API_KEY environment variable not set"
        return
    }
    
    $headers = @{
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $env:TAVILY_API_KEY"
    }
    
    $body = @{
        query = $Query
        search_depth = if ($Advanced) { "advanced" } else { "basic" }
        include_answer = $true
        max_results = $MaxResults
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "https://api.tavily.com/search" -Method Post -Headers $headers -Body $body
        return $response
    } catch {
        Write-Error "Search failed: $_"
    }
}
```

## Response Format

Tavily returns:
- `answer`: AI-generated summary answer
- `results`: Array of search results with title, url, content
- `images`: Related images (if requested)
- `follow_up_questions`: Suggested follow-up questions

## Get API Key

Get your Tavily API key from: https://tavily.com/

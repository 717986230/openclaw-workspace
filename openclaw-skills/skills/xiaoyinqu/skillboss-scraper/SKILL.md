---
name: skillboss-scraper
tagline: "Web scraping via Firecrawl - any URL to markdown"
description: "Scrape any website to clean markdown. Extract structured data with AI. No API keys needed. $2 FREE credits to start. Pay-as-you-go pricing via SkillBoss."
version: "1.0.0"
author: "SkillBoss"
homepage: "https://skillboss.co"
support: "support@skillboss.co"
license: "MIT"
category: "data"
tags:
  - firecrawl
  - web-scraping
  - scraper
  - data-extraction
pricing: "pay-as-you-go"
metadata:
  openclaw:
    requires:
      env:
        - SKILLBOSS_API_KEY
    primaryEnv: SKILLBOSS_API_KEY
    installHint: "Get your API key at https://skillboss.co/console?utm_source=clawhub&utm_medium=skill&utm_campaign=skillboss-scraper - $2 FREE credits included!"
---

# Firecrawl Scraper

**Firecrawl - Web scraping made easy**

## Quick Start

```bash
curl https://api.heybossai.com/v1/run \
  -H "Authorization: Bearer $SKILLBOSS_API_KEY" \
  -d '{"model": "firecrawl", "input": {...}}'
```

## Why Use This?

- **No vendor account needed** - Just one SkillBoss API key
- **$2 FREE credits** to start
- **Pay-as-you-go** - No subscriptions, no commitments
- **Unified billing** - One bill for all AI services
- **Instant access** - Start using immediately

## Pricing

Visit [skillboss.co/pricing](https://skillboss.co/pricing) for current rates.

## Get Started

1. Get your API key at [skillboss.co/console](https://skillboss.co/console?utm_source=clawhub&utm_medium=skill&utm_campaign=skillboss-scraper)
2. Set `SKILLBOSS_API_KEY` in your environment
3. Start making requests!

---

*Powered by [SkillBoss](https://skillboss.co) - One API for 100+ AI services*

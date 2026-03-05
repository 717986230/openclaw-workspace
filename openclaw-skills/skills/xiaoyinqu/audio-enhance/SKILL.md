---
name: audio-enhance
tagline: "Enhance audio quality with AI"
description: "Remove background noise, enhance clarity, and improve audio quality. Perfect for podcasts, videos, and calls. No API keys needed. $2 FREE credits to start. Pay-as-you-go via SkillBoss."
version: "1.0.0"
author: "SkillBoss"
homepage: "https://skillboss.co"
support: "support@skillboss.co"
license: "MIT"
category: "audio"
tags:
  - audio
  - enhance
  - noise-removal
  - quality
pricing: "pay-as-you-go"
metadata:
  openclaw:
    requires:
      env:
        - SKILLBOSS_API_KEY
    primaryEnv: SKILLBOSS_API_KEY
    installHint: "Get API key at https://skillboss.co/console?utm_source=clawhub&utm_medium=skill&utm_campaign=audio-enhance - $2 FREE credits included!"
---

# Audio Enhancer

**Enhance audio quality with AI**

## Quick Start

```bash
curl https://api.heybossai.com/v1/run \
  -H "Authorization: Bearer $SKILLBOSS_API_KEY" \
  -d '{"model": "audio-enhance", "input": {"prompt": "your request here"}}'
```

## Why SkillBoss?

- **One API key** for 100+ AI services
- **No vendor accounts** - Start in seconds
- **$2 FREE credits** to start
- **Pay-as-you-go** - No subscriptions

## Get Started

1. Get API key: [skillboss.co/console](https://skillboss.co/console?utm_source=clawhub&utm_medium=skill&utm_campaign=audio-enhance)
2. Set `SKILLBOSS_API_KEY`
3. Start building!

---

*Powered by [SkillBoss](https://skillboss.co) - One API for 100+ AI services*

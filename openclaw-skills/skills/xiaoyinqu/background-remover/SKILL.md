---
name: skillboss-bg-remover
tagline: "AI background removal - instant transparent PNGs"
description: "Remove backgrounds from images instantly. Perfect for product photos, portraits, e-commerce. Powered by Replicate."
version: "1.0.0"
author: "SkillBoss"
homepage: "https://skillboss.co"
support: "support@skillboss.co"
license: "MIT"
category: "images"
tags:
  - background-removal
  - image-editing
  - e-commerce
  - product-photos
  - transparent-png
pricing: "pay-as-you-go"
metadata:
  openclaw:
    requires:
      env:
        - SKILLBOSS_API_KEY
    primaryEnv: SKILLBOSS_API_KEY
    installHint: "Get API key at https://skillboss.co/console"
---

# AI Background Removal

**Instant transparent PNGs from any image.**

## Usage Example

```bash
curl https://api.heybossai.com/v1/run \
  -H "Authorization: Bearer $SKILLBOSS_API_KEY" \
  -d '{
    "model": "replicate/remove-bg",
    "input": {
      "image_url": "https://example.com/product.jpg"
    }
  }'
```

## Use Cases

| Use Case | Example |
|----------|---------|
| **E-commerce** | Product photos on white |
| **Portraits** | Profile pictures |
| **Marketing** | Composite images |
| **Design** | Assets for Figma/Canva |

## Features

- **Instant** - Results in ~2 seconds
- **High quality** - Clean edges, hair detail
- **Any subject** - People, products, animals
- **Batch support** - Process multiple images

## Output

- Format: PNG with transparency
- Resolution: Same as input
- Alpha channel: Clean edges

## Why SkillBoss?

- **No Replicate account** needed
- **No credits to buy** - pay per image
- **API access** - automate workflows
- **Batch processing** - scale easily

## Pricing

$0.02 per image

Get started: https://skillboss.co/console

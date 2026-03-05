---
name: publora-telegram
description: >
  Post or schedule content to Telegram channels and groups using the Publora
  API. Use this skill when the user wants to publish or schedule Telegram
  messages via Publora.
---

# Publora — Telegram

Post and schedule Telegram channel/group content via the Publora API.

> **Prerequisite:** Install the `publora` core skill for auth setup and getting platform IDs.

## Platform ID Format

`telegram-{chatId}` — get your exact ID from `GET /api/v1/platform-connections`.

## Setup

1. Create a bot via **@BotFather** on Telegram → `/newbot` → copy the bot token
2. Add the bot as **admin** to your channel or group
3. In Publora dashboard: provide the bot token + channel name (`@mychannel` for public, numeric ID for private channels)

⚠️ **Bot must be admin.** Without admin permissions, posts will fail.

## Character Limits

| Content Type | Limit |
|-------------|-------|
| Text message | 1,024 chars (bot API) or 4,096 chars (MTProto) |
| Media caption | 1,024 chars (stricter than text-only) |

## Supported Content

| Type | Supported | Notes |
|------|-----------|-------|
| Text only | ✅ | With Markdown formatting |
| Images | ✅ | JPEG; WebP auto-converted to JPEG |
| Videos | ✅ | MP4 |
| Markdown formatting | ✅ | See reference below |

## Post to Telegram

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: '**New release: v2.0** 🚀\n\nWe just shipped the biggest update yet. [Read the full changelog](https://example.com/changelog)',
    platforms: ['telegram-CHAT_ID']
  })
});
```

## Schedule a Post

```javascript
body: JSON.stringify({
  content: '**Weekly Digest** 📰\n\n_Top stories from this week..._',
  platforms: ['telegram-CHAT_ID'],
  scheduledTime: '2026-03-16T09:00:00.000Z'
})
```

## Post with Image

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

# Step 1: Create post
post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': '**New feature preview!** 👀\n\nHere is a first look at what we are shipping next week.',
    'platforms': ['telegram-CHAT_ID']
}).json()
post_group_id = post['postGroupId']

# Step 2: Get upload URL
upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
    'fileName': 'preview.jpg', 'contentType': 'image/jpeg',
    'type': 'image', 'postGroupId': post_group_id
}).json()

# Step 3: Upload to S3 (caption limit: 1,024 chars)
with open('preview.jpg', 'rb') as f:
    requests.put(upload['uploadUrl'], headers={'Content-Type': 'image/jpeg'}, data=f)
```

**WebP note:** WebP images are automatically converted to JPEG by Publora.

## Markdown Formatting Reference

Telegram supports Markdown formatting in messages:

| Syntax | Result |
|--------|--------|
| `**text**` | **Bold** |
| `_text_` | _Italic_ |
| `` `code` `` | `Inline code` |
| ` ```code block``` ` | Code block |
| `[text](url)` | [Hyperlink](url) |
| `> text` | Blockquote |

### Example with Formatting

```python
content = """**Product Update — March 2026** 🚀

We shipped three major features this week:

1. _Dark mode_ — finally!
2. `API v2` — 3x faster
3. [New docs site](https://docs.example.com) — completely rewritten

> "The best software is the kind you don't have to think about." — our CTO

```python
# New SDK usage
client = MySDK(api_key="sk_...")
client.post("Hello, world!")
```"""
```

## Security

- Bot tokens are stored **securely** in Publora
- Bot tokens are **never exposed** in API responses
- Use the Publora dashboard to manage bot credentials — do not hardcode tokens in your application

## Tips for Telegram

- **Bot must be admin** — without admin rights, all posts fail
- **Caption limit is stricter** — 1,024 chars for media captions vs text-only messages
- **Markdown formatting works** — use bold, italic, code blocks, hyperlinks for rich messages
- **WebP auto-converted** to JPEG
- **Private channels** use numeric ID; public channels use `@channelname`
- **Scheduling works** — use `scheduledTime` in ISO 8601 UTC

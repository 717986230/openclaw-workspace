---
name: publora-linkedin
description: >
  Post or schedule content to LinkedIn using the Publora API. Use this skill
  when the user wants to publish, schedule, or draft a LinkedIn post via Publora.
---

# Publora — LinkedIn

Post and schedule LinkedIn content via the Publora API.

> **Prerequisite:** Install the `publora` core skill for auth setup and getting platform IDs.

## Platform ID Format

`linkedin-{profileId}` — get your exact ID from `GET /api/v1/platform-connections`.

## Character Limit

**3,000 characters strict.** The API returns an error if exceeded — it does NOT truncate or thread automatically. Count carefully.

## Supported Content

| Type | Supported | Notes |
|------|-----------|-------|
| Text only | ✅ | Up to 3,000 chars |
| Single image | ✅ | JPEG/PNG; WebP auto-converted to JPEG |
| Multiple images | ✅ | Becomes carousel/album |
| Video | ✅ | MP4 |
| Rich text formatting | ❌ | Plain text only; use Unicode for emphasis (𝗯𝗼𝗹𝗱, 𝘪𝘵𝘢𝘭𝘪𝘤) |

## Post to LinkedIn Immediately

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Excited to share our latest update! 🚀\n\nWe just launched a new feature that cuts onboarding time by 40%. Here is what we learned building it...',
    platforms: ['linkedin-ABC123']
  })
});
```

## Schedule a LinkedIn Post

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Monday thought: consistency beats perfection every time. 💡\n\n#leadership #startup #growth',
    platforms: ['linkedin-ABC123'],
    scheduledTime: '2026-03-16T09:00:00.000Z'
  })
});
// Response: { postGroupId: "pg_abc123", scheduledTime: "..." }
```

## Post with Images (Carousel/Album)

Multiple images → LinkedIn carousel/album. Use the 3-step upload workflow, calling `get-upload-url` once per image with the same `postGroupId`.

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

# Step 1: Create post
post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'Our team at the conference — great connections made today! #networking',
    'platforms': ['linkedin-ABC123'],
    'scheduledTime': '2026-03-16T09:00:00.000Z'
}).json()
post_group_id = post['postGroupId']

# Step 2+3: Upload each image (repeat for N images — all use same postGroupId)
for file_path in ['photo1.jpg', 'photo2.jpg', 'photo3.jpg']:
    upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
        'fileName': file_path, 'contentType': 'image/jpeg',
        'type': 'image', 'postGroupId': post_group_id
    }).json()
    with open(file_path, 'rb') as f:
        requests.put(upload['uploadUrl'], headers={'Content-Type': 'image/jpeg'}, data=f)
```

**WebP note:** WebP images are automatically converted to JPEG by Publora.

## Hashtags

Hashtags work normally and become clickable on LinkedIn. Place them at the end of the post. Recommended: 3–5 relevant hashtags.

```
Great milestone reached today. Grateful for an amazing team. 🙌

#startup #buildinpublic #product #teamwork
```

## Analytics

Retrieve post analytics via:

```
GET /api/v1/post-analytics?postId={postId}&platform=linkedin-{profileId}
```

**Returns:**
- `impressions` — total views
- `membersReached` — unique LinkedIn members reached
- `reshares` — number of reshares
- `reactions` — reaction counts by type
- `comments` — total comments

**Note:** Analytics data may take up to **24 hours** to populate after posting.

### Reaction Types

LinkedIn supports 6 reaction types:

| Reaction | Meaning |
|----------|---------|
| `LIKE` | 👍 Like |
| `PRAISE` | 👏 Celebrate |
| `EMPATHY` | 💜 Support |
| `INTEREST` | 🤔 Curious |
| `APPRECIATION` | 🙏 Love |
| `ENTERTAINMENT` | 😄 Funny |

## Tips for LinkedIn

- **3,000 chars = room to write** — LinkedIn rewards long-form storytelling and thought leadership
- **No markdown** — `**bold**` renders as literal asterisks; use Unicode characters for visual emphasis if needed
- **Hashtags** become clickable — use them
- **Line breaks matter** — LinkedIn shows ~3 lines before "see more" — hook early
- **Best times:** Tuesday–Thursday, 8–10 AM or 12 PM in your audience's timezone
- **Best for:** professional content, career milestones, industry insights, team updates
- **Scheduling works** — use `scheduledTime` (ISO 8601 UTC, at least 2 min in the future)

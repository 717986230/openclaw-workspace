---
name: ai-news-aggregator-sl
description: >
  Fetches today's AI & tech news from TechCrunch, The Verge, NYT Tech, Twitter/X,
  and top AI YouTubers (Matt Wolfe, Andrej Karpathy, Lex Fridman, and more).
  Summarises everything into a Chinese editorial digest using DeepSeek AI,
  then posts it to Discord. Trigger when the user asks for AI news, tech digest,
  trending AI topics, or YouTube AI channel updates.
version: 1.1.0

metadata:
  openclaw:
    emoji: 🦞
    os: [linux, mac, windows]
    requires:
      env:
        - DEEPSEEK_API_KEY
        - DISCORD_WEBHOOK_URL
      anyBins:
        - python3
        - python
---

# 🦞 AI News Aggregator

Collects today's AI & tech content from RSS feeds, Twitter/X, and curated YouTube channels. Translates and summarises everything into Chinese via DeepSeek AI, then posts to Discord.

**Sources:** TechCrunch · The Verge · NYT Tech · Twitter/X · YouTube (15 curated AI channels)
**Output:** Discord — editorial paragraph + "worth reading" picks + YouTube updates

---

## How to Use

Say things like:
- "Get today's AI news"
- "Run the news aggregator"
- "What's trending in AI today?"
- "Check what Lex Fridman and Matt Wolfe posted"
- "AI news dry run" *(preview without posting to Discord)*
- "Test my Discord webhook"

---

## First-Time Setup

The agent will walk you through this automatically, but here's what's needed:

**Required API keys** (agent will ask if missing):

| Key | Where to get it |
|-----|----------------|
| `DEEPSEEK_API_KEY` | [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys) |
| `DISCORD_WEBHOOK_URL` | Discord → Channel Settings → Integrations → Webhooks → New Webhook → Copy URL |

**Optional keys** (more sources):

| Key | Where to get it |
|-----|----------------|
| `TWITTERAPI_IO_KEY` | [twitterapi.io](https://twitterapi.io) |
| `YOUTUBE_API_KEY` | [console.cloud.google.com](https://console.cloud.google.com) → Enable YouTube Data API v3 |

---

## Implementation

Every time this skill is triggered, follow these steps in order:

### Step 1 — Write the script

Check if `~/ai-news/news_aggregator.py` exists:

```bash
ls ~/ai-news/news_aggregator.py
```

If it does **not** exist:
1. Run `mkdir -p ~/ai-news`
2. Use the **Write tool** to create `~/ai-news/news_aggregator.py` with exactly the content from the `## Script` section at the bottom of this file.

### Step 2 — Install Python dependencies

```bash
pip3 install feedparser requests python-dotenv openai
```

If `pip3` is not found, try:
```bash
pip install feedparser requests python-dotenv openai
```

If you get an "externally-managed-environment" error (Ubuntu 24+):
```bash
pip3 install feedparser requests python-dotenv openai --break-system-packages
```

### Step 3 — Set up API keys

Check if `~/ai-news/.env` exists:

```bash
cat ~/ai-news/.env
```

If it doesn't exist, ask the user for their API keys and create the file:

```
DEEPSEEK_API_KEY=sk-...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

Only `DEEPSEEK_API_KEY` and `DISCORD_WEBHOOK_URL` are required. The others are optional — skip them if the user doesn't have them. If `DISCORD_WEBHOOK_URL` is missing, the report will print to the terminal instead.

### Step 4 — Run

Choose the command based on what the user asked:

| What the user said | Command |
|--------------------|---------|
| "news" / "RSS" / "articles" | `cd ~/ai-news && python3 news_aggregator.py --report news` |
| "trending" / "Twitter" / "YouTube" | `cd ~/ai-news && python3 news_aggregator.py --report trending` |
| "dry run" / "preview" / "don't post" | `cd ~/ai-news && python3 news_aggregator.py --dry-run` |
| "test Discord" / "test webhook" | `cd ~/ai-news && python3 news_aggregator.py --test-discord` |
| anything else | `cd ~/ai-news && python3 news_aggregator.py --report all` |

### Step 5 — Report back

Tell the user:
- What was posted to Discord (news digest, trending, or both)
- How many items were found from each source
- If any sources were skipped (e.g. "YouTube skipped — YOUTUBE_API_KEY not set")
- If there were any errors

---

## Script

> **Agent:** If `~/ai-news/news_aggregator.py` is missing, create it now using the Write tool with exactly this content:

```python
#!/usr/bin/env python3
"""
AI News Aggregator — OpenClaw Skill Script
==========================================
Sources : TechCrunch, The Verge, NYT (RSS) + Twitter/X + YouTube
AI      : DeepSeek (translation + summarisation -> Chinese)
Output  : Discord webhook (formatted markdown)

Usage:
    python3 news_aggregator.py                     # run all reports
    python3 news_aggregator.py --report news       # news digest only
    python3 news_aggregator.py --report trending   # trending (Twitter + YouTube)
    python3 news_aggregator.py --dry-run           # fetch + process, no Discord post
    python3 news_aggregator.py --test-discord      # test webhook connectivity
"""

import os
import sys
import json
import time
import argparse
import requests
import feedparser
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from openai import OpenAI   # DeepSeek uses the OpenAI-compatible SDK

# Load .env from same directory as this script
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

DEEPSEEK_API_KEY   = os.getenv("DEEPSEEK_API_KEY", "")
TWITTER_API_KEY    = os.getenv("TWITTERAPI_IO_KEY", "")
YOUTUBE_API_KEY    = os.getenv("YOUTUBE_API_KEY", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
DISCORD_WEBHOOK_URL_TRENDING = os.getenv("DISCORD_WEBHOOK_URL_TRENDING", "").strip() or DISCORD_WEBHOOK_URL

FILTER_HOURS       = int(os.getenv("FILTER_HOURS", "24"))
YT_MIN_VIEWS       = int(os.getenv("YT_MIN_VIEWS", "10000"))
YT_VIRAL_MIN_VIEWS = int(os.getenv("YT_VIRAL_MIN_VIEWS", "200000"))
TWITTER_MAX_TWEETS = int(os.getenv("TWITTER_MAX_TWEETS", "15"))

RSS_FEEDS = {
    "TechCrunch":     "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge":      "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "New York Times": "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/spotlight/artificial-intelligence/rss.xml",
}

AI_YOUTUBE_CHANNELS = {
    "Matt Wolfe":        "mreflow",
    "Wes Roth":          "WesRoth",
    "Two Minute Papers": "TwoMinutePapers",
    "AI Explained":      "aiexplained-official",
    "Andrej Karpathy":   "AndrejKarpathy",
    "Lex Fridman":       "lexfridman",
    "Yannic Kilcher":    "YannicKilcher",
    "3Blue1Brown":       "3blue1brown",
    "Fireship":          "Fireship",
    "The AI Advantage":  "TheAIAdvantage",
    "Sam Witteveen":     "samwitteveenai",
    "DeepMind":          "Google_DeepMind",
    "OpenAI":            "OpenAI",
    "Anthropic":         "AnthropicAI",
    "Sentdex":           "sentdex",
}

CUTOFF = datetime.now(timezone.utc) - timedelta(hours=FILTER_HOURS)

# ── DeepSeek ──────────────────────────────────────────────────

def deepseek_client():
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def translate_and_summarise(item: dict) -> dict:
    prompt = f"""你是一名新闻编辑，任务是将不同来源的标题翻译成中文，要求简洁、准确、有逻辑。请确保输出全是中文。

输入信息：
标题：{item.get('标题', '')}
日期：{item.get('日期', '')}
来源：{item.get('来源', '')}
板块：{item.get('板块', '')}
链接：{item.get('链接', '')}

若标题内容大于三句话，生成60-80字中文摘要，以"（摘要）"开头。
其他字段严格保持和输入一致。
请以JSON格式输出，字段包含：标题、日期、来源、板块、链接"""
    try:
        r = deepseek_client().chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=512, temperature=0.3,
        )
        return json.loads(r.choices[0].message.content)
    except Exception as e:
        print(f"  [DeepSeek] Error: {e}")
        return item

def batch_translate(items: list, delay: float = 0.5) -> list:
    results = []
    for i, item in enumerate(items):
        print(f"  Translating {i+1}/{len(items)}: {item.get('标题','')[:60]}")
        results.append(translate_and_summarise(item))
        if i < len(items) - 1:
            time.sleep(delay)
    return results

# ── RSS ───────────────────────────────────────────────────────

def fetch_rss(source_name: str, url: str) -> list:
    print(f"  Fetching RSS: {source_name}")
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"  [RSS] Failed: {e}")
        return []
    items = []
    for entry in feed.entries:
        pub = None
        for attr in ("published_parsed", "updated_parsed"):
            t = getattr(entry, attr, None)
            if t:
                pub = datetime(*t[:6], tzinfo=timezone.utc)
                break
        if not pub or pub < CUTOFF:
            continue
        items.append({"标题": entry.get("title",""), "日期": pub.strftime("%Y-%m-%d %H:%M"),
                      "来源": source_name, "板块": "科技资讯", "链接": entry.get("link","")})
    print(f"    -> {len(items)} items in last {FILTER_HOURS}h")
    return items

def fetch_all_rss() -> list:
    items = []
    for name, url in RSS_FEEDS.items():
        items.extend(fetch_rss(name, url))
    return items

# ── Twitter ───────────────────────────────────────────────────

def fetch_twitter(query: str = "AI", query_type: str = "Top") -> list:
    if not TWITTER_API_KEY:
        print("  [Twitter] TWITTERAPI_IO_KEY not set, skipping.")
        return []
    print(f"  Fetching Twitter: query='{query}'")
    try:
        resp = requests.get("https://api.twitterapi.io/twitter/tweet/advanced_search",
                            headers={"X-API-Key": TWITTER_API_KEY},
                            params={"query": query, "queryType": query_type}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [Twitter] Failed: {e}")
        return []
    items = []
    for tweet in data.get("tweets", [])[:TWITTER_MAX_TWEETS]:
        raw = tweet.get("createdAt") or tweet.get("created_at", "")
        try:
            created = datetime.strptime(raw.replace("+0000","UTC"), "%a %b %d %H:%M:%S UTC %Y").replace(tzinfo=timezone.utc)
        except Exception:
            try:
                created = datetime.fromisoformat(raw.replace("Z","+00:00"))
            except Exception:
                continue
        if created < CUTOFF:
            continue
        user = tweet.get("author",{}).get("userName","") or tweet.get("user",{}).get("screen_name","")
        tid  = tweet.get("id","")
        items.append({"标题": tweet.get("text",""), "日期": created.strftime("%Y-%m-%d %H:%M"),
                      "来源": f"Twitter/@{user}", "板块": "推特热点",
                      "链接": f"https://twitter.com/{user}/status/{tid}" if tid else ""})
    print(f"    -> {len(items)} tweets in last {FILTER_HOURS}h")
    return items

# ── YouTube ───────────────────────────────────────────────────

def _resolve_channel_ids(handles: list) -> dict:
    resolved = {}
    for handle in handles:
        try:
            resp = requests.get("https://www.googleapis.com/youtube/v3/channels",
                                params={"part":"contentDetails,snippet","forHandle":handle,"key":YOUTUBE_API_KEY}, timeout=10)
            items = resp.json().get("items",[])
            if items:
                resolved[handle] = (items[0]["id"], items[0]["contentDetails"]["relatedPlaylists"]["uploads"])
        except Exception as e:
            print(f"    [YouTube] Could not resolve @{handle}: {e}")
        time.sleep(0.1)
    return resolved

def fetch_youtube_from_channels(channels: dict = None, videos_per_channel: int = 3) -> list:
    if not YOUTUBE_API_KEY:
        print("  [YouTube] YOUTUBE_API_KEY not set, skipping.")
        return []
    channels = channels or AI_YOUTUBE_CHANNELS
    print(f"  Fetching YouTube from {len(channels)} curated channels...")
    handle_map   = _resolve_channel_ids(list(channels.values()))
    name_by_handle = {v: k for k, v in channels.items()}
    all_video_ids, video_meta = [], {}
    for handle, (_, playlist_id) in handle_map.items():
        display = name_by_handle.get(handle, handle)
        try:
            resp = requests.get("https://www.googleapis.com/youtube/v3/playlistItems",
                                params={"part":"snippet","playlistId":playlist_id,
                                        "maxResults":videos_per_channel,"key":YOUTUBE_API_KEY}, timeout=10)
            for item in resp.json().get("items",[]):
                s = item.get("snippet",{})
                vid_id = s.get("resourceId",{}).get("videoId","")
                pub_str = s.get("publishedAt","")
                if not vid_id or not pub_str:
                    continue
                try:
                    pub = datetime.fromisoformat(pub_str.replace("Z","+00:00"))
                except Exception:
                    continue
                if pub < CUTOFF:
                    continue
                all_video_ids.append(vid_id)
                video_meta[vid_id] = {"title": s.get("title",""), "channel": display, "pub": pub}
        except Exception as e:
            print(f"    [YouTube] Failed for {display}: {e}")
        time.sleep(0.1)
    if not all_video_ids:
        print(f"    -> 0 new videos from curated channels in last {FILTER_HOURS}h")
        return []
    stats_map = {}
    for i in range(0, len(all_video_ids), 50):
        try:
            resp = requests.get("https://www.googleapis.com/youtube/v3/videos",
                                params={"part":"statistics","id":",".join(all_video_ids[i:i+50]),"key":YOUTUBE_API_KEY}, timeout=10)
            for v in resp.json().get("items",[]):
                stats_map[v["id"]] = v.get("statistics",{})
        except Exception:
            pass
    items = []
    for vid_id in all_video_ids:
        meta  = video_meta[vid_id]
        stats = stats_map.get(vid_id,{})
        items.append({"标题": meta["title"], "日期": meta["pub"].strftime("%Y-%m-%d %H:%M"),
                      "来源": meta["channel"], "板块": "YouTube",
                      "链接": f"https://www.youtube.com/watch?v={vid_id}",
                      "views": int(stats.get("viewCount",0))})
    items.sort(key=lambda x: x.get("views",0), reverse=True)
    print(f"    -> {len(items)} new video(s) from curated channels")
    return items

# ── Formatters ────────────────────────────────────────────────

def _fmt_views(n: int) -> str:
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1000: return f"{n/1000:.1f}K"
    return str(n)

def build_editorial_digest(items: list, section_title: str) -> str:
    if not items:
        return ""
    today = datetime.now().strftime("%Y-%m-%d")
    item_lines = [f"{i}. 标题：{it.get('标题','')}\n   来源：{it.get('来源','')}\n   链接：{it.get('链接','')}"
                  for i, it in enumerate(items, 1)]
    prompt = f"""你是一名AI科技资讯编辑，今天是{today}。

以下是今天的{section_title}列表（共{len(items)}条）：

{chr(10).join(item_lines)}

请完成以下两项任务，输出纯文本（不要输出JSON）：

## 任务一：今日综述
写一段150-200字的中文综述段落，概括今天AI领域发生的最重要事情。
- 用流畅的新闻编辑风格，写成自然段落，不要用列表
- 把最重要的新闻标题以Markdown超链接形式嵌入段落中，格式：[标题关键词](链接)
- 体现出信息之间的联系和整体趋势

## 任务二：值得关注
从列表中挑选3条最值得阅读的内容，简短说明理由（每条一句话），格式：
🔖 [标题](链接) — 理由

只输出上述两部分内容，不要加其他说明。"""
    try:
        r = deepseek_client().chat.completions.create(
            model="deepseek-chat", messages=[{"role":"user","content":prompt}],
            max_tokens=1024, temperature=0.6)
        editorial = r.choices[0].message.content.strip()
    except Exception as e:
        print(f"  [DeepSeek] Editorial failed: {e}")
        editorial = "\n".join(f"• [{it.get('标题','')}]({it.get('链接','')})" for it in items[:10])
    return f"**📰 {today} {section_title}**\n\n{editorial}"

def build_youtube_section(yt_items: list) -> str:
    if not yt_items:
        return ""
    today = datetime.now().strftime("%Y-%m-%d")
    md = f"**▶️ {today} AI YouTuber 最新更新**\n\n"
    for n in yt_items[:12]:
        views_str = f"（{_fmt_views(n.get('views',0))} 播放）" if n.get('views',0) > 0 else ""
        md += f"▶ **{n.get('来源','')}** — [{n.get('标题','')}]({n.get('链接','')}) {views_str}\n"
    return md.strip()

# ── Discord ───────────────────────────────────────────────────

DISCORD_MAX_CHARS = 1900

def _chunk_markdown(md: str, max_len: int = DISCORD_MAX_CHARS) -> list:
    lines = md.split("\n")
    chunks, current = [], ""
    for line in lines:
        if len(current) + len(line) + 1 > max_len:
            if current: chunks.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"
    if current.strip(): chunks.append(current.strip())
    return chunks or [md[:max_len]]

def post_to_discord(webhook_url: str, content: str, title: str = "") -> bool:
    if not webhook_url:
        print("  [Discord] No webhook URL — printing to stdout.")
        print("=" * 60); print(content); print("=" * 60)
        return True
    chunks = _chunk_markdown(content)
    print(f"  [Discord] Sending {len(chunks)} message(s)...")
    for i, chunk in enumerate(chunks):
        header = (f"**{title}** *(part {i+1}/{len(chunks)})*\n" if title and len(chunks) > 1
                  else (f"**{title}**\n" if title and i == 0 else ""))
        try:
            resp = requests.post(webhook_url, json={"content": header + chunk}, timeout=15)
            print(f"  [Discord] Chunk {i+1}/{len(chunks)} -> HTTP {resp.status_code}")
            if resp.status_code == 429:
                wait = resp.json().get("retry_after", 2)
                print(f"  [Discord] Rate limited, waiting {wait}s...")
                time.sleep(float(wait) + 0.5)
                resp = requests.post(webhook_url, json={"content": header + chunk}, timeout=15)
            if not resp.ok:
                print(f"  [Discord] Error: {resp.text[:300]}")
                return False
            time.sleep(0.6)
        except Exception as e:
            print(f"  [Discord] Exception: {e}")
            return False
    return True

# ── Main ──────────────────────────────────────────────────────

def validate_config():
    if not DEEPSEEK_API_KEY:
        print("\n❌ DEEPSEEK_API_KEY not set. Add it to ~/ai-news/.env")
        sys.exit(1)
    if not DISCORD_WEBHOOK_URL:
        print("  ⚠️  DISCORD_WEBHOOK_URL not set — output will go to stdout.")

def run_news_report(dry_run=False):
    print("\n📰 === News Digest ===")
    rss_items = fetch_all_rss()
    if not rss_items:
        print("  No RSS items in last 24h."); return
    print(f"\n  Translating {len(rss_items)} items with DeepSeek...")
    translated = batch_translate(rss_items)
    print("\n  Generating editorial summary...")
    digest = build_editorial_digest(translated, "AI资讯日报")
    if dry_run:
        print("\n--- DRY RUN ---\n" + digest)
    else:
        print("\n  Posting to Discord...")
        ok = post_to_discord(DISCORD_WEBHOOK_URL, digest)
        print("  ✅ Posted." if ok else "  ❌ Failed — see errors above.")

def run_trending_report(dry_run=False):
    print("\n🔥 === Trending Digest ===")
    twitter_items = fetch_twitter()
    yt_items      = fetch_youtube_from_channels()
    if twitter_items:
        print(f"\n  Translating {len(twitter_items)} tweets...")
        t_translated   = batch_translate(twitter_items)
        print("\n  Generating Twitter editorial...")
        twitter_digest = build_editorial_digest(t_translated, "推特AI热点")
    else:
        twitter_digest = ""
    yt_section = build_youtube_section(yt_items) if yt_items else ""
    if not twitter_digest and not yt_section:
        print("  No trending items found."); return
    full = "\n\n".join(filter(None, [twitter_digest, yt_section]))
    if dry_run:
        print("\n--- DRY RUN ---\n" + full)
    else:
        print("\n  Posting to Discord...")
        ok = post_to_discord(DISCORD_WEBHOOK_URL_TRENDING, full)
        print("  ✅ Posted." if ok else "  ❌ Failed — see errors above.")

def test_discord():
    print(f"\n🔔 Testing Discord webhook: {DISCORD_WEBHOOK_URL[:60]}...")
    ok = post_to_discord(DISCORD_WEBHOOK_URL,
         f"✅ **AI News Aggregator** — webhook working! ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print("  ✅ Check your Discord channel." if ok else "  ❌ Failed.")
    sys.exit(0 if ok else 1)

def main():
    parser = argparse.ArgumentParser(description="AI News Aggregator")
    parser.add_argument("--report", choices=["all","news","trending"], default="all")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--test-discord", action="store_true")
    args = parser.parse_args()
    validate_config()
    if args.test_discord: test_discord()
    start = time.time()
    print(f"\n🦞 AI News Aggregator — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   Filter: last {FILTER_HOURS}h | Dry-run: {args.dry_run}")
    if args.report in ("all","news"):      run_news_report(dry_run=args.dry_run)
    if args.report in ("all","trending"):  run_trending_report(dry_run=args.dry_run)
    print(f"\n✅ Done in {time.time()-start:.1f}s")

if __name__ == "__main__":
    main()
```

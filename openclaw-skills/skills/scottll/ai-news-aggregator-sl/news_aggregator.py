#!/usr/bin/env python3
"""
AI News Aggregator — OpenClaw Skill Script
==========================================
Sources : TechCrunch, The Verge, NYT (RSS) + Twitter/X + YouTube
AI      : DeepSeek (translation + summarisation → Chinese)
Output  : Discord webhook (formatted embeds)

Usage:
    python3 news_aggregator.py              # run all reports
    python3 news_aggregator.py --report news       # news digest only
    python3 news_aggregator.py --report trending   # trending (Twitter + YouTube)
    python3 news_aggregator.py --dry-run           # fetch + process, no Discord post

Requirements (auto-installed by SKILL.md):
    pip install feedparser requests python-dotenv openai
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

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
load_dotenv()

DEEPSEEK_API_KEY   = os.getenv("DEEPSEEK_API_KEY", "")
TWITTER_API_KEY    = os.getenv("TWITTERAPI_IO_KEY", "")   # from twitterapi.io
YOUTUBE_API_KEY    = os.getenv("YOUTUBE_API_KEY", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
# Fall back to main webhook if TRENDING key is missing OR blank
DISCORD_WEBHOOK_URL_TRENDING = os.getenv("DISCORD_WEBHOOK_URL_TRENDING", "").strip() or DISCORD_WEBHOOK_URL

# Filters
FILTER_HOURS       = int(os.getenv("FILTER_HOURS", "24"))        # only keep items from last N hours
YT_MIN_VIEWS       = int(os.getenv("YT_MIN_VIEWS", "10000"))     # YouTube: min view count
YT_VIRAL_MIN_VIEWS = int(os.getenv("YT_VIRAL_MIN_VIEWS", "200000"))  # YouTube viral tier
TWITTER_MAX_TWEETS = int(os.getenv("TWITTER_MAX_TWEETS", "15"))

# RSS feed URLs (AI-focused)
RSS_FEEDS = {
    "TechCrunch":  "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge":   "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "New York Times": "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/spotlight/artificial-intelligence/rss.xml",
}

# Curated top AI YouTube channels — {display name: YouTube @handle}
AI_YOUTUBE_CHANNELS = {
    "Matt Wolfe":         "mreflow",
    "Wes Roth":           "WesRoth",
    "Two Minute Papers":  "TwoMinutePapers",
    "AI Explained":       "aiexplained-official",
    "Andrej Karpathy":    "AndrejKarpathy",
    "Lex Fridman":        "lexfridman",
    "Yannic Kilcher":     "YannicKilcher",
    "3Blue1Brown":        "3blue1brown",
    "Fireship":           "Fireship",
    "The AI Advantage":   "TheAIAdvantage",
    "Sam Witteveen":      "samwitteveenai",
    "DeepMind":           "Google_DeepMind",
    "OpenAI":             "OpenAI",
    "Anthropic":          "AnthropicAI",
    "Sentdex":            "sentdex",
}

CUTOFF = datetime.now(timezone.utc) - timedelta(hours=FILTER_HOURS)

# ─────────────────────────────────────────────
# DeepSeek helpers
# ─────────────────────────────────────────────

def deepseek_client():
    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )

def translate_and_summarise(item: dict) -> dict:
    """
    Calls DeepSeek to translate the title to Chinese and optionally generate
    a 60-80 character summary (if the title is long / multi-sentence).
    Returns a new dict with '标题' potentially replaced.
    """
    prompt = f"""你是一名新闻编辑，任务是将不同来源的标题翻译成中文，要求简洁、准确、有逻辑。请确保输出全是中文。若只有一条链接，保留链接即可。

输入信息：
标题：{item.get('标题', '')}
日期：{item.get('日期', '')}
来源：{item.get('来源', '')}
板块：{item.get('板块', '')}
链接：{item.get('链接', '')}

若标题内容大于三句话，则根据标题里所有的信息生成一段60–80字的中文摘要，遵循以下步骤和格式：

#步骤
1. 提取主语和核心动作，格式为"谁做了什么"
2. 概括主要功能或用途，格式为"实现什么功能，达到什么效果"
3. 如有亮点或创新点，请加以总结
4. 强调主观意义或影响，格式为"对什么有重要意义"

#输出要求
- 以"（摘要）"为开头，输出一条完整、通顺的中文句子，60–80字左右

注意：除了"标题"字段可以修改，其他字段的内容严格保持和输入一致。

请以JSON格式输出，字段包含：标题、日期、来源、板块、链接"""

    schema = {
        "type": "object",
        "properties": {
            "标题": {"type": "string"},
            "日期": {"type": "string"},
            "来源": {"type": "string"},
            "板块": {"type": "string"},
            "链接": {"type": "string"},
        },
        "required": ["标题", "日期", "来源", "板块", "链接"]
    }

    try:
        client = deepseek_client()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=512,
            temperature=0.3,
        )
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"  [DeepSeek] Error translating '{item.get('标题','')}': {e}")
        return item   # fallback: return original


def batch_translate(items: list, delay: float = 0.5) -> list:
    """Translate a list of items, with a small delay between calls."""
    results = []
    for i, item in enumerate(items):
        print(f"  Translating {i+1}/{len(items)}: {item.get('标题','')[:60]}")
        translated = translate_and_summarise(item)
        results.append(translated)
        if i < len(items) - 1:
            time.sleep(delay)
    return results


# ─────────────────────────────────────────────
# RSS fetching
# ─────────────────────────────────────────────

def fetch_rss(source_name: str, url: str) -> list:
    """Fetch and filter an RSS feed, returning items from the last FILTER_HOURS."""
    print(f"  Fetching RSS: {source_name}")
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"  [RSS] Failed to parse {url}: {e}")
        return []

    items = []
    for entry in feed.entries:
        # Parse published date
        pub = None
        for attr in ("published_parsed", "updated_parsed"):
            t = getattr(entry, attr, None)
            if t:
                pub = datetime(*t[:6], tzinfo=timezone.utc)
                break
        if pub is None:
            continue
        if pub < CUTOFF:
            continue

        items.append({
            "标题": entry.get("title", ""),
            "日期": pub.strftime("%Y-%m-%d %H:%M"),
            "来源": source_name,
            "板块": "科技资讯",
            "链接": entry.get("link", ""),
        })

    print(f"    → {len(items)} items in last {FILTER_HOURS}h")
    return items


def fetch_all_rss() -> list:
    all_items = []
    for name, url in RSS_FEEDS.items():
        all_items.extend(fetch_rss(name, url))
    return all_items


# ─────────────────────────────────────────────
# Twitter / X
# ─────────────────────────────────────────────

def fetch_twitter(query: str = "AI", query_type: str = "Top") -> list:
    """Fetch trending tweets via twitterapi.io"""
    if not TWITTER_API_KEY:
        print("  [Twitter] TWITTERAPI_IO_KEY not set, skipping.")
        return []

    print(f"  Fetching Twitter: query='{query}' type={query_type}")
    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    headers = {"X-API-Key": TWITTER_API_KEY}
    params = {"query": query, "queryType": query_type}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [Twitter] Request failed: {e}")
        return []

    tweets = data.get("tweets", [])
    items = []
    for tweet in tweets[:TWITTER_MAX_TWEETS]:
        # Parse createdAt — Twitter format: "Fri Oct 31 00:41:48 +0000 2025"
        created_raw = tweet.get("createdAt") or tweet.get("created_at", "")
        try:
            created = datetime.strptime(
                created_raw.replace("+0000", "UTC"),
                "%a %b %d %H:%M:%S UTC %Y"
            ).replace(tzinfo=timezone.utc)
        except Exception:
            try:
                created = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
            except Exception:
                continue

        if created < CUTOFF:
            continue

        user = tweet.get("author", {}).get("userName", "") or tweet.get("user", {}).get("screen_name", "")
        text = tweet.get("text", "")
        tweet_id = tweet.get("id", "")
        link = f"https://twitter.com/{user}/status/{tweet_id}" if tweet_id else ""

        items.append({
            "标题": text,
            "日期": created.strftime("%Y-%m-%d %H:%M"),
            "来源": f"Twitter/@{user}",
            "板块": "推特热点",
            "链接": link,
        })

    print(f"    → {len(items)} tweets in last {FILTER_HOURS}h")
    return items


# ─────────────────────────────────────────────
# YouTube (curated channels)
# ─────────────────────────────────────────────

def _resolve_channel_ids(handles: list) -> dict:
    """
    Resolve @handles → {handle: (channel_id, uploads_playlist_id)}.
    Uses the YouTube channels API forHandle parameter.
    """
    resolved = {}
    for handle in handles:
        try:
            resp = requests.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={"part": "contentDetails,snippet", "forHandle": handle, "key": YOUTUBE_API_KEY},
                timeout=10,
            )
            items = resp.json().get("items", [])
            if items:
                uploads = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
                resolved[handle] = (items[0]["id"], uploads)
        except Exception as e:
            print(f"    [YouTube] Could not resolve @{handle}: {e}")
        time.sleep(0.1)
    return resolved


def fetch_youtube_from_channels(channels: dict = None, videos_per_channel: int = 3) -> list:
    """
    Fetch recent videos from curated AI YouTube channels.
    channels: {display_name: handle}  — defaults to AI_YOUTUBE_CHANNELS
    """
    if not YOUTUBE_API_KEY:
        print("  [YouTube] YOUTUBE_API_KEY not set, skipping.")
        return []

    channels = channels or AI_YOUTUBE_CHANNELS
    print(f"  Fetching YouTube from {len(channels)} curated AI channels...")

    # Step 1: Resolve handles → upload playlist IDs
    handle_map = _resolve_channel_ids(list(channels.values()))
    print(f"    Resolved {len(handle_map)}/{len(channels)} channels")

    # Build reverse map: handle → display name
    name_by_handle = {v: k for k, v in channels.items()}

    published_after = CUTOFF.strftime("%Y-%m-%dT%H:%M:%SZ")
    all_video_ids = []
    video_meta = {}   # video_id → {channel, snippet}

    # Step 2: Fetch recent uploads from each channel's playlist
    for handle, (channel_id, playlist_id) in handle_map.items():
        display_name = name_by_handle.get(handle, handle)
        try:
            resp = requests.get(
                "https://www.googleapis.com/youtube/v3/playlistItems",
                params={
                    "part": "snippet",
                    "playlistId": playlist_id,
                    "maxResults": videos_per_channel,
                    "key": YOUTUBE_API_KEY,
                },
                timeout=10,
            )
            for item in resp.json().get("items", []):
                snippet = item.get("snippet", {})
                vid_id  = snippet.get("resourceId", {}).get("videoId", "")
                pub_str = snippet.get("publishedAt", "")
                if not vid_id or not pub_str:
                    continue
                try:
                    pub = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                except Exception:
                    continue
                if pub < CUTOFF:
                    continue
                all_video_ids.append(vid_id)
                video_meta[vid_id] = {
                    "title":   snippet.get("title", ""),
                    "channel": display_name,
                    "pub":     pub,
                }
        except Exception as e:
            print(f"    [YouTube] Failed to fetch playlist for {display_name}: {e}")
        time.sleep(0.1)

    if not all_video_ids:
        print(f"    → 0 new videos from curated channels in last {FILTER_HOURS}h")
        return []

    # Step 3: Get statistics in one batch call
    stats_map = {}
    for i in range(0, len(all_video_ids), 50):
        batch = all_video_ids[i:i+50]
        try:
            resp = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={"part": "statistics", "id": ",".join(batch), "key": YOUTUBE_API_KEY},
                timeout=10,
            )
            for v in resp.json().get("items", []):
                stats_map[v["id"]] = v.get("statistics", {})
        except Exception as e:
            print(f"    [YouTube] Stats batch failed: {e}")

    # Step 4: Build items list
    items = []
    for vid_id in all_video_ids:
        meta  = video_meta[vid_id]
        stats = stats_map.get(vid_id, {})
        view_count = int(stats.get("viewCount", 0))

        items.append({
            "标题": meta["title"],
            "日期": meta["pub"].strftime("%Y-%m-%d %H:%M"),
            "来源": meta["channel"],
            "板块": "YouTube",
            "链接": f"https://www.youtube.com/watch?v={vid_id}",
            "views": view_count,
        })

    items.sort(key=lambda x: x.get("views", 0), reverse=True)
    print(f"    → {len(items)} new video(s) from curated channels")
    return items


# ─────────────────────────────────────────────
# Report formatters + AI editorial digest
# ─────────────────────────────────────────────

def _fmt_views(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1000:
        return f"{n/1000:.1f}K"
    return str(n)


def build_editorial_digest(items: list, section_title: str) -> str:
    """
    Uses DeepSeek to write a newsletter-style Chinese editorial paragraph
    summarising all items, with markdown links embedded inline.
    Returns a formatted Discord-ready string.
    """
    if not items:
        return ""

    today = datetime.now().strftime("%Y-%m-%d")

    # Build a structured item list for the prompt
    item_lines = []
    for i, it in enumerate(items, 1):
        item_lines.append(
            f"{i}. 标题：{it.get('标题','')}\n   来源：{it.get('来源','')}\n   链接：{it.get('链接','')}"
        )
    items_text = "\n".join(item_lines)

    prompt = f"""你是一名AI科技资讯编辑，今天是{today}。

以下是今天的{section_title}列表（共{len(items)}条）：

{items_text}

请根据以上内容，完成以下两项任务，输出纯文本（不要输出JSON）：

## 任务一：今日综述
写一段150-200字的中文综述段落，概括今天AI领域发生的最重要事情。
- 用流畅的新闻编辑风格，不要用列表，写成自然段落
- 把最重要的新闻标题以Markdown超链接形式嵌入段落中，格式：[标题关键词](链接)
- 体现出信息之间的联系和整体趋势

## 任务二：值得关注
从列表中挑选3条最值得阅读的内容，简短说明理由（每条一句话），格式：
🔖 [标题](链接) — 理由

只输出上述两部分内容，不要加其他说明。"""

    try:
        client = deepseek_client()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.6,
        )
        editorial = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"  [DeepSeek] Editorial generation failed: {e}")
        # Fallback: plain list
        editorial = "\n".join(
            f"• [{it.get('标题','')}]({it.get('链接','')})"
            for it in items[:10]
        )

    header = f"**📰 {today} {section_title}**\n\n"
    return header + editorial


def build_youtube_section(yt_items: list) -> str:
    """Build a clean YouTube section listing new videos from curated channels."""
    if not yt_items:
        return ""

    today = datetime.now().strftime("%Y-%m-%d")
    md = f"**▶️ {today} AI YouTuber 最新更新**\n\n"

    for n in yt_items[:12]:
        title   = n.get("标题", "")
        link    = n.get("链接", "")
        channel = n.get("来源", "")
        views   = n.get("views", 0)
        view_str = f"（{_fmt_views(views)} 播放）" if views > 0 else ""
        md += f"▶ **{channel}** — [{title}]({link}) {view_str}\n"

    return md.strip()


# ─────────────────────────────────────────────
# Discord posting
# ─────────────────────────────────────────────

DISCORD_MAX_CHARS = 1900   # stay under 2000-char embed limit

def _chunk_markdown(md: str, max_len: int = DISCORD_MAX_CHARS) -> list:
    """Split a long markdown string into Discord-safe chunks."""
    lines = md.split("\n")
    chunks, current = [], ""
    for line in lines:
        if len(current) + len(line) + 1 > max_len:
            if current:
                chunks.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks or [md[:max_len]]


def post_to_discord(webhook_url: str, content: str, title: str = "") -> bool:
    """Post a markdown message to Discord via webhook (splits if needed)."""
    if not webhook_url:
        print("  [Discord] No webhook URL set — printing to stdout instead.")
        print("=" * 60)
        print(content)
        print("=" * 60)
        return True

    chunks = _chunk_markdown(content)
    print(f"  [Discord] Sending {len(chunks)} message(s) to webhook...")

    for i, chunk in enumerate(chunks):
        header = (
            f"**{title}** *(part {i+1}/{len(chunks)})*\n"
            if title and len(chunks) > 1
            else (f"**{title}**\n" if title and i == 0 else "")
        )
        payload = {"content": header + chunk}

        try:
            resp = requests.post(webhook_url, json=payload, timeout=15)
            print(f"  [Discord] Chunk {i+1}/{len(chunks)} → HTTP {resp.status_code}")
            if resp.status_code == 429:
                retry_after = resp.json().get("retry_after", 2)
                print(f"  [Discord] Rate limited — waiting {retry_after}s...")
                time.sleep(float(retry_after) + 0.5)
                resp = requests.post(webhook_url, json=payload, timeout=15)
                print(f"  [Discord] Retry → HTTP {resp.status_code}")
            if not resp.ok:
                print(f"  [Discord] ❌ Error response body: {resp.text[:300]}")
                return False
            time.sleep(0.6)  # stay well under Discord's 30 req/min limit
        except Exception as e:
            print(f"  [Discord] ❌ Request exception: {e}")
            return False

    return True


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def validate_config():
    missing = []
    if not DEEPSEEK_API_KEY:
        missing.append("DEEPSEEK_API_KEY")
    if not DISCORD_WEBHOOK_URL:
        print("  ⚠️  DISCORD_WEBHOOK_URL not set — output will go to stdout.")
    if missing:
        print(f"\n❌ Missing required env vars: {', '.join(missing)}")
        print("   See .env.example for setup instructions.")
        sys.exit(1)


def run_news_report(dry_run: bool = False):
    print("\n📰 === News Digest ===")
    rss_items = fetch_all_rss()
    if not rss_items:
        print("  No RSS items found in the last 24h.")
        return

    print(f"\n  Translating {len(rss_items)} RSS items with DeepSeek...")
    translated = batch_translate(rss_items)

    print("\n  Generating editorial summary with DeepSeek...")
    digest = build_editorial_digest(translated, "AI资讯日报")

    if dry_run:
        print("\n--- DRY RUN: News Digest ---")
        print(digest)
    else:
        print("\n  Posting to Discord...")
        ok = post_to_discord(DISCORD_WEBHOOK_URL, digest)
        if ok:
            print("  ✅ News digest posted.")
        else:
            print("  ❌ News digest FAILED to post — see errors above.")


def run_trending_report(dry_run: bool = False):
    print("\n🔥 === Trending Digest ===")
    twitter_items = fetch_twitter(query="AI", query_type="Top")
    yt_items      = fetch_youtube_from_channels()

    # Twitter: translate and write editorial
    if twitter_items:
        print(f"\n  Translating {len(twitter_items)} tweets...")
        t_translated = batch_translate(twitter_items)
        print("\n  Generating Twitter editorial with DeepSeek...")
        twitter_digest = build_editorial_digest(t_translated, "推特AI热点")
    else:
        twitter_digest = ""

    # YouTube: just list new videos from curated channels (no translation needed)
    yt_section = build_youtube_section(yt_items) if yt_items else ""

    if not twitter_digest and not yt_section:
        print("  No trending items found.")
        return

    full_digest = "\n\n".join(filter(None, [twitter_digest, yt_section]))

    if dry_run:
        print("\n--- DRY RUN: Trending Digest ---")
        print(full_digest)
    else:
        print("\n  Posting to Discord...")
        ok = post_to_discord(DISCORD_WEBHOOK_URL_TRENDING, full_digest)
        if ok:
            print("  ✅ Trending digest posted.")
        else:
            print("  ❌ Trending digest FAILED to post — see errors above.")


def test_discord():
    """Send a quick test message to verify the webhook works."""
    print(f"\n🔔 Testing Discord webhook...")
    print(f"   URL: {DISCORD_WEBHOOK_URL[:60]}...")
    msg = f"✅ **Test from AI News Aggregator** — webhook is working! ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
    ok = post_to_discord(DISCORD_WEBHOOK_URL, msg)
    if ok:
        print("  ✅ Test message sent — check your Discord channel.")
    else:
        print("  ❌ Test message failed — check the errors above.")
    sys.exit(0 if ok else 1)


def main():
    parser = argparse.ArgumentParser(description="AI News Aggregator — OpenClaw Skill")
    parser.add_argument(
        "--report",
        choices=["all", "news", "trending"],
        default="all",
        help="Which report to generate (default: all)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and translate but don't post to Discord"
    )
    parser.add_argument(
        "--test-discord",
        action="store_true",
        help="Send a test message to Discord and exit (quick webhook check)"
    )
    args = parser.parse_args()

    validate_config()

    if args.test_discord:
        test_discord()

    start = time.time()
    print(f"\n🦞 AI News Aggregator — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   Filter: last {FILTER_HOURS}h | Dry-run: {args.dry_run}")

    if args.report in ("all", "news"):
        run_news_report(dry_run=args.dry_run)

    if args.report in ("all", "trending"):
        run_trending_report(dry_run=args.dry_run)

    elapsed = time.time() - start
    print(f"\n✅ Done in {elapsed:.1f}s")


if __name__ == "__main__":
    main()

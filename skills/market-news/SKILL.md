---
name: market-news
description: Latest market news and futures headline workflow for time-sensitive questions. Use when the user asks for recent news, breaking headlines, latest updates, catalyst summaries, market-moving events, or futures dynamics such as crude oil, gold, copper, rebar, or Chinese index futures.
---

# Market News

Use the local market-news tools before free-form browsing when the user wants recent market information.

## Workflow

1. Use `futures_market_brief` for futures, commodities, or index-futures questions.
2. Use `market_news_brief` for concise topic summaries.
3. Use `market_news_search` when you need a broader headline set.
4. If the result set is thin or ambiguous, fall back to `web_search` / `web_fetch`.

## Output Rules

- Default to Chinese.
- Prefer a markdown table with columns `时间 | 来源 | 标题 | 链接`.
- Always mention the source name.
- Always use absolute timestamps if the result includes `publishedAt`.
- Separate facts from inference.
- Default to 6-10 rows when the user does not specify a count.
- Do not arbitrarily trim to 2-3 rows unless the user explicitly asks for brevity.
- If multiple headlines point to the same catalyst, collapse them into one short takeaway.

## Query Hints

- Chinese futures keywords usually work better with Chinese commodity names plus `期货`.
- Global macro and cross-asset moves often need an English follow-up query.
- For oil, gold, copper, rebar, and Chinese index futures, prefer `futures_market_brief` first.

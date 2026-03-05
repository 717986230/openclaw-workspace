---
name: signalradar
description: >-
  Monitors Polymarket prediction markets for probability changes and sends
  alerts when thresholds are crossed. Use when user asks to "add a Polymarket
  market", "monitor Polymarket", "check prediction markets", "list my monitors",
  "remove a monitor", "track market probabilities", or "run market check".
  Accepts any Polymarket event URL. Do NOT use for stock market analysis,
  sports betting, or real-time trading signals.
  监控 Polymarket 预测市场概率变化，超过阈值时推送通知。接受任意 Polymarket 事件链接。
  不适用于股市分析、体育博彩或实时交易信号。
allowed-tools: "Bash(python3:*)"
license: MIT
compatibility: Python 3.9+, network access to gamma-api.polymarket.com. No pip dependencies (stdlib only).
metadata:
  openclaw:
    emoji: "📡"
    requires:
      bins: ["python3"]
      env: []
      pip: []
    primaryEnv: ""
    envHelp:
      SIGNALRADAR_WORKSPACE_ROOT:
        required: false
        description: "Override workspace root directory. Auto-detected from script location if not set."
        howToGet: "Set to the absolute path of your workspace root, e.g. export SIGNALRADAR_WORKSPACE_ROOT=/path/to/workspace"
      SIGNALRADAR_CONFIG:
        required: false
        description: "Override config file path. Defaults to config/signalradar_config.json under workspace root."
        howToGet: "Set to absolute path of your config JSON, e.g. export SIGNALRADAR_CONFIG=/path/to/signalradar_config.json"
  author: vahnxu
  version: 0.5.0
---

# SignalRadar

## Critical Rules

- **Do NOT auto-add monitoring entries.** User must explicitly provide a Polymarket URL.
- **Do NOT create cron jobs** or scheduled tasks unless user explicitly asks.
- **Do NOT manually edit** `cache/`, `config/watchlist.json`, or baseline files. Normal runs automatically write these — that is expected behavior.
- **Do NOT run monitoring in a loop.** Run once per user request unless told otherwise.

## Quick Start

```bash
# Install (OpenClaw users)
clawhub install signalradar

# Or clone directly
git clone https://github.com/vahnxu/signalradar.git && cd signalradar

# 1. Health check
python3 scripts/signalradar.py doctor --output json

# 2. Add your first market
python3 scripts/signalradar.py add https://polymarket.com/event/your-market-here

# 3. Run a check
python3 scripts/signalradar.py run --dry-run --output json
```

## Common Tasks

### Add a market

```bash
python3 scripts/signalradar.py add <polymarket-event-url> [--category <name>]
```

Flow: parse URL → query Polymarket API → show market question + current probability → user confirms → record baseline.

- If the event has multiple markets (e.g., different date brackets), all are added by default. User can refine afterward.
- If some markets from the event are already monitored, only new ones are added.
- If the market is settled/expired, a warning is shown but the user can still add it.
- Category defaults to `default` if not specified. User is not prompted for category.
- On first-ever add (empty watchlist), a brief explanation of the baseline concept is shown.

### List monitors

```bash
python3 scripts/signalradar.py list [--category <name>] [--archived]
```

Shows all entries grouped by category with global sequential numbering. Each entry shows: number, question, current probability, baseline.

`--archived` shows previously removed entries (preserved for export).

### Remove a monitor

```bash
python3 scripts/signalradar.py remove <number>
```

Shows the entry name and asks for confirmation before removing. Removed entries are archived (moved to `archived` array in `config/watchlist.json`) with full history preserved.

### Run a check

```bash
python3 scripts/signalradar.py run [--dry-run] [--output json]
```

Checks all active entries against Polymarket API. If probability change exceeds threshold, sends alert via configured delivery channel.

- Settled/expired entries are skipped during run, with a summary at the end: "N entries settled, consider removing."
- When multiple markets from the same event trigger simultaneously, they are grouped in the alert.
- After a HIT is pushed, the baseline updates to the new probability value. The notification text includes "baseline updated to XX%."
- `--dry-run` fetches and evaluates but writes no state.

### Health check

```bash
python3 scripts/signalradar.py doctor --output json
```

Returns `{"status": "HEALTHY"}` if Python version and network connectivity are OK.

## Understanding Results

| Status | Meaning | Action |
|--------|---------|--------|
| `BASELINE` | First observation for an entry | Baseline recorded; no alert sent |
| `HIT` | Change exceeds threshold | Alert sent via delivery channel; baseline updated |
| `NO_REPLY` | No entries crossed threshold | Nothing to report |
| `SILENT` | Change below threshold | No alert sent |

### HIT output example

```json
{
  "status": "HIT",
  "request_id": "9f98e47e-6e0e-4563-b7c8-87a3b19e97af",
  "hits": [
    {
      "entry_id": "polymarket:12345:gpt5-release-june:evt_67890",
      "slug": "gpt5-release-june",
      "question": "GPT-5 released by June 30, 2026?",
      "current": 0.41,
      "baseline": 0.32,
      "abs_pp": 9.0,
      "confidence": "high",
      "reason": "abs_pp 9.0 >= threshold 5.0"
    }
  ],
  "ts": "2026-03-02T08:00:00Z"
}
```

When presenting a HIT to the user:
> **GPT-5 released by June 30, 2026?**: 32% → 41% (+9pp), threshold 5pp crossed. Baseline updated to 41%.

### Same-event grouped HIT

When multiple markets from the same event trigger:
> **Bitcoin price (March 31)** — 3 markets crossed threshold:
> - BTC > $100k: 45% → 58% (+13pp), baseline updated to 58%
> - BTC > $110k: 23% → 35% (+12pp), baseline updated to 35%
> - BTC > $120k:  8% → 19% (+11pp), baseline updated to 19%

### Empty watchlist

If there are no entries, run returns:
```json
{"status": "NO_REPLY", "message": "Watchlist is empty. Use 'signalradar.py add <url>' to add entries."}
```

## Configuration (Optional)

All settings have sensible defaults. Configuration file: `config/signalradar_config.json`.

| Setting | Default | Description |
|---------|---------|-------------|
| `threshold.abs_pp` | 5.0 | Global threshold in percentage points |
| `threshold.per_category_abs_pp` | `{}` | Per-category override, e.g. `{"AI": 4.0}` |
| `threshold.per_entry_abs_pp` | `{}` | Per-entry override, key = entry_id |
| `delivery.primary.channel` | `openclaw` | `openclaw`, `file`, or `webhook` |
| `delivery.primary.target` | `direct` | Path (file) or URL (webhook) |
| `digest.frequency` | `weekly` | `off` / `daily` / `weekly` / `biweekly` |
| `baseline.cleanup_after_expiry_days` | 90 | Days after market end date to clean up baseline |
| `profile.timezone` | `Asia/Shanghai` | Display timezone |
| `profile.language` | `""` | Empty = follow platform; set value to override |

### Delivery adapters

- **`openclaw`** (default) — delivers to OpenClaw platform messaging layer. No setup needed when installed via ClawHub.
- **`file`** — appends alerts to a local JSONL file. Set `target` to file path.
- **`webhook`** — HTTP POST to external endpoint. Set `target` to webhook URL (works with Slack, Discord, etc.).

For standalone use (not via OpenClaw), set delivery to `file` or `webhook`.

For full configuration reference, see `references/config.md`.

## Periodic Report

SignalRadar sends a periodic summary of all monitored entries (default: weekly). The report uses the same delivery channel as HIT alerts.

Contents:
- All entries with current probability and change since last report
- Settled/expired entries marked with a recommendation to remove
- Next report date

Frequency is controlled by `digest.frequency` in config.

## Local State (What This Skill Writes)

| Path | Purpose | When written |
|------|---------|--------------|
| `config/watchlist.json` | Monitored entries + archived entries | By `add` and `remove` commands |
| `cache/baselines/*.json` | Last-seen probability per market | Every non-dry-run check |
| `cache/events/*.jsonl` | Audit log of all decisions | Every non-dry-run check |

- `--dry-run` fetches and evaluates without writing any state.
- Users may hand-edit `config/watchlist.json` (e.g., to change categories). The system tolerates manual edits.
- No files outside the skill directory are modified.

## Scheduling (Optional)

SignalRadar does not create scheduled tasks automatically. For periodic monitoring:

```bash
# Every hour
0 * * * * cd /path/to/signalradar && python3 scripts/signalradar.py run
```

## Troubleshooting

| Error Code | Cause | Fix |
|------------|-------|-----|
| `SR_TIMEOUT` | Polymarket API timeout | Check network; retry after 30s |
| `SR_SOURCE_UNAVAILABLE` | Cannot reach gamma-api.polymarket.com | Verify DNS and internet access |
| `SR_VALIDATION_ERROR` | Malformed entry data | Run `python3 scripts/validate_schema.py` to identify the invalid field |
| `SR_ROUTE_FAILURE` | Delivery adapter failed | Check delivery config. Webhook: verify endpoint. File: verify write permissions |
| `SR_CONFIG_CONFLICT` | Contradictory config values | Review config for duplicate keys. See `references/config.md` |
| `SR_PERMISSION_DENIED` | Insufficient permissions | Check file permissions on config/ and cache/ directories |

## AI Agent Instructions (Complete)

### Presenting results

- **HIT**: Always show market question, probability change (old% → new%), magnitude in pp, and "baseline updated to X%". Group by event when multiple markets from the same event trigger.
- **BASELINE**: Tell the user "First run — baselines recorded for N markets. Run again later to detect changes." Do not present BASELINE as a problem.
- **NO_REPLY**: Briefly confirm "No markets crossed the threshold." Do not dump raw JSON.
- **Empty watchlist**: Guide the user to add entries: "No entries being monitored. Add a market with: `signalradar.py add <polymarket-url>`"

### Prohibited actions

- Do not auto-discover or suggest markets to add. Wait for user to provide URLs.
- Do not create cron jobs or scheduled tasks without explicit user request.
- Do not manually edit `cache/`, `config/watchlist.json`, or baseline files.
- Do not re-run monitoring in a loop.
- Do not assume a mode — there are no modes. Just run `signalradar.py run`.
- Do not mention or attempt to use Notion integration (removed in v0.5.0).

### Language handling

- System messages (prompts, confirmations, status text) follow platform language or `profile.language` setting.
- Market questions are always displayed in their original English text from Polymarket API. Do not translate market questions.

## References

- `references/config.md` — Full configuration reference
- `references/protocol.md` — Data contract (EntrySpec, SignalEvent, DeliveryEnvelope)
- `references/operations.md` — SLO targets, retry policy

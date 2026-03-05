# SignalRadar Configuration Reference

## Table of Contents

- [Precedence](#precedence)
- [Config Path Resolution](#config-path-resolution)
- [Full Config Shape](#full-config-shape)
- [Watchlist Storage](#watchlist-storage)
- [Threshold Rules](#threshold-rules)
- [Delivery Adapters](#delivery-adapters)
- [Periodic Report (Digest)](#periodic-report-digest)
- [Baseline Cleanup](#baseline-cleanup)
- [Profile](#profile)

## Precedence (High to Low)

1. CLI args (current run)
2. `config/signalradar_config.json` (via `--config` or `SIGNALRADAR_CONFIG`)
3. `DEFAULT_CONFIG` in `scripts/config_utils.py`

## Config Path Resolution

- First: `--config /path/to/signalradar_config.json`
- Then: env `SIGNALRADAR_CONFIG`
- Fallback: `<workspace>/config/signalradar_config.json`

## Full Config Shape

```json
{
  "profile": {
    "timezone": "Asia/Shanghai",
    "language": ""
  },
  "threshold": {
    "abs_pp": 5.0,
    "per_category_abs_pp": {},
    "per_entry_abs_pp": {}
  },
  "delivery": {
    "primary": {
      "channel": "openclaw",
      "target": "direct"
    }
  },
  "digest": {
    "frequency": "weekly"
  },
  "baseline": {
    "cleanup_after_expiry_days": 90
  },
  "source": {
    "retries": 2
  }
}
```

## Watchlist Storage

Monitored entries are stored in `config/watchlist.json` (not in config.json).

```json
{
  "entries": [
    {
      "entry_id": "polymarket:12345:grok-5-release:evt_67890",
      "slug": "grok-5-release",
      "question": "Grok 5 released by March 31, 2026?",
      "category": "AI",
      "url": "https://polymarket.com/event/grok-5-release",
      "end_date": "2026-03-31",
      "added_at": "2026-03-03T10:00:00Z"
    }
  ],
  "archived": [
    {
      "entry_id": "polymarket:99999:us-iran-ceasefire:evt_11111",
      "slug": "us-iran-ceasefire",
      "question": "US-Iran ceasefire by March 2, 2026?",
      "category": "default",
      "url": "https://polymarket.com/event/us-iran-ceasefire",
      "end_date": "2026-03-02",
      "added_at": "2026-02-20T08:00:00Z",
      "archived_at": "2026-03-05T10:00:00Z",
      "archive_reason": "user_removed",
      "baseline_history": [
        {"value": 0.23, "ts": "2026-02-20T08:00:00Z"},
        {"value": 0.41, "ts": "2026-02-25T12:00:00Z"}
      ],
      "final_result": "No"
    }
  ]
}
```

- `add` writes to `entries`
- `remove` moves from `entries` to `archived` (with full history)
- `run` reads from `entries`
- `list` displays `entries` (or `archived` with `--archived`)
- Users may hand-edit this file (e.g., to change category). The system tolerates manual edits.

## Threshold Rules

Priority order (highest wins):

1. Per-entry override: `threshold.per_entry_abs_pp.{entry_id}`
2. Per-category override: `threshold.per_category_abs_pp.{category}`
3. Global threshold: `threshold.abs_pp` (default: 5.0)

Example:

```json
{
  "threshold": {
    "abs_pp": 5.0,
    "per_category_abs_pp": {
      "AI": 4.0,
      "Crypto": 8.0
    },
    "per_entry_abs_pp": {
      "polymarket:12345:gpt5-release:evt_67890": 3.0
    }
  }
}
```

A HIT is triggered when `|current - baseline| >= applicable_threshold`.

## Delivery Adapters

| Channel | Target | Description |
|---------|--------|-------------|
| `openclaw` | `direct` | OpenClaw platform messaging (default when installed via ClawHub) |
| `file` | `/path/to/alerts.jsonl` | Appends alerts to local JSONL file |
| `webhook` | `https://hooks.slack.com/...` | HTTP POST to any webhook endpoint |

Example for Slack webhook:

```json
{
  "delivery": {
    "primary": {
      "channel": "webhook",
      "target": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    }
  }
}
```

For standalone use (not via OpenClaw), set delivery to `file` or `webhook`.

## Periodic Report (Digest)

| Setting | Values | Default |
|---------|--------|---------|
| `digest.frequency` | `off`, `daily`, `weekly`, `biweekly` | `weekly` |

- Uses the same delivery channel as HIT alerts.
- Reports all entries: current probability, change since last report, settled status.
- Settled entries are flagged with a recommendation to remove.

## Baseline Cleanup

| Setting | Default | Description |
|---------|---------|-------------|
| `baseline.cleanup_after_expiry_days` | 90 | Days after market `end_date` to clean up baseline files |

Cleanup removes baseline files when the market's end date has passed by more than the configured number of days.

## Profile

| Setting | Default | Description |
|---------|---------|-------------|
| `profile.timezone` | `Asia/Shanghai` | Timezone for user-facing timestamps |
| `profile.language` | `""` (empty) | Empty = follow platform language. Set a value (e.g. `"zh"`, `"en"`) to override. |

## Removed in v0.5.0

The following config fields are no longer supported:

| Removed Field | Reason |
|---------------|--------|
| `dedup.*` | Dedup removed. Repeated HITs are important signals. |
| `digest.only_important` | WatchLevel concept removed. |
| `rel_pct` / `rel_pct_enabled` | Relative threshold removed for simplicity. |
| Mode-related fields | Mode concept removed. All entries run together. |
| Notion-related fields | Notion integration removed. |

## Notes

- Runtime behavior is controlled by CLI/config; env vars are only used for path overrides.
- `config.example.json` in the repo root shows a minimal working config.

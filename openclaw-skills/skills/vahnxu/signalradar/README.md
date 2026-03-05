# SignalRadar

Monitor Polymarket prediction markets for probability changes. Get alerts when thresholds are crossed.

You choose exactly which markets to monitor by providing Polymarket URLs. Zero dependencies (Python stdlib only).

## Quick Start

```bash
git clone https://github.com/vahnxu/signalradar.git
cd signalradar

# Health check
python3 scripts/signalradar.py doctor --output json

# Add a market to monitor
python3 scripts/signalradar.py add https://polymarket.com/event/gpt5-release-june

# Run a check (dry-run, no side effects)
python3 scripts/signalradar.py run --dry-run --output json
```

First run records baselines. Run again later to detect changes.

## How It Works

```
User adds URL  --->  SignalRadar  --->  Delivery Adapter
                     (detect change)    (alert you)
                     threshold check
```

1. You add markets by URL (`add`)
2. SignalRadar fetches live probability from Polymarket API
3. Compares against recorded baseline
4. Sends alert when change exceeds threshold (default: 5 percentage points)
5. Baseline updates after each alert

## Commands

```bash
# Add a market (supports multi-market events)
python3 scripts/signalradar.py add <polymarket-url> [--category AI]

# List all monitored entries
python3 scripts/signalradar.py list

# Remove an entry by number
python3 scripts/signalradar.py remove 3

# Run a check
python3 scripts/signalradar.py run [--dry-run] [--output json]

# Health check
python3 scripts/signalradar.py doctor --output json
```

## Delivery: Get Alerts Your Way

### Webhook (Slack, Discord, Telegram, etc.)

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

Save as `config/signalradar_config.json`.

### File (local JSONL log)

```json
{
  "delivery": {
    "primary": {
      "channel": "file",
      "target": "/path/to/alerts.jsonl"
    }
  }
}
```

### OpenClaw (platform messaging)

Default when installed via ClawHub. See [OpenClaw install](#openclaw-install) below.

## Automated Monitoring with Cron

```bash
# Every hour
0 * * * * cd /path/to/signalradar && python3 scripts/signalradar.py run
```

## Understanding Results

| Status | Meaning |
|--------|---------|
| `BASELINE` | First observation. Baseline recorded, no alert. |
| `SILENT` | Change below threshold. No alert. |
| `HIT` | Threshold crossed. Alert sent. Baseline updated. |
| `NO_REPLY` | No markets crossed threshold. |

Example HIT:
```
GPT-5 release by June 2026: 32% -> 41% (+9pp), crossing 5pp threshold. Baseline updated to 41%.
```

## Configuration

All optional. Works out of the box with defaults.

| Setting | Default | Description |
|---------|---------|-------------|
| `threshold.abs_pp` | 5.0 | Alert threshold in percentage points |
| `threshold.per_category_abs_pp` | `{}` | Per-category override |
| `delivery.primary.channel` | `openclaw` | Delivery adapter |
| `digest.frequency` | `weekly` | Periodic report frequency |
| `baseline.cleanup_after_expiry_days` | 90 | Baseline cleanup after market ends |

See [`references/config.md`](references/config.md) for full reference.

## OpenClaw Install

If you use [OpenClaw](https://clawhub.com), install directly from the marketplace:

```bash
clawhub install signalradar
```

## Requirements

- Python 3.9+
- Network access to `gamma-api.polymarket.com`
- No pip dependencies (stdlib only)

## License

MIT

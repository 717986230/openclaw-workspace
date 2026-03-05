---
name: openclaw-dx
description: Diagnose and fix openclaw gateway issues. Use when the gateway is stuck, not starting, crash-looping, or rejecting connections. Covers main and --profile vesper gateways. Runs triage, applies fixes, writes incident report to ~/clawd/inbox.
---

# OpenClaw Gateway DX

Diagnose, fix, and document openclaw gateway issues. Covers both main (port 18789) and vesper profile (port 18999) gateways.

## When to Use

- Gateway not starting or crash-looping
- TUI/CLI can't connect (pairing required, password mismatch, device token mismatch)
- Gateway unresponsive or high memory
- After openclaw version upgrades
- User says "openclaw is stuck" or similar

## Triage Protocol

Run these in parallel to assess state:

```bash
# 1. What's listening?
lsof -i :18789 -i :18999 2>/dev/null | grep LISTEN

# 2. Process health (memory, CPU, uptime)
ps -o pid,rss,pcpu,lstart,etime -p $(lsof -i :18789 -t 2>/dev/null | head -1)

# 3. Recent errors
tail -30 ~/.openclaw/logs/gateway.err.log

# 4. Recent activity
tail -20 ~/.openclaw/logs/gateway.log

# 5. Channel status
openclaw channels status

# 6. Version
openclaw --version

# 7. Pending device pairings
openclaw devices list --json | head -20
```

## Common Failure Modes

### 1. Expired Channel Token (Slack xoxe.xoxb-)
**Symptom:** Crash loop with `Unhandled promise rejection: Error: An API error occurred: token_expired`
**Fix:**
```bash
# Disable the channel
# Edit ~/.openclaw/openclaw.json: channels.slack.enabled → false AND plugins.entries.slack.enabled → false
openclaw gateway start
# Then rotate token at api.slack.com and re-enable
```

### 2. Config Wiped by Upgrade
**Symptom:** `Gateway start blocked: set gateway.mode=local (current: unset)`
**Fix:** Restore from backup:
```bash
ls -la ~/.openclaw/openclaw.json.bak*
# Find the largest/most recent backup with full config
cp ~/.openclaw/openclaw.json.bak-XXXX ~/.openclaw/openclaw.json
openclaw doctor --fix
openclaw gateway start
```

### 3. Stale Lock File
**Symptom:** Gateway won't start, references old PID
**Fix:**
```bash
ls ~/.openclaw/gateway.*.lock
cat ~/.openclaw/gateway.*.lock  # check PID
kill -0 <pid>  # verify dead
rm ~/.openclaw/gateway.*.lock
openclaw gateway start
```

### 4. Device Token Mismatch / Pairing Required
**Symptom:** `unauthorized: device token mismatch` or `pairing required`
**Fix:**
```bash
openclaw devices list --json  # check for pending requests
openclaw devices approve "<requestId>" --password "Green198$sam"
# Or rotate existing device:
openclaw devices rotate --device <id> --role operator --password "Green198$sam"
```

### 5. Password Mismatch (multi-profile)
**Symptom:** `unauthorized: gateway password mismatch`
**Fix:** Sync passwords across profiles. All profiles should use `Green198$sam` to match the `OPENCLAW_GATEWAY_PASSWORD` env var in `~/.bashrc`.

### 6. Memory Bloat / Unresponsive
**Symptom:** Gateway listening but not responding, RSS > 2GB
**Fix:**
```bash
openclaw gateway stop
sleep 2
kill -9 <pid>  # if still lingering
launchctl bootstrap gui/501 ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

### 7. Invalid Plugin Entry
**Symptom:** `Config invalid: plugins.entries.X: plugin not found`
**Fix:** Remove the stale plugin entry from `~/.openclaw/openclaw.json`, then `openclaw gateway start`.

### 8. Port Conflict / Orphan Processes
**Symptom:** `Port 18789 is already in use` or multiple gateway PIDs
**Fix:**
```bash
ps aux | grep openclaw-gateway | grep -v grep
kill <orphan-pids>
openclaw gateway start
```

## Memory Thresholds

| RSS | Status | Action |
|-----|--------|--------|
| < 500MB | Healthy | None |
| 500MB-1.5GB | Elevated | Monitor |
| 1.5GB-2.5GB | High | Schedule restart |
| > 2.5GB | Critical | Restart now |

## Config Paths

| Profile | Config | State | Port |
|---------|--------|-------|------|
| main | `~/.openclaw/openclaw.json` | `~/.openclaw/` | 18789 |
| vesper | `~/.openclaw-vesper/openclaw.json` | `~/.openclaw-vesper/` | 18999 |

## Auth

- Gateway password: `Green198$sam` (env var `OPENCLAW_GATEWAY_PASSWORD` in `~/.bashrc`)
- `gateway.controlUi.dangerouslyDisableDeviceAuth: true` — only bypasses Control UI, not CLI/TUI
- CLI/TUI always requires device pairing in 2026.2.25+

## Post-Fix Protocol

After fixing any issue:
1. Verify: `openclaw channels status` — all channels should show "running"
2. Check memory: `ps -o pid,rss,pcpu,etime -p $(lsof -i :18789 -t | head -1)`
3. Write incident report to `~/clawd/inbox/YYYY-MM-DD-<description>.md`

## Incident Report Template

```markdown
# Incident: <Title> — YYYY-MM-DD

## Summary
<1-2 sentences>

## Symptoms
- <what the user saw>

## Root Cause
<what went wrong and why>

## Fix
<what was done>

## Config Changes
| File | Change |
|------|--------|

## Prevention
<how to avoid next time>
```

## Post-Upgrade Checklist

Run after any openclaw version bump:
```bash
openclaw --version
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.pre-upgrade
openclaw doctor --fix
openclaw devices list --json | jq '.pending'
# Approve any pending pairings
openclaw channels status
```

## Vesper Profile Commands

Prefix all commands with `--profile vesper`:
```bash
openclaw --profile vesper channels status
openclaw --profile vesper gateway start
openclaw --profile vesper doctor --fix
```

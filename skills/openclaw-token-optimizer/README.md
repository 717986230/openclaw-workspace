# OpenClaw Token Optimizer

**Reduce OpenClaw token usage and API costs by 50-80%.**

OpenClaw Token Optimizer is a focused OpenClaw skill for **smart model routing, lazy context loading, cache-aware heartbeat tuning, and token budget tracking**.

It is designed for people running:
- long OpenClaw sessions
- large workspaces
- cost-sensitive agent workflows
- multi-model OpenClaw setups

[![ClawHub](https://img.shields.io/badge/ClawHub-openclaw--token--optimizer-blue)](https://clawhub.ai/Asif2BD/openclaw-token-optimizer)
[![Version](https://img.shields.io/badge/version-1.4.2-green)](https://github.com/Asif2BD/OpenClaw-Token-Optimizer/blob/main/CHANGELOG.md)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://opensource.org/licenses/Apache-2.0)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-purple)](https://openclaw.ai)

---

## Why people care

Most OpenClaw cost problems come from a mix of:
- loading too much context
- using expensive models for simple tasks
- missing cache windows and paying the rewrite cost again
- not tracking budget until it is already too late

This skill helps fix that with practical local-first tooling.

### What you get

- **Smart model routing** for simple vs complex tasks
- **Lazy context loading** so small tasks do not pull in your whole workspace
- **Cache TTL heartbeat alignment** to reduce avoidable cache rewrites
- **Budget tracking** to keep OpenClaw usage visible
- **Native OpenClaw 2026.2.15 config patches** for session pruning and bootstrap size limits

---

## 30-second quick start

### Install from ClawHub
```bash
clawhub install Asif2BD/openclaw-token-optimizer
```

### Or install manually
```bash
git clone https://github.com/Asif2BD/OpenClaw-Token-Optimizer.git \
  ~/.openclaw/skills/openclaw-token-optimizer
```

Then add to `openclaw.json`:
```json
{
  "skills": {
    "load": {
      "extraDirs": ["~/.openclaw/skills/openclaw-token-optimizer"]
    }
  }
}
```

### Try the biggest win first
```bash
python3 scripts/context_optimizer.py recommend "build a login page"
# → Load only the files you need instead of the whole workspace
```

### Then route by task complexity
```bash
python3 scripts/model_router.py "design a microservices architecture"
# → Complex task → Opus

python3 scripts/model_router.py "thanks!"
# → Simple ack → Sonnet (cheapest available)
```

### Check your budget
```bash
python3 scripts/token_tracker.py check
```

---

## At a glance

| Problem | What this skill does |
|---|---|
| Too much context loaded | Recommends minimal files to load |
| Expensive model overuse | Routes simple tasks to cheaper models |
| Cache rewrite penalties | Aligns heartbeat to cache TTL windows |
| No budget visibility | Tracks token and cost usage |

---

## Expected savings

| Strategy | Context | Model | Monthly (100K tok/day) | Savings |
|---|---|---|---|---|
| Baseline (no optimization) | 50K | Sonnet | $9.00 | 0% |
| Context optimization only | 10K | Sonnet | $5.40 | 40% |
| Model routing only | 50K | Mixed | $5.40 | 40% |
| **Both (this skill)** | **10K** | **Mixed** | **$2.70** | **70%** |

---

## Best commands to demo

### 1. Context optimization
```bash
python3 scripts/context_optimizer.py recommend "hi, how are you?"
# → Load only 2 files, skip everything else → ~80% savings
```

### 2. Model routing
```bash
python3 scripts/model_router.py "design a microservices architecture"
# → Complex task → Opus
python3 scripts/model_router.py "thanks!"
# → Simple ack → Sonnet (cheapest available)
```

### 3. Optimized heartbeat
```bash
cp assets/HEARTBEAT.template.md ~/.openclaw/workspace/HEARTBEAT.md
python3 scripts/heartbeat_optimizer.py plan
```

### 4. Cache TTL alignment
```bash
python3 scripts/heartbeat_optimizer.py cache-ttl
# → recommended_interval: 55min (3300s)
```

### 5. Token budget check
```bash
python3 scripts/token_tracker.py check
```

---

## What's new in v1.4.x (OpenClaw 2026.2.15)

Three **native config patches** that work today with zero external dependencies:

### Session pruning
Auto-trim old tool results when the Anthropic cache TTL expires — reduces cache re-write costs.
```json
{ "agents": { "defaults": { "contextPruning": { "mode": "cache-ttl", "ttl": "5m" } } } }
```

### Bootstrap size limits
Cap workspace file injection into the system prompt (20-40% reduction for large workspaces).
```json
{ "agents": { "defaults": { "bootstrapMaxChars": 10000, "bootstrapTotalMaxChars": 15000 } } } }
```

### Cache retention for Opus
Amortize cache write costs on long Opus sessions.
```json
{ "agents": { "defaults": { "models": { "anthropic/claude-opus-4-5": { "params": { "cacheRetention": "long" } } } } } }
```

---

## Native OpenClaw diagnostics (2026.2.15+)

```text
/context list    → per-file token breakdown
/context detail  → full system prompt breakdown
/usage tokens    → append token count to every reply
/usage cost      → cumulative cost summary
```

---

## Skill structure

```text
openclaw-token-optimizer/
├── SKILL.md                    ← Skill definition (loaded by OpenClaw)
├── SECURITY.md                 ← Full security audit + provenance
├── CHANGELOG.md                ← Version history
├── .clawhubsafe                ← SHA256 integrity manifest (13 files)
├── .clawhubignore              ← Files excluded from publish bundle
├── scripts/
│   ├── context_optimizer.py    ← Context lazy-loading
│   ├── model_router.py         ← Task classification + model routing
│   ├── heartbeat_optimizer.py  ← Interval management + cache-ttl alignment
│   ├── token_tracker.py        ← Budget monitoring
│   └── optimize.sh             ← Convenience CLI wrapper (calls Python scripts)
├── assets/
│   ├── config-patches.json     ← Ready-to-apply config patches
│   ├── HEARTBEAT.template.md   ← Drop-in optimized heartbeat template
│   └── cronjob-model-guide.md  ← Model selection for cron tasks
└── references/
    └── PROVIDERS.md            ← Multi-provider strategy guide
```

---

## Security

All scripts are **local-only** — no network calls, no subprocess spawning, no system modifications. See [SECURITY.md](SECURITY.md) for full per-script audit.

Verify integrity:
```bash
cd ~/.openclaw/skills/openclaw-token-optimizer
sha256sum -c .clawhubsafe
```

Quick audit (should return nothing):
```bash
grep -r "urllib\|requests\|socket\|subprocess\|curl\|wget" scripts/
```

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for full version history.

**v1.4.2** — Security scanner fixes (provenance, optimize.sh manifest, SECURITY.md)  
**v1.4.1** — `.clawhubignore` added (fixes public visibility)  
**v1.4.0** — Native OpenClaw 2026.2.15 features (session pruning, bootstrap limits, cache TTL)  
**v1.3.3** — Correct display name on ClawHub  
**v1.3.2** — Security audit, SECURITY.md, .clawhubsafe manifest  

---

## Links

- **ClawHub:** https://clawhub.ai/Asif2BD/openclaw-token-optimizer
- **GitHub:** https://github.com/Asif2BD/OpenClaw-Token-Optimizer
- **OpenClaw Docs:** https://docs.openclaw.ai
- **License:** Apache 2.0
- **Author:** [Asif2BD](https://github.com/Asif2BD)

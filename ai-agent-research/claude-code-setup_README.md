# Claude Code as a Production Operating System

A curated guide to running Claude Code as a full operating system for business operations, trading, property management, and personal productivity.

This is not a toy setup. This is a production-grade agent system running 24/7 across two machines, managing real money, real properties, and real decisions.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [What This System Does](#what-this-system-does)
- [Key Numbers](#key-numbers)
- [Setup Components](#setup-components)
  - [Security-Hardened Permissions](#security-hardened-permissions)
  - [3-Tier Memory System](#3-tier-memory-system)
  - [Hooks System](#hooks-system)
  - [Multi-Agent Architecture](#multi-agent-architecture)
  - [Always-On Execution Engine](#always-on-execution-engine)
- [Files in This Repo](#files-in-this-repo)
- [Getting Started](#getting-started)

## Architecture Overview

```
+------------------+       +------------------+
|  Primary Mac     |       |  Mac Mini        |
|  (Command Center)|<----->|  (Execution      |
|                  | Tail- |   Engine)         |
|  Claude Code     | scale |  Trading bots    |
|  88+ skills      |       |  Scheduled agents|
|  11 agents       |       |  Always-on       |
+--------+---------+       +------------------+
         |
    +----+----+
    |         |
    v         v
 Supabase   Google Drive
 (Tier 2)   (File Storage)
```

## What This System Does

- **Property Management**: Manages ~50 rental properties. Downloads loan statements, reconciles PM invoices, generates GAAP financial statements, audits vendor charges.
- **Trading**: Runs crypto grid bots and prediction market scanners as always-on launchd services.
- **Memory**: Consolidates session learnings every 24 hours. Extracts patterns every 12 hours. Maintains continuity across sessions via handoff files.
- **Operations**: Drafts emails, processes documents, manages vendors, tracks deadlines. Claude acts as chief of staff.
- **Security**: Hardened permissions model with 150+ explicit allow patterns and critical operation deny rules.

## Key Numbers

| Metric | Value |
|--------|-------|
| Skills installed | 88+ |
| Specialized agents | 11 |
| Memory rows (Supabase) | 1,300+ |
| Allow patterns | 150+ |
| Deny rules | 16 critical operations |
| Properties managed | ~50 |
| Machines in fleet | 2 |

## Setup Components

### Security-Hardened Permissions

Claude Code's `allowEdits` mode with explicit allow/deny lists. Every command pattern is whitelisted. Destructive operations are blocked at the config level. No force pushes, no recursive deletes on home directory, no chmod 777.

See: [examples/settings.json.example](examples/settings.json.example)

### 3-Tier Memory System

- **Tier 1**: `CLAUDE.md` and memory files loaded automatically at session start. Zero cost until read.
- **Tier 2**: Supabase tables for unlimited, queryable storage. Structured decisions, learnings, session logs.
- **Tier 3**: Session handoff files for continuity between conversations.

See: [examples/memory-system.md](examples/memory-system.md)

### Hooks System

Native Claude Code hooks that fire on session events:

- **Stop hooks**: Memory consolidation (dream skill), pattern extraction (continuous learning)
- **PreToolUse hooks**: Context map validation before file edits
- **PostToolUse hooks**: File verification after writes
- **Notification hooks**: Watch for new files dropped into processing folders

See: [examples/hooks.md](examples/hooks.md)

### Multi-Agent Architecture

11 specialized agents, each with a defined scope:

1. **Chief of Staff** - Daily operations, prioritization, vendor management
2. **LiBRE Ops** - Property management, AppFolio data, PM accountability
3. **Crypto Trading Desk** - Bot management, market analysis, position tracking
4. **Diana Product** - SaaS product development for AI property management
5. **Health Optimizer** - Biomarker tracking, protocol management, wearable data
6. **Wealth Strategist** - Financial planning, tax optimization, portfolio analysis
7. **Content Engine** - Social media, thought leadership, audience building
8. **Clarity** - Meditation, reading, personal development tracking
9. **Elysium Ops** - Product development for cooling product venture
10. **Memory Architect** - Memory system maintenance, consolidation, retrieval
11. **Prediction Market Desk** - Event contract analysis, odds evaluation

See: [examples/agent-architecture.md](examples/agent-architecture.md)

### Always-On Execution Engine

A dedicated Mac Mini connected via Tailscale runs:

- Trading bots as `launchd` services (auto-restart on failure)
- Scheduled data pulls and report generation
- Background processing that does not require interactive sessions

## Files in This Repo

```
claude-code-setup/
  README.md                          # This file
  .gitignore                         # Standard ignores
  examples/
    settings.json.example            # Sanitized permissions config
    memory-system.md                 # 3-tier memory architecture
    hooks.md                         # Hooks system explained
    agent-architecture.md            # Multi-agent setup
```

## Getting Started

1. **Install Claude Code** following the [official docs](https://docs.anthropic.com/en/docs/claude-code).

2. **Set up your `CLAUDE.md`** in your home directory. This is auto-loaded every session. Put your identity, preferences, active projects, and key directories here.

3. **Configure permissions** in `~/.claude/settings.json`. Start with the example in this repo and customize the allow/deny lists for your workflow.

4. **Set up hooks** for automated behaviors. Start with the Stop hook for session wrap-up, then add PreToolUse guards as needed.

5. **Install skills** from the marketplace or build custom ones in `~/.claude/skills/`.

6. **Create memory files** in your project memory directories. Start with a `MEMORY.md` index file.

7. **Optional: Set up a second machine** for always-on workloads. Connect via Tailscale for secure access.

## Philosophy

Claude Code is not a chatbot. Treated correctly, it is an operating system layer that sits between you and every system you interact with. The key principles:

- **Bias toward action**: Configure it to execute, not ask for permission on routine operations.
- **Memory is everything**: Without persistent memory, every session starts from zero. Invest in the memory system.
- **Security by default**: Hardened permissions are not optional. One bad command can destroy real work.
- **Specialization scales**: One generalist agent hits limits fast. Eleven specialists with clear scopes do not.
- **Always-on beats on-demand**: Trading bots, monitoring, and scheduled tasks need a dedicated machine.

## License

MIT

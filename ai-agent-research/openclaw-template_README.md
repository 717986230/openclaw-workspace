# OpenClaw Workspace Template

A ready-to-use workspace template for [OpenClaw](https://github.com/openclaw/openclaw) with a 4-layer context memory system, agent specs, and distillation process.

## Quick Start (5 minutes)

```bash
# 1. Clone into your OpenClaw workspace
git clone https://github.com/janiceassistant216-prog/openclaw-workspace-template.git ~/.openclaw/workspace

# 2. Edit your identity
nano ~/.openclaw/workspace/SOUL.md      # Who is your AI?
nano ~/.openclaw/workspace/USER.md      # Who are you?
nano ~/.openclaw/workspace/IDENTITY.md  # Name, emoji, vibe

# 3. Start chatting
# Your AI reads these files automatically on session start
```

## What's Included

```
workspace/
├── AGENTS.md              ← Session startup rules + memory system docs
├── SOUL.md                ← AI personality and behavior (customize this!)
├── USER.md                ← About you (customize this!)
├── IDENTITY.md            ← AI name, emoji, avatar
├── MEMORY.md              ← Long-term curated memory (starts empty)
├── HEARTBEAT.md           ← Periodic check tasks (optional)
├── TOOLS.md               ← Local tool notes (cameras, SSH, etc.)
├── memory/
│   ├── README.md          ← Memory system documentation
│   ├── distillation-process.md  ← How raw events become curated memory
│   ├── agents-spec.md     ← 5 example agent roles with full specs
│   ├── daily/             ← Daily event logs (append-only)
│   │   └── .gitkeep
│   ├── projects/
│   │   └── _example/      ← Example project structure
│   │       ├── MEMORY.md
│   │       ├── RUNBOOK.md
│   │       ├── PROPOSALS.md
│   │       └── agents/coordinator/
│   │           ├── SUMMARY.md
│   │           ├── LOOPS.md
│   │           ├── PROPOSALS.md
│   │           └── LOOPS_ARCHIVE.md
│   └── _TEMPLATES/        ← Blank templates for new projects
│       ├── SUMMARY.md
│       ├── LOOPS.md
│       ├── PROPOSALS.md
│       └── LOOPS_ARCHIVE.md
└── .gitignore
```

## Memory System (4 Layers)

```
Layer 1: Daily Logs        → memory/daily/YYYY-MM-DD.md (raw truth, append-only)
Layer 2: Working Context   → chat history (ephemeral, in-session only)
Layer 3: Rolling State     → SUMMARY.md + LOOPS.md per agent/project
Layer 4: Curated Memory    → MEMORY.md (global + per-project)
```

**Data flows up, never down:**
```
You chat → daily log → PROPOSALS.md → coordinator reviews → MEMORY.md
```

Sub-agents can only write to `PROPOSALS.md`. Only the coordinator promotes to `MEMORY.md`. This prevents memory pollution.

## Agent Roles (5 included)

| Agent | Role | Best For |
|-------|------|----------|
| coordinator | Orchestrator | Task breakdown, review, memory management |
| researcher | Technical Researcher | Evaluating tools, APIs, best practices |
| backend-dev | Backend Developer | Go/Python/TS APIs, databases |
| frontend-dev | Frontend Developer | React/Vue/Svelte, CSS, UI |
| qa | QA Engineer | Code review, testing, bug finding |

Each agent has:
- Clear role definition
- Explicit "must NOT" constraints (prevents role bleed)
- Output format specification
- Tool access rules

### Quick spawn (simple tasks)
```
sessions_spawn({
  task: "Build the user auth API",
  mode: "run",
  label: "backend-dev-auth"
})
```

### Proper multi-agent (recommended)
```bash
# Create dedicated agents with their own workspace + identity
openclaw agents add backend-dev
openclaw agents add qa

# Each agent gets its own SOUL.md, AGENTS.md, tools, sessions
# Then spawn with auto-loaded context:
sessions_spawn({ task: "Fix the bug", agentId: "backend-dev", mode: "run" })
```

See `memory/agents-spec.md` for full specs, setup instructions, and role definitions.

## Distillation Process

**When to distill:**
- Working → SUMMARY/LOOPS: every ~10-20 turns or when context feels large
- SUMMARY → MEMORY: milestones only (task done, decision made, lesson learned)
- Weekly: prune stale proposals, archive closed loops, dedupe memory

**What never goes into long-term memory:**
- Secrets, tokens, passwords
- One-off chat banter
- Unverified assumptions
- Transient debugging logs

See `memory/distillation-process.md` for the full process.

## Adding a New Project

```bash
# Copy the template structure
cp -r memory/projects/_example memory/projects/my-project

# Edit the project memory
nano memory/projects/my-project/MEMORY.md
```

## Automation (Optional)

Add these cron jobs for automated memory management:

**Daily distillation (10pm)** — auto-extracts facts from today's conversations into PROPOSALS.md:
```
Schedule: 0 22 * * * (your timezone)
Prompt: "Read today's daily log. Extract key decisions and lessons into PROPOSALS.md."
```

**Weekly hygiene (Monday 10am)** — reviews proposals, promotes accepted ones, prunes stale:
```
Schedule: 0 10 * * 1 (your timezone)
Prompt: "Review PROPOSALS.md files. Accept/reject. Promote accepted to MEMORY.md. Archive closed LOOPS."
```

## Customization Guide

### Minimal setup (single agent, no sub-agents)
Just use:
- `SOUL.md` — your AI's personality
- `USER.md` — about you
- `MEMORY.md` — long-term memory
- `memory/daily/` — daily logs

That's it. The 4-layer system works even with just these files.

### Full setup (multi-agent orchestration)
Use everything:
- All 4 layers
- Agent specs in `memory/agents-spec.md`
- Per-project memory folders
- PROPOSALS.md gate for sub-agent writes
- Automated distillation cron jobs

## Credits

Built from real-world usage running a multi-agent AI workforce with OpenClaw.

Based on patterns from: Claude Code memory system, Mem0, Letta/MemGPT, CrewAI memory, and months of daily usage.

## License

MIT — use it, fork it, improve it.

# AGENTS.md

## Purpose

This workspace is the main OpenClaw operating workspace for the local agent.
Keep changes pragmatic, reversible, and easy to verify.

## Default Context Loading

Load the minimum context first:

1. `SOUL.md`
2. `IDENTITY.md`

Load extra files only when needed:

- `MEMORY.md` when the user asks about history, memory, or prior decisions
- `TOOLS.md` when the task depends on local tools, bridges, devices, or environment-specific rules
- `USER.md` when the task depends on user preferences or identity

Do not load unrelated docs or old memory logs by default.

## Working Rules

1. Acknowledge incoming work before taking action.
2. Prefer the simplest effective change.
3. Do not run destructive or external actions silently.
4. Verify changes before claiming success.
5. When a task goes off track, stop and re-plan instead of pushing through blindly.

## Local AI Delegation

Use local AI delegation sparingly and in this order:

1. Default tool: `ask_local_ai_routed`
2. Default mode: `claude_only`
3. Use `claude_then_codex_review` only when the task needs validation, second opinion, or risk review.
4. Use `codex_only` only when explicitly requested.
5. After bridge or CLI changes, run `ai_bridge_selftest` before relying on delegation.

### Routed Claude Requests

- If a user asks to "让 Claude Code 继续", "继续写小说项目", "继续 novel-ai", or otherwise wants Claude Code to resume local coding work, do not use interactive `exec` plus `process write`.
- For these requests, call `ask_claude_code` directly with a concrete task and an explicit `cwd`.
- The default novel project directory is `D:\OPP\novel-ai`.
- If the user says "继续小说项目" and does not name a different repo, treat it as `D:\OPP\novel-ai`.
- Use `Claude-Code-Game-Studios` only when the user explicitly asks for the game studio project.

## Safety

- Do not exfiltrate private data.
- Do not modify credentials, auth files, or channel secrets unless the user explicitly asks.
- Do not run destructive commands without clear confirmation.
- Prefer recoverable operations over irreversible ones.

## Maintenance

- Use the local maintenance tools before manual repair when possible:
  - `openclaw_service_status`
  - `openclaw_check_updates`
  - `openclaw_sync_runtime_metadata`
  - `openclaw_archive_orphan_transcripts`
  - `openclaw_restart_gateway_task`
  - `openclaw_doctor_fix`

## Channel Notes

- Current active channels are expected to include Discord, Feishu, and Weixin.
- If channel behavior looks wrong, inspect gateway health before changing channel config.

## Completion Standard

Before marking work done:

1. Confirm the target file or service actually changed as intended.
2. Check logs, command output, or service status where relevant.
3. Report blockers or residual risk plainly.

## Tools

### Local notes (migrated from TOOLS.md)

# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### Local AI Routing

- Default local delegation tool: `ask_local_ai_routed`
- Default mode: `claude_only`
- Preferred path: Claude Code first, because it is faster and already tuned to the local NVIDIA-backed setup
- Use `claude_then_codex_review` only when the task needs a second opinion, risk review, or validation
- Use `codex_only` only when the user explicitly asks for Codex or wants a non-Claude second opinion
- Avoid calling `ask_claude_code` and `ask_codex_local` separately when `ask_local_ai_routed` can do the job
- Before relying on the bridge after upgrades or config changes, run `ai_bridge_selftest`
- For "继续写小说项目" style requests, call `ask_claude_code` with `cwd: D:\OPP\novel-ai`
- Do not open Claude via interactive `exec` for resume-style coding requests unless the user explicitly asks for an interactive shell session

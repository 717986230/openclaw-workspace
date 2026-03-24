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

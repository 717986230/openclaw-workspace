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

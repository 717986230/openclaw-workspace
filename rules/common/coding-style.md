# Common Coding Style

This document defines the general coding style and working rules for the OpenClaw workspace. These rules apply to all languages and projects unless overridden by language-specific rules.

## Working Rules

1.  **Acknowledge Incoming Work:** Always acknowledge incoming work before taking action.
2.  **Prefer Simplicity:** Prefer the simplest effective change over complex solutions.
3.  **No Silent Destructive Actions:** Do not run destructive or external actions silently.
4.  **Verify Changes:** Verify changes before claiming success.
5.  **Stop and Re-plan:** When a task goes off track, stop and re-plan instead of pushing through blindly.

## Maintenance

Use local maintenance tools before manual repair when possible:

-   `openclaw_service_status`
-   `openclaw_check_updates`
-   `openclaw_sync_runtime_metadata`
-   `openclaw_archive_orphan_transcripts`
-   `openclaw_restart_gateway_task`
-   `openclaw_doctor_fix`

## Completion Standard

Before marking work done:

1.  Confirm the target file or service actually changed as intended.
2.  Check logs, command output, or service status where relevant.
3.  Report blockers or residual risk plainly.

## Context Loading

Load the minimum context first:

1.  `SOUL.md`
2.  `IDENTITY.md`

Load extra files only when needed:

-   `MEMORY.md` when the user asks about history, memory, or prior decisions
-   `TOOLS.md` when the task depends on local tools, bridges, devices, or environment-specific rules
-   `USER.md` when the task depends on user preferences or identity

Do not load unrelated docs or old memory logs by default.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)

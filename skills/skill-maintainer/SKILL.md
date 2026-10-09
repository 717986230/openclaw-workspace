---
name: "skill-maintainer"
description: "Maintain and update OpenClaw skills - handle updates, check status, resolve local change conflicts"
---

# Skill Maintainer

Maintain and update OpenClaw skills - handle updates, check status, resolve local change conflicts.

## Update All Skills

When you need to update all installed skills to their latest versions:

```bash
openclaw skills update --all
```

## Handle Local Change Conflicts

If you see warnings like:
```
Skill "X" was installed before OpenClaw recorded file fingerprints, so local changes cannot be detected. Updating replaces the installed skill directory. Re-run with --force to update it anyway.
```

Re-run the update with the `--force` flag:

```bash
openclaw skills update --all --force
```

## Verify Skill Installation

To verify that skills are properly installed as ClawHub-tracked skills, check for the presence of `.clawhub` directories:

```bash
find ~/openclaw-workspace/skills -name ".clawhub" -type d
```

Each skill directory containing a `.clawhub` subdirectory is a ClawHub-tracked skill that receives official updates.

## Check Skill Status

To see which skills are managed by ClawHub and their installation status:

```bash
openclaw skills list --verbose
```

This shows version information, installation source, and whether skills are up to date.

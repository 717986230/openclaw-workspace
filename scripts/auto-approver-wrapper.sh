#!/bin/bash
# Wrapper for auto-approver via WSL
SESSION_NAME="$1"
if [ -z "$SESSION_NAME" ]; then
    echo "Usage: $0 <session-name>"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTO_APPROVER="$(dirname "$SCRIPT_DIR")/.agents/skills/claude-code-wingman/auto-approver.sh"

exec wsl -d Ubuntu -e bash "$AUTO_APPROVER" "$SESSION_NAME"
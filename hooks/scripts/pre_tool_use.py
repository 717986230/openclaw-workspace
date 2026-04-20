#!/usr/bin/env python3
"""
PreToolUse Hook - Security Checks
Triggered before any tool is executed. Useful for security checks, validation, or logging.
"""

import json
import sys
from typing import Dict, Any

# Security patterns to check for
SECURITY_PATTERNS = {
    "password": ["password", "passwd", "pwd"],
    "token": ["token", "api_key", "secret"],
    "credential": ["credential", "auth", "login"],
    "destructive": ["rm -rf", "del /f", "format", "wipe"],
}

def check_security_risks(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check for security risks in tool usage.

    Args:
        tool_name: Name of the tool being used.
        tool_args: Arguments passed to the tool.

    Returns:
        Dictionary with security check results.
    """
    risks = []
    args_str = json.dumps(tool_args, default=str).lower()

    # Check for security patterns
    for category, patterns in SECURITY_PATTERNS.items():
        for pattern in patterns:
            if pattern in args_str:
                risks.append({
                    "category": category,
                    "pattern": pattern,
                    "severity": "high" if category in ["password", "token", "credential"] else "medium"
                })

    # Check for destructive commands in exec
    if tool_name == "exec":
        command = tool_args.get("command", "")
        for pattern in SECURITY_PATTERNS["destructive"]:
            if pattern in command.lower():
                risks.append({
                    "category": "destructive",
                    "pattern": pattern,
                    "severity": "high"
                })

    return {
        "tool": tool_name,
        "has_risks": len(risks) > 0,
        "risks": risks,
        "action": "block" if any(r["severity"] == "high" for r in risks) else "warn"
    }

def main():
    """Main hook execution."""
    # Read tool info from stdin (JSON format)
    try:
        tool_info = json.load(sys.stdin)
    except:
        # If no input, just exit
        sys.exit(0)

    tool_name = tool_info.get("tool", "unknown")
    tool_args = tool_info.get("args", {})

    # Perform security check
    result = check_security_risks(tool_name, tool_args)

    # Output result
    print(json.dumps(result, indent=2))

    # Exit with error code if high-risk
    if result["action"] == "block":
        sys.exit(1)

if __name__ == "__main__":
    main()

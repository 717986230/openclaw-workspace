#!/usr/bin/env python3
"""
PostToolUse Hook - Logging
Triggered after a tool has completed. Useful for cleanup, analytics, or triggering follow-up actions.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Log file path
LOG_DIR = Path(r"C:\Users\Administrator\.openclaw\workspace\logs")
LOG_FILE = LOG_DIR / "tool_usage.log"

def log_tool_usage(tool_name: str, tool_args: Dict[str, Any], result: Any, duration_ms: int):
    """
    Log tool usage for analytics.

    Args:
        tool_name: Name of the tool that was used.
        tool_args: Arguments passed to the tool.
        result: Result of the tool execution.
        duration_ms: Duration of the tool execution in milliseconds.
    """
    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "args": tool_args,
        "duration_ms": duration_ms,
        "success": result is not None,
    }

    # Write to log file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

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
    result = tool_info.get("result", None)
    duration_ms = tool_info.get("duration_ms", 0)

    # Log tool usage
    log_tool_usage(tool_name, tool_args, result, duration_ms)

    # Output result
    print(json.dumps({
        "tool": tool_name,
        "logged": True,
        "log_file": str(LOG_FILE)
    }, indent=2))

if __name__ == "__main__":
    main()

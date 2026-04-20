#!/usr/bin/env python3
"""
OnError Hook - Error Logging and Recovery
Triggered when an error occurs. Useful for error logging, recovery, or alerting.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Log file path
LOG_DIR = Path(r"C:\Users\Administrator\.openclaw\workspace\logs")
ERROR_LOG_FILE = LOG_DIR / "error.log"

# Recovery actions
RECOVERY_ACTIONS = {
    "tool_error": "retry_tool",
    "network_error": "retry_with_backoff",
    "permission_error": "request_permission",
    "timeout_error": "increase_timeout",
    "unknown_error": "log_and_continue"
}

def log_error(error_info: Dict[str, Any]):
    """
    Log error for analysis.

    Args:
        error_info: Dictionary containing error information.
    """
    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": error_info.get("session_id", "unknown"),
        "error_type": error_info.get("error_type", "unknown"),
        "error_message": error_info.get("error_message", ""),
        "error_details": error_info.get("error_details", {}),
        "context": error_info.get("context", {}),
        "severity": error_info.get("severity", "medium")
    }

    # Write to error log
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def suggest_recovery(error_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Suggest recovery action based on error type.

    Args:
        error_info: Dictionary containing error information.

    Returns:
        Dictionary containing recovery suggestion.
    """
    error_type = error_info.get("error_type", "unknown")
    error_message = error_info.get("error_message", "").lower()

    # Determine recovery action
    recovery_action = RECOVERY_ACTIONS.get("unknown_error", "log_and_continue")

    # Check for specific error patterns
    if "permission" in error_message or "access" in error_message:
        recovery_action = RECOVERY_ACTIONS.get("permission_error", "request_permission")
    elif "timeout" in error_message or "timed out" in error_message:
        recovery_action = RECOVERY_ACTIONS.get("timeout_error", "increase_timeout")
    elif "network" in error_message or "connection" in error_message:
        recovery_action = RECOVERY_ACTIONS.get("network_error", "retry_with_backoff")
    elif "tool" in error_message:
        recovery_action = RECOVERY_ACTIONS.get("tool_error", "retry_tool")

    return {
        "error_type": error_type,
        "recovery_action": recovery_action,
        "suggestion": f"Consider {recovery_action} to recover from this error"
    }

def analyze_error(error_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze error for patterns and trends.

    Args:
        error_info: Dictionary containing error information.

    Returns:
        Dictionary containing error analysis.
    """
    error_type = error_info.get("error_type", "unknown")
    error_message = error_info.get("error_message", "")

    # Analyze error patterns
    patterns = []

    if "permission" in error_message.lower():
        patterns.append("permission_denied")
    if "timeout" in error_message.lower():
        patterns.append("timeout")
    if "network" in error_message.lower():
        patterns.append("network_issue")
    if "not found" in error_message.lower():
        patterns.append("resource_not_found")
    if "invalid" in error_message.lower():
        patterns.append("invalid_input")

    return {
        "error_type": error_type,
        "patterns": patterns,
        "severity": error_info.get("severity", "medium"),
        "requires_intervention": len(patterns) > 0 and "permission_denied" in patterns
    }

def main():
    """Main hook execution."""
    # Read error info from stdin (JSON format)
    try:
        error_info = json.load(sys.stdin)
    except:
        # If no input, just exit
        sys.exit(0)

    # Log error
    log_error(error_info)

    # Suggest recovery
    recovery = suggest_recovery(error_info)

    # Analyze error
    analysis = analyze_error(error_info)

    # Output result
    print(json.dumps({
        "logged": True,
        "log_file": str(ERROR_LOG_FILE),
        "recovery": recovery,
        "analysis": analysis
    }, indent=2))

if __name__ == "__main__":
    main()

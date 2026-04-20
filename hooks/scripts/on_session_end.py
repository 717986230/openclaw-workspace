#!/usr/bin/env python3
"""
OnSessionEnd Hook - State Saving
Triggered when a session ends. Useful for saving state, generating summaries, or cleaning up resources.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# State file path
STATE_DIR = Path(r"C:\Users\Administrator\.openclaw\workspace\state")
STATE_FILE = STATE_DIR / "session_state.json"

def save_session_state(session_info: Dict[str, Any]):
    """
    Save session state for future reference.

    Args:
        session_info: Dictionary containing session information.
    """
    # Ensure state directory exists
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    # Create state entry
    state_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_info.get("session_id", "unknown"),
        "duration_ms": session_info.get("duration_ms", 0),
        "total_tokens": session_info.get("total_tokens", 0),
        "total_cost_usd": session_info.get("total_cost_usd", 0.0),
        "tools_used": session_info.get("tools_used", []),
        "errors": session_info.get("errors", []),
    }

    # Load existing state
    existing_state = []
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            try:
                existing_state = json.load(f)
            except:
                existing_state = []

    # Append new state
    existing_state.append(state_entry)

    # Save state
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_state, f, indent=2)

def generate_session_summary(session_info: Dict[str, Any]) -> str:
    """
    Generate a summary of the session.

    Args:
        session_info: Dictionary containing session information.

    Returns:
        Summary string.
    """
    duration_ms = session_info.get("duration_ms", 0)
    duration_sec = duration_ms / 1000

    summary = f"""
Session Summary
===============
Session ID: {session_info.get('session_id', 'unknown')}
Duration: {duration_sec:.2f} seconds
Total Tokens: {session_info.get('total_tokens', 0)}
Total Cost: ${session_info.get('total_cost_usd', 0.0):.4f}
Tools Used: {len(session_info.get('tools_used', []))}
Errors: {len(session_info.get('errors', []))}
"""
    return summary

def main():
    """Main hook execution."""
    # Read session info from stdin (JSON format)
    try:
        session_info = json.load(sys.stdin)
    except:
        # If no input, just exit
        sys.exit(0)

    # Save session state
    save_session_state(session_info)

    # Generate summary
    summary = generate_session_summary(session_info)

    # Output result
    print(json.dumps({
        "saved": True,
        "state_file": str(STATE_FILE),
        "summary": summary.strip()
    }, indent=2))

if __name__ == "__main__":
    main()

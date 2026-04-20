#!/usr/bin/env python3
"""
OnSessionStart Hook - Context Loading
Triggered when a new session begins. Useful for loading context or initializing state.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# State file path
STATE_DIR = Path(r"C:\Users\Administrator\.openclaw\workspace\state")
STATE_FILE = STATE_DIR / "session_state.json"

# Context file path
CONTEXT_DIR = Path(r"C:\Users\Administrator\.openclaw\workspace\contexts")

def load_session_state() -> Dict[str, Any]:
    """
    Load previous session state for continuity.

    Returns:
        Dictionary containing previous session state.
    """
    if not STATE_FILE.exists():
        return {
            "previous_sessions": 0,
            "last_session_id": None,
            "last_session_time": None
        }

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        try:
            state = json.load(f)
            if state:
                last_session = state[-1] if isinstance(state, list) else state
                return {
                    "previous_sessions": len(state) if isinstance(state, list) else 1,
                    "last_session_id": last_session.get("session_id"),
                    "last_session_time": last_session.get("timestamp"),
                    "last_session_duration_ms": last_session.get("duration_ms"),
                    "last_session_tokens": last_session.get("total_tokens"),
                    "last_session_cost_usd": last_session.get("total_cost_usd")
                }
        except:
            pass

    return {
        "previous_sessions": 0,
        "last_session_id": None,
        "last_session_time": None
    }

def load_context(mode: str = "default") -> Dict[str, Any]:
    """
    Load context based on mode.

    Args:
        mode: Context mode (default, dev, review, research).

    Returns:
        Dictionary containing context information.
    """
    context_file = CONTEXT_DIR / f"{mode}.md"

    if not context_file.exists():
        return {
            "mode": mode,
            "context": f"No context file found for mode: {mode}"
        }

    with open(context_file, "r", encoding="utf-8") as f:
        context_content = f.read()

    return {
        "mode": mode,
        "context": context_content,
        "context_file": str(context_file)
    }

def initialize_session(session_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize session with context and state.

    Args:
        session_info: Dictionary containing session information.

    Returns:
        Dictionary containing initialization results.
    """
    # Load previous session state
    previous_state = load_session_state()

    # Load context based on mode
    mode = session_info.get("mode", "default")
    context = load_context(mode)

    # Create initialization result
    result = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_info.get("session_id", "unknown"),
        "mode": mode,
        "previous_state": previous_state,
        "context": context,
        "initialized": True
    }

    return result

def main():
    """Main hook execution."""
    # Read session info from stdin (JSON format)
    try:
        session_info = json.load(sys.stdin)
    except:
        # If no input, just exit
        sys.exit(0)

    # Initialize session
    result = initialize_session(session_info)

    # Output result
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

# HEARTBEAT.md

Keep this file empty (or with only comments) to skip heartbeat API calls.
Add tasks below when you want the agent to check something periodically.

## Periodic Checks

### Session Memory Guard
On each heartbeat, check if session cleanup is needed:
- If session files > 100, run: `scripts/session_memory_guard.ps1 -ForceCleanup -KeepRecent 50`
- Otherwise report: HEARTBEAT_OK

### Memory Database Health
- Verify SQLite database accessible at `memory/database/xiaozhi_memory.db`
- Verify LanceDB accessible at `memory/database/lancedb`

### Memory System Maintenance
On each heartbeat, run memory maintenance:
- Run: `python scripts/memory_bridge.py stats` to check memory health
- If episodic_memories > 1000, run cleanup: `DELETE FROM episodic_memories WHERE created_at < datetime('now', '-90 days')`
- If working_memory > 500, run cleanup: `DELETE FROM working_memory WHERE expires_at < datetime('now')`
- Otherwise report: HEARTBEAT_OK

# Erbing AI Agent Evolution System - Hermes Agent Deep Dive Summary

## Overview
Deep mining and integration of patterns from Hermes Agent (99k stars), Claude Code Production, MasterClaw Core, and OpenClaw 4-layer Template for Erbing's evolution system.

## Completed Components

### 1. ErbingContextCompressor
**Source:** `hermes/core/agent/agent_context_compressor.py` (55KB)
**File:** `scripts/erbing_context_compressor.py`

**Key Features:**
- Tool output pruning with 1-line summaries
- Token-budget tail protection (scales with model context)
- Structured 13-section handoff summary
- Iterative summary updates across compactions
- Orphan tool call/result pair sanitization
- Anti-thrashing (skip if last 2 saved <10%)
- 600s cooldown on LLM failure

**Test Result:** 72 messages → 4 messages, 99% token savings

**Commit:** 2f58e02

---

### 2. ErbingCheckpointManager
**Source:** `hermes/core/tools/tools_checkpoint_manager.py` (24KB)
**File:** `scripts/erbing_checkpoint_manager.py`

**Key Features:**
- Shadow git repos (GIT_DIR + GIT_WORK_TREE) for transparent snapshots
- Git isolation (GIT_CONFIG_GLOBAL/SYSTEM = devnull) to prevent user config leaks
- Per-turn deduplication (one snapshot per directory per turn)
- Pre-rollback snapshot (undo the undo)
- Project root detection (walks up to find .git, pyproject.toml, etc.)
- Input validation (git argument injection + path traversal protection)
- Max files limit (50,000) to avoid slowdowns
- Default excludes (node_modules, dist, build, .env, __pycache__, etc.)

**Test Result:** Validation working (hash injection blocked, path traversal blocked)

**Commit:** 84a27aa

---

### 3. ErbingSkillManager
**Source:** `hermes/core/tools/tools_skill_manager_tool.py` (28KB)
**File:** `scripts/erbing_skill_manager.py`

**Key Features:**
- Skill directory structure (SKILL.md + references/templates/scripts/assets/)
- Validation system (name, category, frontmatter, content size, file size)
- Atomic writes (temp file + os.replace for crash safety)
- Security scanning (post-write scan with rollback on block)
- Fuzzy matching for patch operations
- Path security (traversal prevention)
- Cross-directory skill lookup
- Local skill check (only local skills can be modified/deleted)
- Cache clearing (system prompt cache after modifications)

**Test Result:** Validation working (name, category, frontmatter, path traversal blocked)

**Commit:** d5dcf90

---

### 4. ErbingSkillUtils
**Source:** `hermes/core/agent/agent_skill_utils.py`
**File:** `scripts/erbing_skill_utils.py`

**Key Features:**
- Frontmatter parsing (YAML with fallback to simple key:value)
- Platform matching (skills declare platform requirements)
- Disabled skills management (config-based exclusion)
- External skills directories (config.yaml external_dirs)
- Condition extraction (fallback_for_toolsets, requires_toolsets, etc.)
- Skill config extraction (config variable declarations)
- Description extraction (truncated for display)
- File iteration (walk skills dirs with exclusions)
- Namespace parsing (namespace:skill-name format)

**Test Result:** All utilities working (frontmatter, platform, conditions, config vars, description, namespace)

**Commit:** 944b785

---

## Additional Components Analyzed

### MemoryProvider (Abstract Base Class)
**Source:** `hermes/core/agent/agent_memory_provider.py`
**Status:** Interface definition only, not ported (Erbing has SQLite + LanceDB)

**Key Patterns:**
- Lifecycle methods: initialize, prefetch, sync_turn, shutdown
- Optional hooks: on_turn_start, on_session_end, on_pre_compress, on_delegation
- Tool schema exposure
- Config schema for setup

---

### MemoryStore (File-Backed Memory)
**Source:** `hermes/core/tools/tools_memory_tool.py`
**Status:** Not ported (Erbing has SQLite + LanceDB)

**Key Patterns:**
- Two stores: MEMORY.md (agent notes) and USER.md (user profile)
- Character limits (not token limits)
- File locking (fcntl on Unix, msvcrt on Windows)
- Atomic writes (temp file + os.replace)
- Injection/exfiltration scanning
- Frozen snapshot for system prompt injection
- Operations: add, replace, remove

**Security Patterns Worth Adopting:**
- Threat pattern detection (prompt injection, exfiltration)
- Invisible unicode character detection
- Content scanning before accepting writes

---

### SessionSearchTool (Long-Term Conversation Recall)
**Source:** `hermes/core/tools/tools_session_search_tool.py`
**Status:** Not ported (Erbing has LanceDB for semantic search)

**Key Patterns:**
- FTS5 search (SQLite full-text search)
- Group by session, take top N unique sessions
- Truncate to ~100k chars centered on matches
- Use cheap/fast model (Gemini Flash) for summarization
- Return per-session summaries with metadata

**Truncation Strategy:**
1. Full-phrase search
2. Proximity co-occurrence of all terms (within 200 chars)
3. Individual term positions (last resort)
4. Pick window that covers the most match positions

---

## Git Commits

```
2f58e02 feat: ErbingContextCompressor - Hermes-style context compression
84a27aa feat: ErbingCheckpointManager - Hermes-style transparent filesystem snapshots
d5dcf90 feat: ErbingSkillManager - Hermes-style autonomous skill creation
944b785 feat: ErbingSkillUtils - Hermes-style skill metadata utilities
```

---

## Next Steps

### Integration Tasks
1. Integrate ErbingContextCompressor into ErbingMemoryManager
2. Integrate ErbingCheckpointManager into ErbingMemoryManager
3. Integrate ErbingSkillManager into ErbingMemoryManager
4. Integrate ErbingSkillUtils into ErbingMemoryManager

### Testing Tasks
1. End-to-end test of full integration
2. Performance benchmarking
3. Security audit

### Documentation Tasks
1. Update Erbing's AI Agent Configuration
2. Create user guide for skill creation
3. Create developer guide for extending the system

---

## Key Insights

### Hermes Agent's Self-Evolution Loop
1. **Context Compression:** Keeps context window clean, enables long conversations
2. **Checkpoint System:** Transparent snapshots, safe experimentation
3. **Skill Creation:** Turns successful approaches into reusable procedural knowledge
4. **Skill Management:** Validation, security scanning, atomic writes
5. **Memory System:** Persistent recall across sessions

### Erbing's Evolution Path
1. **Four-Layer Memory Stack:** Working/Episodic/Semantic/Procedural
2. **Hermes-Style Components:** Context compressor, checkpoint manager, skill manager
3. **Database-First:** All memory in SQLite + LanceDB (no local files)
4. **Multi-Agent System:** Coordinator/Researcher/Developer/QA/MemoryArchitect
5. **Cron Scheduling:** Daily hygiene, weekly distillation, weekly report

---

## References

- Hermes Agent: https://github.com/NousResearch/hermes-agent
- Claude Code Production: https://github.com/anthropics/claude-code
- MasterClaw Core: https://github.com/openclaw/masterclaw
- OpenClaw 4-layer Template: https://github.com/openclaw/openclaw

---

**Generated:** 2026-04-19
**Status:** 4 components ported, 4 commits pushed
**Next:** Integrate all components into ErbingMemoryManager
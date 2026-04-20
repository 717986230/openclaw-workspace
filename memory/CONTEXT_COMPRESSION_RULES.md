# CONTEXT COMPRESSION RULES

## When Context is Compressed

### MANDATORY BEHAVIOR
1. DO NOT rely on session memory for historical information
2. ALWAYS query database for:
   - User preferences (USER.md, preferences/)
   - Past decisions (MEMORY.md, learnings/)
   - Event history (events/, database/)
   - Skill knowledge (skills/, memory/)

### Database Query Priority
1. LanceDB vector search for semantic/similarity queries
2. SQLite for structured/exact queries
3. File read for markdown/config files

### After Compression
- Re-read SOUL.md, IDENTITY.md, USER.md
- Use memory_search before answering history questions
- Use memory_get to fetch specific snippets
- NEVER assume you remember previous context

## Database Locations
- SQLite: C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db
- LanceDB: C:\Users\Administrator\.openclaw\workspace\memory\database\lancedb

---
*Generated: 2026-04-16 13:30:33*


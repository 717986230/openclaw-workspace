# FORCE DATABASE QUERY RULES

## Effective: 2026-04-15 09:51:24

## Core Rules
1. NO session memory dependency - context only for current conversation
2. FORCE database query - all history via SQLite or LanceDB
3. AUTO cleanup trigger - archive when threshold exceeded

## Database Locations
- SQLite: C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db
- LanceDB: C:\Users\Administrator\.openclaw\workspace\memory\database\lancedb

## Query Priority
1. LanceDB vector search - semantic similarity
2. SQLite structured query - exact match
3. Memory cache - current session hot data only

## Cleanup Strategy
- Keep recent: 50 session files
- Old files archived to archive/ dir
- Archived files still queryable via database


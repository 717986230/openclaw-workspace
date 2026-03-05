# Bug Records — Project-Specific Bug Documentation

> **Purpose**: Record all bugs fixed in the current project with root cause and fix details.
> **Update Rule**: MANDATORY update after every bug fix. If previous fix was incomplete, update the record.

---

## Record Template

```markdown
### [BUG-XXX] Brief Description
**Date**: YYYY-MM-DD
**Severity**: P0/P1/P2

**Root Cause**:
[1-2 sentences explaining WHY the bug occurred]

**Fix Method**:
[Concise description of HOW the bug was fixed]

**Files Modified**:
- `path/to/file1.ts`
- `path/to/file2.ts`

**Environment Impact**:
- [ ] Development
- [ ] Staging
- [ ] Production
```

---

## Bug Records

<!-- Add new records below this line, newest first -->

*(No records yet — add entries as bugs are fixed)*

---

## Quick Reference: Common Root Causes

| Category | Root Cause Pattern | Prevention |
|----------|-------------------|------------|
| **Environment** | Config only in one env file | Check ALL env files |
| **Import** | Wrong import path/syntax | Verify module resolution |
| **State** | Race condition/stale state | Add proper synchronization |
| **Type** | Type mismatch/null check | Enable strict typing |
| **API** | Contract mismatch | Verify request/response schema |
| **Dependency** | Version incompatibility | Lock versions, test upgrades |

---

## Statistics

| Month | Total | P0 | P1 | P2 | Most Common Category |
|-------|-------|----|----|----|--------------------|
| YYYY-MM | 0 | 0 | 0 | 0 | — |

---

## Update Checklist

After fixing a bug:
- [ ] New record added with root cause and fix method
- [ ] Previous incomplete records updated if applicable
- [ ] Environment impact correctly marked
- [ ] `bug-patterns.md` updated if this is a new pattern

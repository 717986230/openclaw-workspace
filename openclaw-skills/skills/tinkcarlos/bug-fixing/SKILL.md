---
name: bug-fixing-openclaw
description: |
  Zero-regression bug fix workflow: reproduce, root cause, scope, impact predict,
  fix, regression verify, code review, self-reflect, and knowledge deposit.

  Use when:
  - Feature broken, incorrect behavior, wrong output, errors/exceptions
  - Console errors/warnings even when feature appears functional
  - Regressions, timeouts, degraded performance
  - Keywords: "fix bug", "debug", "not working", "error", "broken"

  Output: Bug summary + verification report + code review + self-reflection score.
  Not for: new features (use fullstack-developer); pure review (use code-review);
  optimization (use performance-optimization).
allowed-tools: [read, write, execute, grep, glob]
metadata:
  language: en
  version: 3.0.0
  last_updated: 2026-03-04
  platform: openclaw
---

# Bug Fix — Zero-Regression Workflow

**Core Promise**: Fix completely. Fix everywhere. Break nothing. Learn from every fix.

---

## Iron Rules

| # | Rule | Phase |
|---|------|-------|
| R0 | After RCA, check the bug pattern library for known fixes | 2.5 |
| R1 | Before fix, search bug records for historical context | 2.6 |
| R2 | Root cause must pass 4 confirmation gates | 2 |
| R3 | Scope must pass 4 accuracy gates | 3 |
| R4 | Before coding, predict side effects (change blueprint) | 3.5 |
| R5 | Before coding, check AI blind spot registry | 3.5 |
| R6 | After fix, run regression verification | 5 |
| R7 | Before done, output bug summary in standard format | 5.2 |
| R8 | Before done, run code review | 5.2 |
| R9 | Before done, update bug records | 6 |
| R10 | Before done, update bug pattern library (if new pattern) | 6 |
| R11 | Before done, complete self-reflection | 6.5 |
| R12 | Framework behavior assumptions must be verified via source | 2 |
| R13 | Trace full impact chain (A->B->C) before fixing | 2.7 |
| R14 | Scan for similar issues across all files | 2.8 |
| R15 | Test all impacted functions after fix | 5.1 |
| R16 | Fix is not done until verification passes | 5 |

---

## Workflow Overview

```
Phase 0: Triage
  -> Phase 1: Reproduce (evidence required)
  -> Phase 2: Root Cause Analysis (4-gate confirmation)
    -> Phase 2.5: Check bug pattern library
    -> Phase 2.6: Search bug records
    -> Phase 2.7: Impact chain analysis
    -> Phase 2.8: Similar issue scan
  -> Phase 3: Scope Discovery (4-gate accuracy)
    -> Phase 3.5: Impact prediction + blind spot check
  -> Phase 4: Fix (minimal change)
  -> Phase 5: Regression verify + code review
  -> Phase 6: Knowledge deposit
    -> Phase 6.5: Self-reflection
```

| Phase | Action | Gate | Key Output |
|-------|--------|------|------------|
| 0 | Triage: classify fault vs noise | — | Classification |
| 1 | Reproduce with evidence | Must have evidence | Repro steps + evidence bundle |
| 2 | Root cause via hypothesis ladder + 5 Whys | Root Cause Gate (4 conditions) | Confirmed root cause |
| 2.5 | Search bug pattern library | Must output result | Matched/unmatched patterns |
| 2.6 | Search bug records | Must output result | Historical context |
| 2.7 | Impact chain analysis (A->B->C) | Must complete chain | Impact chain table |
| 2.8 | Similar issue scan | Must scan | Similar issues table |
| 3 | Scope: consumers, contracts, invariants | Scope Gate (4 conditions) | Consumer list + contracts |
| 3.5 | Impact prediction + blind spot check | Impact Gate | Blueprint + go/no-go |
| 4 | Minimal fix, max 50 LOC | LOC limit | Code change |
| 5.1 | Comprehensive regression verification | Zero new failures | Test report |
| 5.2 | Bug summary + code review | Review clean | Summary + review |
| 6 | Update records + pattern library | Must dual-update | Knowledge entries |
| 6.5 | Self-reflection + scoring | Must reflect | Quality score |

---

## Phase 1: Reproduce

Collect a standardized evidence bundle before proceeding.

```markdown
## Evidence Bundle

### Trigger Conditions
- Input/params: [...]
- Environment: [OS/browser/runtime version]
- Timing: [action sequence or time interval]

### Observable Output
- Error message: [full error text]
- Logs: [key log lines]
- Screenshot/recording: [if available]

### Correlation IDs
- requestId/traceId: [...]
- sessionId: [...]

### State Snapshot
- URL/route: [...]
- Config flags: [...]
- Version/build hash: [...]
```

---

## Phase 2: Root Cause Analysis

### Hypothesis Ladder

List 3-5 candidate hypotheses before diving deep. Sort by likelihood.

```markdown
| # | Hypothesis | Likelihood | Confirmation Test | Rejection Test | Status |
|---|-----------|-----------|-------------------|----------------|--------|
| 1 | [description] | High/Med/Low | [prove it IS this] | [prove it is NOT this] | [ ] |
| 2 | ... | ... | ... | ... | [ ] |
```

**Rules**:
1. Sort by likelihood (most likely first)
2. Each must be falsifiable
3. Run rejection tests first (cheaper to eliminate)
4. Move to next hypothesis once current is rejected

### Five Whys

Start with the symptom and ask "why" five times to reach the root cause.

### Root Cause Confirmation Gate

Root cause is only confirmed when ALL 4 conditions are met:

| Condition | Meaning |
|-----------|---------|
| **Reproducible** | Can reproduce symptom in controlled scenario |
| **Causal** | Minimal change makes bug disappear |
| **Reversible** | Reverting the change makes bug reappear |
| **Mechanistic** | Can point to exact code path / state transition |

If any condition fails, keep iterating the hypothesis ladder.

### Framework Assumption Audit (R12)

When fix involves third-party framework/library behavior:

1. List all framework behavior assumptions
2. Read source code in `venv/`/`node_modules/` to verify actual semantics
3. Document verified behavior in code comments with source file references

**Common pitfalls**:

| Area | Assumption | Reality |
|------|-----------|---------|
| Config load order | First file has priority | Often last file wins (dict.update) |
| ORM lazy loading | Relations auto-load | Default lazy, causes N+1 |
| Async/subprocess | Works on all platforms | Windows may need different event loop |
| Serialization | model_dump() includes all fields | exclude_unset=True changes behavior |

### Code Path Tracing

Trace data flow from entry point to error:

```
Entry: Component.tsx:23 (user.name)
  <- user comes from props
  <- props from Page.tsx:15
  <- useUser hook
  <- API response
  <- API returns null when user not found
Root Cause: No null handling for API response
```

### Root Cause Categories

| Category | Common Patterns |
|----------|----------------|
| **Logic** | Off-by-one, wrong operator, wrong condition |
| **Async/Timing** | Race condition, stale closure, unhandled rejection |
| **State** | Direct mutation, invalid transition, stale state |
| **Data** | Unexpected type, missing validation, structural assumption |
| **Integration** | API contract mismatch, version mismatch, env difference |

---

## Phase 2.7: Impact Chain Analysis (R13)

Trace the impact chain layer by layer. Do not stop at direct impact.

```markdown
## Impact Chain Analysis

### L0: Original Bug File
- File: [path]
- Issue: [description]

### L1: Direct Impact (files calling L0)
| File | Function | Impact | Needs Fix? |
|------|----------|--------|------------|

### L2: Indirect Impact (files calling L1)
| File | Function | Impact | Needs Fix? |
|------|----------|--------|------------|

### L3: Deep Impact (files calling L2)
| File | Function | Impact | Needs Fix? |
|------|----------|--------|------------|

### Fix Decision
- L1 changes: [yes/no] - reason: [...]
- L2 changes: [yes/no] - reason: [...]
- L3 changes: [yes/no] - reason: [...]
```

---

## Phase 2.8: Similar Issue Scan (R14)

Do not only fix the current file — check all files for the same problem.

| Issue Type | Scan Keywords | Scope |
|-----------|---------------|-------|
| Missing import | `import`, `require`, `from` | All files of same type |
| Null risk | `null`, `undefined`, `None` | Related modules |
| Resource leak | `open()`, `connect()`, `new` | Same resource type |
| Hardcoded secrets | `API_KEY`, `password`, `secret` | Entire project |
| Type errors | `any`, `as`, `cast` | Same module |

```markdown
## Similar Issue Scan

### Scan Type: [type]
### Keywords: [keywords]
### Scope: [scope]

| File | Line | Issue | Severity |
|------|------|-------|----------|

### Decision
- Fix together: [yes/no]
- Reason: [...]
- Affected files: [N]
```

---

## Phase 3: Scope Discovery

### Scope Accuracy Gate

Scope is only accurate when ALL 4 conditions are met:

| Condition | Meaning |
|-----------|---------|
| **Consumer List** | All consumers (callers/dependents) enumerated |
| **Contract List** | Modified contracts/interfaces/behaviors listed |
| **Invariant Check** | Must-hold invariants listed |
| **Call Site Enum** | All call sites enumerated and classified |

### Consumer List

```markdown
| Consumer | Layer | Entry Point | Contract Used | Risk | Verification |
|----------|-------|-------------|---------------|------|-------------|
| [who] | [frontend/backend/test] | [file:line] | [signature] | [H/M/L] | [how to verify] |
```

**Consumer types**: Direct callers, indirect dependents (via re-export), config consumers,
cache consumers, event subscribers, test consumers.

### Contract & Invariant List

```markdown
## Contract List
| Contract Type | Before | After | Breaking? |
|---------------|--------|-------|-----------|

## Invariant List
| ID | Invariant | Why It Matters | Verification |
|----|-----------|---------------|-------------|
```

### Call Site Enumeration

```bash
rg -n "symbol_name" . --glob "*.{ts,tsx,py,go,java}"
rg -n "export.*symbol_name" .
```

Classify each call site as: **Runtime critical** | **Test only** | **Dev only** | **Dead code**

---

## Phase 3.5: Impact Prediction (R4, R5)

Complete BEFORE writing ANY fix code.

### Step 1: Change Blueprint

```markdown
## Change Blueprint

| # | File | Lines | Current Code | Planned Change | Reason |
|---|------|-------|-------------|----------------|--------|

### Change Type
- [ ] Logic change
- [ ] Data flow change
- [ ] State change
- [ ] API/Interface change
- [ ] Configuration change
- [ ] Dependency change
```

### Step 2: Impact Ripple Analysis

```
L0: The changed code itself
 -> L1: Direct callers/consumers
 -> L2: Callers of L1 (indirect)
 -> L3: Cross-module/cross-service
 -> L4: User-facing behavior
```

```markdown
### L1: Direct Consumers
| Consumer | Usage Pattern | Predicted Impact | Risk |
|----------|--------------|------------------|------|

### L2: Indirect Consumers
| Consumer | Via L1 | Predicted Impact | Risk |
|----------|--------|------------------|------|
```

### Step 3: Side Effect Prediction

```markdown
| # | Predicted Side Effect | Probability | Severity | Mitigation |
|---|----------------------|-------------|----------|------------|

### Edge Cases to Verify
| # | Edge Case | Test Method | Expected Result |
|---|-----------|-------------|-----------------|
```

### Step 4: Blind Spot Check (R5)

Review the AI Blind Spot Registry. Common blind spots:

| Category | Blind Spot | Check |
|----------|-----------|-------|
| Scope | Forgetting indirect callers via re-exports | `rg "export.*symbol"` |
| Scope | Missing test file updates | Search `*.test.*` / `*.spec.*` |
| State | Not considering race conditions | "Can this be called concurrently?" |
| State | Ignoring initialization order | Check load order |
| API | Assuming response format matches types | Verify actual response shape |
| API | Not checking error paths | Test 4xx/5xx/null/undefined |
| Types | Trusting type assertions | Verify runtime values |
| Config | Forgetting environment differences | Check all env configs |
| Cache | Not invalidating after mutation | Check cache strategy |
| UI | Not testing different screen sizes | Check responsive behavior |

### Step 5: Go/No-Go Decision

```markdown
| Criteria | Status |
|----------|--------|
| All L1 consumers identified | [ ] |
| No high-risk side effects without mitigation | [ ] |
| Edge cases have test plan | [ ] |
| Change is minimal (ideally <=20 LOC, max 50) | [ ] |
| No API contract breaking changes | [ ] |

Decision: [ ] GO  |  [ ] STOP - adjust approach
```

**Red flags (immediate STOP)**: Changing function signature, touching shared utility,
changing data schema, modifying error handling, adding new dependency, >3 files.

**Quick version** (for simple bugs, <=5 LOC, 1 file):

```markdown
## Quick Impact Check
- Change: [one-line description]
- Direct callers: [list or "none - local function"]
- Could break: [prediction or "low risk - isolated"]
- Edge cases: [list 1-2 or "none"]
- Decision: GO
```

---

## Phase 4: Fix

Apply the minimal change that addresses the root cause:

1. Stay strictly within the Change Blueprint
2. If additional changes are discovered, STOP, update blueprint, re-assess
3. Limit to 50 LOC maximum
4. Single concern only — fix the bug, no refactoring

---

## Phase 5: Regression Verify + Code Review

### Phase 5.1: Comprehensive Regression Verification (R15, R16)

Test the entire impact chain, not just the original bug.

**Test matrix based on impact chain**:

| Impact Level | What to Test |
|-------------|-------------|
| L0 (original file) | Original bug fix verification |
| L1 (direct impact) | All L1 functions/interfaces |
| L2 (indirect impact) | All L2 functions/interfaces |
| L3 (deep impact) | Key L3 functions/interfaces |

**Test types to execute**:

| Test Type | When | Tool |
|-----------|------|------|
| Unit tests | Functions have unit tests | pytest, jest |
| Integration tests | Integration test cases exist | Test framework |
| API tests | API endpoints impacted | curl, httpx |
| E2E tests | UI changes involved | playwright |
| Manual tests | No automated coverage | Manual verification |

**Side effect verification** (against impact prediction):

```markdown
| Predicted Side Effect | Actual Result | Status |
|----------------------|---------------|--------|
| [from prediction] | [observation] | PASS/FAIL |

| Predicted Edge Case | Test Result | Status |
|--------------------|-------------|--------|
| [from prediction] | [result] | PASS/FAIL |
```

**Consumer regression check**:

```markdown
| Consumer | Verification Method | Result | Status |
|----------|-------------------|--------|--------|
| [from scope] | [method] | [result] | PASS/FAIL |
```

If ANY verification fails, return to Phase 4. Do NOT proceed.

### Phase 5.2: Bug Summary + Code Review (R7, R8)

Only after regression verification passes.

**Bug Summary** (standard format):

```markdown
## Bug Summary [BUG-XXX]
- **Symptom**: [one-sentence user-visible problem]
- **Root Cause**: [one-sentence actual cause]
- **Fix**: [one-sentence fix description]
- **Files Modified**: [file1.py, file2.ts]
- **Time**: YYYY-MM-DD HH:mm:ss
- **Severity**: P0/P1/P2
```

Then run code review. If review finds bugs:
- Correctness/security/behavior issues = bugs, must fix
- Style/minor issues = not bugs, can address later
- If regression found during review, execute Regression Autopsy
- After fixing, return to Phase 5.1 (regression verify) and loop

**Stop condition**: Code review clean + regression verification all passed + original bug fixed.

---

## Phase 5 — Special Checks

### API Bug Check

For CRUD API bugs, trace the full data flow:

1. Frontend -> API -> Schema -> Service -> Database
2. Check Update/Create Schema field completeness
3. Compare request params vs response output consistency

```markdown
| Field | Request Value | Response Value | Consistent? |
|-------|--------------|----------------|-------------|
```

If a field is in the request but not in the response, the Update Schema likely
misses that field definition.

### System-Level Bug Check

For cross-layer/cross-process bugs:

1. Draw end-to-end chain (all participants)
2. Define "handshake correct" evidence for each edge
3. Insert probes before modifying behavior
4. Narrow search: find last correct edge and first broken edge
5. Root cause is between those two edges

### Cross-Surface Regression Check

When fix involves shared artifacts (API schema, DB models, shared config, shared components):

1. **Identify shared contract** — what changed, what must stay stable
2. **Build consumer list** — UI, API, background, ops consumers
3. **Regression matrix** — normal flow + boundary for each high-risk consumer
4. **Cross-surface invariants** — field naming, defaults, caching, feature flags

---

## Phase 6: Knowledge Deposit (R9, R10)

### 6.1 Update Bug Records

Add entry to project-level bug records:

```markdown
### [BUG-XXX] Brief Description
**Date**: YYYY-MM-DD
**Severity**: P0/P1/P2

**Root Cause**: [1-2 sentences]
**Fix**: [how it was fixed]
**Files Modified**: [list]
```

### 6.2 Update Bug Pattern Library

When a new pattern, new fix strategy, or new root cause is discovered:

1. Identify the pattern category (Input Handling / State / API Integration / Data Flow / Config / Platform)
2. Generalize: remove project-specific names, use universal terms
3. Add row to the category table

```markdown
| Pattern | Typical Symptom | Detection | Fix Strategy |
|---------|-----------------|-----------|--------------|
| [name] | [symptom] | [detection] | [fix] |
```

**Generalization rules**:
- `UserService.login()` -> "Service method"
- `React useState` -> "Frontend state management"
- `/api/v1/users` -> "API endpoint"
- Specific error message -> Error type (TypeError, 500, etc.)

**Quality standards**: General (not project-specific), Actionable (executable steps),
Searchable (multiple keywords), Complete (symptom + detection + fix).

### 6.3 Pre-Fix Knowledge Query

Before every fix, search the pattern library:

| Match Level | Definition | Action |
|-------------|-----------|--------|
| High | Symptom, root cause, and tech stack all match | Apply known fix, can skip RCA |
| Medium | Similar symptom but different details | Reference strategy, verify |
| No match | Nothing related | Full investigation, must deposit after fix |

---

## Phase 6.5: Self-Reflection (R11)

Complete BEFORE declaring fix done.

### Fix Quality Score

```markdown
| Dimension | Score (1-5) | Evidence |
|-----------|------------|----------|
| First-time correctness | [1-5] | Did the fix work on first attempt? |
| Scope accuracy | [1-5] | Did I find all affected areas? |
| Minimal change | [1-5] | Was the change as small as possible? |
| Side effect prediction | [1-5] | Did I predict all side effects? |
| Root cause depth | [1-5] | Did I fix root cause, not symptom? |
| **Total** | [/25] | |
```

### What Went Wrong

```markdown
| Issue | What Happened | Why I Missed It | Prevention |
|-------|--------------|-----------------|------------|
```

### Debugging Efficiency

```markdown
| Metric | Value |
|--------|-------|
| Hypotheses generated | [N] |
| Hypotheses tested before root cause | [N] |
| False starts / wrong paths | [N] |
| Fix attempts before success | [N] |
| Regressions introduced | [N] |
```

### Pattern Recognition

- Similar to a previous bug? If yes, did I apply past lessons?
- Did I introduce new bugs during this fix? If yes, add to blind spot list.
- Was there a simpler fix I missed? If yes, why did I choose the complex approach?

### Regression Autopsy (when fix introduced a regression)

```markdown
## Regression Autopsy

- **Original Bug**: [what was being fixed]
- **New Bug Introduced**: [what broke]
- **Discovered By**: [code review / testing / user]
- **What changed**: [specific line/logic]
- **Why it broke**: [mechanism]
- **Why I didn't predict it**: [blind spot]
- **Classification**: [missed consumer / contract violation / edge case / race condition / ...]

### Prevention
1. Immediate: [checklist addition]
2. Structural: [process change]
3. Tooling: [automated check]
```

---

## AI Blind Spot Registry

Maintain a running list. Check before every fix, update after every fix.

```markdown
## Active Blind Spots

| ID | Blind Spot | First Seen | Times Hit | Mitigation Check |
|----|-----------|------------|-----------|------------------|
| BS-001 | Forgetting to update test files | Seed | 0 | Search *.test.* / *.spec.* |
| BS-002 | Not checking indirect callers via re-exports | Seed | 0 | rg "export.*symbol" |
| BS-003 | Assuming API response matches TypeScript types | Seed | 0 | Verify actual response |
| BS-004 | Missing cache invalidation after mutation | Seed | 0 | Search cache usage |
| BS-005 | Not testing error/failure paths | Seed | 0 | Test 4xx/5xx/null |
| BS-006 | Ignoring race conditions in async code | Seed | 0 | "Can this run concurrently?" |
| BS-007 | Fix scope creep | Seed | 0 | Enforce <=50 LOC |

## Retired (avoided 5+ consecutive fixes)

| ID | Blind Spot | Retired Date | Reason |
|----|-----------|-------------|--------|
```

**Evolution triggers**: If a blind spot repeats 2+ times, consider adding to Iron Rules.

---

## Skill Delegation

| Trigger | Delegate To |
|---------|-----------|
| Need new API endpoint | fullstack-developer |
| UI fix needed | frontend-design |
| Schema change needed | database-migrations |
| After fix (mandatory) | code-review |

---

## Anti-Patterns

| Forbidden | Correct |
|-----------|---------|
| Fix without RCA | Hypothesis ladder first |
| Single hypothesis then fix | List 3-5 hypotheses, verify each |
| Root cause without 4 gates | Meet all: reproducible/causal/reversible/mechanistic |
| Skip bug pattern library | Always check pattern library first |
| Skip consumer list for shared code | Fill consumer list first |
| Code without impact prediction | Blueprint + ripple analysis first |
| Skip blind spot check | Check blind spot registry every time |
| No regression verify before review | Verify ALL predicted side effects |
| Skip code review | Code review is mandatory |
| Skip bug records update | Must update every time |
| Skip self-reflection | Must score, analyze, and learn |
| Trust framework docs blindly | Read source code to verify (R12) |

---

## Final Checklist

Before declaring fix complete, ALL items must be checked:

### Core

| # | Check | Status |
|---|-------|--------|
| 1 | Root cause passes 4 gates | [ ] |
| 2 | Checked bug pattern library | [ ] |
| 3 | Searched bug records | [ ] |
| 4 | Scope passes 4 gates | [ ] |
| 5 | Impact prediction complete (blueprint + blind spots) | [ ] |
| 6 | Impact chain analysis complete (A->B->C) | [ ] |
| 7 | Similar issue scan complete | [ ] |
| 8 | All similar issues fixed | [ ] |
| 9 | Regression verification all passed (L0-L3) | [ ] |
| 10 | Bug summary output (standard format) | [ ] |
| 11 | Code review — no P0/P1/P2 | [ ] |
| 12 | Bug records updated | [ ] |
| 13 | Bug pattern library updated (if new pattern) | [ ] |
| 14 | Self-reflection complete (score + analysis) | [ ] |
| 15 | User confirmed bug is fixed + no new bugs | [ ] |

### Verification Gate (R16)

Fix is NOT done until:
- [ ] Original bug is fixed
- [ ] All tests in impact scope pass
- [ ] No new bugs introduced
- [ ] User confirmation received

### API Bug Extra Checks (if applicable)

- [ ] Checked full data flow (Frontend->API->Schema->Service->DB)
- [ ] Checked Update/Create Schema field completeness
- [ ] Compared request params vs response output consistency

### System Bug Extra Checks (if applicable)

- [ ] Drew end-to-end chain
- [ ] Defined handshake evidence for each edge
- [ ] Inserted probes before modifying behavior

---

## Verification Commands (Quick Reference)

### Frontend (React/Vue/TypeScript)

```bash
npm run lint
npm run typecheck
npm run build
npm test -- --coverage
```

### Backend (Python)

```bash
ruff check .
mypy .
pytest --cov=src
```

### Backend (Node.js)

```bash
npm run lint
npm run build
npm test
```

---

## Verification Report Template

```markdown
## Bug Fix Verification Report

**Bug ID**: BUG-XXXX
**Date**: YYYY-MM-DD

### Summary
- Root Cause: [one sentence]
- Fix Approach: [one sentence]
- Files Changed: [count] files, [LOC] lines

### Matrix Results

| Section | Checks | Passed | Notes |
|---------|--------|--------|-------|
| A: Pre-Fix Baseline | 5 | /5 | |
| B: Fix Quality | 4 | /4 | |
| C: Correctness | 6 | /6 | |
| D: Regression | 4 | /4 | |
| E: Code Quality | 4 | /4 | |
| F: Completeness | 3 | /3 | |
| **Total** | **26** | **/26** | |
```

---

## Periodic Self-Assessment (Every 5 Fixes)

```markdown
| Fix # | Bug | Quality (/25) | Regressions? | First-time? |
|-------|-----|--------------|:------------:|:-----------:|
| 1 | [bug] | [score] | Y/N | Y/N |
| ... | ... | ... | ... | ... |

### Trend
- Quality improving? [Yes/No/Stable]
- Most common weakness: [dimension]
- Most improved area: [dimension]

### Top 3 Lessons
1. [lesson]
2. [lesson]
3. [lesson]
```

---

## Reference Files

### Living Data Files (grow over time)

| File | Purpose |
|------|---------|
| `references/bug-records.md` | Project-specific bug history (update after every fix) |
| `references/blind-spots.md` | AI blind spot registry (check before, update after every fix) |

### Pattern Libraries (domain knowledge)

| File | Purpose |
|------|---------|
| `references/bug-patterns.md` | Universal bug pattern library (11 categories, 18 root causes) |
| `references/backend-patterns.md` | Backend issues (API, ORM, timeout, LLM integration) |
| `references/frontend-patterns.md` | Frontend issues (React hooks, race conditions, CORS) |

### Detailed Guides

| File | Purpose |
|------|---------|
| `references/system-rca.md` | System-level RCA (cross-layer, multi-process bugs) |
| `references/regression-matrix.md` | Complete 34-item zero-regression verification matrix |

---

## Skill Evolution

Update this skill when:
- Code review finds a bug that the workflow should have prevented
- A recurring bug class repeats across fixes

Prefer updating specific sections over adding new rules.
After updates, validate that the workflow is still coherent and not overly bureaucratic.

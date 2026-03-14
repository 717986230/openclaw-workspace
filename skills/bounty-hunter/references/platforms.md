
# Platform-Specific Engagement Rules

## GitHub

### Bounty Labels to Monitor
- `label:"help wanted" label:bounty`
- `label:"good first issue"`
- `label:"bug"` + description mentions "reward" or "bounty"

### Engagement Protocol
1. **Claim**: Comment "I'm looking into this and plan to submit a PR shortly."
2. **Update**: If stuck, comment "Making progress, will update in ~2h."
3. **Deliver**: PR with Problem Summary, Solution Approach, Test Evidence.

---

## Upwork

### Filters
- Fixed-price: $50-$500 range
- Skill tags: Python, TypeScript, React, Node.js, Go, Rust
- Client history: &gt;$10k spent, &gt;90% hire rate

### Proposal Template
&gt; "Hi [Client Name], I'm Atlas, a senior developer with 8+ years of experience. I can deliver this in [X] hours with full testing and documentation. Let's discuss."

---

## Bug Bounty (HackerOne/Bugcrowd)

### Rules
- **ONLY** authorized scopes
- **NO** destructive testing
- **ALWAYS** private disclosure first

### Targets
- Web: XSS, CSRF, Auth bypass
- API: IDOR, Rate limit issues, Injection
- Mobile: Deep link issues, Keystore insecurity

---

*Last updated: 2026-03-06*


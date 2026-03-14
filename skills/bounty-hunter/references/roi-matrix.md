
# ROI Matrix - Detailed Scoring for Task Selection

## Quick Decision Formula

```
IF (Payout - (TokenCost * 1.5) &gt; 0) AND (ProfitMargin &gt; 50%)
  → PROCEED
ELSE
  → SKIP
```

---

## Complexity vs Token Cost Estimates

| Complexity | Time Estimate | Token Budget | Max Acceptable |
|------------|---------------|--------------|----------------|
| Low        | 1-2 hours     | $5           | $10            |
| Medium     | 4-8 hours     | $20          | $40            |
| High       | 16+ hours     | $50          | Only if payout &gt; $500 |

---

## Payout Multipliers by Platform

| Platform   | Trust Level | Multiplier | Notes |
|------------|-------------|------------|-------|
| GitHub     | High        | 1.0x       | Transparent, public |
| Upwork     | Medium      | 0.9x       | Need escrow |
| Bugcrowd   | Medium      | 0.85x      | VDP, may be slow |
| HackerOne  | Medium      | 0.85x      | VDP, may be slow |
| Random     | Low         | 0.5x       | Reject unless pre-paid |

---

## Profit Margin Tiers

| Margin | Priority | Action |
|--------|----------|--------|
| &gt;80%  | P0       | DROP EVERYTHING |
| 60-80% | P1       | High priority |
| 50-60% | P2       | Normal priority |
| &lt;50%  | SKIP     | Not worth it |

---

## Stop-Loss Triggers

- **3x Time Overrun**: STOP immediately
- **2x Token Overrun**: STOP immediately
- **Scope Creep**: Request re-negotiation or STOP
- **Unresponsive Client**: Wait 24h, then STOP

---

*Last updated: 2026-03-06*


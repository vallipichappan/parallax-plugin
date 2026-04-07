---
description: Prioritized trade recommendations with health flags, score trends, replacements, and before/after comparison
argument-hint: "[ticker weight, ...] [optional: target=..., constraints=...]"
---

# Rebalance

Optional inputs: `target` (e.g., "reduce concentration, improve quality") and `constraints` (e.g., "max 25% per position, no energy").

**Mode detection:** If the user provides tickers without weights → watchlist mode (surveillance scan). With weights → rebalance mode.

---

## Watchlist Mode (no weights)

1. `get_score_analysis` for each symbol with weeks=4-8 (all in parallel) — compute score change.
2. Flag movers: >1 point total score change or any factor >2 points.
3. For flagged symbols only (in parallel): `get_news_synthesis` (async — don't block), `get_technical_analysis` (async — poll `check_job_status` every 15s until completed, do NOT retry original call), `get_stock_outlook` (aspect="recommendations").

**Output:** Alert table ranked by magnitude of change → Per-alert detail (which factors moved, catalyst) → Stable names (one-liner each) → Which names warrant `/parallax:deep-dive`.

---

## Rebalance Mode (with weights)

### Batch A — Current state (parallel)

| Tool | Parameters | Notes |
|---|---|---|
| `analyze_portfolio` | `holdings`, lens="performance" | Returns/risk. May exceed 180K chars — fall back to Batch A alternatives if truncated |
| `analyze_portfolio` | `holdings`, lens="concentration" | Concentration analysis |
| `quick_portfolio_scores` | `holdings` | Factor scores (apply mixed-exchange fallback if needed) |
| `check_portfolio_redundancy` | `holdings` | Overlap detection |
| `list_macro_countries` | — | Market coverage |

### Batch B — Macro + score trends (after A)

1. `macro_analyst` with component="tactical" per unique covered market (cap 3).
2. `get_score_analysis` per holding (parallel). For 10+ holdings: prioritize top/bottom 5 by weight.

### Batch C — Health flags + trade decisions

1. Evaluate 5 health flags per holding per health-flags skill.
2. Assign priority: **High** (3+ flags) → Trim/Exit. **Medium** (2 flags) → Investigate/Trim. **Low** (1 flag) → Monitor/Hold.
3. Determine actions combining flags + score trends + macro:
   - **Trim/Exit:** High priority, or declining scores + any flag
   - **Hold:** Stable/improving scores, no flags
   - **Reweight:** Concentration flag only, scores healthy
   - **Investigate:** Medium priority, ambiguous signal → suggest `/parallax:deep-dive`
4. For trim candidates: `build_stock_universe` with portfolio factor profile theme → `get_peer_snapshot` for replacement candidates.

### Batch D — Validation

`quick_portfolio_scores` on proposed new allocation to verify improvement vs current.

### Output

- **Current Assessment** — factor scores, concentration, redundancy
- **Health Status** — Healthy/Monitor/Attention badge
- **Health Flags** — table: each triggered flag per holding with priority
- **Macro Context** — relevant market outlook, sector implications
- **Score Momentum** — table: each holding's trend (improving/stable/declining)
- **Trade Recommendations** — table: Priority | Action | Symbol | Current Weight | Target Weight | Rationale (every recommendation cites a specific flag or finding)
- **Replacement Candidates** — if trimming, scored alternatives
- **Before/After Comparison** — factor scores: current vs proposed
- **Implementation Notes** — execution order, liquidity

*"These are analytical outputs based on Parallax factor scores, not investment advice."*

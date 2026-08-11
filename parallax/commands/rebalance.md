---
description: Prioritized rebalancing classifications with health flags, score trends, replacements, and before/after comparison
argument-hint: "[ticker weight, ...] [optional: target=..., constraints=...]"
---

# Rebalance

Optional inputs: `target` (e.g., "reduce concentration, improve quality") and `constraints` (e.g., "max 25% per position, no energy").

**Mandate parsing (fail loud):** match `constraints=` against exactly two patterns — "max N% per position" and "no <sector>" — and `target=` against "reduce concentration" / "improve <factor>". Any unmatched clause renders as "constraint not recognized — not applied" in a **Mandate Constraints Applied** output block. Never silently drop a constraint.

**Mode detection:** If the user provides tickers without weights → watchlist mode (surveillance scan). With weights → rebalance mode. (The same weightless input runs an equal-weight checkup in `/parallax:portfolio` — different product.)

**Asset-class routing:** classify holdings per the asset-class-routing skill before scoring — factor tools are equity-only; ETFs get a separate block, never silent drops.

---

## Watchlist Mode (no weights)

1. `get_score_analysis` for each symbol (all in parallel, server-default window) — compute score change over the recent weeks.
2. Flag movers: >1 point total score change or any factor >2 points. Add a verdict-sensitivity line naming the 1-2 symbols nearest those cutoffs.
3. For flagged symbols only, fire as ONE parallel batch (never serially): `get_news_synthesis` (async — don't block), `get_technical_analysis` (async — poll `check_job_status` per the async-jobs skill, do NOT retry), `get_stock_outlook` (aspect="recommendations").

**Output:** Alert table ranked by magnitude of change → Per-alert detail (which factors moved, catalyst) → Stable names (one-liner each) → Which names warrant `/parallax:deep-dive`.

---

## Rebalance Mode (with weights)

### Batch A — Current state (parallel)

| Tool | Parameters | Notes |
|---|---|---|
| `analyze_portfolio` | `portfolio=[{date, symbol, weight}]`, `fields=["portfolio_summary","performance_metrics","rolling_metrics","drawdown_analysis"]` | Returns/risk. No `holdings`/`lens` params exist. `fields` is a passthrough — invalid names fail silently, so use only names from the `response-shapes` skill. May exceed 180K chars — fall back to Batch A alternatives if truncated |
| `analyze_portfolio` | `portfolio=[{date, symbol, weight}]`, `fields=["concentration_metrics","sector_allocation","company_contribution"]` | Concentration analysis |
| `quick_portfolio_scores` | equity holdings | Factor scores (fallback ladder per health-flags skill; cross-validate per conventions — mismatches excluded, ⚠ MISMATCH table) |
| `check_portfolio_redundancy` | holdings list | Overlap detection |
| `list_macro_countries` | — | Market coverage |

After Batch A completes, render one summary line: "N/M holdings scored; sections degraded: [list or none]."

### Batch B — Macro + score trends (after A)

1. `macro_analyst` with component="tactical" per unique covered market (cap 3).
2. `get_score_analysis` per holding (parallel). For 10+ holdings: prioritize top/bottom 5 by weight.

### Batch C — Health flags + classifications

1. Evaluate the 5 health flags per holding at **holding level** per the health-flags skill.
2. Assign priority: **High** (3+ flags) → Trim/Exit. **Medium** (2 flags) → Investigate/Trim. **Low** (1 flag) → Monitor/Hold.
3. Determine classifications combining flags + score trends + macro (§12 framing per the conventions skill — these are threshold classifications, not instructions):
   - **Trim/Exit:** High priority, or declining scores + any flag
   - **Hold:** Stable/improving scores, no flags
   - **Reweight:** Concentration flag only, scores healthy
   - **Investigate:** Medium priority, ambiguous signal → suggest `/parallax:deep-dive`
4. For trim candidates: `build_stock_universe` with portfolio factor profile theme → `get_peer_snapshot` for replacement candidates. Drop any candidate whose returned name fails the cross-validation check against `get_company_info` — never propose a replacement from a mismatched mapping.

### Batch D — Validation

`quick_portfolio_scores` on proposed new allocation to verify improvement vs current.

### Output

- **Mandate Constraints Applied** — if target/constraints given
- **Current Assessment** — factor scores, concentration, redundancy
- **Health Status** — Healthy/Monitor/Attention badge + verdict-sensitivity line
- **Health Flags** — table: each triggered flag per holding with priority
- **⚠ MISMATCH table** — if any holdings excluded
- **Macro Context** — relevant market outlook, sector implications
- **Score Momentum** — table: each holding's trend (improving/stable/declining)
- **Rebalancing Classifications** — informational preface, then table: Priority | Classification | Symbol | Current Weight | Threshold Result | Rationale (descriptive verbs; every row cites a specific flag or finding)
- **Replacement Candidates** — if trimming, scored alternatives
- **Before/After Comparison** — factor scores: current vs proposed
- **Implementation Notes** — sequencing considerations, liquidity caveats (not validated against ADV/borrow)

Render the AI-interaction disclosure per the conventions skill §9.2 immediately above the disclaimer, then the standard disclaimer verbatim from the conventions skill §9.1.

## Render discipline

Apply the Render Discipline section of the conventions skill: suppress step scaffolding, hoist every integrity surface (⚠ MISMATCH rows, degraded-coverage notes, "Data unavailable" / "Analysis pending" markers) into the final output, and close with the §9.2 disclosure immediately above the §9.1 disclaimer.

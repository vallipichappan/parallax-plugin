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
3. For flagged symbols only, fire as ONE parallel batch (never serially): `get_news_synthesis` (async — server waits for the result; never re-call), `get_technical_analysis` (async — on a "still running" reply follow the async-jobs skill; never re-call), `get_stock_outlook` (aspect="recommendations").

**Output:** Alert table ranked by magnitude of change → Per-alert detail (which factors moved, catalyst) → Stable names (one-liner each) → Which names warrant `/parallax:deep-dive`.

---

## Rebalance Mode (with weights)

### Batch A — Current state (parallel)

| Tool | Parameters | Notes |
|---|---|---|
| `get_company_info` | each equity holding | Ground-truth name for scoring cross-validation |
| `analyze_portfolio` | `portfolio=[{date, symbol, weight}]`, `fields=["portfolio_summary","performance_metrics","rolling_metrics","drawdown_analysis"]` | Async — server waits for the result; never re-call. Returns/risk. No `holdings`/`lens` params exist. `fields` is a validated enum — an invalid name fails the call with a schema error, not a silently-dropped entry in `invalid_fields`. Use only names from the `response-shapes` skill. May exceed 180K chars — fall back to Batch A alternatives if truncated |
| `analyze_portfolio` | `portfolio=[{date, symbol, weight}]`, `fields=["concentration_metrics","sector_allocation","company_contribution"]` | Async — server waits for the result; never re-call. Concentration analysis |
| `quick_portfolio_scores` | equity holdings | Factor scores (fallback ladder per health-flags skill; cross-validate per conventions — mismatches excluded, ⚠ MISMATCH table) |
| `check_portfolio_redundancy` | holdings list | Overlap detection |
| `list_macro_countries` | — | Market coverage |

After Batch A completes, render one summary line: "N/M holdings scored; sections degraded: [list or none]."

### Batch B — Macro + score trends (after A)

1. `macro_analyst` with component="tactical" per unique covered market (cap 3).
2. `get_score_analysis` per holding (parallel). For 10+ holdings: prioritize top/bottom 5 by weight.

### Batch C — Health flags + classifications

1. Evaluate the 5 health flags per holding at **holding level** per the health-flags skill.
2. Assign priority per the health-flags skill: **High** (3+ flags), **Medium** (2 flags), **Low** (1 flag).
3. Determine classifications combining flags + score trends + macro (§12 framing per the conventions skill — these are threshold classifications, not instructions):
   Apply the health-flags skill's Classification Types table exactly, including its precedence order and its rule for holdings with no usable `get_score_analysis` result. Every holding gets exactly one classification. First match wins:
   - **Exit:** 3+ flags + deteriorating score trend
   - **Trim:** concentration + other flags, or 3+ flags without a measured deteriorating trend
   - **Reweight:** concentration flag only
   - **Investigate:** 1-2 flags, none of them concentration → suggest `/parallax:deep-dive`
   - **Hold:** no flags (priority None)
4. For Trim and Exit candidates: `build_stock_universe` with portfolio factor profile theme → `get_company_info` and `get_peer_snapshot` in parallel for each replacement candidate. Drop any candidate whose returned name fails the cross-validation check against `get_company_info` — never propose a replacement from a mismatched mapping.

**Atomic sizing gate:** if any holding needed for sizing lacks a verified identity, score, weight, or required allocation input, do not render proposed weights or the before/after comparison. Name each failed component and offer the operator a choice to correct or remove it. A partial research summary may still render.

### Batch D — Validation

`quick_portfolio_scores` on proposed new allocation to verify improvement vs current.


**Universe reproducibility:** any candidate list here comes from `build_stock_universe`, which is not reproducible run-to-run — set membership varies, not just ordering. Tell the user the candidate set is a point-in-time sample, per the conventions skill's Universe Search Reproducibility section. Decide emptiness from the `companies` array alone, and when the response carries `degraded: true`, name the `relaxed` screens in a degraded-coverage note, per the same skill.

### Output

- **Mandate Constraints Applied** — if target/constraints given
- **Current Assessment** — factor scores, concentration, redundancy
- **Health Status** — Healthy/Monitor/Attention badge + verdict-sensitivity line
- **Health Flags** — table: each triggered flag per holding with priority
- **⚠ MISMATCH table** — if any holdings excluded
- **Macro Context** — relevant market outlook, sector implications
- **Score Momentum** — table: each holding's trend (improving/stable/declining)
- **Rebalancing Classifications** — informational preface, then table: Priority | Classification | Symbol | Current Weight | Threshold Result | Rationale (descriptive verbs; every row cites a specific flag or finding)
- **Replacement Candidates** — for Trim and Exit classifications, scored alternatives
- **Before/After Comparison** — factor scores: current vs proposed
- **Implementation Notes** — sequencing considerations, liquidity caveats (not validated against ADV/borrow)

Render the AI-interaction disclosure per the conventions skill §9.2 immediately above the disclaimer, then the standard disclaimer verbatim from the conventions skill §9.1.

## Render discipline

Apply the Render Discipline section of the conventions skill: suppress step scaffolding, hoist every integrity surface (⚠ MISMATCH rows, degraded-coverage notes, "Data unavailable" / "Analysis pending" markers) into the final output, and close with the §9.2 disclosure immediately above the §9.1 disclaimer.

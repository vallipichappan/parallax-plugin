---
description: Portfolio analysis with health flags, drill-down, macro context, and advisor mode
argument-hint: "[ticker weight, ticker weight, ... e.g. AAPL 30%, MSFT 20%, SPY 50%]"
---

# Portfolio Analysis

Parse holdings into `{symbol, weight}` pairs. Equal-weight if no weights given. Stocks need RIC format (AAPL.O); ETFs plain (SPY).

**Mode detection:** If user provides client context, benchmark, or advisor framing → advisor mode (presentation-ready, drill-down on flagged holdings). Otherwise → checkup mode (educational, plain language).

For mixed stocks + ETFs → use `analyze_mixed_portfolio` instead of `analyze_portfolio` (same cost, expands ETFs to underlying for true factor exposure). Same 180K truncation fallback applies.

## Checkup Mode

### Batch A — Scoring + macro (parallel)

| Tool | Parameters | Notes |
|---|---|---|
| `quick_portfolio_scores` | `holdings` | Factor scores per holding + portfolio |
| `check_portfolio_redundancy` | `holdings` | Overlap detection |
| `list_macro_countries` | — | Check market coverage |

### Batch B — Macro context (after A)

Derive home markets from RIC suffixes. Call `macro_analyst` with component="tactical" for each unique covered market (cap 3).

### Batch C — Health flag evaluation

Per health-flags skill, evaluate all 5 flags: Low Score, Concentration, Redundancy, Value Trap, Macro Misalignment.

If `quick_portfolio_scores` coverage <50%: execute mixed-exchange fallback (split by suffix, re-score, merge).

Assign status: **Healthy** (0 flags) / **Monitor** (1-2) / **Attention** (3+).

**Output:** Health badge → Scorecard (plain-language labels) → Flags → Overlap → Macro → What This Means → Consider (suggestions as questions, not directives).

## Advisor Mode

Checkup Batches A, B, C still execute. Advisor mode adds the following:

### Batch A — adds to checkup Batch A (parallel)

| Tool | Parameters | Notes |
|---|---|---|
| `analyze_portfolio` | `holdings`, lens="performance" | Returns/risk. May exceed 180K chars — fall back to checkup path if truncated |
| `analyze_portfolio` | `holdings`, lens="concentration" | Sector/factor concentration |

### Batch C — Per-holding drill-down

Select up to 8 holdings per health-flags drill-down rules (flag count desc, weight desc). For each:

| Tool | Parameters | Notes |
|---|---|---|
| `get_score_analysis` | `symbol`, weeks=26 | Score trend |
| `get_stock_outlook` | `symbol`, aspect="risk_return" | Risk vs peers |
| `get_peer_snapshot` | `symbol` | Current scores |

News: `get_news_synthesis` for holdings >10% weight AND flagged, cap 5.

### Batch D — AI Assessment (after all data)

`get_assessment` with prompt incorporating: portfolio findings, flags, macro, drill-down data, client context.

**Output:** Performance vs Benchmark → Health badge → Scorecard → Flags → Per-Holding Analysis → Macro Context → Suitability Assessment → Prioritized Actions (per recommendation matrix from health-flags skill).

*"This is informational analysis based on Parallax factor scores, not investment advice."*

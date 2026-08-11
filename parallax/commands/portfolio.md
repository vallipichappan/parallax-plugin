---
description: Portfolio analysis with health flags, drill-down, macro context, and advisor mode
argument-hint: "[ticker weight, ticker weight, ... e.g. AAPL 30%, MSFT 20%, SPY 50%]"
---

# Portfolio Analysis

Parse holdings into `{symbol, weight}` pairs. Equal-weight if no weights given (state that assumption in the output). Stocks need RIC format (AAPL.O) — resolve via `search_stocks` per the conventions skill; ETFs plain (SPY). Note: the same tickers-without-weights input runs watchlist surveillance in `/parallax:rebalance` — here it runs a weighted checkup.

**Asset-class routing:** classify each holding per the asset-class-routing skill BEFORE any scoring or price pull (`etf_profile` is the oracle). Factor scoring and `export_price_series` are equity-only; `etf_daily_price` is ETF-only. Both fail empty, not loudly. Score equities; report ETFs in a separate "ETF holdings" block (profile + holdings via `etf_profile`/`etf_holdings`) rather than silently dropping them.

**Mode detection:** If user provides client context, benchmark, or advisor framing → advisor mode (presentation-ready, drill-down on flagged holdings). Otherwise → checkup mode (educational, plain language).

## Checkup Mode

### Batch A — Scoring + macro (parallel)

| Tool | Parameters | Notes |
|---|---|---|
| `quick_portfolio_scores` | equity holdings | Factor scores per holding + portfolio. Cross-check per-row `company_name` per the conventions skill — mismatches are excluded from aggregates and listed in a ⚠ MISMATCH table |
| `check_portfolio_redundancy` | holdings list | Overlap detection |
| `list_macro_countries` | — | Check market coverage |

### Batch B — Macro context (after A)

Derive home markets from RIC suffixes. Call `macro_analyst` with component="tactical" for each unique covered market (cap 3).

### Batch C — Health flag evaluation

Per health-flags skill, evaluate all 5 flags: Low Score, Concentration, Redundancy, Value Trap, Macro Misalignment.

If `quick_portfolio_scores` coverage <50%: execute the scoring fallback ladder per the health-flags skill.

Assign status: **Healthy** (0 flags) / **Monitor** (1-2) / **Attention** (3+), with the verdict-sensitivity line per the health-flags skill.

**Output:** Health badge → Scorecard (plain-language labels) → Flags → Overlap → Macro → What This Means → Consider (suggestions as questions, not directives).

## Advisor Mode

Checkup Batches A, B, C still execute. Advisor mode adds the following:

### Batch A — adds to checkup Batch A (parallel)

| Tool | Parameters | Notes |
|---|---|---|
| `analyze_portfolio` | `portfolio=[{date, symbol, weight}]`, `fields=["portfolio_summary","performance_metrics","rolling_metrics","drawdown_analysis"]` | Returns/risk. May exceed 180K chars — fall back to checkup path if truncated |
| `analyze_portfolio` | `portfolio=[{date, symbol, weight}]`, `fields=["concentration_metrics","sector_allocation","company_contribution"]` | Sector/factor concentration. There is no `holdings` or `lens` parameter — the tool takes a dated `portfolio` array plus a `fields` subset |

`fields` is a **direct passthrough** to the API, not a validated enum — an invalid name fails silently rather than erroring. Use only names from the `response-shapes` skill.

If the user names a benchmark: ETFs route through `etf_daily_price` (plain ticker), equities through `export_price_series` (RIC) — mixing them silently fails empty.

### Batch C — Per-holding drill-down

Select up to 8 holdings per health-flags drill-down rules (flag count desc, weight desc). For each:

| Tool | Parameters | Notes |
|---|---|---|
| `get_score_analysis` | `symbol` | Score trend (server-default window) |
| `get_stock_outlook` | `symbol`, aspect="risk_return" | Risk vs peers |
| `get_peer_snapshot` | `symbol` | Current scores |

News: `get_news_synthesis` for holdings >10% weight AND flagged, cap 5. Async — never blocks.

### Batch D — AI Assessment (after all data)

`get_assessment` with prompt incorporating: portfolio findings, flags, macro, drill-down data, client context. Fire it the moment classifications are assigned — do not wait on pending news. Exclude ⚠ MISMATCH holdings from the assessment prompt (empty profiles produce hallucinated factor narratives). Poll per the async-jobs skill; on wait-cap expiry render "Analysis pending" and continue.

**Output:** Performance vs Benchmark → Health badge → Scorecard → Flags → ⚠ MISMATCH table (if any) → Per-Holding Analysis → Macro Context → Suitability Assessment → Prioritized Classifications (per health-flags skill, with §12 informational preface).

Render the AI-interaction disclosure per the conventions skill §9.2 immediately above the disclaimer, then the standard disclaimer verbatim from the conventions skill §9.1.

## Render discipline

Apply the Render Discipline section of the conventions skill: suppress step scaffolding, hoist every integrity surface (⚠ MISMATCH rows, degraded-coverage notes, "Data unavailable" / "Analysis pending" markers) into the final output, and close with the §9.2 disclosure immediately above the §9.1 disclaimer.

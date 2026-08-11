---
name: asset-class-routing
description: Which Parallax tool covers equities vs ETFs, how to classify a symbol before calling one, and what to do when a call fails — consult before adding any price or scoring call.
---

# Asset-Class Routing

Mismatched tool/asset-class pairs (e.g. `export_price_series("SPY")`) fail-empty rather than erroring loudly. Left unchecked they cause silent data drops in downstream computation. Classify before you call.

## Asset Class × Tool

| Tool | Equity (AAPL.O, JPM.N) | ETF (SPY, EWJ, QQQ) | Notes |
|---|---|---|---|
| `export_price_series` | ✓ supported | ✗ returns `{success:false, error}` (NOT `[]`) | Equity-only, FREE. Pass RIC with exchange suffix. A `success:false` response is itself a usable equity/ETF discriminator. |
| `etf_daily_price` | ✗ returns `[]` | ✓ supported | ETF-only. Pass plain ticker (no suffix). Returns per-row `date` + `changepercent` — move AND date in one call. 1 token. |
| `etf_profile` | ✗ returns `{"error":"No profile data found"}` | ✓ rich profile (name, exchange, scores, recommendation, `change_percent`) | **The asset-class oracle.** Its `change_percent` carries NO as-of/date field — use `etf_daily_price` when a dated ETF move is needed. Single-symbol probe. 1 token. |
| `etf_search` | n/a | ✓ supported | Discovery by market / keyword / score. |
| `etf_holdings` | n/a | ✓ supported | Underlying holdings of an ETF. |
| `get_company_info` | ✓ supported | ✓ partial (returns an equity-shaped record for some ETFs) | **Has NO `asset_class` field** — cannot distinguish equity from ETF. Use `etf_profile` for that. |
| `get_peer_snapshot` | ✓ supported | partial — peer set may include both | Sector ETFs occasionally appear as peers; classify each peer before any downstream price call. |
| `export_peer_comparison` | ✓ (peer set may include ETFs) | partial | Same caveat as `get_peer_snapshot`. |
| `get_score_analysis` | ✓ supported | UNVERIFIED | Likely equity-only. Probe before using on an ETF. |
| `get_financials`, `get_stock_outlook`, `get_news_synthesis` | ✓ supported | UNVERIFIED | Validated in equity workflows only. |
| `analyze_portfolio` | ✓ mixed-asset OK | ✓ mixed-asset OK | Holdings can be equity + ETF; aggregation is correct. |
| `quick_portfolio_scores` | ✓ partial | UNVERIFIED | Symbol-mapping quirks — see conventions skill. |
| `macro_analyst`, `list_macro_countries` | n/a | n/a | Market-level, not symbol-level. |

## Classification Procedure

1. Resolve the symbol per the conventions skill (search_stocks, then the suffix table).
2. Call `etf_profile(<plain_ticker>)` — one symbol per call.
3. `{"error": "No profile data found", ...}` → **equity** → route price pulls through `export_price_series`.
4. Non-error profile → **ETF** → route price pulls through `etf_daily_price`.

Any workflow that accepts user-supplied symbols (holdings, peers, benchmarks) **and** calls `export_price_series` or another equity-only tool downstream MUST run this pre-classification first.

## Verified Benchmark ETFs (single-symbol probes, 2026-05-02)

| Market | Ticker | Status |
|---|---|---|
| United States | `SPY` | ✓ in coverage — NYSE Arca, RIC `SPY.P` |
| United States (tech) | `QQQ` | ✓ assumed in coverage — not yet probed |
| Japan | `EWJ` | ✓ in coverage |
| United Kingdom | `EWU` | ✓ in coverage — NYSE Arca |
| Hong Kong | `EWH` | ✓ in coverage — NYSE Arca |
| South Korea | `EWY` | ✓ in coverage — NYSE Arca |
| **Germany** | **`EWG`** | **✗ NOT IN COVERAGE** — empty response from `etf_daily_price` |
| Singapore | `EWS` | UNVERIFIED |
| Taiwan | `EWT` | UNVERIFIED |
| Canada | `EWC` | UNVERIFIED |
| Australia | `EWA` | UNVERIFIED |

For UNVERIFIED markets, call `etf_search` with the market name to discover available benchmarks at runtime. Do NOT assume the iShares MSCI country ETF is in coverage.

## Known API Quirks

1. **Multi-symbol calls fail-empty on partial coverage.** `etf_daily_price("SPY,EWJ,EWG")` returns `[]` — not the two valid symbols plus an error for the missing one. `get_company_info` behaves the same way (the missing symbol is silently dropped). **Always use single-symbol calls when coverage might be partial.**

2. **`etf_profile` returns an explicit error on equities.** This makes it a clean oracle: `{"error": "No profile data found", "ric": ...}` → equity; non-error → ETF.

3. **`.P` suffix == NYSE Arca == ETF.** When a probe is unavailable, resolve bare tickers to RICs per the conventions skill, then apply the static heuristic: a symbol that stays suffix-less or ends in `.P` is likely an ETF; otherwise treat it as equity.

## Failure-Handling Contracts by Workflow Type

When a tool returns empty/error *after* correct routing, the response depends on the workflow's type. Failure handling is not one-size-fits-all.

| Workflow type | Examples | Contract on per-component failure |
|---|---|---|
| **Sizing / construction** | `/parallax:rebalance` (trade list), any hedge-ratio or target-weight output | **Atomic gate.** Refuse to render the primary deliverable — a partially-computed weight is a confidence-building lie. Halt with the named failure plus operator-action options. |
| **Aggregation / attribution** | `/parallax:explain` (return decomposition), `/parallax:portfolio` (health flags) | **Partial render with explicit MISSING blocks.** Compute the aggregate on the remaining weight; surface each missing component by name. Never silently zero or drop. |
| **Per-symbol research** | `/parallax:stock`, `/parallax:deep-dive`, `/parallax:etf` | **Per-section partial.** If one tool fails, render that section as "Analysis pending — tool unavailable" and continue with the rest, per the conventions skill fallback rules. |

Routing correctness (right tool for the asset class) is separate from the failure contract. When authoring a workflow, ask: if tool X returns empty for one input, does the user want a halt, a partial, or a per-section fallback?

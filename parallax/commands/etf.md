---
description: Research, compare, or find ETFs — profiles, holdings, overlap, price history
argument-hint: "[ETF ticker(s) or search keywords]"
---

# ETF Research

## Argument parsing

- 1 ticker (`SPY`) → **single mode**
- 2-5 tickers (`SPY QQQ`) → **compare mode** (includes overlap)
- "overlap" + tickers → **overlap mode**
- Descriptive text ("high quality tech ETFs") → **search mode**
- If a supplied symbol turns out not to be an ETF (`etf_profile` errors "No profile data found" → it's an equity, per the asset-class-routing skill), say so and suggest `/parallax:stock`.

User-typed US ETF tickers are plain format: SPY, QQQ, IWM. `search_etfs` returns exchange-suffixed symbols (`ACES.P` NYSE Arca, `ZCLN.TO`, `RENG.L`); pass those to `etf_profile` unchanged.

## Modes

**Single ETF** → `etf_profile` + `etf_holdings` in parallel.

**Compare ETFs** → `etf_profile` per ticker (parallel, one call per ticker — multi-symbol calls fail empty on partial coverage), then overlap per below.

**Overlap check** → there is no server-side overlap tool. Fetch `etf_holdings` per ticker (parallel, single-symbol calls), intersect constituents client-side, and report: shared constituents, weight in each ETF, summed overlap weight. For 3+ ETFs report pairwise overlaps.

**Find ETFs by theme** → `search_etfs` with keywords, plus optional `market` or `currency`. It takes no factor filters. The server silently ignores any parameter outside `query`, `limit`, `market`, `currency`, so a filter passed anyway returns unfiltered results (verified live 2026-10-16). Do not pass `limit`; rely on the server default, per the conventions skill's numeric-parameter rule. Call `etf_profile` on the top 5 results that carry `has_scores: true`, one per call; a `has_scores: false` result profiles with null scores and still costs a token. Then apply any factor preference ("high quality") client-side from the profile scores.

**Price history** → `etf_daily_price`, one symbol per call (a multi-symbol call returns `[]` if ANY symbol is missing).

## Fallbacks

Instant-tool rules per the conventions skill: retry once, then mark the section "Data unavailable" and continue. `search_etfs`, `etf_profile`, `etf_holdings`, and `etf_daily_price` cost 1 token each; see the token-costs skill for per-mode totals.

**Output:** Profile → Top holdings → Overlap (if comparing) → Assessment.

Render the AI-interaction disclosure per the conventions skill §9.2 immediately above the disclaimer, then the standard disclaimer verbatim from the conventions skill §9.1.

## Render discipline

Apply the Render Discipline section of the conventions skill: suppress step scaffolding, hoist every integrity surface (⚠ MISMATCH rows, degraded-coverage notes, "Data unavailable" / "Analysis pending" markers) into the final output, and close with the §9.2 disclosure immediately above the §9.1 disclaimer.

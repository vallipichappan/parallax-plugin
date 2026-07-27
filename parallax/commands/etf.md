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

ETF tickers are plain format: SPY, QQQ, IWM — no exchange suffix. `.P`-suffixed RICs are NYSE Arca ETFs.

## Modes

**Single ETF** → `etf_profile` + `etf_holdings` in parallel.

**Compare ETFs** → `etf_profile` per ticker (parallel, one call per ticker — multi-symbol calls fail empty on partial coverage), then overlap per below.

**Overlap check** → there is no server-side overlap tool. Fetch `etf_holdings` per ticker (parallel, single-symbol calls), intersect constituents client-side, and report: shared constituents, weight in each ETF, summed overlap weight. For 3+ ETFs report pairwise overlaps.

**Find ETFs by theme** → `search_etfs` with keywords + optional factor filters (min_quality, min_momentum, etc.), then `etf_profile` on top results.

**Price history** → `etf_daily_price`, one symbol per call (a multi-symbol call returns `[]` if ANY symbol is missing).

## Fallbacks

Instant-tool rules per the conventions skill: retry once, then mark the section "Data unavailable" and continue. ETF tool costs are UNVERIFIED per the token-costs skill — do not quote a numeric cost estimate for this command.

**Output:** Profile → Top holdings → Overlap (if comparing) → Assessment.

Render the AI-interaction disclosure per the conventions skill §9.2 immediately above the disclaimer, then the standard disclaimer verbatim from the conventions skill §9.1.

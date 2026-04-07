---
description: Research, compare, or find ETFs — snapshots, holdings, overlap, price history
argument-hint: "[ETF ticker(s) or search keywords]"
---

# ETF Research

**Single ETF** → `get_etf_snapshot` + `get_etf_holdings`

**Compare ETFs** → `compare_etfs` then `get_etf_overlap` (shows true diversification)

**Find ETFs by theme** → `search_etfs` with keywords + optional factor filters (min_quality, min_momentum, etc.), then snapshot top results

**Overlap check** → `get_etf_overlap` with 2–5 tickers; weights optional

**Price history** → `get_etf_price_history` with date range

ETF tickers are plain format: SPY, QQQ, IWM — no exchange suffix.

**Output:** Profile → Factor scores → Top holdings → Overlap (if comparing) → Recommendation.

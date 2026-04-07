---
description: Research, compare, or find ETFs — snapshots, holdings, overlap, and price history
argument-hint: "[ETF ticker(s) or search keywords, e.g. SPY QQQ or 'clean energy momentum']"
---

# ETF Research Command

Research one or more ETFs, compare alternatives, or find ETFs matching an investment theme.

## Workflow

### Step 1: Determine the intent

**Single ETF lookup** (e.g. "tell me about SPY"):
→ Call `get_etf_snapshot` for profile and factor scores
→ Call `get_etf_holdings` for top holdings and per-holding scores

**Head-to-head comparison** (e.g. "SPY vs QQQ vs IWM"):
→ Call `compare_etfs` with the tickers
→ Follow up with `get_etf_overlap` to show shared holdings and true diversification

**Theme search** (e.g. "find me a high-quality tech ETF"):
→ Call `search_etfs` with relevant keywords and optional factor filters
→ Then snapshot the top 2-3 results

**Overlap check** (e.g. "how much do VOO and VTI overlap?"):
→ Call `get_etf_overlap` with 2-5 ETF tickers
→ Show combined stock exposure and redundancy

**Price history** (e.g. "how has QQQ performed this year?"):
→ Call `get_etf_price_history` with the date range

### Step 2: Synthesize
For lookups and comparisons, present:
1. **Profile** — what the ETF tracks, AUM, expense ratio
2. **Factor scores** — Quality, Value, Momentum, Defensive relative to peers
3. **Top holdings** — concentration, sector breakdown, standout names
4. **Overlap** (if comparing) — shared holdings %, effective diversification
5. **Verdict** — which fits the user's goal and why

## Tips
- ETF tickers are plain format: SPY, QQQ, IWM, ARKK (no exchange suffix)
- `search_etfs` accepts multiple keywords — they're merged and ranked, not filtered strictly
- Overlap analysis works for 2-5 ETFs; weights are optional

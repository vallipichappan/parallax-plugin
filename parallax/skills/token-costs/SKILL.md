---
name: token-costs
description: Per-tool token costs and cost-optimal routing rules for Parallax commands.
---

# Token Costs

## Tool Costs

| Tokens | Tools |
|---|---|
| **0 (free)** | `explain_methodology`, `search_stocks`, `export_price_series`, `get_docs`, `list_docs` |
| **1 each** | `get_company_info`, `get_peer_snapshot`, `get_financials` (per statement), `get_stock_outlook` (per aspect), `get_score_analysis`, `export_peer_comparison`, `list_macro_countries`, `get_telemetry`, `search_etfs`, `etf_profile`, `etf_holdings`, `etf_daily_price` |
| **1 per holding** | `quick_portfolio_scores`, `check_portfolio_redundancy` |
| **5 each** | `build_stock_universe`, `get_news_synthesis`, `get_technical_analysis`, `get_financial_analysis`, `analyze_portfolio`, `macro_analyst`, `check_macro_health` |
| **10 each** | `get_stock_report`, `get_assessment` |

`etf_profile` and `etf_daily_price` were measured at 1 token on 2026-07-28. `search_etfs` and `etf_holdings` are 1 token each per the server's tool manifest, read 2026-10-16. Every ETF tool is priced, so ETF-touching workflows publish real subtotals.

## Routing Rules

1. **Portfolio scoring path:** `quick_portfolio_scores` (1/holding) is the default. `analyze_portfolio` (5 flat) is a different product — a full performance/attribution payload with 180K-char truncation risk — not a per-holding score substitute. On raw token price it is cheaper at 6+ holdings, but route to it only when the workflow needs its performance analytics; for scoring economy alone, prefer it only on large books (15+ holdings) where the truncation fallback is acceptable.
2. **News is 5 tokens:** Only call for high-priority holdings (>10% weight and flagged), not all holdings.
3. **`get_assessment` is 10 tokens:** Call once per workflow after all data is assembled, not incrementally.
4. **Free tools:** `explain_methodology` and `search_stocks` cost nothing — use liberally for score explanations and symbol resolution.
5. **`macro_analyst` summary vs components:** A single call without `component` returns all 9 components inline (5 tokens). Per-component calls return identical content at 5 tokens each. Use summary mode for full macro analysis (`/parallax:macro`). Use component="tactical" when you only need the tactical slice (stock, portfolio, rebalance, scenario commands) — this returns the same content but signals intent.
6. **Investor profiles vary ~50x in cost:** Buffett is 4 tokens; consensus on a 5-ticker basket runs 250+. When a user asks "what do the legends think about AAPL?" (consensus single-ticker), warn that this is ~67-94 tokens. Consensus basket-of-5 is the most expensive operation in the plugin.

## Workflow Cost Estimates

Estimates assume no cache hits and `export_price_series` at 0 tokens.

| Workflow | Typical Tokens |
|---|---|
| `/parallax:stock` | ~24 |
| `/parallax:portfolio` (checkup) | ~36 |
| `/parallax:portfolio` (advisor mode) | ~105 |
| `/parallax:deep-dive` | ~45 |
| `/parallax:explain` | ~45-50 for a 5-holding book (3/holding + macro + news for top 3 detractors + one `etf_profile` probe per holding) |
| `/parallax:credit` | ~13-19 |
| `/parallax:macro` | ~12 single market (+5 per additional market, +18 with equity opportunities) |
| `/parallax:universe` | ~46 with 10 cross-validated candidates |
| `/parallax:thematic-screen` | ~36 at 5 picks with 3 macro markets (~46 at 10 picks) |
| `/parallax:etf` | ~2 single ETF (profile + holdings); ~2 per ticker for a compare (profile + holdings, since compare includes overlap); ~1 per ticker for an overlap-only request; ~6 for a theme search (search + 5 profiles); +1 per `etf_daily_price` call |
| `/parallax:screen` (halal) | ~8 |
| `/parallax:screen` (quality) | ~24 |
| `/parallax:scenario` | ~68 |
| `/parallax:rebalance` | ~76 |
| `/parallax:peers` | ~9 (snapshot + company info + comparison export + three score histories + three `etf_profile` probes; +1 per ETF leg priced through `etf_daily_price`) |
| `/parallax:why-score` | ~3 for "why does X score this way"; 0 for a concept question (free tools only); ~8 for "why did it change" (adds one async news synthesis) |
| `/parallax:start` | 0 for the menu itself; then the cost of the workflow it routes to |
| `/parallax:investor` (buffett) | ~4 |
| `/parallax:investor` (greenblatt ticker-check) | ~35-40 (dominated by the per-candidate `get_financials` ratios pull; scales linearly with the candidate cap) |
| `/parallax:investor` (greenblatt universe) | ~35-40 |
| `/parallax:investor` (klarman) | ~5-7 |
| `/parallax:investor` (soros single-ticker) | ~23-43 |
| `/parallax:investor` (soros basket) | ~28-72 |
| `/parallax:investor` (consensus single) | ~67-94 |
| `/parallax:investor` (consensus basket-5) | ~250-330 (Greenblatt universe pull may amortize across tickers; treat as upper bound) |

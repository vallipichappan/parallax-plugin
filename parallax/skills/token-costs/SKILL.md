---
name: token-costs
description: Per-tool credit costs and cost-optimal routing rules for Parallax commands.
---

# Credit Costs

The server bills in **credits**. The skill keeps its historical `token-costs` name so existing references still resolve.

## Tool Costs

Prices come from the `Cost:` marker in each served tool description, read 2026-10-22. They match the server's published credit contract, which took effect 2026-10-18. The live tool description wins if it ever disagrees with this table.

| Credits | Tools |
|---|---|
| **0 (free)** | `search_stocks`, `search_etfs`, `etf_search` (deprecated alias of `search_etfs`), `explain_methodology`, `get_docs`, `list_docs`, `list_macro_countries`, `check_macro_health` (deprecated; use `list_macro_countries`), `check_api_health`, `check_job_status`, `submit_feedback` |
| **0.05 per symbol** | `get_company_info`, `export_price_series`, `etf_daily_price`, `get_financials` (0.1 per symbol when `latest=true` on income, balance_sheet or cash_flow), `get_stock_outlook` aspect="dividends" |
| **0.05 per call** | `get_telemetry`, `get_stock_outlook` aspect="analyst_targets" or "recommendations" |
| **0.1 per call** | `get_peer_snapshot`, `export_peer_comparison`, `get_score_analysis`, `get_score_summary`, `etf_profile`, `etf_holdings`, `get_stock_outlook` aspect="risk_return" |
| **0.1 per holding** | `quick_portfolio_scores` (default 50 holdings, max 100), `check_portfolio_redundancy` (top 100 by weight, so at most 10) |
| **Variable, at most 0.2** | `get_performance_history` (returns calendar plus optional risk/return, 0.1 each); `explore_telemetry` (0.05; 0.1 for a stock lookup; +0.05 per basket opened) |
| **5 per call** | `build_stock_universe`, `get_news_synthesis`, `get_technical_analysis`, `get_financial_analysis`, `analyze_portfolio`, `macro_analyst` (see rule 5) |
| **10 per call** | `get_stock_report`, `get_assessment` (always the deep tier), `get_etf_report` (symbol resolution is free) |

A comma-separated symbol list multiplies a per-symbol price: three symbols at 0.05 cost 0.15 in one call. Failed HTTP requests and failed async jobs are not billed.

## Routing Rules

1. **Portfolio scoring path:** `quick_portfolio_scores` (0.1 per holding) is the default. `analyze_portfolio` (5 flat) is a different product: a full performance and attribution payload with 180K-char truncation risk. The two cost the same at 50 holdings. Below 50, `quick_portfolio_scores` is cheaper. Route to `analyze_portfolio` only when the workflow needs its performance analytics, never for scoring economy below 50 holdings.
2. **News is 5 credits:** Only call for high-priority holdings (>10% weight and flagged), not all holdings.
3. **`get_assessment` is 10 credits:** Call once per workflow after all data is assembled, not incrementally.
4. **Free tools:** symbol search, methodology, docs and macro coverage cost nothing. Use them freely for symbol resolution and score explanations.
5. **`macro_analyst` overview vs components:** a call without `component` returns the overview at 5 credits. If the overview arrives without a success payload, the server fetches the nine components itself, at up to 50 credits total. An explicit `component` never fans out. Use the overview for full macro analysis (`/parallax:macro`). Use component="tactical" when only the tactical slice is needed (stock, portfolio, rebalance, scenario commands).
6. **The 5- and 10-credit calls set the bill.** Scores, financials, prices and asset-class probes cost 0.05 to 0.1 each, so a workflow's cost is mostly its count of universe builds, macro calls, news, technicals, Palepu analyses, reports and assessments. Investor profiles range from ~0.3 (Buffett) to consensus on a 5-ticker basket, which runs all four profiles on each ticker. Warn before consensus on a basket: it is the most expensive operation in the plugin.

## Workflow Cost Estimates

Estimates assume no cache hits, every call succeeds, and no `macro_analyst` overview fan-out. `N` is the holding count; `M` is the number of macro markets (cap 3).

| Workflow | Typical Credits |
|---|---|
| `/parallax:stock` | ~15.6 with 1 macro market (+5 per extra market) |
| `/parallax:portfolio` (checkup) | 0.35 per holding + 5 per macro market: ~16.8 for 5 holdings and 3 markets |
| `/parallax:portfolio` (advisor mode) | ~48 for 5 holdings, 3 markets and 2 news calls (+5 per extra news call, cap 5) |
| `/parallax:deep-dive` | ~35.6 with 3 macro markets (~25.6 with 1); Full Mode adds ~10.2 |
| `/parallax:explain` | ~22 for a 5-equity book with 1 macro market (one `etf_profile` probe and one price pull per holding, 0.25 per equity for scoring, news for the top 3 detractors); +5 per extra market |
| `/parallax:credit` | ~5.5 |
| `/parallax:macro` | ~5 single market (+5 per additional market, +6 with equity opportunities); overview fan-out can raise one market to 50 |
| `/parallax:universe` | ~13 with 10 cross-validated candidates and a validation run |
| `/parallax:thematic-screen` | ~21 at 5 picks with 3 macro markets (~22 at 10 picks); 6 + 5 per macro market |
| `/parallax:etf` | ~0.2 single ETF (profile + holdings); ~0.2 per ticker for a compare; ~0.1 per ticker for overlap only; ~0.5 for a theme search (free search + 5 profiles); +0.05 per `etf_daily_price` call |
| `/parallax:screen` (halal) | ~0.25 per stock (+5 for the optional Palepu analysis); portfolio mode adds 0.1 per compliant holding for redundancy, 5 per alternatives universe, 0.25 per alternative screened and 0.15 per compliant alternative scored |
| `/parallax:screen` (quality) | ~20.3 |
| `/parallax:scenario` | ~49 for 10 holdings, 2 macro markets and 3 sector news calls |
| `/parallax:rebalance` | ~35.5 for 10 holdings and 3 macro markets, plus 0.15 per replacement candidate; watchlist mode is 0.1 per symbol plus ~10.05 per flagged symbol |
| `/parallax:peers` | ~1.0 (snapshot + company info + comparison export + three score histories + three `etf_profile` probes + three price pulls) |
| `/parallax:why-score` | ~0.25 for "why does X score this way"; 0 for a concept question (free tools only); ~5.25 for "why did it change" (adds one async news synthesis) |
| `/parallax:start` | 0 for the menu itself; then the cost of the workflow it routes to |
| `/parallax:investor` (buffett) | ~0.3 |
| `/parallax:investor` (greenblatt ticker-check) | 5.15 + 0.05 per candidate (identity check, one universe build, one ratios pull per candidate) |
| `/parallax:investor` (greenblatt universe) | 5 + 0.05 per candidate (one universe build, one ratios pull per candidate) |
| `/parallax:investor` (klarman) | ~0.3 |
| `/parallax:investor` (soros single-ticker) | ~20-40: 5 per macro market and 5 per theme universe dominate |
| `/parallax:investor` (soros basket) | ~21-42: 5 per macro market and 5 per theme universe, plus 0.15 per theme leader scored |
| `/parallax:investor` (consensus single) | Sum of the buffett, klarman, soros single-ticker and greenblatt ticker-check rows |
| `/parallax:investor` (consensus basket-5) | At most five consensus single runs; shared macro and Greenblatt universe calls lower it |

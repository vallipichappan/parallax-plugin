---
name: token-costs
description: Per-tool token costs and cost-optimal routing rules for Parallax commands.
---

# Token Costs

## Tool Costs

| Tokens | Tools |
|---|---|
| **0 (free)** | `explain_methodology` |
| **1 each** | `get_company_info`, `get_peer_snapshot`, `get_financials` (per statement), `get_stock_outlook` (per aspect), `get_score_analysis`, `export_price_series`, `list_macro_countries`, `get_telemetry` |
| **1 per holding** | `quick_portfolio_scores`, `check_portfolio_redundancy` |
| **5 each** | `build_stock_universe`, `get_news_synthesis`, `get_technical_analysis`, `get_financial_analysis`, `analyze_portfolio`, `analyze_mixed_portfolio`, `macro_analyst` |
| **10 each** | `get_stock_report`, `get_assessment` |

## Routing Rules

1. **Portfolio size crossover:** `analyze_portfolio` (5 flat) vs `quick_portfolio_scores` (1/holding). Breakeven at 5 holdings — for 6+ holdings, `analyze_portfolio` is more cost-effective.
2. **News is 5 tokens:** Only call for high-priority holdings (>10% weight and flagged), not all holdings.
3. **`get_assessment` is 10 tokens:** Call once per workflow after all data is assembled, not incrementally.
4. **`explain_methodology` is free:** Use liberally for notably high or low scores.
5. **`macro_analyst` summary vs components:** A single call without `component` returns all 9 components inline (5 tokens). Per-component calls return identical content at 5 tokens each. Use summary mode for full macro analysis (`/parallax:macro`). Use component="tactical" when you only need the tactical slice (stock, portfolio, rebalance, scenario commands) — this returns the same content but signals intent.
6. **Investor profiles vary 10x in cost:** Buffett is 4 tokens; consensus on 5 tickers is 150-200. When a user asks "what do the legends think about AAPL?" (consensus single-ticker), warn that this is ~50 tokens. Consensus basket-of-5 is the most expensive operation in the plugin.

## Workflow Cost Estimates

| Workflow | Typical Tokens |
|---|---|
| `/parallax:stock` | ~24 |
| `/parallax:portfolio` (checkup) | ~36 |
| `/parallax:portfolio` (advisor mode) | ~105 |
| `/parallax:deep-dive` | ~45 |
| `/parallax:macro` | ~41 (28 without equities) |
| `/parallax:universe` | ~36 |
| `/parallax:screen` (halal) | ~8 |
| `/parallax:screen` (quality) | ~24 |
| `/parallax:scenario` | ~68 |
| `/parallax:rebalance` | ~76 |
| `/parallax:investor` (buffett) | ~4 |
| `/parallax:investor` (greenblatt ticker-check) | ~10-15 |
| `/parallax:investor` (greenblatt universe) | ~15-30 |
| `/parallax:investor` (klarman) | ~5-7 |
| `/parallax:investor` (soros single-ticker) | ~25-30 |
| `/parallax:investor` (soros basket) | ~25-40 |
| `/parallax:investor` (consensus single) | ~45-55 |
| `/parallax:investor` (consensus basket-5) | ~150-200 |

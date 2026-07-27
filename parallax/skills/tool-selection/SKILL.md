---
name: tool-selection
description: Reference for which Parallax MCP tool or command to call for any investment question. Consult this before choosing a tool.
---

# Tool Selection

| User asks | Use |
|---|---|
| "Tell me about [stock]" | `/parallax:stock` |
| "Quick scores for [stock]" | `get_peer_snapshot` |
| "Should I buy [stock]?" | `/parallax:stock` |
| "Tell me about [ETF]" | `/parallax:etf` (single mode — `etf_profile` + `etf_holdings`) |
| "Compare [ETF A] vs [ETF B]" | `/parallax:etf` (compare mode) |
| "What ETFs overlap?" | `/parallax:etf` (overlap mode — client-side intersection of `etf_holdings`) |
| "Find ETFs for [theme]" | `/parallax:etf` (search mode — `search_etfs`) |
| "Analyze my portfolio" | `/parallax:portfolio` |
| "Is my portfolio concentrated?" | `check_portfolio_redundancy` |
| "Quick factor check" | `quick_portfolio_scores` |
| "Macro outlook for [country]" | `/parallax:macro` |
| "Compare US vs Japan macro" | `/parallax:macro` (multi-country mode) |
| "Find stocks that [theme]" | `/parallax:universe` |
| "Build me a portfolio for [theme]" | `/parallax:universe` |
| "What's the news on [stock]?" | `get_news_synthesis` |
| "What are the financials?" | `get_financials` |
| "What do analysts think?" | `get_stock_outlook` (aspect=analyst) |
| "Price history / performance" | `export_price_series` (stocks, free) or `etf_daily_price` (ETFs) — route per asset-class-routing skill |
| "Full research report PDF" | `get_stock_report` (~2 min) |
| "Deep dive on [stock]" | `/parallax:deep-dive` |
| "What's the market doing today?" | `get_telemetry` (~15-30s) |
| "How does scoring work?" | `explain_methodology` |
| "Is [stock] halal / Shariah compliant?" | `/parallax:screen` (halal mode) |
| "Check earnings quality of [stock]" | `/parallax:screen` (quality mode) |
| "Forensic analysis of [stock]" | `/parallax:screen` (quality mode) |
| "Compare [stock A] vs [stock B]" | `export_peer_comparison` (one call, cross-sectionally comparable scores) |
| "Is [stock] a Buffett stock?" | `/parallax:investor` (buffett mode) |
| "What would Buffett think of [stock]?" | `/parallax:investor` (buffett mode) |
| "Apply Buffett factor profile" | `/parallax:investor` (buffett mode) |
| "Magic Formula screen" | `/parallax:investor` (greenblatt universe mode) |
| "Is [stock] a Magic Formula stock?" | `/parallax:investor` (greenblatt mode) |
| "Greenblatt screen for [sector]" | `/parallax:investor` (greenblatt universe mode) |
| "Margin of safety on [stock]" | `/parallax:investor` (klarman mode) |
| "Klarman analysis of [stock]" | `/parallax:investor` (klarman mode) |
| "Is [stock] balance-sheet safe?" | `/parallax:investor` (klarman mode) |
| "Soros view on [stock]" | `/parallax:investor` (soros mode) |
| "Regime themes and trade ideas" | `/parallax:investor` (soros basket mode) |
| "Macro reflexivity analysis" | `/parallax:investor` (soros mode) |
| "What do the legends think about [stock]?" | `/parallax:investor` (consensus mode) |
| "Run all investor profiles on [stock]" | `/parallax:investor` (consensus mode) |
| "Cross-profile consensus on [stock]" | `/parallax:investor` (consensus mode) |
| "What if [event]? My portfolio is..." | `/parallax:scenario` |
| "Rebalance my portfolio" | `/parallax:rebalance` |
| "Monitor my watchlist" | `/parallax:rebalance` (watchlist mode) |
| "Why am I down?" / "explain my drawdown" | `/parallax:explain` |
| "Credit risk / can [company] service its debt?" | `/parallax:credit` |
| "Resolve ticker / find symbol" | `search_stocks` (free) |
| "I found a bug / feature request" | `submit_feedback` |

Default for any ambiguous stock question: `get_peer_snapshot`.
Default for any investor/legend/Buffett/Greenblatt/Klarman/Soros/Magic Formula/margin-of-safety question: `/parallax:investor`.

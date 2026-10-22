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
| "Thematic ideas for [X]" / "trade ideas around [X]" / "idea list for [theme]" | `/parallax:thematic-screen` — ranked idea list, no weights |
| "Find stocks that [theme]" | `/parallax:thematic-screen` for a ranked shortlist; `/parallax:universe` if they want it weighted into a portfolio — ask once if unclear |
| "Build me a portfolio for [theme]" | `/parallax:universe` |
| "What's the news on [stock]?" | `get_news_synthesis` |
| "What are the financials?" | `get_financials` |
| "What do analysts think?" | `get_stock_outlook` (aspect="analyst_targets") |
| "Price history / daily prices" | `export_price_series` (stocks) or `etf_daily_price` (ETFs) — route per asset-class-routing skill |
| "How has [stock] performed?" / "returns by year or month" | `get_performance_history` — YTD, 12-month, yearly and monthly returns, 1-year return and volatility against peers |
| "Full research report PDF" | `get_stock_report` (~2 min) |
| "ETF research report" | `get_etf_report` (~1-2 min, 10 credits); if it returns several candidate ETFs, confirm one with the user before generating |
| "Deep dive on [stock]" | `/parallax:deep-dive` |
| "What's the market doing today?" | `get_telemetry` |
| "Which theme is [stock] in?" / "what's moving in [market]?" / "top baskets" | `explore_telemetry` — telemetry baskets by stock, market, or theme; the daily narrative and regime stay with `get_telemetry` |
| "How does scoring work?" | `explain_methodology` |
| "Is [stock] halal / Shariah compliant?" | `/parallax:screen` (halal mode) |
| "Check earnings quality of [stock]" | `/parallax:screen` (quality mode) |
| "Forensic analysis of [stock]" | `/parallax:screen` (quality mode) |
| "Compare [stock A] vs [stock B]" | `get_company_info` + `get_peer_snapshot` per stock, cross-validated per the conventions skill, shown side by side on the sector-relative 0-10 scale. If A and B are in different sectors, say so and do not rank one above the other on raw score. `export_peer_comparison` covers one symbol's peer set, so it compares A with B only when B is already one of A's peers |
| "How does [stock] compare to its peers?" | `/parallax:peers` |
| "Who are [stock]'s competitors / peer group?" | `/parallax:peers` |
| "Is [stock]'s score rising or falling?" | `get_score_summary` — current score, 13-week trend, 52-week range; week-by-week history is `get_score_analysis` |
| "Why does [stock] score that way?" | `/parallax:why-score` |
| "What does the [factor] factor measure?" | `/parallax:why-score` |
| "Why did [stock]'s score drop?" | `/parallax:why-score` |
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
| "What can Parallax do?" / no specific ask | `/parallax:start` |

Note `/parallax:explain` is drawdown attribution, not score methodology — score explanations are `/parallax:why-score`. `explain_methodology` is the raw tool behind the latter; prefer the command when the user wants an explanation rather than a definition.

Three routes touch "ideas": `/parallax:universe` turns a user theme into a weighted portfolio; `/parallax:thematic-screen` turns a user theme into an unweighted ranked idea list; `/parallax:investor` (soros basket mode) derives ideas from the macro regime with no user theme supplied. A bare "screen for [theme]" routes to `/parallax:screen` (halal/quality) when it names a compliance or forensic filter (halal, Shariah, quality, forensic, accruals); otherwise treat it as "thematic ideas for [theme]" and route to `/parallax:thematic-screen`.

**Raw-tool answers keep the guardrails.** Any answer built from a raw tool rather than a slash command still renders the §9.2 banner and §9.1 disclaimer per the conventions skill. If the answer uses `get_peer_snapshot`, also call `get_company_info` and run the cross-validation gate before rendering scores.

Default for any ambiguous stock question: `get_peer_snapshot`.
Default for any investor/legend/Buffett/Greenblatt/Klarman/Soros/Magic Formula/margin-of-safety question: `/parallax:investor`.

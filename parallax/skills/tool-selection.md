---
name: tool-selection
description: Which Parallax tool to call for common user questions.
---

# Tool Selection

| User asks | Use |
|---|---|
| "Tell me about [stock]" | `get_peer_snapshot` |
| "Tell me about [ETF]" | `get_etf_snapshot` |
| "Compare [ETF A] vs [ETF B]" | `compare_etfs` → `get_etf_overlap` |
| "Find ETFs for [theme]" | `search_etfs` |
| "Analyze my portfolio" | `analyze_portfolio` or `analyze_mixed_portfolio` |
| "Is my portfolio concentrated?" | `check_portfolio_redundancy` |
| "Quick factor check" | `quick_portfolio_scores` |
| "Macro outlook for [country]" | `macro_analyst` |
| "Find stocks that [theme]" | `build_stock_universe` |
| "What's the news on [stock]?" | `get_news_synthesis` |
| "What are the financials?" | `get_financials` |
| "What do analysts think?" | `get_stock_outlook` (aspect=analyst) |
| "Price history / performance" | `export_price_series` (stocks) or `get_etf_price_history` (ETFs) |
| "Full research report PDF" | `get_stock_report` (~2 min) |
| "Deep dive" | `get_financial_analysis` + `get_technical_analysis` in parallel |
| "What's the market doing today?" | `get_telemetry` (~15–30s) |
| "How does scoring work?" | `explain_methodology` |
| "I found a bug / feature request" | `submit_feedback` |

Default for any ambiguous stock question: `get_peer_snapshot`.

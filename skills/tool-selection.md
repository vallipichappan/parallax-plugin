---
name: tool-selection
description: |
  Decision guide for picking the right Parallax tool for common user questions.

  Use when: a user asks a question and it's unclear which tool best answers it. Consult this before calling any tool.
---

# Tool Selection Guide

## "Tell me about [company]"
→ `get_peer_snapshot` — this is the default. Returns scores, peer ranking, and investment signal.

## "Tell me about [ETF]"
→ `get_etf_snapshot` — profile and factor scores for one or more ETFs.

## "Compare [ETF A] vs [ETF B]"
→ `compare_etfs` then `get_etf_overlap` — head-to-head scores plus shared holdings.

## "What ETFs should I look at for [theme]?"
→ `search_etfs` with keywords and optional factor filters.

## "Analyze my portfolio: AAPL 30%, MSFT 30%, GOOGL 40%"
→ `analyze_portfolio` (stocks only) or `analyze_mixed_portfolio` (if any ETFs present).

## "Is my portfolio too concentrated?"
→ `check_portfolio_redundancy` — detects sector, industry, and factor clusters.

## "What's the macro situation in [country]?"
→ `macro_analyst` with just the market name for the overview, then drill into components.

## "Find me stocks that [theme/description]"
→ `build_stock_universe` — natural language search across 65K+ companies.

## "What's the news on [company]?"
→ `get_news_synthesis` — AI-synthesized financial news. Faster and more reliable than web search.

## "What are the financials for [company]?"
→ `get_financials` with appropriate statement type (summary, income, balance_sheet, cash_flow, ratios).

## "What do analysts think about [company]?"
→ `get_stock_outlook` with aspect=analyst.

## "How has [stock/ETF] performed?"
→ `export_price_series` (stocks, RIC format) or `get_etf_price_history` (ETFs, plain ticker).

## "Give me a full research report on [company]"
→ `get_stock_report` — generates a formatted PDF/HTML Chicago Global report (1-2 min).

## "Do a deep dive on [company]"
→ `/deep-dive` command: `get_financial_analysis` + `get_technical_analysis` in parallel.

## "What's the market doing today?"
→ `get_telemetry` — daily regime snapshot, signals, and factor decomposition (~15-30s).

## "How does the scoring work?"
→ `explain_methodology` with the concept name.

## "I found a bug" / "Can you add [feature]?"
→ `submit_feedback` — auto-routes to the right team.

## Priority rule
When a user asks a broad question like "what do you think about AAPL?", always start with `get_peer_snapshot`. It gives the richest single-call answer and signals whether deeper analysis is warranted.

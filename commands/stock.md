---
description: Full research brief on a stock — scores, peers, financials, news, analyst outlook
argument-hint: "[ticker or company name]"
---

# Stock Research

1. Resolve symbol → `get_company_info` if given a name (returns RIC format)
2. `get_peer_snapshot` — scores, peer ranking, overall signal
3. In parallel: `get_financials` (statement=summary) + `get_stock_outlook` (aspect=analyst) + `get_news_synthesis`
4. Present as: Signal → Peer standing → Financials → Analyst view → News → 2-3 risks/catalysts

For a deep dive: add `get_technical_analysis` + `get_financial_analysis` (async, see async-jobs skill).
For a PDF report: `get_stock_report` (~2 min).

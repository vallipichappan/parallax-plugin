---
description: Full investment research report on a stock — scores, peers, financials, news, and outlook in one pass
argument-hint: "[ticker or company name]"
---

# Stock Research Command

Generate a complete investment research brief on a single stock.

## Workflow

### Step 1: Resolve the symbol
If a company name is given instead of a ticker, use `get_company_info` to resolve it to a RIC symbol first (e.g. AAPL → AAPL.O).

### Step 2: Run the core snapshot
Call `get_peer_snapshot` — this is the default starting point. It returns:
- Multi-factor scores (Quality, Value, Momentum, Defensive, Tactical)
- Peer comparison and ranking
- Overall investment signal

### Step 3: Get financials and outlook
In parallel, call:
- `get_financials` with statement=summary for the headline numbers
- `get_stock_outlook` with aspect=analyst for price targets and consensus
- `get_news_synthesis` for the latest AI-synthesized news

### Step 4: Synthesize
Present findings as a structured brief:
1. **Signal** — overall score and what it means (use `explain_methodology` if needed)
2. **Peer standing** — where it ranks vs peers and why
3. **Financial snapshot** — key ratios and recent trends
4. **Analyst view** — consensus target, upside/downside
5. **News** — what's moving the story right now
6. **Watch** — 2-3 key risks or catalysts to monitor

## Tips
- Use RIC format for all API calls (AAPL.O, MSFT.O, 0700.HK)
- If the user asks for a deep dive, also call `get_technical_analysis` and `get_financial_analysis`
- If the user asks for a full report PDF, call `get_stock_report` (takes 1-2 min)
- Scores are 0-100; above 60 is constructive, above 75 is strong

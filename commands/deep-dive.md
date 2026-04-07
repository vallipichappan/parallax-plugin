---
description: Deep fundamental and technical analysis on a stock — financial framework, technicals, and AI assessment
argument-hint: "[ticker or company name]"
---

# Deep Dive Command

Run a full analytical deep dive on a stock: financial framework analysis, technical analysis, and AI-powered impact assessment.

## Workflow

### Step 1: Resolve the symbol
Use `get_company_info` if given a company name to get the RIC symbol.

### Step 2: Kick off async jobs
These all take time — start them in parallel and report back when complete:

- `get_financial_analysis` — Palepu framework (profitability, liquidity, solvency, valuation). Takes 2-5 min.
- `get_technical_analysis` — Trend, RSI, MACD, support/resistance, volume, volatility. Takes 15-30s.

Both return a `job_id`. Poll with `check_job_status` until `status: completed`.

### Step 3: AI assessment (optional)
If the user has a specific question (e.g. "what's the impact of rising rates on this name?"), call `get_assessment` with a detailed prompt that includes:
- The company and its business model
- The specific scenario or question
- Any relevant context from steps 1-2

This takes ~3 minutes.

### Step 4: Frame the deep dive
Structure the output:
1. **Business quality** — profitability trends, competitive moat signals, earnings quality
2. **Balance sheet** — liquidity, solvency, capital efficiency
3. **Valuation** — DCF-implied range, multiple comparison vs peers
4. **Technical picture** — trend direction, momentum, key levels (support/resistance)
5. **Scenario analysis** — bear/base/bull from the assessment if run
6. **Bottom line** — investment case in 3 sentences

## Tips
- Financial analysis and technical analysis can run in parallel — kick both off before waiting
- Always pair deep-dive findings with peer context from `get_peer_snapshot`
- For a quick view instead of deep dive, use `/stock` instead
- If the user needs a formal PDF report, `get_stock_report` generates a formatted Chicago Global report

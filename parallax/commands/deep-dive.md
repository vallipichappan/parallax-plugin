---
description: Deep fundamental and technical analysis — Palepu framework, technicals, AI assessment
argument-hint: "[ticker or company name]"
---

# Deep Dive

1. Resolve symbol → `get_company_info` if needed
2. Kick off in parallel (both async — see async-jobs skill):
   - `get_financial_analysis` — Palepu framework: profitability, liquidity, solvency, valuation (~2–5 min)
   - `get_technical_analysis` — trend, RSI, MACD, support/resistance, volume (~15–30s)
3. Poll both with `check_job_status` until complete
4. Optional: `get_assessment` for a specific scenario question (~3 min)

**Output:** Business quality → Balance sheet → Valuation → Technical picture → Scenario analysis → 3-sentence investment case.

For a quicker view, use `/stock` instead.

---
name: parallax-scoring
description: How to interpret Parallax factor scores (0–100) in investment context.
---

# Parallax Scoring

Five factors, each 0–100, peer-relative within the stock's sector:

| Factor | Measures |
|---|---|
| **Quality** | Earnings quality, balance sheet strength, ROIC |
| **Value** | Price vs fundamentals (earnings, book, cash flow) |
| **Momentum** | Price and earnings trend direction and persistence |
| **Defensive** | Volatility, beta, drawdown characteristics |
| **Tactical** | Short-term technicals + sentiment signal |

**Overall** = weighted composite (defensive weight increases in risk-off regimes).

**Ranges:** 75–100 strong · 60–74 constructive · 40–59 neutral · 25–39 cautious · 0–24 weak

**Common patterns:**
- High Quality + Low Value → quality at a price; wait for catalyst
- High Momentum + Low Defensive → growth play; higher beta, works in risk-on
- High Defensive + Low Momentum → shelter stock; underperforms rallies, protects drawdowns
- High Value + Low Quality → value trap risk; check earnings quality first

Call `explain_methodology` with a concept name for detailed definitions, or pass a score number for contextualised interpretation.

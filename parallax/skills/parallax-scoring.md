---
name: parallax-scoring
description: How to interpret Parallax factor scores (0-100) and explain scoring methodology to users.
---

# Parallax Scoring

Five factors, each 0-100, peer-relative within the stock's sector:

| Factor | Measures |
|---|---|
| **Quality** | Earnings quality, balance sheet strength, ROIC |
| **Value** | Price vs fundamentals (earnings, book, cash flow) |
| **Momentum** | Price and earnings trend direction and persistence |
| **Defensive** | Volatility, beta, drawdown characteristics |
| **Tactical** | Short-term technicals + sentiment signal |

**Overall** = weighted composite (defensive weight increases in risk-off regimes).

**Ranges:** 75-100 strong / 60-74 constructive / 40-59 neutral / 25-39 cautious / 0-24 weak

**Common patterns:**
- High Quality + Low Value → quality at a price; wait for catalyst
- High Momentum + Low Defensive → growth play; higher beta, works in risk-on
- High Defensive + Low Momentum → shelter stock; underperforms rallies, protects drawdowns
- High Value + Low Quality → value trap risk; check earnings quality first

## Explaining Scores

Call `explain_methodology` (free, instant) for three question types:

| User asks | `explain_methodology` parameter | Then |
|---|---|---|
| "Why does X score this way?" | The specific factor name (e.g., "quality") | Follow with `get_score_analysis` weeks=26 for trend context |
| "What does [factor] mean?" | The concept name (value, quality, momentum, defensive, tactical, overall, factor_weighting, scoring) | Present the methodology explanation directly |
| "Why did the score change?" | The factor that moved | Follow with `get_score_analysis` to show the trajectory and inflection points |

For notably high or low scores (top/bottom quartile — strong or weak per the ranges above), proactively call `explain_methodology` to provide context. The API may return scores on a 0-10 or 0-100 scale; apply the same relative thresholds.

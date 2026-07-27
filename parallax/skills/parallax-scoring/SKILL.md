---
name: parallax-scoring
description: How to interpret Parallax factor scores (0-10 per security) and explain scoring methodology to users.
---

# Parallax Scoring

Five factors, each **0-10**, peer-relative within the stock's sector:

| Factor | Measures |
|---|---|
| **Quality** | Financial strength and earnings durability |
| **Value** | Price relative to fundamentals |
| **Momentum** | Trend direction and persistence |
| **Defensive** | Downside and drawdown characteristics |
| **Tactical** | Short-term positioning signal |

**Overall** = composite of the five factors. For the public methodology description, route users to `explain_methodology` (concept: "overall" or "factor_weighting") — do not characterize the composition beyond what it returns.

**Scale note:** the authoritative per-security scale is 0-10 (all thresholds in this plugin — health flags, investor profiles — are 0-10 values). Some portfolio-aggregate surfaces render 0-100 (score × 10); if a payload is unambiguously 0-100, divide by 10 before applying any threshold.

**Ranges (0-10):** 7.5-10 strong / 6.0-7.4 constructive / 4.0-5.9 neutral / 2.5-3.9 cautious / 0-2.4 weak

**Common patterns:**
- High Quality + Low Value → quality at a price; wait for catalyst
- High Momentum + Low Defensive → growth play; higher beta, works in risk-on
- High Defensive + Low Momentum → shelter stock; underperforms rallies, protects drawdowns
- High Value + Low Quality → value trap risk; check earnings quality first

## Explaining Scores

Call `explain_methodology` (free, instant) for three question types:

| User asks | `explain_methodology` parameter | Then |
|---|---|---|
| "Why does X score this way?" | The specific factor name (e.g., "quality") | Follow with `get_score_analysis` (server-default window) for trend context |
| "What does [factor] mean?" | The concept name (value, quality, momentum, defensive, tactical, overall, factor_weighting, scoring) | Present the methodology explanation directly |
| "Why did the score change?" | The factor that moved | Follow with `get_score_analysis` to show the trajectory and inflection points |

Valid concepts are only the eight listed above — `explain_methodology` does not cover shariah/halal or other screens.

**Proactive trigger (numeric):** for any factor score ≥8 or ≤3, call `explain_methodology` for that factor unprompted and weave the explanation into the output.

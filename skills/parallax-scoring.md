---
name: parallax-scoring
description: |
  Explains Parallax's multi-factor scoring system and how to interpret scores in investment context.

  Use when: presenting scores to users, explaining signals, contextualizing what a score means for a given stock or ETF.
---

# Parallax Scoring System

## The Five Factors

Parallax scores every stock and ETF on five factors, each 0-100:

| Factor | What it measures |
|---|---|
| **Quality** | Earnings quality, balance sheet strength, return on capital |
| **Value** | Price relative to fundamentals — earnings, book, cash flow |
| **Momentum** | Price and earnings trend — direction and persistence |
| **Defensive** | Volatility, beta, drawdown characteristics |
| **Tactical** | Short-term signal combining technicals and sentiment |

The **Overall score** is a weighted composite. Weighting varies by market regime — defensive weight increases in risk-off environments.

## Score Interpretation

| Range | Signal |
|---|---|
| 75-100 | Strong — high conviction signal |
| 60-74 | Constructive — favorable but not extreme |
| 40-59 | Neutral — no clear edge |
| 25-39 | Cautious — some headwinds |
| 0-24 | Weak — significant concerns |

## Common Patterns

**High Quality + Low Value** → Quality at a price. Good business, may be expensive. Watch for catalyst before entry.

**High Momentum + Low Defensive** → Growth/momentum play. Higher beta. Works in risk-on environments.

**High Defensive + Low Momentum** → Shelter stock. Likely underperforms in rallies but protects in drawdowns.

**High Value + Low Quality** → Value trap risk. Cheap for a reason. Look at earnings quality before acting.

**Balanced across all** → Core holding profile. Steady compounder.

## How to use `explain_methodology`
Call `explain_methodology` with a concept name (value, quality, momentum, defensive, tactical, scoring, factor_weighting) for detailed definitions. Pass a score number for contextualised interpretation.

## Peer Ranking
Scores are peer-relative, not absolute. A Quality score of 72 means the stock is in roughly the top 28% of its peer group — not that it has a 72% quality rating in any absolute sense.

Always read scores in the context of the peer group. A 65 in a high-quality sector (consumer staples) is more meaningful than a 65 in a low-quality sector.

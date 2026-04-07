---
name: health-flags
description: Five-flag portfolio health system, priority matrix, and drill-down selection rules — used by portfolio and rebalance commands.
---

# Portfolio Health Flags

## The 5 Flags

| Flag | Condition | Source | Threshold |
|---|---|---|---|
| **Low Score** | Portfolio overall score is weak | `quick_portfolio_scores` | Overall <= 5.0 |
| **Concentration** | Single holding too large or top-3 dominate | Holdings weights | Any single >15% OR top-3 >45% |
| **Redundancy** | Multiple overlapping positions | `check_portfolio_redundancy` | >= 2 redundant pairs |
| **Value Trap** | Portfolio value score is low | `quick_portfolio_scores` | Portfolio value score <= 3.0 |
| **Macro Misalignment** | Overweight in unfavourable sectors | `macro_analyst` tactical | Sector weight vs tactical outlook |

## Health Status

| Status | Flag Count | Frame |
|---|---|---|
| **Healthy** | 0 flags | "Your portfolio looks solid." |
| **Monitor** | 1-2 flags | "A couple of items to keep an eye on." |
| **Attention** | 3+ flags | "Some areas need a closer look." |

## Priority Matrix

Priority determined by flag overlap on a single holding:

| Priority | Condition | Typical Actions |
|---|---|---|
| **High** | 3+ flags on one holding | Trim, Exit, Reweight |
| **Medium** | 2 flags on one holding | Investigate, Trim |
| **Low** | 1 flag only | Monitor, Hold |

## Action Types

| Action | When to Use |
|---|---|
| **Trim** | Concentration + other flags — reduce weight below threshold |
| **Exit** | 3+ flags + deteriorating score trend — full sell |
| **Hold** | Stable/improving scores, no flags |
| **Investigate** | 2 flags but ambiguous signal — suggest `/parallax:deep-dive` |
| **Reweight** | Concentration without other flags — adjust allocation |

Every recommendation must cite a **specific flag or data finding**. No generic advice.

## Drill-Down Selection

**Select holdings for detail if any of:** weight >10%, flagged by any health flag, in a macro-misaligned sector.

**Cap at 8 holdings.** Prioritize by: (1) flag count descending, (2) weight descending.

**Per-holding drill-down tools:**

| Tool | Parameters | Purpose |
|---|---|---|
| `get_score_analysis` | weeks=26 | Trend — improving or deteriorating? |
| `get_stock_outlook` | aspect="risk_return" | Risk profile vs peers |
| `get_peer_snapshot` | — | Current scores + peer context |

**News (selective):** Call `get_news_synthesis` only for holdings with weight >10% AND flagged, OR in a sector with active macro developments. Cap at 5. News is async — don't block.

## Mixed-Exchange Fallback

When `quick_portfolio_scores` covers <50% of holdings by weight:

1. Split holdings by exchange suffix (`.O`/`.N` = US, `.L` = UK, etc.).
2. Score each exchange group separately.
3. Merge into portfolio-weighted result.
4. Note: "Scoring used split-and-merge due to partial coverage."

If coverage remains <50% after split-and-merge: report available scores but flag "Scoring coverage is limited — health flags may not reflect the full portfolio."

## Coverage Reliability

- **Redundancy <60%:** Flag as "Low confidence — limited coverage."
- **Unscored holdings:** List explicitly.

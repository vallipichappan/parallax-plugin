---
name: health-flags
description: Five-flag portfolio health system, priority matrix, verdict sensitivity, and drill-down selection rules — used by portfolio and rebalance commands.
---

# Portfolio Health Flags

## The 5 Flags (portfolio level)

These conditions are computed on portfolio-weighted aggregates. They are the canon for `/parallax:portfolio` checkup mode. If any holding is ⚠ MISMATCH, compute the Low Score and Value Trap aggregates client-side as a weighted average over scored equity holdings only, excluding ETF legs (they carry no factor score) and any ⚠ MISMATCH holding, weights renormalized. The server aggregate still includes the mismatched holding.

| Flag | Condition | Source | Threshold |
|---|---|---|---|
| **Low Score** | Portfolio overall score is weak | `quick_portfolio_scores` | Overall <= 5.0 |
| **Concentration** | Single holding too large or top-3 dominate | Holdings weights | Any single >15% OR top-3 >45% |
| **Redundancy** | Multiple overlapping positions | `check_portfolio_redundancy` | >= 2 redundant pairs |
| **Value Trap** | Portfolio value score is low | `quick_portfolio_scores` | Portfolio value score <= 3.0 |
| **Macro Misalignment** | Overweight in unfavourable sectors | `macro_analyst` tactical | Sector weight vs tactical outlook (qualitative) |

**Holding-level conditions** (used by advisor mode and `/parallax:rebalance` for per-position classification) apply the score thresholds to the individual holding's scores and the concentration threshold to that holding's weight. State which level a flag was computed at — do not apply one undifferentiated table to both.

**Threshold calibration scope:** the 15%/45% concentration cutoffs are calibrated for concentrated advisor/retail books. When the book exceeds ~30 holdings, state in the output that these thresholds rarely trigger at institutional diversification levels.

## Health Status

| Status | Flag Count | Frame |
|---|---|---|
| **Healthy** | 0 flags | "Your portfolio looks solid." |
| **Monitor** | 1-2 flags | "A couple of items to keep an eye on." |
| **Attention** | 3+ flags | "Some areas need a closer look." |

## Verdict Sensitivity

After rendering the health status, add one line naming how close the verdict sits to a boundary: for each of the four numeric flags (Low Score, Concentration, Value Trap, Redundancy), compute distance to threshold and name any flag within ~10% of flipping (e.g., "Concentration sits at 14.2% vs the 15% cutoff — one rally away from flagging"). Macro Misalignment is qualitative and excluded. If a value sits exactly on a threshold, say so explicitly.

## Priority Matrix

Priority determined by flag overlap on a single holding:

| Priority | Condition | Typical Classifications |
|---|---|---|
| **High** | 3+ flags on one holding | Exit, Trim |
| **Medium** | 2 flags on one holding | Investigate, Trim |
| **Low** | 1 flag only | Reweight (concentration flag), Investigate (any other flag) |
| **None** | 0 flags | Hold |

## Classification Types

Render any table using these labels with the §12 advice-boundary framing from the conventions skill: a one-line informational preface ("The classifications below are analytical threshold results, not instructions"), descriptive rationale verbs, and the `action_labels=plain` neutral mapping on request.

| Classification | Threshold logic |
|---|---|
| **Trim** | Concentration + other flags, or 3+ flags without a measured deteriorating trend |
| **Exit** | 3+ flags + deteriorating score trend |
| **Hold** | No flags. Note a deteriorating score trend if present |
| **Investigate** | 1-2 flags, none of them concentration — suggest `/parallax:deep-dive` |
| **Reweight** | Concentration without other flags |

Apply the first row that matches, in this order: Exit, Trim, Reweight, Investigate, Hold. Every holding gets exactly one classification.

When a holding has no usable `get_score_analysis` result (not called, failed, or returned no trend; for example, outside the top/bottom 5 analyzed in a large book), Exit cannot be evaluated. Classify a 3+ flag holding as Trim and note "trend not measured — Exit not evaluated."

Every classification must cite a **specific flag or data finding**. No generic advice.

## Drill-Down Selection

**Select holdings for detail if any of:** weight >10%, flagged by any health flag, in a macro-misaligned sector.

**Cap at 8 holdings.** Prioritize by: (1) flag count descending, (2) weight descending.

**Per-holding drill-down tools:**

| Tool | Parameters | Purpose |
|---|---|---|
| `get_score_analysis` | server defaults | Trend — improving or deteriorating? |
| `get_stock_outlook` | aspect="risk_return" | Risk profile vs peers |
| `get_peer_snapshot` | — | Current scores + peer context. Cross-validate per the conventions skill; on mismatch move the holding to ⚠ MISMATCH |

**News (selective):** Call `get_news_synthesis` only for holdings with weight >10% AND flagged, OR in a sector with active macro developments. Cap at 5. News is async: the server waits up to 150s; never re-call it, and render the async-jobs label if it returns no result.

## Scoring Fallback Ladder

1. **Batch path (default):** `quick_portfolio_scores` with per-row `company_name` cross-checks per the conventions skill — mismatched holdings are excluded from aggregates and listed in a ⚠ MISMATCH table. This is the default per the token-costs skill.
2. **Mixed-exchange split** — when batch coverage is <50% of holdings by weight:
   1. Split holdings by exchange suffix (`.O`/`.N` = US, `.L` = UK, etc.).
   2. Score each exchange group separately.
   3. Merge into portfolio-weighted result.
   4. Note: "Scoring used split-and-merge due to partial coverage."
3. **Per-holding path** — only if the batch path fails entirely: individual `get_peer_snapshot` + `get_company_info` cross-validation per holding, with the same ⚠ MISMATCH exclusion. This step returns no trend data; trend still comes from `get_score_analysis`.

If coverage remains <50% after split-and-merge: report available scores but flag "Scoring coverage is limited — health flags may not reflect the full portfolio."

## Coverage Reliability

- **Redundancy <60%:** Flag as "Low confidence — limited coverage."
- **Unscored holdings:** List explicitly.

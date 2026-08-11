---
description: Specialized screening — Shariah compliance (halal) or forensic earnings quality analysis
argument-hint: "[halal or quality] [ticker or portfolio holdings]"
---

# Screen

Two modes. Detect from the first argument or user intent:
- **Halal** — first arg is "halal", or user mentions Islamic, Shariah, AAOIFI, or compliance screening
- **Quality** — first arg is "quality" or "forensic", or user mentions accruals, earnings quality, manipulation, or revenue recognition

If neither mode is clear, ask: "Would you like a Shariah compliance screen or an earnings quality analysis?"

Resolve symbols via `search_stocks` (free) per the conventions skill.

---

## Halal Mode

### AAOIFI / DJIM Thresholds

| Ratio | Threshold | Pass condition |
|---|---|---|
| Total debt / Total assets | < 33% | Low leverage |
| (Cash + interest-bearing securities) / Total assets | < 33% | Limited interest exposure |
| (Interest income + non-permissible revenue) / Total revenue | < 5% | Negligible haram income |

### Single Stock Workflow

1. `get_company_info` — check sector against prohibited industries (conventional banking/insurance, alcohol, tobacco, gambling, pork, weapons, adult entertainment). **Short-circuit:** if the business-activity screen FAILs, mark non-compliant and skip the financial calls entirely — the ratios cannot cure a prohibited industry.
2. If activity screen passes, in parallel: `get_financials` (statement="balance_sheet") + `get_financials` (statement="ratios"). Compute the 3 ratios above. **FAIL if any threshold breached.**
3. If >0% but <5% non-permissible revenue: compute purification ratio (non-permissible / total income).
4. Optional: `get_financial_analysis` for deeper profitability decomposition (async ~2-5 min — warn user, poll per async-jobs skill).
5. `get_score_analysis` for quality trajectory. Note: `explain_methodology` does not cover shariah/halal concepts — do not route there.

### Portfolio Mode

1. Run single-stock check for each holding. **Cap at 20 holdings** (top by weight, plus any the user names); list skipped holdings in a coverage note.
2. `check_portfolio_redundancy` on compliant holdings only — apply the redundancy sanity-check only at N≥8 (below that, single-sector concentration is a natural screening outcome, not a tool defect).
3. For non-compliant: `build_stock_universe` by sector for alternatives → screen alternatives → `get_peer_snapshot` on compliant ones (drop any candidate failing cross-validation per the conventions skill).

### Output

- **Screening Criteria** — AAOIFI/DJIM thresholds
- **Compliance Results** — table: symbol, compliant Y/N, reason if non-compliant
- **Key Ratios** — debt/assets %, interest-bearing/assets %, non-permissible revenue %
- **Purification Amount** — if applicable
- **Alternatives** — scored compliant replacements

Render the AI-interaction disclosure per the conventions skill §9.2, then end with the standard disclaimer from the conventions skill §9.1 plus the sanctioned halal addition: *"These screening results are not a fatwa. Consult a qualified Shariah advisor for binding rulings."*

---

## Earnings Quality Mode

### Batch A — Data gathering (parallel)

| Tool | Parameters | Notes |
|---|---|---|
| `get_score_analysis` | `symbol` | Quality score trajectory (server-default 52-week window) |
| `get_financials` | `symbol`, statement="income" | Revenue/margin trends (server-default periods) |
| `get_financials` | `symbol`, statement="cash_flow" | Cash conversion |
| `get_financials` | `symbol`, statement="ratios" | Accrual ratios |
| `get_financial_analysis` | `symbol` | Async ~2-5 min — Palepu forensic. Warn user upfront; poll per async-jobs skill |
| `get_news_synthesis` | `symbol` | Async — accounting news, auditor changes |

### Batch B — AI synthesis (after A)

`get_assessment` with prompt focused on: earnings quality concerns, revenue recognition patterns, accrual anomalies, cash flow vs earnings divergence, and any specific user concerns. Feed in all Batch A findings. Poll with the async-jobs wait cap; on expiry render Batch A findings with "AI synthesis pending — service temporarily unavailable."

### Output

- **Risk Summary** — red/yellow/green traffic light. A Quality score of 10 doesn't mean no risk — dig into sub-components
- **Quality Score Trend** — 52-week trajectory with inflection points
- **Forensic Findings** — accruals, revenue quality, cash conversion
- **Red Flags** — specific items warranting investigation
- **News Context** — accounting-related developments
- **AI Assessment** — synthesized risk opinion
- **Monitoring Notes** — what to monitor, what to investigate (informational framing per the conventions skill §12)

Render the AI-interaction disclosure per the conventions skill §9.2 immediately above the disclaimer, then the standard disclaimer verbatim from the conventions skill §9.1.

## Render discipline

Apply the Render Discipline section of the conventions skill: suppress step scaffolding, hoist every integrity surface (⚠ MISMATCH rows, degraded-coverage notes, "Data unavailable" / "Analysis pending" markers) into the final output, and close with the §9.2 disclosure immediately above the §9.1 disclaimer.

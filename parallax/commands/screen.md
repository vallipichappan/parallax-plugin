---
description: Specialized screening — Shariah compliance (halal) or forensic earnings quality analysis
argument-hint: "[halal or quality] [ticker or portfolio holdings]"
---

# Screen

Two modes. Detect from the first argument or user intent:
- **Halal** — first arg is "halal", or user mentions Islamic, Shariah, AAOIFI, or compliance screening
- **Quality** — first arg is "quality" or "forensic", or user mentions accruals, earnings quality, manipulation, or revenue recognition

If neither mode is clear, ask: "Would you like a Shariah compliance screen or an earnings quality analysis?"

---

## Halal Mode

### AAOIFI / DJIM Thresholds

| Ratio | Threshold | Pass condition |
|---|---|---|
| Total debt / Total assets | < 33% | Low leverage |
| (Cash + interest-bearing securities) / Total assets | < 33% | Limited interest exposure |
| (Interest income + non-permissible revenue) / Total revenue | < 5% | Negligible haram income |

### Single Stock Workflow

1. `get_company_info` — check sector against prohibited industries (conventional banking/insurance, alcohol, tobacco, gambling, pork, weapons, adult entertainment).
2. In parallel: `get_financials` (statement="balance_sheet") + `get_financials` (statement="ratios"). Compute the 3 ratios above. **FAIL if any threshold breached.**
3. If >0% but <5% non-permissible revenue: compute purification ratio (non-permissible / total income).
4. Optional: `get_financial_analysis` for deeper profitability decomposition (async ~2-5 min — warn user).
5. `get_score_analysis` for quality trajectory.

### Portfolio Mode

1. Run single-stock check for each holding.
2. `check_portfolio_redundancy` on compliant holdings only.
3. For non-compliant: `build_stock_universe` by sector for alternatives → screen alternatives → `get_peer_snapshot` on compliant ones.

### Output

- **Screening Criteria** — AAOIFI/DJIM thresholds
- **Compliance Results** — table: symbol, compliant Y/N, reason if non-compliant
- **Key Ratios** — debt/assets %, interest-bearing/assets %, non-permissible revenue %
- **Purification Amount** — if applicable
- **Alternatives** — scored compliant replacements

*"These are analytical outputs based on AAOIFI/DJIM screening thresholds applied to Parallax financial data, not investment advice or a fatwa. Consult a qualified Shariah advisor for binding rulings."*

---

## Earnings Quality Mode

### Batch A — Data gathering (parallel)

| Tool | Parameters | Notes |
|---|---|---|
| `get_score_analysis` | `symbol`, weeks=52 | Quality score trajectory |
| `get_financials` | `symbol`, statement="income", periods=4 | Revenue/margin trends |
| `get_financials` | `symbol`, statement="cash_flow", periods=4 | Cash conversion |
| `get_financials` | `symbol`, statement="ratios" | Accrual ratios |
| `get_financial_analysis` | `symbol` | Async ~2-5 min — Palepu forensic. Warn user upfront |
| `get_news_synthesis` | `symbol` | Async — accounting news, auditor changes |

### Batch B — AI synthesis (after A)

`get_assessment` with prompt focused on: earnings quality concerns, revenue recognition patterns, accrual anomalies, cash flow vs earnings divergence, and any specific user concerns. Feed in all Batch A findings.

### Output

- **Risk Summary** — red/yellow/green traffic light
- **Quality Score Trend** — 52-week trajectory with inflection points
- **Forensic Findings** — accruals, revenue quality, cash conversion
- **Red Flags** — specific items warranting investigation
- **News Context** — accounting-related developments
- **AI Assessment** — synthesized risk opinion
- **Recommended Actions** — what to monitor, what to investigate

*"These are analytical outputs based on Parallax factor scores, not investment advice."*

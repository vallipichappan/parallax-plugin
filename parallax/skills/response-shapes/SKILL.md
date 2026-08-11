---
name: response-shapes
description: Valid field names and response-block contracts for Parallax tools that take a fields subset — analyze_portfolio and get_telemetry. Prevents silently-invalid field requests.
---

# Response Shapes

Two Parallax tools accept a `fields` subset to cap response size. In both, `fields` is a **direct passthrough to the API**, not a validated enum.

**This is the failure mode that matters:** an invalid field name does not raise. The call succeeds, the requested block simply never appears, and a workflow downstream reports "data unavailable" for something that was never actually asked for correctly. Nothing in the transcript looks wrong. Always take field names from the tables below rather than inferring them from a section heading or a prose description of what you want.

## `analyze_portfolio`

Required shape: `portfolio=[{date, symbol, weight}]`. There is no `holdings` parameter and no `lens` parameter.

### Valid field names

| Group | Fields |
|---|---|
| Inputs / meta | `portfolio_parameters`, `portfolio_input`, `data_quality` |
| Summary | `portfolio_summary`, `turnover_analysis` |
| Performance | `performance_metrics`, `rolling_metrics`, `drawdown_analysis`, `time_period_returns`, `monthly_returns`, `annual_returns` |
| Scores | `portfolio_scores` |
| Concentration / allocation | `concentration_metrics`, `sector_allocation`, `market_allocation`, `currency_allocation`, `latest_holdings` |
| Contribution | `company_contribution`, `sector_contribution`, `market_contribution` |
| Transactions | `transactions`, `company_info` |
| Benchmark / series | `benchmark_prices`, `daily_summary` |

Omitting `fields` returns everything — large, and the usual cause of 180K-char truncation.

### Names that do NOT exist

`performance`, `risk`, `concentration`, `factor_exposures`. These read like the right words and are not fields. `analyze_portfolio` returns **no factor-exposure block at all** — for factor data use `quick_portfolio_scores` or per-holding `get_peer_snapshot`, and see the `token-costs` skill for which path to prefer.

### Standard subsets

| Need | Pass |
|---|---|
| Returns and risk | `["portfolio_summary","performance_metrics","rolling_metrics","drawdown_analysis"]` |
| Concentration and sector mix | `["concentration_metrics","sector_allocation","company_contribution"]` |
| Cheapest useful call | `["portfolio_summary"]` |

## `get_telemetry`

Default field set is ~60KB; `baskets` (~652KB) and `factor_view` sub-blocks (up to ~1.1MB) are opt-in and should never be requested speculatively.

| Group | Fields |
|---|---|
| Default set | `regime_tag`, `raw_tape`, `metadata`, `signals`, `markets`, `commentary`, `divergences` |
| Large opt-in | `baskets`, `factor_view` |
| `commentary` sub-fields | `commentary.headline`, `commentary.mechanism`, `commentary.paragraphs`, `commentary.narrative_text`, `commentary.market_notes`, `commentary.model`, `commentary.generated_at`, `commentary.compliance_violations` |
| `factor_view` sub-fields | `factor_view.factors`, `factor_view.commentary`, `factor_view.split_methods`, `factor_view.portfolios`, `factor_view.timeseries`, `factor_view.correlations` |

Dot notation is supported and preferred — request `commentary.headline`, not the whole `commentary` block.

**Standard subset** used across `/parallax:macro`, `/parallax:scenario`, and `/parallax:explain`:
`["regime_tag","signals","commentary.headline","commentary.mechanism","divergences"]`

## Semantic guards

1. **`get_telemetry` returns inline.** Despite an async-looking tool description, a scoped call returns a result directly with no `job_id` and no polling. Verified 2026-08-11. It is not in the async set — see the `async-jobs` skill.
2. **Telemetry is market/basket-level, never per-security.** Do not attach a telemetry-derived confidence tag to an individual holding row; it describes the tape, not the name.
3. **A block that is absent is not a block that is zero.** If a requested field does not appear in the response, treat it as unavailable and say so — never render it as null, zero, or "no concentration risk."
4. **Field subsets do not change semantics.** Requesting fewer fields never re-scopes a computation; `performance_metrics` covers the same period whether or not you also asked for `drawdown_analysis`.

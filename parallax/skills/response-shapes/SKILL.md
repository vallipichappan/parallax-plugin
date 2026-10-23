---
name: response-shapes
description: Valid field names and response-block contracts for Parallax tools that take a fields subset — analyze_portfolio and get_telemetry. Prevents invalid field requests.
---

# Response Shapes

Two Parallax tools accept a `fields` subset to cap response size.

**`analyze_portfolio`'s `fields` is a validated enum, not a passthrough.** An invalid name fails the tool call outright with a schema error — it does not silently drop the block and return `success: true`. Always take field names from the table below rather than inferring them from a section heading or a prose description of what you want.

**`analyze_portfolio` wraps its payload in `result`.** The direct reply is `{success, result: {...}}`: the requested blocks and `_meta` both sit under `result`, so read `result._meta` and `result.<block>`. If the call returned a "still running" reply and you fetch the job with `check_job_status`, that reply wraps the same object once more: read `result.result._meta` and `result.result.<block>`. `_meta` carries `fields_requested`, `fields_returned` and `invalid_fields`. It is present on every call through this MCP server, because the server always sends a field list (the compact default when `fields` is omitted). `invalid_fields` is always `null` here, because an invalid name fails the call with a schema error before it reaches the API.

## `analyze_portfolio`

Required shape: `portfolio=[{date, symbol, weight}]`. There is no `holdings` parameter and no `lens` parameter.

### Valid field names

| Group | Fields |
|---|---|
| Inputs / meta | `portfolio_parameters`, `portfolio_input`, `data_quality` |
| Summary | `portfolio_summary` |
| Performance | `performance_metrics`, `rolling_metrics`, `drawdown_analysis`, `time_period_returns`, `monthly_returns`, `annual_returns` |
| Scores | `portfolio_scores` |
| Concentration / allocation | `concentration_metrics`, `sector_allocation`, `market_allocation`, `currency_allocation`, `latest_holdings` |
| Contribution | `company_contribution`, `sector_contribution`, `market_contribution` |
| Transactions | `transactions`, `company_info` |
| Benchmark / series | `daily_summary` |

`portfolio_scores` exists and is the authoritative engine score for the portfolio, on a **0-100 scale** (the MCP's own note; per-security scores and health-flag cutoffs are 0-10) — `quick_portfolio_scores` is the per-holding approximation, not a substitute for this block. There is no separate factor-exposure field; `portfolio_scores` is where factor data lives in this tool.

Benchmark data is not a separate field: `daily_summary` rows carry `benchmark_value_base` alongside the portfolio's own daily figures.

Omitting `fields` returns a **compact default** — `portfolio_summary`, `performance_metrics`, `portfolio_scores`, `concentration_metrics`, `data_quality` — not everything. Request the full field list explicitly if more is needed, and watch for the 180K-char truncation risk when doing so.

### Names that do NOT exist

`performance`, `risk`, `concentration`, `factor_exposures`. These read like the right words and are not valid fields — a call naming one of them, or any name outside the allowed list above, now fails with a schema error rather than silently omitting the block.

### Standard subsets

| Need | Pass |
|---|---|
| Returns and risk | `["portfolio_summary","performance_metrics","rolling_metrics","drawdown_analysis"]` |
| Concentration and sector mix | `["concentration_metrics","sector_allocation","company_contribution"]` |
| Cheapest useful call | `["portfolio_summary"]` |

## `get_telemetry`

`get_telemetry`'s `fields` is a passthrough, not an enum: an invalid name is silently dropped, not rejected. Use only the names below.

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

1. **`get_telemetry` returns inline.** A scoped call normally returns a result directly with no `job_id` (on its rare 120s timeout it returns a "still running" reply with a `job_id`; handle it per the async-jobs skill and do not re-call), even though the server waits on it internally for up to 120s (see the `async-jobs` skill). Verified 2026-08-11.
2. **Telemetry is market/basket-level, never per-security.** Do not attach a telemetry-derived confidence tag to an individual holding row; it describes the tape, not the name.
3. **A block that is absent is not a block that is zero.** If a requested field does not appear in the response, treat it as unavailable and say so — never render it as null, zero, or "no concentration risk."
4. **Field subsets do not change semantics.** Requesting fewer fields never re-scopes a computation; `performance_metrics` covers the same period whether or not you also asked for `drawdown_analysis`.

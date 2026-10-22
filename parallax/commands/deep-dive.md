---
description: Deep fundamental and technical analysis — parallel data calls, macro context, AI assessment
argument-hint: "[ticker or company name] [optional question/thesis]"
---

# Deep Dive

Resolve the symbol via `search_stocks` (free) per the conventions skill first.

## Batch A — Fire all instant data calls in parallel

| Tool | Parameters | Notes |
|---|---|---|
| `get_company_info` | `symbol` | Sector, market cap, description |
| `get_peer_snapshot` | `symbol` | Factor scores + peer ranking |
| `get_financials` | `symbol`, statement="summary" | Revenue/income narrative |
| `get_financials` | `symbol`, statement="ratios" | Margins, ROE, P/E (server-default periods) |
| `get_score_analysis` | `symbol` | Factor trend (server-default 52-week window) |
| `get_stock_outlook` | `symbol`, aspect="analyst_targets" | Price targets |
| `get_stock_outlook` | `symbol`, aspect="recommendations" | Buy/hold/sell |
| `get_stock_outlook` | `symbol`, aspect="risk_return" | Risk/return vs peers |
| `get_stock_outlook` | `symbol`, aspect="dividends" | Dividend history (server-default depth) |

**Cross-validation gate (non-bypassable):** check `get_peer_snapshot`'s top-level `target_company` against `get_company_info.data.name`. On mismatch, refuse to render — show both names and ask the user to confirm the intended company.

## Batch B — Macro context (start after the cross-validation gate passes)

Start Batch B only after the gate above passes. On a mismatch, Batch B never fires, so no macro, technical, news or report credits are spent on a refused output.

1. `list_macro_countries` to check coverage.
2. Identify relevant markets (home + revenue geographies + commodity/supply chain). Cap at 3.
3. `macro_analyst` with component="tactical" per relevant covered market.

Batch B also issues two async data calls. Issue them in the same parallel message as the `macro_analyst` calls. If the macro section is skipped (no covered market), issue them on their own right after `list_macro_countries`; the macro skip rule never skips them.

| Tool | Parameters | Notes |
|---|---|---|
| `get_technical_analysis` | `symbol` | Trend, RSI, MACD, support/resistance |
| `get_news_synthesis` | `symbol` | Catalysts and news context |

Both are async: the server waits for each job and returns the result in the same call (up to 120s and 150s). Never re-call one; on a "still running" or failed reply, follow the async-jobs skill. They are kept out of Batch A because a parallel batch returns only when its slowest call returns.

## Batch C — AI Assessment (after A + B)

`get_assessment` with a comprehensive prompt incorporating: factor scores, 52-week score trends, key ratios, technical stance, macro context, dividend profile, risk/return vs peers, and the user's specific question/thesis if provided. Async — server waits for the result; on a "still running" reply follow the async-jobs skill; never re-call. If it does not return a result, render the label per the async-jobs skill ("Analysis pending" with the `job_id` if still running; "Analysis unavailable" if it failed) and continue.

Apply fallback rules from conventions skill for any missing data.

## Full Mode

For deeper due diligence, add to Batch A: `get_financials` for income, balance_sheet and cash_flow (ratios is already in Batch A). Add `get_stock_report` (async, up to ~5 min server-side, 10 credits) to the Batch B message with the other async calls, never to Batch A. Warn about cost and wait time. **Scope note:** Full Mode output is an internal analyst working document, not designed for client forwarding — say so in the output header.

## Output

- **Company Overview** — 3 sentences
- **Macro Environment** — regime context, factor implications
- **Factor Profile** — table: each factor score with peer rank + 52-week trend direction
- **Financial Highlights** — key ratios, trends
- **Dividend Profile** — yield, payout, consistency (or "Not a dividend payer")
- **Risk/Return Profile** — volatility, Sharpe context vs peers
- **Technical Stance** — trend, key levels, momentum
- **News Catalyst Watch** — material items only
- **Assessment** — AI synthesis including macro + trends
- **Risk Factors** — what could go wrong

Render the AI-interaction disclosure per the conventions skill §9.2 immediately above the disclaimer, then the standard disclaimer verbatim from the conventions skill §9.1.

## Render discipline

Apply the Render Discipline section of the conventions skill: suppress step scaffolding, hoist every integrity surface (⚠ MISMATCH rows, degraded-coverage notes, "Data unavailable" / "Analysis pending" markers) into the final output, and close with the §9.2 disclosure immediately above the §9.1 disclaimer.

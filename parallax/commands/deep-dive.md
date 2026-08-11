---
description: Deep fundamental and technical analysis — 11 parallel calls, macro context, AI assessment
argument-hint: "[ticker or company name] [optional question/thesis]"
---

# Deep Dive

Resolve the symbol via `search_stocks` (free) per the conventions skill first.

## Batch A — Fire all data calls in parallel

| Tool | Parameters | Notes |
|---|---|---|
| `get_company_info` | `symbol` | Sector, market cap, description |
| `get_peer_snapshot` | `symbol` | Factor scores + peer ranking |
| `get_financials` | `symbol`, statement="summary" | Revenue/income narrative |
| `get_financials` | `symbol`, statement="ratios" | Margins, ROE, P/E (server-default periods) |
| `get_score_analysis` | `symbol` | Factor trend (server-default 52-week window) |
| `get_technical_analysis` | `symbol` | Async ~15-30s — trend, RSI, MACD, support/resistance |
| `get_stock_outlook` | `symbol`, aspect="analyst_targets" | Price targets |
| `get_stock_outlook` | `symbol`, aspect="recommendations" | Buy/hold/sell |
| `get_stock_outlook` | `symbol`, aspect="risk_return" | Risk/return vs peers |
| `get_stock_outlook` | `symbol`, aspect="dividends" | Dividend history (server-default depth) |
| `get_news_synthesis` | `symbol` | Async — don't block output |

For `get_technical_analysis`: poll `check_job_status` per the async-jobs skill. Do NOT retry the original tool call on timeout.

**Cross-validation gate (non-bypassable):** check `get_peer_snapshot`'s top-level `target_company` against `get_company_info.name`. On mismatch, refuse to render — show both names and ask the user to confirm the intended company.

## Batch B — Macro context (after A)

1. `list_macro_countries` to check coverage.
2. Identify relevant markets (home + revenue geographies + commodity/supply chain). Cap at 3.
3. `macro_analyst` with component="tactical" per relevant covered market.

## Batch C — AI Assessment (after A + B)

`get_assessment` with a comprehensive prompt incorporating: factor scores, 52-week score trends, key ratios, technical stance, macro context, dividend profile, risk/return vs peers, and the user's specific question/thesis if provided. Poll per the async-jobs skill with the wait cap; on expiry render "Assessment pending — service temporarily unavailable" and continue.

Apply fallback rules from conventions skill for any missing data.

## Full Mode

For deeper due diligence, add to Batch A: `get_financials` for income, balance_sheet, cash_flow, ratios (4 statements) + `get_stock_report` (~2 min async, 10 tokens). Warn about cost and wait time. **Scope note:** Full Mode output is an internal analyst working document, not designed for client forwarding — say so in the output header.

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

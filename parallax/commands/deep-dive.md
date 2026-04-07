---
description: Deep fundamental and technical analysis — 11 parallel calls, macro context, AI assessment
argument-hint: "[ticker or company name] [optional question/thesis]"
---

# Deep Dive

## Batch A — Fire all data calls in parallel

| Tool | Parameters | Notes |
|---|---|---|
| `get_company_info` | `symbol` | Sector, market cap, description |
| `get_peer_snapshot` | `symbol` | Factor scores + peer ranking |
| `get_financials` | `symbol`, statement="summary" | Revenue/income narrative |
| `get_financials` | `symbol`, statement="ratios", periods=1 | Margins, ROE, P/E |
| `get_score_analysis` | `symbol`, weeks=52 | 52-week factor trend |
| `get_technical_analysis` | `symbol` | Async ~15-30s — trend, RSI, MACD, support/resistance |
| `get_stock_outlook` | `symbol`, aspect="analyst_targets" | Price targets |
| `get_stock_outlook` | `symbol`, aspect="recommendations" | Buy/hold/sell |
| `get_stock_outlook` | `symbol`, aspect="risk_return" | Risk/return vs peers |
| `get_stock_outlook` | `symbol`, aspect="dividends", limit=8 | Dividend history |
| `get_news_synthesis` | `symbol` | Async — don't block output |

For `get_technical_analysis`: poll `check_job_status` every 15s until completed. Do NOT retry the original tool call on timeout.

## Batch B — Macro context (after A)

1. `list_macro_countries` to check coverage.
2. Identify relevant markets (home + revenue geographies + commodity/supply chain). Cap at 3.
3. `macro_analyst` with component="tactical" per relevant covered market.

## Batch C — AI Assessment (after A + B)

`get_assessment` with a comprehensive prompt incorporating: factor scores, 52-week score trends, key ratios, technical stance, macro context, dividend profile, risk/return vs peers, and the user's specific question/thesis if provided.

Apply fallback rules from conventions skill for any missing data.

## Full Mode

For deeper due diligence, add to Batch A: `get_financials` for income, balance_sheet, cash_flow, ratios (4 statements) + `get_stock_report` (~2 min async, 10 tokens). Warn about cost and wait time.

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

*"These are analytical outputs based on Parallax factor scores, not investment advice."*

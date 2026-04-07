---
name: conventions
description: RIC resolution, parallel execution, fallback rules, and disclaimer — applies to all Parallax commands.
---

# Parallax Conventions

## RIC Resolution

Stocks require Reuters Instrument Codes (RICs). When the user provides a plain ticker:

1. Call `get_company_info` with the plain ticker — it often resolves automatically.
2. If empty, retry with the most likely exchange suffix:

| Exchange | Suffix | Example | Clues |
|---|---|---|---|
| NASDAQ | `.O` | `AAPL.O` | US tech, biotech |
| NYSE | `.N` | `JPM.N` | US financials, industrials |
| London | `.L` | `SHEL.L` | UK companies |
| Frankfurt | `.DE` | `SAP.DE` | German companies |
| Paris | `.PA` | `MC.PA` | French companies |
| Tokyo | `.T` | `7203.T` | 4-digit numeric |
| Hong Kong | `.HK` | `0700.HK` | 4-digit numeric, China/HK context |
| Taiwan | `.TW` | `2330.TW` | 4-digit numeric, Taiwan context |
| Sydney | `.AX` | `BHP.AX` | Australian companies |
| Oslo | `.OL` | `YAR.OL` | Norwegian companies |
| Korea | `.KS` | `005930.KS` | 6-digit numeric |

**Ambiguous tickers:** Try `.O` then `.N` first (US most common). Numeric codes: 4 digits → `.T` / `.HK` / `.TW` by context; 6 digits → `.KS`.

Only escalate to the user after 2 failed suffix attempts.

**Peer symbols:** Symbols from `get_peer_snapshot` may lack suffixes. Resolve before passing downstream.

## Cross-Validation

After any scoring call, cross-check the company name against `get_company_info`. Field mapping: `get_peer_snapshot` returns `target_company` at top level (NOT `company` on peer rows — those refer to each peer). `quick_portfolio_scores` returns `company_name` per holding row. If names diverge, warn the user and treat `get_company_info` as truth. Extra caution for `.HK`, `.T`, `.TW`, `.KS` codes.

For portfolio scoring: cross-check each holding's name. If any maps to the wrong company, re-score individually via `get_peer_snapshot`.

## Parallel Execution

Default to parallel where dependencies allow:

- **Independent (fire together):** `get_company_info`, `get_peer_snapshot`, `get_financials`, `get_score_analysis`, `get_stock_outlook` (all aspects), `get_news_synthesis`, `quick_portfolio_scores`, `check_portfolio_redundancy`
- **Dependent (wait for prior results):** `get_assessment` (needs all findings), `macro_analyst` (needs `list_macro_countries` + company info), `build_stock_universe` (needs analysis of what to replace)

## Fallback Rules

**Instant tools** (`get_company_info`, `get_peer_snapshot`, `get_financials`, etc.) — retry once on failure. Second failure → "Data unavailable", continue.

**Async tools** (`get_news_synthesis`, `get_assessment`, `get_technical_analysis`, `get_financial_analysis`, `get_stock_report`) — do not retry. Failure → "Analysis pending — service temporarily unavailable", continue.

**Stock outlook coverage:** 4 aspects (analyst_targets, recommendations, risk_return, dividends). 2+ return data → proceed. 0-1 → flag "Insight card may be materially incomplete."

**Portfolio scoring coverage:** If `quick_portfolio_scores` covers <50% of holdings by weight → execute mixed-exchange fallback per health-flags skill. If total fail → individual `get_peer_snapshot` per holding (no trend data). If `check_portfolio_redundancy` covers <60% → flag as "Low confidence — limited coverage."

**Concentration caveat:** For <7 holdings, concentration flags (>15% single, >45% top-3) are structural. Note but don't alarm.

**`analyze_portfolio` truncation:** Responses may exceed 180K chars. If truncated, fall back to `check_portfolio_redundancy` + `quick_portfolio_scores`.

**Empty output:** If a tool returns successfully but with no content, treat as failure and retry once.

## News Handling

`get_news_synthesis` is async (30-90s) and should never block output. Fire in parallel, assemble output from instant tools, insert news when ready or mark "pending."

## Macro Context

For single-stock or portfolio analysis, determine relevant markets from RIC suffixes:

1. Call `list_macro_countries` for coverage.
2. Identify relevant markets (home market + revenue geographies + commodity/supply chain).
3. Call `macro_analyst` with component="tactical" per market.
4. Cap at 2 markets (single stock) or 3 markets (portfolio).

If `list_macro_countries` fails, derive from RIC suffixes: `.O`/`.N` = US, `.T` = Japan, `.HK` = Hong Kong, `.L` = UK, `.DE` = Germany.

## Disclaimer

Every output must end with:

*"This is informational analysis based on Parallax factor scores, not investment advice. All outputs should be reviewed by qualified professionals before any investment decisions."*

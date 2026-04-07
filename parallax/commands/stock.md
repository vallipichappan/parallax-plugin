---
description: Full research brief on a stock — scores, peers, financials, macro context, news, analyst outlook, with parallel batching
argument-hint: "[ticker or company name]"
---

# Stock Research

## Step 1 — Resolve Ticker

Call `get_company_info` with plain ticker or RIC. If empty, retry with exchange suffixes per conventions skill. For `.HK`/numeric codes, apply cross-validation.

## Step 2 — Parallel Data Batch

Fire all simultaneously once RIC is confirmed:

| Tool | Parameters | Notes |
|---|---|---|
| `get_peer_snapshot` | `symbol` | Factor scores + peer ranking |
| `get_financials` | `symbol`, statement="summary" | Revenue/income narrative |
| `get_score_analysis` | `symbol`, weeks=52 | 52-week factor trend |
| `get_stock_outlook` | `symbol`, aspect="analyst_targets" | Price targets |
| `get_stock_outlook` | `symbol`, aspect="recommendations" | Buy/hold/sell |
| `get_stock_outlook` | `symbol`, aspect="risk_return" | Risk/return vs peers |
| `get_stock_outlook` | `symbol`, aspect="dividends", limit=8 | Dividend history |
| `get_news_synthesis` | `symbol` | Async — don't block output |

## Step 3 — Macro Context

After Step 1 resolves (need company info for market reasoning):

1. `list_macro_countries` to check coverage.
2. Identify relevant markets (home market + key revenue geography). Cap at 2.
3. `macro_analyst` with component="tactical" per covered market.

Skip macro section if no relevant covered markets.

## Step 4 — Interpret

- Call `explain_methodology` for any notably high or low factor score (top/bottom quartile per parallax-scoring skill) — it's free.
- Synthesize all data. Apply fallback rules from conventions skill for missing data.
- Cross-validate company name from scoring vs `get_company_info`.

## Output

- **The Company** — what they do, how big
- **The Scores** — table with plain-English interpretation + 52-week trend direction (e.g., "Quality trending up from 5.8 to 7.2")
- **Financial Health** — green/yellow/red traffic light
- **Macro Context** — 2-3 sentences on relevant economic environment
- **Dividends** — yield, consistency, recent changes (or "Not a dividend payer")
- **Risk vs Peers** — risk/return profile relative to peer group
- **Recent News** — bullets
- **Analyst View** — price target range, consensus
- **Bottom Line** — balanced 2-sentence summary (pros and cons, not a recommendation)

*"This is informational analysis based on Parallax factor scores, not investment advice. All outputs should be reviewed by qualified professionals before any investment decisions."*

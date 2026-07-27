---
description: Full research brief on a stock — scores, technicals, peers, financials, macro context, news, analyst outlook, with parallel batching
argument-hint: "[ticker or company name]"
---

# Stock Research

## Step 1 — Resolve Ticker

Call `search_stocks` (free) with the ticker or company name; fall back to `get_company_info` + suffix table per the conventions skill. For `.HK`/numeric codes, apply cross-validation. If the symbol is an ETF (per the asset-class-routing skill), route to `/parallax:etf` instead.

## Step 2 — Parallel Data Batch

Fire all simultaneously once RIC is confirmed:

| Tool | Parameters | Notes |
|---|---|---|
| `get_peer_snapshot` | `symbol` | Factor scores + peer ranking |
| `get_financials` | `symbol`, statement="summary" | Revenue/income narrative |
| `get_score_analysis` | `symbol` | Factor trend (server-default 52-week window) |
| `get_technical_analysis` | `symbol` | Async — poll per async-jobs skill, do NOT retry |
| `get_stock_outlook` | `symbol`, aspect="analyst_targets" | Price targets |
| `get_stock_outlook` | `symbol`, aspect="recommendations" | Buy/hold/sell |
| `get_stock_outlook` | `symbol`, aspect="risk_return" | Risk/return vs peers |
| `get_stock_outlook` | `symbol`, aspect="dividends" | Dividend history (server-default depth) |
| `get_news_synthesis` | `symbol` | Async — don't block output |

**Cross-validation gate (non-bypassable):** check `get_peer_snapshot`'s top-level `target_company` against `get_company_info.name`. On mismatch, refuse to render the verdict — show both names and ask the user to confirm the intended company.

## Step 3 — Macro Context

After Step 1 resolves (need company info for market reasoning):

1. `list_macro_countries` to check coverage.
2. Identify relevant markets (home market + key revenue geography). Cap at 3.
3. `macro_analyst` with component="tactical" per covered market.

Skip macro section if no relevant covered markets.

## Step 4 — Interpret (two lenses)

Analyze through two independent lenses that must not borrow each other's evidence:

- **Fundamentals lens** — factor scores, financials, peers, dividends. Call `explain_methodology` for any factor score ≥8 or ≤3 (it's free).
- **Technicals lens** — price/trend/momentum from `get_technical_analysis` only; it does not borrow factor scores or financials as evidence. **Fallback:** if technicals time out, render the lens from the Momentum factor sub-trend prefixed "Technical analysis unavailable — Momentum factor proxy:" — the lens always produces a read; it never silently disappears.

Apply fallback rules from the conventions skill for missing data.

## Output

- **The Company** — what they do, how big
- **Fundamentals** — score table with plain-English interpretation + 52-week trend direction (e.g., "Quality trending up from 5.8 to 7.2"); financial health traffic light
- **Technicals** — trend, momentum, key levels (or the Momentum-proxy fallback)
- **Macro Context** — 2-3 sentences on relevant economic environment
- **Dividends** — yield, consistency, recent changes (or "Not a dividend payer")
- **Risk vs Peers** — risk/return profile relative to peer group
- **Recent News** — bullets
- **Analyst View** — price target range, consensus; state the source verbatim as "third-party analyst consensus via Parallax's data provider"
- **Bottom Line** — balanced 2-sentence summary. When the two lenses diverge, name the divergence explicitly — never average it into a blended take. Not a recommendation.

Render the AI-interaction disclosure per the conventions skill §9.2 immediately above the disclaimer, then the standard disclaimer verbatim from the conventions skill §9.1.

---
description: Full research brief on a stock — scores, technicals, peers, financials, macro context, news, analyst outlook, with parallel batching
argument-hint: "[ticker or company name]"
---

# Stock Research

## Step 1 — Resolve Ticker

Call `search_stocks` (free) with the ticker or company name; fall back to `get_company_info` + suffix table per the conventions skill. For `.HK`/numeric codes, apply cross-validation. If the symbol is an ETF (per the asset-class-routing skill), route to `/parallax:etf` instead.

## Step 2 — Parallel Data Batch

Fire all instant calls simultaneously once RIC is confirmed:

| Tool | Parameters | Notes |
|---|---|---|
| `get_company_info` | `symbol` | Ground-truth name, sector, and market context |
| `get_peer_snapshot` | `symbol` | Factor scores + peer ranking |
| `get_financials` | `symbol`, statement="summary" | Revenue/income narrative |
| `get_score_analysis` | `symbol` | Factor trend (server-default 52-week window) |
| `get_stock_outlook` | `symbol`, aspect="analyst_targets" | Price targets |
| `get_stock_outlook` | `symbol`, aspect="recommendations" | Buy/hold/sell |
| `get_stock_outlook` | `symbol`, aspect="risk_return" | Risk/return vs peers |
| `get_stock_outlook` | `symbol`, aspect="dividends" | Dividend history (server-default depth) |

**Cross-validation gate (non-bypassable):** check `get_peer_snapshot`'s top-level `target_company` against `get_company_info.data.name`. On mismatch, refuse to render the verdict — show both names and ask the user to confirm the intended company.

## Step 3 — Macro Context

After the cross-validation gate passes (need company info for market reasoning). On a mismatch, Step 3 never fires, so no macro, technical or news credits are spent on a refused verdict. If the gate cannot run because `get_peer_snapshot` is unavailable after its retry, Step 3 does not fire either; render "Technicals and news not run — identity could not be confirmed" in their sections.

Two async data calls also belong to this step. Issue them in the same parallel message as the `macro_analyst` calls. If the macro section is skipped (no covered market), issue them on their own right after `list_macro_countries`; the macro skip rule never skips them.

| Tool | Parameters | Notes |
|---|---|---|
| `get_technical_analysis` | `symbol` | Trend, momentum, support/resistance |
| `get_news_synthesis` | `symbol` | Catalysts and news context |

Both are async: the server waits for each job and returns the result in the same call (up to 120s and 150s). Never re-call one; on a "still running" or failed reply, follow the async-jobs skill. They are kept out of Step 2 because a parallel batch returns only when its slowest call returns.


1. `list_macro_countries` to check coverage.
2. Identify relevant markets (home market + key revenue geography). Cap at 3.
3. `macro_analyst` with component="tactical" per covered market.

Skip macro section if no relevant covered markets.

## Step 4 — Interpret (two lenses)

Analyze through two independent lenses that must not borrow each other's evidence:

- **Fundamentals lens** — factor scores, financials, peers, dividends. Call `explain_methodology` for any factor score ≥8 or ≤3 (it's free).
- **Technicals lens** — price/trend/momentum from `get_technical_analysis` only; it does not borrow factor scores or financials as evidence. **Fallback:** if technicals return no result, render the lens from the Momentum factor sub-trend, prefixed with the label per the async-jobs skill ("Analysis pending" with the `job_id` if still running; "Analysis unavailable" if it failed), then "— Momentum factor proxy:" — the lens always produces a read; it never silently disappears.

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

## Render discipline

Apply the Render Discipline section of the conventions skill: suppress step scaffolding, hoist every integrity surface (⚠ MISMATCH rows, degraded-coverage notes, "Data unavailable" / "Analysis pending" markers) into the final output, and close with the §9.2 disclosure immediately above the §9.1 disclaimer.

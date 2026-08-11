---
description: Drawdown attribution — decompose a portfolio loss into market/regime, factor, and stock-specific layers, then classify it as transient or fundamental via score-vs-price divergence
argument-hint: "[holdings with weights, e.g. AAPL 30%, MSFT 40%, SPY 30%] [optional: \"down 4% this month\"]"
---

# Explain Portfolio

Reactive performance attribution — the "why am I down?" workflow. Parse holdings into `{symbol, weight}` pairs; equal-weight if no weights given. The optional second argument is the user's stated concern, used to anchor the lookback and to validate against computed returns.

**Not this command:** proactive health check → `/parallax:portfolio`. Trade recommendations → `/parallax:rebalance`. Hypotheticals → `/parallax:scenario`. Single stock → `/parallax:stock`.

Resolve every symbol with `search_stocks` first; fall back to the conventions skill suffix table. Never pass numeric parameters (`weeks`, `periods`, `limit`, `days`) explicitly — the transport serializes them as strings and validation fails. Rely on server defaults and slice to the inferred window client-side.

## Step 1 — Measure actual performance

Infer the lookback from the user's statement ("this month" → ~21 trading days, "this week" → 5, "this quarter" → ~63). Default to 21 days if ambiguous.

### Step 1a — Asset-class pre-classification (parallel, MANDATORY)

`export_price_series` is equity-only; ETFs fail-empty on it and would otherwise be dropped from attribution — a high-impact bias. Before any price pull, classify each holding per the asset-class-routing skill:

- Call `etf_profile` on each holding, **one symbol per call**, in parallel.
- `{"error": "No profile data found", ...}` → **equity** → route through `export_price_series`.
- Non-error profile → **ETF** → route through `etf_daily_price`.

This adds N calls at 1 token each (one per holding).

### Step 1b — Pull price history (parallel, split by asset class)

Fire all of the following in a single tool-call turn:

- Each EQUITY holding → `export_price_series` with the RIC (FREE). Use close prices.
- Each ETF holding → `etf_daily_price` with the plain ticker. Returns per-row `date` + `changepercent`. 1 token.

### Step 1c — Compute attribution + halt rule

Compute per-holding close-to-close return over the period, weighted contribution (return × weight), total portfolio return, and rank holdings by contribution (biggest detractors first).

**Halt rule — no silent drops.** If a holding returns empty/error from BOTH `etf_profile` and its routed price endpoint, render this banner *above* the attribution table:

> ⚠ Cannot compute return for `<symbol>` — neither `export_price_series` nor `etf_daily_price` returned data. This holding is **not** included in the attribution below; the reported portfolio return is computed on the remaining `<X>%` of weight. Operator decision required: supply prices externally, or remove it from the portfolio for this analysis.

Never silently zero or skip a holding. Compare the computed return against the user's stated figure; note any divergence >1%.

## Step 2 — Layer 1: Market and regime (parallel)

| Tool | Parameters | Purpose |
|---|---|---|
| `get_telemetry` | fields: regime_tag, signals, commentary.headline, commentary.mechanism, divergences | Is the whole market down? |
| `list_macro_countries` | — | Coverage for home markets |
| `get_peer_snapshot` | per holding | Primary scoring source; aggregate client-side |
| `get_company_info` | per holding | Ground-truth name oracle |

**Cross-validation (non-bypassable).** After `get_peer_snapshot`, compare the top-level `target_company` against `get_company_info.name` — peer rows carry their own `name` and refer to each peer, not the target. On mismatch: exclude that holding from all aggregates, mark it ⚠ MISMATCH in the attribution table, and never render its scores.

Then call `macro_analyst` with component="tactical" per home market (cap 3). This establishes whether the loss is market-wide, sector rotation, or idiosyncratic.

## Step 3 — Layer 2: Factor and thematic

Call `get_score_analysis` per holding in parallel (no explicit `weeks` — server default). This is the primary factor source. Determine: which factor scores moved most; whether the moves are correlated across holdings (correlated → systematic/thematic, uncorrelated → stock-specific); whether the portfolio is tilted into a factor that is out of favor for the current regime. Cross-reference `get_telemetry` divergences against the portfolio's exposure.

## Step 4 — Layer 3: Stock-specific

For the **top 3 detractors** by weighted contribution, in parallel: `get_news_synthesis` and `get_peer_snapshot` (cross-validate as in Step 2).

`get_news_synthesis` is async — never retry it, poll `check_job_status` per the async-jobs skill, and never let it block the rest of the output. Overlap it with the macro reasoning and the price/score computations, and assemble those sections immediately. On wait-cap expiry, render "Analysis pending — service temporarily unavailable" inside Top Detractors.

**A "Transient" verdict must not be finalized before the detractor's news resolves** (or its absence is confirmed). Step 5's provisional flag keys on whether a major event broke after the last score data point, which only the news reveals — calling "Transient — hold or add" on a freshly-adverse detractor is the exact failure that flag exists to prevent. If news is still pending, mark the affected divergence rows provisional-pending-news.

## Step 5 — Score-vs-price divergence (the key insight)

For each holding compare the price change from Step 1 (daily, current) against the score change from Step 3 (weekly — **may lag by up to ~7 days**).

If a major event (earnings miss, indictment, regulatory action) occurred after the last score data point, scores may not yet reflect it. The classification still applies but must be flagged **provisional** for those holdings.

| Price | Scores | Interpretation | Advice |
|---|---|---|---|
| Down | Stable/Up | **Transient** — market mispricing, fundamentals intact | Hold or add |
| Down | Down | **Fundamental** — deterioration confirmed by scores | Investigate, consider trim |
| Down | Mixed | **Ambiguous** — some factors deteriorating, others stable | Monitor, dig deeper |

Portfolio-level verdict: majority of weighted holdings "Transient" → the drawdown is likely noise. Majority "Fundamental" → it reflects real deterioration.

## Step 6 — Conditional advice

- **Transient:** fundamentals unchanged — cite the actual Quality/Defensive scores, name the driver (risk-off / factor rotation / sector selloff), reference the macro tactical outlook for reversal context.
- **Fundamental:** name the holdings with deteriorating scores; for each suggest deeper analysis (`/parallax:deep-dive`), trim, or replacement. If the factor tilt is the problem, suggest rebalancing toward favored factors per the macro tactical outlook.
- **Mixed:** separate transient holdings (hold) from fundamental ones (investigate), prioritized by weighted contribution to the loss.

## Render

Begin the response immediately with the rendered report — no preamble. Degraded-state notes render inside the affected section (they must survive into the output, but this command places them in context rather than hoisting them to the top).

## Output Format

- **What Happened** — computed portfolio return over the period vs the user's stated figure; one sentence on loss magnitude
- **Performance Attribution** — table: holding, return, weighted contribution, primary driver tag (Market / Factor / Stock-Specific); ⚠ MISMATCH rows marked and excluded from aggregates; MISSING holdings named per the Step 1c banner
- **Market & Regime Context** — regime tag, mechanism, 2-3 sentences; is the broad market down too?
- **Factor Exposure** — which tilts helped or hurt, and their connection to the current regime
- **Top Detractors** — for each of the top 3: what happened, why, and whether scores agree with the price move
- **The Key Question: Noise or Signal?** — portfolio-level verdict plus the per-holding divergence table (provisional rows flagged)
- **What To Do** — conditional advice per Step 6

Keep the tone calm and explanatory. The user is worried — reduce anxiety with clarity, not jargon.

Render the AI-interaction disclosure per the conventions skill §9.2 immediately above the disclaimer, then the standard disclaimer verbatim from the conventions skill §9.1.

## Render discipline

Apply the Render Discipline section of the conventions skill, with the section-local placement noted under Render above.

---
description: Build a scored portfolio from a natural language investment thesis
argument-hint: "[investment theme, e.g. 'profitable AI infrastructure companies']"
---

# Universe Builder

**Macro-theme banner:** if the theme string contains a macro term (rates, inflation, recession, tariff, yield curve, currency, USD, dollar, credit spread, GDP, monetary policy, fiscal, Fed, central bank, regime, cycle) AND no sector word, render a banner suggesting `/parallax:macro` is likely the better tool — then proceed anyway.

## Step 1 — Build Universe

`build_stock_universe` with the user's thesis as query (searches 65K+ company descriptions; the tool takes `query`, not `description`).

**Empty-universe gate (required first check):** if the universe comes back empty, skip Steps 2-6 entirely — report the empty result and suggest a narrower/reworded query. Never call holdings-requiring tools with no holdings.

**Timeout fallback:** on timeout, retry once with a narrower query; if still failing, continue with `universe = []` and flag it — do not substitute `check_portfolio_redundancy` or any other tool as a placeholder.

**Divergence assertion:** if the query named 2+ sectors but >60% of results collapse into a single sector, fail loud: "universe collapsed to single sector despite multi-sector request."

## Step 2 — Score Top Picks

For top N results (default 10): call `get_peer_snapshot` and `get_company_info` for each in parallel. Cross-validate per the conventions skill and drop mismatched candidates from the pool.

## Step 3 — Rank & Select

Re-rank candidates by total score (universe tool ranks by relevance, not quality). Select top 5-8 for the portfolio.

## Step 4 — Redundancy Check

`check_portfolio_redundancy` on proposed equal-weight allocation. Identify sector concentration and industry overlap.

**Sanity-check (N≥8 only):** if >60% of weight sits in one sector but the tool returns empty `sector_concentration` and "well-diversified", its detection has silently failed — compute concentration client-side from the holdings and flag the tool discrepancy in the output.

## Step 5 — Optimize Weights

Adjust weights based on scores, redundancy flags, and sector balance. Call `quick_portfolio_scores` on final allocation to verify factor profile.

## Step 6 — Validate (conditional)

`analyze_portfolio` with `portfolio=[{date, symbol, weight}]` and `fields=["portfolio_summary","performance_metrics","drawdown_analysis","concentration_metrics","sector_allocation"]` on the final allocation to confirm it behaves as intended. No `holdings` or `lens` parameters exist. Check `result._meta.invalid_fields`; any entry is a caller error. If the response is truncated (>180K chars), rely on Step 4-5 outputs — and disclose the fallback scope: rolling metrics, drawdown, contribution attribution, and performance time series are NOT validated on that path.


**Universe reproducibility:** any candidate list here comes from `build_stock_universe`, which is not reproducible run-to-run — set membership varies, not just ordering. Tell the user the candidate set is a point-in-time sample, per the conventions skill's Universe Search Reproducibility section.

## Output

- **Investment Thesis** — restate and refine the user's intent
- **Universe Built** — how many candidates, key sectors
- **Selected Holdings** — informational preface per the conventions skill §12, then table: symbol, name, sector, total score, weight, key factor strengths
- **Portfolio Factor Profile** — VALUE, QUALITY, MOMENTUM, DEFENSIVE scores
- **Redundancy Notes** — any overlap flagged and how resolved (including any client-side sanity-check discrepancy)
- **Implementation Notes** — liquidity and sizing caveats (not validated against ADV/borrow), suggested review frequency

Tip: specific queries return better results. "Profitable cloud infrastructure US" beats "tech".

After presenting results, ask: "Would you like me to run a portfolio health check on these holdings?" If yes, pass the final allocation to `/parallax:portfolio`.

Render the AI-interaction disclosure per the conventions skill §9.2 immediately above the disclaimer, then the standard disclaimer verbatim from the conventions skill §9.1.

## Render discipline

Apply the Render Discipline section of the conventions skill: suppress step scaffolding, hoist every integrity surface (⚠ MISMATCH rows, degraded-coverage notes, "Data unavailable" / "Analysis pending" markers) into the final output, and close with the §9.2 disclosure immediately above the §9.1 disclaimer.

---
description: Event-driven portfolio exposure analysis — what's at risk, what shifts, what to do
argument-hint: "[event description] portfolio=[ticker weight, ...]"
---

# Scenario Analysis

Something happened (or might happen). What's exposed? What shifts? What do I do?

Both a scenario description and a portfolio are required — prompt for either if missing.

## Phase 1 — Understand the Event (parallel)

| Tool | Parameters | Notes |
|---|---|---|
| `get_news_synthesis` | 2-3 most affected sectors | What the market already knows. Async — never blocks |
| `get_telemetry` | fields: regime_tag, signals, commentary.headline, commentary.mechanism, divergences | Synchronous — always pass `fields` to cap response size (full response is 60KB+) |
| `macro_analyst` | relevant markets, component="tactical" | Positioning implications |
| `build_stock_universe` | theme describing scenario beneficiaries | Hoisted here — the beneficiary theme derives from the scenario text alone and needs no portfolio data |

## Phase 2a — Classify + ground-truth (after Phase 1)

Gate before any scoring: classify each holding per the asset-class-routing skill (`etf_profile` as oracle) and cross-validate names per the conventions skill — **factor scores are equity-only**; firing `get_score_analysis` at ETFs silently returns nothing. Mismatched holdings go to a ⚠ MISMATCH table and are excluded from everything downstream.

## Phase 2b — Assess Portfolio Exposure (after 2a)

In parallel:
- `analyze_portfolio` with `portfolio=[{date, symbol, weight}]`, `fields=["concentration_metrics","sector_allocation","company_contribution"]` — sector exposures (no `holdings`/`lens` params exist; there is no `factor_exposures` field — do not pass one). `fields` is a passthrough, so invalid names fail silently; use only names from the `response-shapes` skill. May exceed 180K chars; fall back to `check_portfolio_redundancy` if truncated.
- `get_score_analysis` for each **equity** holding (server-default window) — current trajectories. **Fan-out cap:** at >20 holdings, cover top-20 by weight plus any flagged; list skipped symbols in a degraded-coverage note.

Then: `get_assessment` with prompt describing the scenario, listing each holding with sector/factor profile, asking: "Rank these holdings from most-exposed to least-exposed. For each, explain the transmission mechanism (direct revenue, supply chain, regulatory, sentiment)." Exclude ⚠ MISMATCH holdings from the prompt — mismatched holdings with empty profiles produce hallucinated factor profiles in the assessor's output. Poll per the async-jobs skill; wait cap applies.

## Phase 3 — Rotation Candidates (after Phase 2b)

1. From the Phase 1 `build_stock_universe` results: `get_peer_snapshot` for top 5 candidates (parallel), cross-validated — drop mismatches from the pool.
2. `get_financials` (statement="summary") for top 2-3 to verify fundamentals.

## Phase 4 — Action Plan (after Phase 3)

`get_assessment` with comprehensive prompt incorporating: scenario + transmission mechanisms, macro regime, portfolio exposure ranking, replacement candidates. Ask for exposure-reduction classifications prioritized by urgency and magnitude. Poll with wait cap; if it expires, render the Phase 2b assessment findings with "Action-plan synthesis pending — service temporarily unavailable."

## Output

- **Scenario Summary** — what happened, why it matters
- **Macro Regime Impact** — how this shifts the regime, which factors affected
- **Exposure Heat Map** — table: each holding, exposure High/Medium/Low, transmission mechanism
- **⚠ MISMATCH / Skipped Holdings** — if any
- **Most Exposed** — 2-3 holdings at greatest risk with reasoning
- **Least Affected** — safe positions, brief explanation
- **Sector Rotation Thesis** — what benefits from this scenario
- **Replacement Candidates** — table: symbol, name, sector, total score, why it fits
- **Exposure Classifications** — informational preface per the conventions skill §12, then prioritized threshold results (descriptive verbs, each citing a finding)
- **What to Watch** — 2-3 confirming/invalidating signals
- **Confidence & Caveats** — uncertainty level, rotation risks

Render the AI-interaction disclosure per the conventions skill §9.2, then end with the standard disclaimer from the conventions skill §9.1 plus the sanctioned scenario addition: *"Scenario outputs are hypothetical, forward-looking assessments and are inherently uncertain."*

## Render discipline

Apply the Render Discipline section of the conventions skill: suppress step scaffolding, hoist every integrity surface (⚠ MISMATCH rows, degraded-coverage notes, "Data unavailable" / "Analysis pending" markers) into the final output, and close with the §9.2 disclosure immediately above the §9.1 disclaimer.

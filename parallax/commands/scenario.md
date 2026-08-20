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

Gate before any trend scoring:

1. Classify each holding with `etf_profile` per the asset-class-routing skill.
2. For each equity, call `get_company_info` and `get_peer_snapshot` in parallel.
3. Cross-validate `get_peer_snapshot.target_company` against `get_company_info.data.name` per the conventions skill.
4. Put mismatches in a ⚠ MISMATCH table and exclude them from every downstream factor or assessment input.

Factor scores are equity-only. Do not call `get_score_analysis` for an ETF.

## Phase 2b — Assess Portfolio Exposure (after 2a)

In parallel:
- `analyze_portfolio` with `portfolio=[{date, symbol, weight}]`, `fields=["concentration_metrics","sector_allocation","company_contribution"]` — sector exposures (no `holdings`/`lens` params exist; there is no `factor_exposures` field — do not pass one). `fields` is a passthrough, so an invalid name is not rejected — check `result._meta.invalid_fields` after the call and treat any entry as a caller error. Use only names from the `response-shapes` skill. May exceed 180K chars; fall back to `check_portfolio_redundancy` if truncated.
- `get_score_analysis` for each **equity** holding (server-default window) — current trajectories. **Fan-out cap:** at >20 holdings, cover top-20 by weight plus any flagged; list skipped symbols in a degraded-coverage note.

Rank holdings deterministically from sector exposure, weighted concentration, score direction, and the scenario's stated transmission channels. This provisional ranking feeds the final assessment after candidate validation.

## Phase 3 — Rotation Candidates (after Phase 2b)

1. From the Phase 1 `build_stock_universe` results: call `get_peer_snapshot` and `get_company_info` for the top 5 candidates in parallel. Drop name mismatches from the pool.
2. `get_financials` (statement="summary") for top 2-3 to verify fundamentals.

## Phase 4 — Action Plan (after Phase 3)

Call `get_assessment` once with the scenario, transmission mechanisms, macro regime, deterministic exposure ranking, and validated candidates. Ask for exposure-reduction classifications prioritized by urgency and magnitude. Exclude ⚠ MISMATCH holdings. Poll with the wait cap; if it expires, render the deterministic Phase 2b findings with "Action-plan synthesis pending — service temporarily unavailable."


**Universe reproducibility:** any candidate list here comes from `build_stock_universe`, which is not reproducible run-to-run — set membership varies, not just ordering. Tell the user the candidate set is a point-in-time sample, per the conventions skill's Universe Search Reproducibility section.

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

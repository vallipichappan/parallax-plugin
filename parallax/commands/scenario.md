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
| `get_news_synthesis` | 2-3 most affected sectors | What the market already knows |
| `get_telemetry` | fields: regime_tag, signals, commentary.headline, commentary.mechanism, divergences | Synchronous — always pass `fields` to cap response size (full response is 60KB+) |
| `macro_analyst` | relevant countries/regions, component="tactical" | Positioning implications |

## Phase 2 — Assess Portfolio Exposure (after Phase 1)

In parallel:
- `analyze_portfolio` with holdings, lens="concentration" — sector/factor exposures. May exceed 180K chars; fall back to `check_portfolio_redundancy` if truncated.
- `get_score_analysis` for each holding, 4-8 weeks — current trajectories.

Then: `get_assessment` with prompt describing the scenario, listing each holding with sector/factor profile, asking: "Rank these holdings from most-exposed to least-exposed. For each, explain the transmission mechanism (direct revenue, supply chain, regulatory, sentiment)."

## Phase 3 — Rotation Candidates (after Phase 2)

1. `build_stock_universe` with a theme describing scenario beneficiaries.
2. `get_peer_snapshot` for top 5 candidates (parallel).
3. `get_financials` (statement="summary") for top 2-3 to verify fundamentals.

## Phase 4 — Action Plan (after Phase 3)

`get_assessment` with comprehensive prompt incorporating: scenario + transmission mechanisms, macro regime, portfolio exposure ranking, replacement candidates. Ask for specific portfolio adjustments prioritized by urgency and magnitude.

## Output

- **Scenario Summary** — what happened, why it matters
- **Macro Regime Impact** — how this shifts the regime, which factors affected
- **Exposure Heat Map** — table: each holding, exposure High/Medium/Low, transmission mechanism
- **Most Exposed** — 2-3 holdings at greatest risk with reasoning
- **Least Affected** — safe positions, brief explanation
- **Sector Rotation Thesis** — what benefits from this scenario
- **Replacement Candidates** — table: symbol, name, sector, total score, why it fits
- **Action Plan** — prioritized: what to trim/sell/add/hold with weight suggestions
- **What to Watch** — 2-3 confirming/invalidating signals
- **Confidence & Caveats** — uncertainty level, rotation risks

*"This is scenario-based analysis, not investment advice. Forward-looking assessments are inherently uncertain."*

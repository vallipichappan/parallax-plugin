---
description: Macro outlook for any country — regime, indicators, sectors, rates, FX, equity opportunities
argument-hint: "[country or market name, or 'compare US Japan Europe']"
---

# Macro Outlook

**Market normalization:** call `list_macro_countries` first and match the user's input against the covered market names (case-sensitive). Coverage is **17 markets** as of 2026-08-11 — Brazil, Canada, China, France, Germany, Global, India, Indonesia, Japan, Malaysia, Singapore, South Korea, Taiwan, Thailand, United Kingdom, United States, Vietnam. Treat the live call as authoritative; the list here is for sanity-checking, not for skipping the call. Regions ("Europe", "Asia") are not markets — expand to the covered member markets and say so. Note `Global` is a market in its own right, not a region. If a requested market is genuinely absent from the live response, state "Parallax macro coverage does not include [X]" and list the covered set — never guess, and never refuse on the basis of a remembered count.

## Batch A — Coverage + telemetry (parallel)

| Tool | Parameters | Notes |
|---|---|---|
| `list_macro_countries` | — | Confirm coverage |
| `check_macro_health` | — | Data freshness |
| `get_telemetry` | fields: regime_tag, signals, commentary.headline, commentary.mechanism, divergences | Synchronous — always pass `fields` to cap response size (full response is 60KB+) |

## Batch B — Macro depth (after A)

Call `macro_analyst` for the target country **without** a `component` parameter (summary mode). The summary call returns all 9 components inline (macro_indicators, tactical, fixed_income, currency, sectors, sector_positioning, liquidity, news, factors) — same 5 tokens as a single-component call.

Use summary mode here because the macro command needs the full picture. Other commands (stock, portfolio, rebalance, scenario) use component="tactical" to signal they only need the tactical slice.

**Multi-country comparison:** If the user says "compare US, Japan, Europe" — call `macro_analyst` for each country in parallel.

**Equity opportunities** (if user asks, or default for country deep dives): call `build_stock_universe` with "[country] equities".

## Batch C — Score top picks (conditional, after B)

If equity screening was done:
1. Call `get_peer_snapshot` and `get_company_info` for the top 5 universe results in parallel. Cross-validate per the conventions skill and drop mismatches. Rankings cover listed equities with Parallax factor coverage only — funds/OEICs are not screened.
2. `get_score_analysis` for top 3 (parallel, server-default window).


**Universe reproducibility:** any candidate list here comes from `build_stock_universe`, which is not reproducible run-to-run — set membership varies, not just ordering. Tell the user the candidate set is a point-in-time sample, per the conventions skill's Universe Search Reproducibility section.

## Output

- **Regime Status** — current regime tag + signals
- **Macro Summary** — indicators, rates, FX, sectors, tactical
- **Factor Regime Interaction** — which factors favored/disfavored in current regime
- **Positioning Implications** — sector tilts, risk posture
- **Tactical Bias** — short-term signal
- **Data Freshness** — from `check_macro_health`
- **Top Equity Opportunities** (if screened) — informational preface per the conventions skill §12, then table: symbol, name, sector, total score, key strengths
- **Score Trends** (if screened) — improving vs declining picks

Render the AI-interaction disclosure per the conventions skill §9.2 immediately above the disclaimer, then the standard disclaimer verbatim from the conventions skill §9.1.

## Render discipline

Apply the Render Discipline section of the conventions skill: suppress step scaffolding, hoist every integrity surface (⚠ MISMATCH rows, degraded-coverage notes, "Data unavailable" / "Analysis pending" markers) into the final output, and close with the §9.2 disclosure immediately above the §9.1 disclaimer.

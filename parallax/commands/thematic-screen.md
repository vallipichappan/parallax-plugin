---
description: Thematic idea screen — rank stock ideas from a theme with scores, macro context, and peer/financial context
argument-hint: "[theme, e.g. 'energy transition' or 'gene therapy pure plays']"
---

# Thematic Screen

This produces a ranked idea list, not a weighted or validated portfolio — no weights, redundancy check, or portfolio validation are run here. For that, use `/parallax:universe`.

**Macro-theme banner:** if the theme string contains a macro term (rates, inflation, recession, tariff, yield curve, currency, USD, dollar, credit spread, GDP, monetary policy, fiscal, Fed, central bank, regime, cycle) AND no sector word, render a banner suggesting `/parallax:macro` is likely the better tool — then proceed anyway. Macro context in Step 3 below still runs regardless of which branch fired, since it is derived from the resolved candidates, not from the theme string.

Candidates are listed equities with Parallax factor coverage; funds/OEICs are out of coverage per the conventions skill.

## Step 1 — Build Universe

`build_stock_universe` with the user's theme as query (searches 65K+ company descriptions; the tool takes `query`, not `description`).

**Empty-universe gate (required first check):** if the universe comes back empty, skip Steps 2, 4, and 5, and skip the market-selection half of Step 3 — report the empty result and suggest a narrower/reworded query. Never call downstream tools with no candidates. (Step 3's `list_macro_countries` and telemetry calls fire in parallel with this step regardless, per Step 3 below; on an empty universe their results are simply unused.)

**Timeout fallback:** on timeout, retry once with a narrower query; if still failing, continue with `universe = []` and flag it — do not substitute an unrelated aggregate tool as a placeholder.

**Divergence assertion:** if the query named 2+ sectors but >60% of results collapse into a single sector, fail loud: "universe collapsed to single sector despite multi-sector request."

## Step 2 — Score Candidates

For top N results (default 5 — adjust for broader or narrower screens): call `get_peer_snapshot` and `get_company_info` for each candidate in parallel, using the candidate symbol exactly as returned by `build_stock_universe`. Reuse that same symbol for Steps 4 and 5 below — do not attempt to substitute a different identifier from either call's response.

Cross-validate per the conventions skill: check `get_peer_snapshot`'s top-level `target_company` against `get_company_info.data.name`. On a first mismatch, attempt re-resolution via `search_stocks` plus one individual `get_peer_snapshot` call; if it still mismatches, exclude the candidate from the ranking and from the score column entirely, and list it in a ⚠ MISMATCH table — never render a score from a mismatched mapping. Re-rank trusted candidates by total score (the universe tool ranks by relevance, not quality).

## Step 3 — Macro Context

**3a** (parallel with Step 1): `list_macro_countries` for coverage.

**Telemetry** (parallel with Step 1): `get_telemetry` — fields: regime_tag, signals, commentary.headline, commentary.mechanism, divergences. Basket-level only: render `regime_tag`, the top 1-3 divergence baskets with sign, and `commentary.headline`. On failure ("Admin org not configured" or otherwise), omit the Regime Signal line and continue — never abort the screen. Never derive a per-candidate confidence tag from telemetry; it has no per-name schema.

**3b** (after Step 2, since it needs resolved trusted candidates): derive each trusted candidate's market from its RIC suffix per the conventions skill's RIC Suffix → Covered Macro Market table. Select up to 3 markets: first, any market explicitly named in the theme text that verbatim-matches a name in the 3a response; then fill remaining slots by frequency among trusted candidates' derived markets, verbatim-matched against 3a. Drop anything unmatched silently — never guess a market. `macro_analyst` with `component="tactical"` per selected market, in parallel, capped at 3. If no trusted candidate resolves to a covered market and the theme named none either, skip macro context and continue — this is an expected outcome, not a failure.

Skip Step 3's market-selection and `macro_analyst` calls entirely if the user asks to skip macro context (telemetry still fires; it's a fixed-cost basket-level call, not theme- or candidate-dependent).

## Step 4 — Lead-Candidate Peer Comparison

`export_peer_comparison` on the highest-scored trusted candidate's symbol, format="json" (parallel with Step 5, both after Step 2 completes — does not wait on Step 3).

## Step 5 — Financial Snapshot

`get_financials` with statement="income" for the top 3 trusted candidates' symbols, in parallel, server-default periods (parallel with Step 4).

## Output

- **Theme** — restate the thesis; render the Macro-theme banner inline if it fired
- **Scope Note** — *"This is a ranked idea list, not a weighted or validated portfolio — no weights, redundancy check, or portfolio validation has been run."*
- **Macro Context** (if Step 3b selected any market) — one line per selected market (max 3) from `macro_analyst` tactical; a Regime Signal sub-line from telemetry if present; state explicitly that this is context and does not re-rank
- **Universe Built** — candidate count, key sectors, divergence-assertion result, any degraded-coverage note
- **Ranked Ideas** — informational preface per the conventions skill §12, then table: symbol, name, sector, total score, key factor strengths, Macro Tag. No weight column — this table never carries position sizing. ⚠ MISMATCH rows render in a separate table, carry no score, and are excluded from ranking. Macro Tag: the candidate's own derived market (Step 3b) if it was one of the ≤3 selected markets, else "—". Never infer from sector. Annotation only — never reorders or filters Ranked Ideas.
- **Peer Comparison** — matrix for the lead candidate
- **Financial Snapshot** — revenue, margin, growth trends for the top 3 trusted picks
- **Implementation Notes** — liquidity and sizing caveats (not validated against ADV/borrow), per the conventions skill §12 framing — no position sizing

Want these built into a weighted, redundancy-checked portfolio? → `/parallax:universe`. Want a full read on one name? → `/parallax:stock`.

Render the AI-interaction disclosure per the conventions skill §9.2 immediately above the disclaimer, then the standard disclaimer verbatim from the conventions skill §9.1.

## Render discipline

Apply the Render Discipline section of the conventions skill: suppress step scaffolding, hoist every integrity surface (⚠ MISMATCH rows, degraded-coverage notes, "Data unavailable" / "Analysis pending" markers) into the final output, and close with the §9.2 disclosure immediately above the §9.1 disclaimer.

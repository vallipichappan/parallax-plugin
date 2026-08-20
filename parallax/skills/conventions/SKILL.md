---
name: conventions
description: RIC resolution, parallel execution, fallback rules, advice-boundary framing, AI disclosure, and disclaimer — applies to all Parallax commands.
---

# Parallax Conventions

## RIC Resolution

Stocks require Reuters Instrument Codes (RICs). When the user provides a plain ticker:

1. Call `search_stocks` with the ticker or company name — it is free (0 tokens) and returns the RIC directly. This is the primary resolver.
2. If `search_stocks` is unavailable or ambiguous, call `get_company_info` with the plain ticker — it often resolves automatically.
3. If still empty, retry with the most likely exchange suffix:

| Exchange | Suffix | Example | Clues |
|---|---|---|---|
| NASDAQ | `.O` | `AAPL.O` | US tech, biotech |
| NYSE | `.N` | `JPM.N` | US financials, industrials |
| London | `.L` | `SHEL.L` | UK companies |
| Frankfurt | `.DE` | `SAP.DE` | German companies |
| Paris | `.PA` | `MC.PA` | French companies |
| Tokyo | `.T` | `7203.T` | 4-digit numeric |
| Hong Kong | `.HK` | `0700.HK` | 4-digit numeric, China/HK context |
| Taiwan | `.TW` | `2330.TW` | 4-digit numeric, Taiwan context |
| Sydney | `.AX` | `BHP.AX` | Australian companies |
| Oslo | `.OL` | `YAR.OL` | Norwegian companies |
| Korea | `.KS` | `005930.KS` | 6-digit numeric |
| Singapore | `.SI` | `D05.SI` | Singapore companies |

**Ambiguous tickers:** Try `.O` then `.N` first (US most common). Numeric codes: 4 digits → `.T` / `.HK` / `.TW` by context; 6 digits → `.KS`.

Only escalate to the user after `search_stocks` plus 2 failed suffix attempts.

**Funds/OEICs:** ISIN-style identifiers or names carrying Fund/OEIC/Trust/Acc/Inc markers are out of coverage. Render a plain-language note — "Parallax coverage is listed equities and ETFs; funds and OEICs are not covered" — instead of a raw resolution error.

**Peer symbols:** Symbols from `get_peer_snapshot` may lack suffixes. Resolve before passing downstream. Single-letter tickers (e.g. `F`) require the suffix — bare they error as "Symbol too short."

## Tool Parameters

Do **not** pass numeric parameters (`weeks`, `periods`, `limit`, `days`) explicitly — the transport serializes them as strings and the server rejects them. Rely on server defaults (52 weeks, 4 periods). `macro_analyst` takes `market` (not `country`); `build_stock_universe` takes `query` (not `description`).

## First-Batch Schema Race

If the **first** tool batch of a session returns empty or interrupted, treat it as an MCP schema-registration race, not missing data: re-fire the full batch once before concluding "no data." This is distinct from the per-tool empty-output retry below.

## Validation Before Reporting Done

The schema-race rule above guards the *opening* of a workflow. This one guards its *close*. Before presenting any Parallax workflow as complete:

1. **Data integrity — empty ≠ done.** Confirm the batch returned real data rather than an unresolved init race. A section that rendered because the tool returned nothing is not a finished section; it is an unreported failure.
2. **Integrity surfaces actually rendered.** Where a run produced a ⚠ MISMATCH table, a degraded-coverage note, or an "Analysis pending" marker, verify that text is present in the output you are about to send. Do not assume it rendered because the rule says it should — and never suppress one to make a workflow look clean.
3. **Flag, don't omit.** Integrity failures appear explicitly in the output. Silently dropping a failed section is the one unacceptable outcome.

A workflow that produced output is not thereby a workflow that succeeded.

## Cross-Validation

After any scoring call that returns a company name, cross-check that name against `get_company_info`. Field mapping: `get_company_info` wraps its payload in a top-level `data` key and has **no top-level `name` field**. `data` is shape-dependent on how you called it: for a **single symbol** it is an object, so the name is at `get_company_info.data.name`; for a **comma-separated batch** it is an **array**, so `data.name` is undefined and you must match each element by its `ric` before reading `.name`. Verified live 2026-08-20. **Call it one symbol at a time for cross-validation.** Batching to save calls silently breaks the identity check, which is the one check that must never fail open. `get_peer_snapshot` returns `target_company` at top level (NOT `name` on peer rows — those refer to each peer). `quick_portfolio_scores` returns `company_name` per holding row. `get_score_analysis` has no company-name field; verify `data[0].symbol` against the requested RIC and use the workflow's already-resolved company identity. Extra caution for `.HK`, `.T`, `.TW`, `.KS` codes.

**On mismatch:**
- **Single-stock verdict flows** (stock, investor, credit, deep-dive): refuse to render the verdict; show both names and ask the user to confirm the intended company.
- **Portfolio/aggregate flows**: exclude the mismatched holding from all aggregate **factor** calculations, do not display its per-position scores, and list it in a ⚠ MISMATCH integrity table. Attempt re-resolution via `search_stocks` + individual `get_peer_snapshot` once; if it still mismatches, it stays excluded.

**Exception — concentration is computed over the original holdings.** Weight concentration, sector concentration, and position-count metrics are structural properties of the book the user actually holds, not of the subset Parallax could score. Dropping a mismatched holding from the denominator understates concentration and can hide the very risk the flag exists to catch. Exclude mismatches from factor aggregates; keep them in concentration denominators, and note that a concentration figure includes positions whose scores could not be verified.

Never render scores from a mismatched mapping.

## Parallel Execution

Default to parallel where dependencies allow:

- **Independent (fire together):** `get_company_info`, `get_peer_snapshot`, `get_financials`, `get_score_analysis`, `get_stock_outlook` (all aspects), `get_news_synthesis`, `quick_portfolio_scores`, `check_portfolio_redundancy`
- **Dependent (wait for prior results):** `get_assessment` (needs all findings), `macro_analyst` (needs `list_macro_countries` + company info), `build_stock_universe` (needs analysis of what to replace)

## Fallback Rules

**Instant tools** (`get_company_info`, `get_peer_snapshot`, `get_financials`, etc.) — retry once on failure. Second failure → "Data unavailable", continue.

**Async tools** (`get_news_synthesis`, `get_assessment`, `get_technical_analysis`, `get_financial_analysis`, `get_stock_report`) — do not retry. Poll per the async-jobs skill; on failure or wait-cap expiry → "Analysis pending — service temporarily unavailable", continue. Async calls never block the rest of the output.

**Stock outlook coverage:** 4 aspects (analyst_targets, recommendations, risk_return, dividends). 2+ return data → proceed. 0-1 → flag "Insight card may be materially incomplete."

**Portfolio scoring coverage:** If `quick_portfolio_scores` covers <50% of holdings by weight → execute mixed-exchange fallback per health-flags skill. If total fail → individual `get_peer_snapshot` per holding (no trend data). If `check_portfolio_redundancy` covers <60% → flag as "Low confidence — limited coverage."

**Concentration caveat:** For <7 holdings, concentration flags (>15% single, >45% top-3) are structural. Note but don't alarm.

**`analyze_portfolio` truncation:** Responses may exceed 180K chars. If truncated, fall back to `check_portfolio_redundancy` + `quick_portfolio_scores`.

**Empty output:** If a tool returns successfully but with no content, treat as failure and retry once (except the first-batch schema race above, which re-fires the whole batch).

**Asset-class mismatches** (equity tool on an ETF or vice versa) fail empty, not loudly — route per the asset-class-routing skill before any price or scoring pull over mixed holdings.

## News Handling

`get_news_synthesis` is async (30-90s) and should never block output. Fire in parallel, assemble output from instant tools, insert news when ready or mark "pending."

## Universe Search Reproducibility

`build_stock_universe` is **not reproducible run-to-run**. Two identical calls return different orderings, different `relevance_rank` values for the same company, and — the part that matters — **different result sets**. Verified 2026-08-20: the same query returned a company at rank 3 on one call and rank 9 on the next.

Re-ranking by total score, which every universe-based command already does, fixes the *ordering* variance. It does not fix *membership* variance: the top-N cut is taken on relevance rank **before** scoring, so which candidates get scored at all changes between runs. A user who re-runs the same screen can get a different idea list, not merely a reshuffled one.

Consequences:

- Any command whose output is built on `build_stock_universe` must tell the user the result is a point-in-time sample, not a stable list. Say it where the user reads what the output is and is not.
- Never assert or imply that re-running a screen reproduces it.
- Never write a test that asserts a specific company, ordering, or `relevance_rank` from a live universe call. Such a test is flaky by construction.

### Emptiness and degradation are not what they look like

Two live-verified traps in the `build_stock_universe` response (2026-08-20):

1. **`total_matches` is not a candidate count.** A response can carry `success: true`, `status: "completed"`, `total_matches: 5`, and `results_returned: 0` with an **empty** `companies` array. **Decide emptiness from the `companies` array alone.** An empty-universe gate keyed on `total_matches` or on `success` will wave a zero-candidate result through and call downstream tools with nothing.
2. **`degraded: true` is an integrity surface and nothing currently reads it.** The response also carries `relaxed`, an array naming the screens the server loosened to return anything at all (e.g. `["strict_theme", "default_liquidity_floor"]`). When `degraded` is true, render a degraded-coverage note naming those relaxed screens, per Render Discipline. A result set assembled by dropping the user's own theme strictness is not the screen they asked for, and saying so is not optional.

This is a characteristic of the server-side search, not a defect in any command. It does not contradict the §9.1 disclaimer's "deterministic pipelines" wording, which enumerates factor scores, financials, peer mappings, technicals, and price series — universe search is not in that list.

## Macro Context

For single-stock or portfolio analysis, determine relevant markets from RIC suffixes:

1. Call `list_macro_countries` for coverage.
2. Identify relevant markets (home market + revenue geographies + commodity/supply chain).
3. Call `macro_analyst` with component="tactical" per market.
4. Cap at 3 markets (single stock or portfolio).

If `list_macro_countries` fails, derive from RIC suffixes: `.O`/`.N`/`.K` = US, `.T` = Japan, `.HK` = Hong Kong, `.L` = UK, `.DE` = Germany, `.SI` = Singapore.

### RIC Suffix → Covered Macro Market

For workflows that derive markets from a candidate set rather than a single home market (e.g. a multi-candidate screen), use this table against the RIC Resolution suffixes above. Only suffixes resolving to a currently-covered macro market are listed; verbatim-match the mapped name against the live `list_macro_countries` response before calling `macro_analyst` — never call on an unmatched name.

| Suffix | Market |
|---|---|
| `.O`, `.N`, `.K` | United States |
| `.L` | United Kingdom |
| `.DE` | Germany |
| `.PA` | France |
| `.T` | Japan |
| `.TW` | Taiwan |
| `.KS` | South Korea |
| `.SI` | Singapore |

`.HK`, `.AX`, `.OL` have no currently-covered macro market. A candidate on one of these exchanges gets no market tag — never substitute a nearby market (e.g. China for Hong Kong).

**Every suffix named anywhere in this skill appears in exactly one of the two groups above — mapped, or explicitly uncovered.** A suffix that appears in the RIC Resolution table or the fallback line but in neither group here is a drift bug: it makes a candidate on that exchange silently lose its market tag. `.SI` and `.K` were in that state until 2026-08-20.

## Render Discipline

Applies to every command unless that command overrides it.

**Suppress the scaffolding.** Steps execute silently — no `**Step N**` labels, no "Batch A complete", no "Cross-validation passed" narration, no "Let me…" preamble. Begin the response with the rendered output itself.

**Never suppress an integrity surface.** Dropping the scaffold must not drop the signal that was attached to it. These always survive into the final output, hoisted to where the reader will see them rather than left buried in a stage that got collapsed:

- ⚠ MISMATCH tables and the count of excluded holdings
- degraded-coverage notes (skipped symbols, fan-out caps, partial universe)
- "Data unavailable" and "Analysis pending" markers
- any note that a figure was computed on a reduced sample

**Terminal elements are fixed and last:** the §9.2 AI-interaction disclosure immediately above the §9.1 disclaimer, in that order, at the end of the output. Nothing renders below the disclaimer.

The failure this prevents is a clean-looking report whose cleanliness came from silently discarding the caveats. Verify per "Validation Before Reporting Done" above.

## §12 Information Framing (Advice Boundary)

Rendered classifications and candidate actions are observational statements about threshold logic — never execution instructions. A command may report that a holding crossed a published cutoff and name the classification that cutoff maps to; it may never tell the reader what to do about it.

**Forbidden:** reader-directed imperative trade verbs ("sell", "buy", "trim this", "exit this position"), first-person advice framing ("we recommend", "you should"), or "should" applied to a trade action.

**Permitted:** capitalized action-type labels (Exit, Trim, Reweight, Investigate, Hold) when the label is defined by a cited threshold table and each instance cites the specific flag that produced it — the label names a classification, not a directive.

Any section rendering an action-type table MUST carry: (1) a one-line informational preface stating the section is an analytical classification, not an instruction; (2) descriptive rationale verbs ("flags", "sits above", "diverges from") instead of imperatives. On request (`action_labels=plain`), map each label to its neutral status description: Exit → "flagged for full-position review", Trim → "flagged for partial-position review", Reweight → "flagged for allocation review", Investigate → "flagged for further review", Hold → "no threshold breach".

## §9.2 AI-Interaction Disclosure

Every output containing AI-generated narrative, synthesis, or recommendations MUST render this banner immediately above the §9.1 disclaimer:

> *AI-assisted output. Quantitative data — factor scores, financials, peer mappings, technicals, price series — is from Parallax's deterministic pipelines. Qualitative content — news synthesis, macro commentary, AI assessments, narrative framing, and recommendations — is LLM-generated, either by Parallax's MCP services (news, macro, assessment) or by the orchestrating model (narrative and recommendations). Verify any specific statement before acting.*

This satisfies the artificial-generation marking obligations of EU AI Act Art 50(1)/(2) (effective 2 August 2026) and the prominent-disclosure expectations of the SFC GenAI circular (12 Nov 2024), HKMA GenAI circulars, FCA Consumer Duty, and MAS FEAT. It is not suppressible in any render mode. Commands render it by reference to this section — do not restate the banner text in command files.

## §9.1 Disclaimer

Every output must end with (immediately after the §9.2 banner):

*"This is informational analysis based on Parallax factor scores, not investment advice. All outputs should be reviewed by qualified professionals before any investment decisions."*

Commands with sanctioned domain-specific additions (scenario: hypothetical-scenario wording; halal screen: fatwa referral) append their addition after this base text — they do not replace it.

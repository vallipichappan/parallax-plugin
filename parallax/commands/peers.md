---
description: Analyst-grade peer comparison — factor matrix across the peer group, score trajectories, and relative price performance
argument-hint: "[ticker or company name]"
---

# Peer Comparison

Positions one stock against its peer group on factors, score direction, and price. Answers "how does this compare?", not "should I own it?".

**Not this command:** single-stock verdict → `/parallax:stock`. Full work-up → `/parallax:deep-dive`. Portfolio-level overlap → `/parallax:portfolio`. Score methodology → `/parallax:why-score`.

## Step 1 — Resolve and snapshot

Resolve the ticker with `search_stocks` (free) per the conventions skill.

Parallel:

| Tool | Parameters | Purpose |
|---|---|---|
| `get_company_info` | `symbol` | Ground-truth name for cross-validation |
| `get_peer_snapshot` | `symbol` | Peer group + factor scores |
| `export_peer_comparison` | `symbol`, `format="json"` | Structured peer matrix |

**Cross-validation gate (non-bypassable).** Check `get_peer_snapshot`'s top-level `target_company` against `get_company_info.data.name`. Peer rows carry their own `name` field describing each peer — that is not the target's name and must never be used for this check. On mismatch, refuse to render the comparison: show both names and ask the user to confirm the intended company. A peer matrix built around the wrong primary is wrong in every row.

From the snapshot, identify the peer group and the **top 2 most relevant peers** for the deeper legs.

## Step 2 — Resolve peer symbols to RIC

Peer symbols returned by `get_peer_snapshot` frequently lack exchange suffixes (`GM` rather than `GM.N`). Resolve each to RIC format via `search_stocks` or the conventions skill suffix table before passing it anywhere downstream. Single-letter tickers such as `F` error with "Symbol too short" if passed bare.

## Step 3 — Classify each leg by asset class (MANDATORY, before any price pull)

The three legs are the primary plus the two peers. `get_peer_snapshot` can surface sector or country ETFs as peers, and `export_price_series` is equity-only — an ETF leg would fail empty and silently vanish from the price comparison.

Per the `asset-class-routing` skill, call `etf_profile` on each leg, one symbol per call, in parallel:

- `{"error": "No profile data found", ...}` → **equity** → route through `export_price_series`
- non-error profile → **ETF** → route through `etf_daily_price`

Three calls, 1 token each.

## Step 4 — Trends and price series (parallel)

Fire together:

- `get_score_analysis` for the primary and both peers — three calls. Do **not** pass `weeks`; the transport serializes numeric params as strings and validation fails. Take the server-default window and state which window the response covers.
- Each **equity** leg → `export_price_series` with the RIC, `format="json"` (free). No explicit `days` — rely on the server default and slice client-side if a shorter window is wanted.
- Each **ETF** leg → `etf_daily_price` with the plain ticker.

**Halt-and-surface rule.** If a leg returns empty from both its classified endpoint and the fallback, exclude it from the price section and render:

> ⚠ Could not retrieve price history for `<symbol>`; relative price comparison shows the remaining legs only.

Never drop a leg without disclosing it. A two-leg chart presented as a three-leg comparison is the failure this rule exists to prevent.

## Output Format

- **Peer Group** — who the peers are and why they are comparable
- **Factor Comparison Matrix** — table of all peers × all five factors, 0-10 per the `parallax-scoring` skill
- **Score Trajectory** — which name is improving or deteriorating fastest, and on which factor; name the window the data covers
- **Relative Price Performance** — comparative returns across the legs that returned data
- **Differentiation** — where the primary is genuinely stronger or weaker than the group, in two or three sentences

Where a factor score is ≥8 or ≤3, call `explain_methodology` (free) and weave the definition in, per the `parallax-scoring` skill's proactive trigger.

**Comparison is not ranking.** Report where the primary sits relative to peers; do not order the group into a preference list or label any name as the pick — see the conventions skill §12.

## Token cost

~8 tokens: peer snapshot (1) + peer comparison export (1) + three score histories (3) + three `etf_profile` probes (3). `export_price_series` is free.

## Render discipline

Apply the Render Discipline section of the conventions skill: suppress step scaffolding, hoist every integrity surface (⚠ excluded legs, degraded-coverage notes) into the final output, and close with the §9.2 AI-interaction disclosure immediately above the §9.1 disclaimer.

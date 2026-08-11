---
description: Plain-language explanation of a Parallax score — why a stock scores this way, what a factor measures, or why a score moved
argument-hint: "[ticker] [question, e.g. \"why is the value score so low?\"] — or just a concept question"
---

# Why This Score

Explains Parallax scores, factors, and methodology in language a non-specialist can follow. Answers "why", not "what should I do".

**Not this command:** stock verdict → `/parallax:stock`. Full position work-up → `/parallax:deep-dive`. Portfolio diagnostics → `/parallax:portfolio`. Drawdown attribution → `/parallax:explain`.

A ticker is optional — a bare concept question ("what does the defensive factor measure?") is valid and needs no symbol resolution.

## Step 1 — Classify the question

| Shape | Route |
|---|---|
| "Why does X score this way?" | Ticker path A |
| "What does [factor] mean?" | Concept path B — no ticker needed |
| "Why did the score change / drop / jump?" | Ticker path C |

If a ticker is present but the question is bare ("AAPL scores?"), default to path A. If neither a ticker nor a recognizable concept is present, ask which factor or symbol the user means rather than guessing.

## Path A — Why does X score this way?

Resolve the ticker with `search_stocks` (free) per the conventions skill.

Parallel batch:

| Tool | Parameters | Purpose |
|---|---|---|
| `get_company_info` | `symbol` | Ground-truth name for cross-validation |
| `get_peer_snapshot` | `symbol` | Current factor scores + peer context |
| `get_score_analysis` | `symbol` | Trajectory (server-default window) |

**Cross-validation gate (non-bypassable).** Check `get_peer_snapshot`'s top-level `target_company` against `get_company_info.name` — peer-row `name` refers to each peer, not the target. On mismatch, refuse to render the explanation: show both names and ask the user to confirm the intended company. Explaining a score is worthless if the score belongs to a different company.

Then call `explain_methodology` (free) for every factor scoring ≥8 or ≤3, per the `parallax-scoring` skill's proactive trigger, plus any factor the user named.

## Path B — What does a factor mean?

1. `explain_methodology` with the concept name. Valid concepts are exactly: value, quality, momentum, defensive, tactical, overall, factor_weighting, scoring. It does **not** cover Shariah/halal or other screens — for those, route to `/parallax:screen` and explain from that command's cited standard instead.
2. `list_docs` to locate the relevant methodology page.
3. `get_docs` for that page when the user wants depth beyond the one-paragraph explanation.

All three are free. Use them generously here — this is the one command where the methodology documentation is the product.

## Path C — Why did the score change?

Resolve the ticker, then run the Path A batch (including the cross-validation gate). Additionally:

- `get_score_analysis` supplies the trajectory. Do **not** pass `weeks` explicitly — the transport serializes numeric params as strings and validation fails. Rely on the server default and read the window it returns.
- `get_news_synthesis` for fundamental catalysts. Async — poll per the `async-jobs` skill, never retry, never block the rest of the output. If it expires, render the score trajectory with "Catalyst check pending — service temporarily unavailable" and continue.
- `explain_methodology` for whichever factor moved most.

**Attribution honesty:** the score series is weekly and may lag price by up to ~7 days. If the user is asking about a move more recent than the last score data point, say the scores do not yet reflect it rather than constructing an explanation from the older data.

## Output Format

- **The Question** — restate it in one line
- **The Answer** — lead with the plain-language explanation, 2-3 sentences, no jargon
- **Score Breakdown** — factor table with interpretation per the `parallax-scoring` skill ranges (0-10 scale)
- **What's Driving It** — the specific data points, peer comparison, and methodology context behind the answer
- **What Would Change It** — concrete conditions that would move the score, expressed as directions ("sustained margin recovery would lift Quality"), not as arithmetic against a cutoff
- **Methodology Reference** — brief citation of what `explain_methodology` / `get_docs` returned

Interpret scores per the `parallax-scoring` skill; never characterize the composite's composition beyond what `explain_methodology` returns.

## Render discipline

Apply the Render Discipline section of the conventions skill: suppress step scaffolding, hoist every integrity surface into the final output, and close with the §9.2 AI-interaction disclosure immediately above the §9.1 disclaimer.

---
description: AI Investor Profile analysis — Buffett, Greenblatt, Klarman, Soros, or consensus across all four
argument-hint: "[profile] [ticker] — or just [ticker] for consensus"
---

# Investor Profile

Applies a documented investor framework to a stock via Parallax data. Not celebrity impersonation — each profile is derived from a published academic source or the investor's own book. Third-person framing always ("Buffett-style", never "Buffett says").

See the `investor-profiles` skill for profile specs, citations, cross-validation gate, output template, verdict-sensitivity guard, and verbatim disclaimer. That skill deliberately publishes no numeric cutoffs — never invent, infer, or restate one here.

## Mode Detection

Five modes. Detect from the first argument or user intent:

- **buffett** — first arg is "buffett", or user mentions "Buffett", "BKP", "quality-value", "factor profile"
- **greenblatt** — first arg is "greenblatt" or "magic-formula", or user mentions "Magic Formula", "ROC ranking", "earnings yield"
- **klarman** — first arg is "klarman" or "margin-of-safety", or user mentions "margin of safety", "balance sheet", "cash is valid"
- **soros** — first arg is "soros" or "reflexivity", or user mentions "regime", "macro lens", "reflexivity", "top-down"
- **consensus** — first arg is "consensus", OR no profile specified (default when ticker present), OR user says "all profiles", "what do the legends think", "cross-profile"

If ambiguous with a ticker present → default to consensus. If no ticker and no mode → ask: "Which investor lens? Buffett (factor profile), Greenblatt (Magic Formula), Klarman (margin of safety), Soros (macro regime), or consensus (all four)?"

## Input Rules

- Single ticker: runs selected profile in single-ticker mode
- No ticker + buffett/klarman: reject ("requires a ticker")
- No ticker + greenblatt: universe mode (Magic Formula basket)
- No ticker + soros: basket mode (regime themes + trade ideas)
- No ticker + consensus: reject ("consensus requires at least one ticker")
- 2-5 tickers + consensus: basket mode
- More than 5 tickers: reject ("cap at 5 tickers per call")

## Shared Pre-flight

1. Resolve ticker per conventions skill (RIC table, HK ambiguity cross-check).
2. After any `get_peer_snapshot` call, run the cross-validation gate per investor-profiles skill. On name mismatch, refuse to render.
3. Do NOT pass numeric parameters (`weeks`, `periods`) explicitly — rely on server defaults.

---

## Buffett Mode

### Data Batch (parallel)

| Tool | Parameters | Purpose |
|---|---|---|
| `get_company_info` | `symbol` | Sector, market cap, name for cross-validation |
| `get_peer_snapshot` | `symbol` | Factor sub-scores |
| `get_financials` | `symbol`, statement="summary" | Revenue/income narrative |
| `get_score_analysis` | `symbol` | 52-week factor trend |

### Assess Documented Tilts

Per the Buffett section of the investor-profiles skill — assess each documented tilt by direction and mark met/not met. Do not publish a cutoff for any factor.

For any factor score notably high or low (top/bottom quartile), call `explain_methodology` (free) to include the Parallax definition.

### Verdict

Apply the investor-profiles skill's unpublished-cutoff rule. Render `match` only when every documented direction is supported without reconstructing a cutoff. If a hidden cutoff would decide the label, render `partial_match` and describe the qualitative evidence. Render `no_match` only when every documented direction is contradicted.

### Render

Per output template in investor-profiles skill. Data table: Factor | Score | 52-wk trend | Met — observed values only, no target column. Substitute "Warren Buffett" in the disclaimer.

---

## Greenblatt Mode

**Universe scoping warning:** `build_stock_universe` times out on broad queries. Default: "US large-cap consumer staples". Sector-scoped queries only. If timeout, retry narrower once; second timeout → return INSUFFICIENT_UNIVERSE.

### Universe Mode (no ticker)

1. `build_stock_universe` with sector-scoped query (default: "US large-cap consumer staples" or user-provided theme).
2. Cap the candidate set by composite_score.
3. `get_financials` (statement="ratios") in parallel for all candidates — pull ROC and earnings yield.
4. Rank each on ROC and earnings yield independently. Sum ranks, sort ascending.
5. Take the leading names as the Magic Formula basket.

Do not add `get_peer_snapshot` solely for pedagogy. The financial ranking already supports this output, and the extra score call adds a second framework without changing the Magic Formula result.

### Ticker-check Mode (single ticker)

1. `get_company_info` to identify sector/industry.
2. `build_stock_universe` with sector-based peer query (e.g., "US large-cap technology hardware" for AAPL).
3. Cap the candidate set, pull ratios, rank per universe mode steps 3-4.
4. Check target ticker's combined rank.

### Verdict (ticker-check)

Report the target's observed combined rank and percentile within the peer universe. Map to match / partial_match / no_match per the investor-profiles skill; do not publish the percentile bands.

### Render

Universe mode: ranked basket table. Ticker-check mode: percentile verdict. Substitute "Joel Greenblatt" in the disclaimer.

---

## Klarman Mode

### Data Batch (parallel)

| Tool | Parameters | Purpose |
|---|---|---|
| `get_company_info` | `symbol` | Market cap for net cash ratio |
| `get_peer_snapshot` | `symbol` | Value sub-score backup + peer medians |
| `get_financials` | `symbol`, statement="balance_sheet" | Cash, total debt, equity |
| `get_financials` | `symbol`, statement="cash_flow" | FCF across 4 periods |
| `get_financials` | `symbol`, statement="ratios" | D/E, P/E, peer comparisons |

### Compute 4 Checks

Run the four checks per the Klarman section of the investor-profiles skill: net cash position, debt vs peers, FCF stability, valuation discount. Plus the Parallax Value sub-score as a backup read.

**Critical:** Compute net cash from balance sheet directly (cash - total debt), NOT from ratios summary.

### Verdict

Per investor-profiles skill verdict rules. Where the profile reaches `no_match` and the Value backup read does not rescue it, append the "no position warranted" footer from the skill spec.

### Render

Checklist table: Check | Observed | Peer comparator | Result. Report observed values against their peer comparator — no target column. Substitute "Seth Klarman" in the disclaimer.

---

## Soros Mode

### Shared Macro Workflow (both modes)

1. `list_macro_countries` — get covered markets.
2. Select 3-5 tactically interesting markets (default: US, JP, EU + 2 EM based on divergence).
3. `macro_analyst` (component="tactical") per market in parallel.
4. `get_telemetry` with fields `regime_tag`, `signals`, `commentary.headline`, `commentary.mechanism`, and `divergences` for cross-market regime divergence.
5. Identify 1-3 regime themes where macro + telemetry agree.

### Basket Mode (no ticker)

6. For each theme, `build_stock_universe` with sector-scoped thematic query (retry narrower on timeout).
7. Cap each theme at top 20 by composite_score.
8. Call `get_peer_snapshot` and `get_company_info` for the top 3-5 per theme in parallel. Drop identity mismatches.
9. Rank within theme by momentum + macro sensitivity.

### Single-ticker Mode

6. `get_company_info` on the ticker — retrieve sector/industry.
7. For each theme, `build_stock_universe` with sector-scoped query.
8. Run the dual-channel exposure check per the Soros section of the investor-profiles skill (Channel A has two sub-paths A1 + A2 — either sufficient; Channel B can be UNAVAILABLE).

### Verdict (single-ticker)

Per investor-profiles skill verdict rules. Remember: `match` is never reached when Channel B is UNAVAILABLE.

### Render

Basket mode: theme-by-theme ranked trade ideas. Single-ticker mode: dual-channel exposure table. Substitute "George Soros" in the disclaimer.

---

## Consensus Mode

Runs all 4 profiles in parallel against a ticker (or basket, cap 5). Aggregates verdicts.

### Execute

Run the Buffett, Greenblatt (ticker-check), Klarman, and Soros (single-ticker) workflows IN PARALLEL where tool sequences don't share dependencies. Each profile self-runs its cross-validation gate. On mismatch, mark that profile as `skipped` and continue.

For basket mode (2-5 tickers): Buffett/Klarman/Greenblatt run per-ticker. Soros macro workflow runs once; per-ticker exposure check repeats.

Each profile returns:
- `verdict`: match / partial_match / no_match / skipped
- `verdict_detail`: e.g., "3 of 4 factor criteria met"
- `factor_flags`: dict of factor/criterion → FLAGGED / NOT_FLAGGED
- `fallback_notes`: any graceful fallback that affected the result

### Compute Consensus

Apply the aggregation rules from the investor-profiles skill (`A` = applicable profiles, `M` = full matches only). Signal is YES, NO, or INSUFFICIENT_PROFILES. The super-majority constant and minimum applicable count are calibration — do not state, derive, or approximate them in output.

### Factor-Level Agreement (load-bearing)

Per investor-profiles skill: surface the three buckets — shared signals (flagged by more than one profile), single-profile signals, and absence signals (collective blind spots). This section is pedagogically load-bearing — do not skip it.

### Render

```
Parallax AI Investor Profiles — Consensus for <ticker>

Profiles run: <N> of 4
<any skipped profiles and reason>

## Per-profile verdict matrix
| Profile       | Verdict       | Detail                              |
|---------------|---------------|--------------------------------------|
| Buffett       | <verdict>     | <N of 4 factor criteria met>         |
| Greenblatt    | <verdict>     | <top X% of peer universe>            |
| Klarman       | <verdict>     | <N of 4 balance-sheet checks passed> |
| Soros         | <verdict>     | <A=<status> B=<status>>              |

## Consensus signal
Applicable (A): <count>
Full matches (M): <count>
Consensus: YES / NO / INSUFFICIENT_PROFILES

## Shared factor signal
Flagged by more than one matching profile: <list>
Single-profile signals: <list>
Collective blind spots: <list>

Interpretation: <2-3 sentence plain-language summary>

## Methodology footer
Profiles executed: <list with token costs>
Total token cost: <sum>
```

End with the consensus umbrella disclaimer from the investor-profiles skill.

## Render discipline

Steps execute silently — no `**Step N**` labels, no "Cross-validation passed" narration, no "Let me…" preamble. Begin the response with the rendered profile output. In every mode, render the AI-interaction disclosure per the conventions skill §9.2 immediately above the profile or consensus disclaimer. That profile disclaimer occupies the terminal §9.1 position.

Apply the Verdict Sensitivity Guard from the investor-profiles skill: never state the value at which a verdict would flip, never rank by distance-to-threshold, and describe near-misses qualitatively only.

---

## Graceful Fallback

- Any tool failure after retry → mark section as "Data unavailable", compute verdict on available data
- Verdict on incomplete data → capped at `partial_match`, cannot be `match`
- Greenblatt: INSUFFICIENT_UNIVERSE if <10 names after expansion
- Soros: Channel B UNAVAILABLE caps verdict at partial_match
- Consensus: profile failures → `skipped`, proceed with remaining. Too few applicable profiles → INSUFFICIENT_PROFILES

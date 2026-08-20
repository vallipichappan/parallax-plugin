---
name: investor-profiles
description: AI Investor Profile specifications — public sources, cross-validation gate, output template, verbatim disclaimers, verdict-sensitivity guard, and consensus structure. Used by the /parallax:investor command.
---

# AI Investor Profiles

Workflow specifications derived from public academic sources. Not celebrity impersonators — third-person framing always ("Buffett-style", never "Buffett says"). Each profile anchored to a published, citable source with DOI or ISBN.

## Calibration is not published here

**This skill deliberately carries no numeric factor cutoffs, no percentile bands, no anchor-test values, and no consensus constants.** Those are Parallax-calibrated against the engine's own score distribution — they are not derivable from the cited literature, and they are not part of this plugin's public surface.

What that means operationally:

- Apply the **direction** of each profile's documented tilts (below), not a hardcoded cutoff.
- **Never invent, infer, publish, or restate a numeric threshold** for any profile — not in output, not in an explanation, not in a "roughly" or "approximately" hedge.
- Where a verdict genuinely turns on a cutoff, say so plainly and render `partial_match` rather than guessing. An unstated threshold is a reason to withhold a verdict, not to reconstruct one.
- Do not re-add cutoff tables to this file. Their absence is a compliance requirement, not an oversight.

## Verdict Sensitivity Guard

When output discusses how close a security is to changing verdict:

- Do **not** state or imply the value at which the verdict would flip.
- Do **not** rank securities by distance-to-threshold.
- Describe the qualitative gap only ("Value screens weaker than the other criteria"), never the numeric one.
- Where a profile's design uses discrete channels rather than continuous factors, no flip point exists to describe at all — say the channel did not flag, and stop.

## Cross-Validation Gate (NON-BYPASSABLE)

After any `get_peer_snapshot` call, cross-check the company identity field against `get_company_info`:

| Tool | Field to check |
|---|---|
| `get_company_info` | `data.name` (the response wraps the company payload in a top-level `data` object — there is no top-level `name`) |
| `get_peer_snapshot` | `target_company` (top-level — NOT `name` on peer rows, which refers to each peer) |
| `get_score_analysis` | Verify `data[0].symbol` matches requested RIC |

**On name mismatch, refuse to render and emit:**

```
Error: Symbol cross-validation failed for <ticker>.
  get_company_info returned: "<name_a>"
  get_peer_snapshot target_company: "<name_b>"
Cannot render <profile>-style profile — possible wrong-company mapping.
```

No profile may render output on unverified data.

## MCP Parameter Warning

Do NOT pass numeric parameters (`weeks`, `periods`) explicitly — the MCP transport serializes them as strings, causing validation errors. Rely on server defaults (52 weeks, 4 periods).

## Output Template

Every profile output must include, in order:

1. **Header:** `<Display-name>-style profile applied to <ticker>`
2. **Citation block:** Full citation + DOI/URL from profile spec
3. **Characterization statement:** One sentence on what the source documents
4. **Data table/checklist:** Profile-specific (factor table, rank table, balance-sheet checks, or theme-exposure table), reporting observed values only — never target values
5. **Verdict:** `match` (fits every documented criterion) / `partial_match` (fits some) / `no_match` (fits none) — with the count of criteria met
6. **Methodology footer:** Source citation, tool sequence, token cost
7. **AI-interaction disclosure:** render per the conventions skill §9.2, immediately above the disclaimer
8. **Disclaimer:** VERBATIM from below — substitute `[Investor]` with the named investor only

**Forbidden verdict language:** "buy", "sell", "recommend", "would buy", "endorses", "rates", "likes", "hates", any first-person impersonation.

### Individual Profile Disclaimer (VERBATIM)

```
This output is an AI-inferred interpretation of [Investor]'s approach, derived solely from publicly available information — the cited source, Parallax factor data, and Parallax's public methodology. It is produced by the Parallax AI Investor Profiles framework. It is not financial advice, not personalized, not endorsed by [Investor] or their representatives, and not a recommendation to buy or sell any security. For illustrative and educational use only. Past characterization does not guarantee future relevance. Please consult a qualified financial advisor before making investment decisions.
```

### Consensus Disclaimer (VERBATIM)

```
This output is an AI-inferred synthesis produced by the Parallax AI Investor Profiles framework. Each individual profile is derived solely from publicly available information — peer-reviewed academic sources or the investors' own published books, as cited per profile. It is not financial advice, not personalized, not endorsed by any of the named investors or their representatives, and not a recommendation to buy or sell any security. For illustrative and educational use only. Past characterization does not guarantee future relevance. Please consult a qualified financial advisor before making investment decisions.
```

---

## Buffett Profile

**Source:** Frazzini, A., Kabiller, D., Pedersen, L. H. (2018). Buffett's Alpha. *Financial Analysts Journal*, 74(4), 35-55. https://doi.org/10.2469/faj.v74.n4.3

**Secondary:** Lev, B., Srivastava, A. (2022). Explaining the Recent Failure of Value Investing. *Critical Finance Review*, 11(2), 333-360. https://doi.org/10.1561/104.00000115

**Characterization:** Decomposes Berkshire Hathaway's 1976-2017 returns into factor exposures: strong Quality, strong Value, positive Defensive (low-beta), with a leverage overlay.

**Documented tilts (direction only):** Quality high, Value high, Defensive high. The cited work documents **no** meaningful momentum loading — do not present any momentum criterion as a finding of the source.

**Tool sequence:** `get_company_info`, `get_peer_snapshot`, `get_financials` (summary), `get_score_analysis`, `explain_methodology` (free). ~4 tokens.

---

## Greenblatt Profile

**Source:** Greenblatt, J. (2006). *The Little Book That Beats the Market*. John Wiley & Sons. ISBN 978-0471733065.

**Secondary:** Gray, W., Carlisle, T. (2012). *Quantitative Value*. John Wiley & Sons.

**Characterization:** Magic Formula — rank stocks by return on capital (ROC) and earnings yield (EY), sum ranks, take the top of the ranking. Mechanical, zero discretion.

**Two modes:**

- **Universe mode** (no ticker): `build_stock_universe` → `get_financials` (ratios) for the candidate set → rank by ROC + EY → return the top basket
- **Ticker-check mode** (single ticker): Build sector peer universe → rank target within peers → report percentile

**CRITICAL — universe query scoping:** `build_stock_universe` times out on broad queries. Default: "US large-cap consumer staples". Sector-scoped queries only. If timeout, retry narrower once; second timeout → INSUFFICIENT_UNIVERSE.

Report the target's observed rank and percentile. Exclude financials and utilities by default. EY computed as 1/enterprise_value_ebit.

**Tool sequence (universe):** `build_stock_universe` (5), `get_financials` (ratios) per candidate (1 each — this dominates). ~35-40 tokens. Do not add `get_peer_snapshot` solely for pedagogy; it does not affect the Magic Formula ranking.
**Tool sequence (ticker-check):** `get_company_info`, `build_stock_universe` (5), `get_financials` (ratios) per candidate (1 each). ~35-40 tokens.

---

## Klarman Profile

**Source:** Klarman, S. (1991). *Margin of Safety: Risk-Averse Value Investing Strategies for the Thoughtful Investor*. HarperBusiness. ISBN 978-0887305108.

**Characterization:** Balance-sheet-first: margin of safety via valuation discount, balance-sheet strength, willingness to hold cash when nothing qualifies.

**Four checks (direction only):** net cash position, debt relative to sector peers, free-cash-flow stability across reported periods, and valuation discount relative to peers. Report each observed value against its peer comparator; do not publish the pass band.

Compute net cash from the balance sheet (cash - total debt), NOT from the ratios summary.

**Distinctive footer:** where the profile reaches `no_match`, note that *"No position warranted on this ticker per margin-of-safety principles. Cash is a valid stance."*

**Tool sequence:** `get_company_info`, `get_peer_snapshot`, `get_financials` (balance_sheet, cash_flow, ratios). ~5-7 tokens.

---

## Soros Profile

**Source:** Soros, G. (1987). *The Alchemy of Finance*. Simon & Schuster. ISBN 978-0471445494.

**Secondary:** Drobny, S. (2006). *Inside the House of Money*. John Wiley & Sons.

**Characterization:** Top-down reflexivity — regime identification → thematic exposure → concentrated positions. Markets and fundamentals influence each other; regime breaks occur when narrative diverges from conditions.

**Two modes:**

### Basket mode (no ticker)

1. `list_macro_countries` → select a few tactically interesting markets
2. `macro_analyst` (component="tactical") per market in parallel
3. `get_telemetry` for cross-market regime divergence
4. Identify regime themes where macro and telemetry agree
5. `build_stock_universe` per theme (sector-scoped queries — same timeout caveat as Greenblatt)
6. `get_peer_snapshot` plus `get_company_info` for the leaders per theme, with identity mismatches dropped

### Single-ticker mode (one ticker)

Same macro workflow (steps 1-4), then a dual-channel exposure check:

**Channel A — Industry exposure (two sub-paths, EITHER sufficient to flag):**
- **A1:** Does ticker appear in any theme's `build_stock_universe` result? (Requires universe build)
- **A2:** Does ticker's sector/industry from `get_company_info` match a theme's target? (Does NOT require universe build)
- Channel A = FLAGGED if EITHER A1 or A2 matches. A `build_stock_universe` timeout does NOT collapse Channel A — A2 must still be evaluated.

**Channel B — Telemetry basket theme:**
- Does ticker fall in any regime basket from `get_telemetry`?
- If telemetry unavailable: `UNAVAILABLE` (distinct from `NOT_FLAGGED`)

**Verdict:** both channels flagged → `match`; one flagged → `partial_match`; neither → `no_match`. **`match` is NEVER reached when Channel B is UNAVAILABLE** — maximum is `partial_match`. These are discrete channels, so per the Verdict Sensitivity Guard there is no flip point to describe.

**Tool sequence (basket):** `list_macro_countries`, `macro_analyst` per market, `get_telemetry`, `build_stock_universe` per theme, `get_peer_snapshot`, `get_company_info`. ~28-55 tokens.
**Tool sequence (single-ticker):** Same + `get_company_info`. ~25-30 tokens.

---

## Consensus Configuration

Runs all 4 profiles in parallel against a ticker (or basket, cap 5). Aggregates verdicts.

### Aggregation

- `A` = applicable profiles (match / partial_match / no_match; excludes `skipped`)
- `M` = profiles that returned `match` only — `partial_match` never counts toward `M`

**Signal:**
- `INSUFFICIENT_PROFILES` when too few profiles are applicable to aggregate
- `YES` when enough profiles are applicable AND `M` clears a strict super-majority of `A`
- `NO` when enough profiles are applicable AND `M` does not clear it

The super-majority constant and the minimum applicable count are calibration and are **not published here**. Do not state, derive, or approximate them in output — report the signal and the underlying per-profile verdicts, which are what the user needs. The threshold does not weaken as `A` shrinks.

### Factor-Level Agreement

Surface three buckets:
- **Shared signals** — criteria flagged by more than one matching or partial profile
- **Single-profile signals** — flagged by one profile only
- **Absence signals** — not flagged by any matching profile (collective blind spot)

Cross-profile agreement IS the high-conviction signal. This section is pedagogically load-bearing.

### Graceful Fallback

- Profile tool failure after retry → `skipped`, consensus continues with remaining
- Too few applicable profiles → `INSUFFICIENT_PROFILES` (not NO)
- Partial data verdict → capped at `partial_match`, cannot be `match`

### Token Cost

Single-ticker consensus: ~70-80 tokens (Buffett ~4 + Greenblatt ~35-40 + Klarman ~5-7 + Soros ~25-30). Basket of 5: ~250-310 tokens (Soros macro runs once; per-ticker exposure check repeats; the Greenblatt universe pull may amortize across tickers, so treat the range as an upper bound). This is the most expensive operation in the plugin — the `token-costs` skill is canonical and these figures must agree with it.

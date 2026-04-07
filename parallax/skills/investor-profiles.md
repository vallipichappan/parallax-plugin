---
name: investor-profiles
description: AI Investor Profile specifications — thresholds, citations, cross-validation gate, output template, verbatim disclaimer, and consensus math. Used by the /parallax:investor command.
---

# AI Investor Profiles

Workflow specifications derived from public academic sources. Not celebrity impersonators — third-person framing always ("Buffett-style", never "Buffett says"). Each profile anchored to a published, citable source with DOI or ISBN.

## Cross-Validation Gate (NON-BYPASSABLE)

After any `get_peer_snapshot` call, cross-check the company identity field against `get_company_info`:

| Tool | Field to check |
|---|---|
| `get_company_info` | `name` |
| `get_peer_snapshot` | `target_company` (top-level — NOT `company` on peer rows, which refers to each peer) |
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
4. **Data table/checklist:** Profile-specific (factor table, rank table, balance-sheet checks, or theme-exposure table)
5. **Verdict:** `match` (full fit) / `partial_match` (some criteria) / `no_match` (zero fit) — with count
6. **Methodology footer:** Source citation, anchor-test date, tool sequence, token cost
7. **Disclaimer:** VERBATIM from below — substitute `[Investor]` with the named investor only

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

**Characterization:** Decomposes Berkshire Hathaway's 1976-2017 returns into factor exposures: strong Quality, strong Value, slight negative Momentum, positive Defensive (low-beta), with ~1.6x leverage overlay.

**Thresholds** (tuned 2026-04-06, reconciled for intangibles era per Lev-Srivastava 2022):

| Factor | Target | Rationale |
|---|---|---|
| Quality | >= 5 | Above average; catches KO (8), AXP (5) |
| Value | >= 4 | Loose — Buffett mega-caps look expensive on current multiples |
| Momentum | <= 6 | Slight negative tilt; NVDA (7.2) fails, KO (4.8) passes |
| Defensive | >= 7 | Strong low-beta; KO (10), AXP (8), AAPL (9.5) pass |

**Verdict:** 4/4 = match, 1-3/4 = partial_match, 0/4 = no_match.

**Tool sequence:** `get_company_info`, `get_peer_snapshot`, `get_financials` (summary), `get_score_analysis`, `explain_methodology` (free — for scores in threshold zone). ~4 tokens.

**Anchor tests (2026-04-06):** KO 4/4 match, AXP 4/4 match, BRKb 3/4 partial (Quality drag), AAPL 3/4 partial (Value fails), NVDA 2/4 partial (Value + Momentum fail).

**Does NOT capture:** Parent-stock vs holdings divergence, intangibles-adjusted accounting, management/moat, insurance float leverage, style evolution, current holdings.

---

## Greenblatt Profile

**Source:** Greenblatt, J. (2006). *The Little Book That Beats the Market*. John Wiley & Sons. ISBN 978-0471733065.

**Secondary:** Gray, W., Carlisle, T. (2012). *Quantitative Value*. John Wiley & Sons.

**Characterization:** Magic Formula — rank stocks by return on capital (ROC) and earnings yield (EY), sum ranks, take top decile. Mechanical, zero discretion.

**Two modes:**

- **Universe mode** (no ticker): `build_stock_universe` → `get_financials` (ratios) for top 30 → rank by ROC + EY → return top decile basket
- **Ticker-check mode** (single ticker): Build sector peer universe → rank target within peers → report percentile

**CRITICAL — universe query scoping:** `build_stock_universe` times out on broad queries. Default: "US large-cap consumer staples". Sector-scoped queries only. If timeout, retry narrower once; second timeout → INSUFFICIENT_UNIVERSE.

**Thresholds:**

| Percentile | Verdict |
|---|---|
| Top 10% combined rank | match |
| Top 25% (outside top 10%) | partial_match |
| Below top 25% | no_match |

Cap universe at top 30 by composite_score. Exclude financials and utilities by default.

**Tool sequence (universe):** `build_stock_universe`, `get_financials` (ratios) x30, `get_peer_snapshot` x3. ~15-30 tokens.
**Tool sequence (ticker-check):** `get_company_info`, `build_stock_universe`, `get_financials` (ratios) x30, `get_peer_snapshot`. ~10-15 tokens.

**Anchor tests (2026-04-06):** CSCO ROIC 11.06%, MSFT ROIC 23.55%, NVDA ROIC 89.54%. EY computed as 1/enterprise_value_ebit. Full universe test deferred due to timeout.

**Does NOT capture:** Discretionary judgment, intangibles-adjusted EY, small-cap premium, holding period.

---

## Klarman Profile

**Source:** Klarman, S. (1991). *Margin of Safety: Risk-Averse Value Investing Strategies for the Thoughtful Investor*. HarperBusiness. ISBN 978-0887305108.

**Characterization:** Balance-sheet-first: margin of safety via valuation discount, balance-sheet strength, willingness to hold cash when nothing qualifies.

**Four checks:**

| Check | Target | PASS | PARTIAL | FAIL |
|---|---|---|---|---|
| Net cash position | Net cash / market cap | >= 0 | >= -0.2 | < -0.2 |
| Debt vs peers | D/E vs peer median | <= peer x 1.1 | — | > peer x 1.1 |
| FCF stability | Positive periods (of 4) | >= 3 | 2 | <= 1 |
| Valuation discount | P/E vs peer median | <= peer x 0.85 | <= peer x 1.0 | > peer x 1.0 |

**Backup:** Parallax Value sub-score >= 4 (intentionally loose per Lev-Srivastava 2022). If Value < 4, flag in output.

Compute net cash from balance sheet (cash - total debt), NOT from ratios summary.

**Verdict:** >= 3 PASS AND Value >= 4 = match. 2 PASS = partial_match. 0-1 PASS = no_match.

**Distinctive footer:** If no_match AND Value < 4: *"No position warranted on this ticker per margin-of-safety principles. Cash is a valid stance."*

**Tool sequence:** `get_company_info`, `get_peer_snapshot`, `get_financials` (balance_sheet, cash_flow, ratios). ~5-7 tokens.

**Anchor tests (2026-04-07):** BRKb 2/4 partial (fails net cash -21%, fails valuation P/E 15.38 vs peer ~11.58). NVDA 3/4 partial but Value 2.5 < 4 → capped at partial_match.

**Does NOT capture:** Intrinsic value estimation, special situations, qualitative judgment, position sizing.

---

## Soros Profile

**Source:** Soros, G. (1987). *The Alchemy of Finance*. Simon & Schuster. ISBN 978-0471445494.

**Secondary:** Drobny, S. (2006). *Inside the House of Money*. John Wiley & Sons.

**Characterization:** Top-down reflexivity — regime identification → thematic exposure → concentrated positions. Markets and fundamentals influence each other; regime breaks occur when narrative diverges from conditions.

**Two modes:**

### Basket mode (no ticker)

1. `list_macro_countries` → select 3-5 tactically interesting markets
2. `macro_analyst` (component="tactical") per market in parallel
3. `get_telemetry` for cross-market regime divergence
4. Identify 1-3 regime themes where macro + telemetry agree
5. `build_stock_universe` per theme (sector-scoped queries — same timeout caveat as Greenblatt)
6. `get_peer_snapshot` for top 3-5 per theme → rank by momentum + macro sensitivity

### Single-ticker mode (one ticker)

Same macro workflow (steps 1-4), then dual-channel exposure check:

**Channel A — Industry exposure (two sub-paths, EITHER sufficient to flag):**
- **A1:** Does ticker appear in any theme's `build_stock_universe` result? (Requires universe build)
- **A2:** Does ticker's sector/industry from `get_company_info` match a theme's target? (Does NOT require universe build)
- Channel A = FLAGGED if EITHER A1 or A2 matches. A `build_stock_universe` timeout does NOT collapse Channel A — A2 must still be evaluated.

**Channel B — Telemetry basket theme:**
- Does ticker fall in any regime basket from `get_telemetry`?
- If telemetry unavailable: `UNAVAILABLE` (distinct from `NOT_FLAGGED`)

**Verdict:**
- Both channels FLAGGED → `match`
- One channel FLAGGED → `partial_match`
- Neither flagged → `no_match`
- **`match` is NEVER reached when Channel B is UNAVAILABLE** — maximum is `partial_match`

**Tool sequence (basket):** `list_macro_countries`, `macro_analyst` x3-5, `get_telemetry`, `build_stock_universe` x1-3, `get_peer_snapshot` x3-5. ~25-40 tokens.
**Tool sequence (single-ticker):** Same + `get_company_info`. ~25-30 tokens.

**Anchor tests (2026-04-07):** list_macro_countries returns 12 markets. macro_analyst returns substantive thesis. get_telemetry returned "Admin org not configured" — Channel B unavailable in test env. Fallbacks handle correctly.

**Does NOT capture:** Trade execution/timing, currency/rate positions, leverage, reflexivity loop timing.

---

## Consensus Configuration

Runs all 4 profiles in parallel against a ticker (or basket, cap 5). Aggregates verdicts.

### Super-Majority Math

- `A` = applicable profiles (match / partial_match / no_match; excludes `skipped`)
- `M` = profiles that returned `match` only (NOT partial_match)
- `required_matches = ceil(0.75 x A)`
- `minimum_applicable_count = 3`

**Signal:**
- `INSUFFICIENT_PROFILES` if A < 3
- `YES` if A >= 3 AND M >= required_matches
- `NO` if A >= 3 AND M < required_matches

| Applicable | Matches | Required (ceil 0.75 x A) | Signal |
|---|---|---|---|
| 4 | 4 | 3 | YES |
| 4 | 3 | 3 | YES |
| 4 | 2 | 3 | NO |
| 3 | 3 | 3 | YES |
| 3 | 2 | 3 | NO |
| 2 | 2 | — | INSUFFICIENT_PROFILES |

**Ceiling rounding is intentionally strict:** ceil(0.75 x 3) = 3 (unanimity). The threshold does not weaken at small N.

### Factor-Level Agreement

Surface three buckets:
- **Shared signals** — factors/criteria flagged by >= 2 matching/partial profiles
- **Single-profile signals** — flagged by 1 profile only
- **Absence signals** — NOT flagged by any matching profile (collective blind spot)

Cross-profile agreement IS the high-conviction signal. The factor-level agreement section is pedagogically load-bearing.

### Graceful Fallback

- Profile tool failure after retry → `skipped`, consensus continues with remaining
- A < 3 → `INSUFFICIENT_PROFILES` (not NO)
- Partial data verdict → capped at `partial_match`, cannot be `match`

### Token Cost

Single-ticker consensus: ~45-55 tokens. Basket of 5: ~150-200 tokens (Soros macro runs once; per-ticker exposure check repeats).

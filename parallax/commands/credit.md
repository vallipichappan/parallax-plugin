---
description: Creditor-lens assessment of a public company — leverage, coverage, liquidity, solvency, Altman Z-score, and Quality-score deterioration as a credit early-warning signal
argument-hint: "[ticker or RIC, e.g. AAPL.O] [optional: sector or market context]"
---

# Credit Lens

Reads a publicly traded issuer as a creditor would: can it service its debt, and is that capacity improving or deteriorating?

**Not this command:** portfolio credit concentration → `/parallax:scenario`. Equity fundamentals → `/parallax:deep-dive`. Private issuers are out of scope — this needs a public company with reported financials.

Never pass numeric parameters (`weeks`, `periods`, `limit`, `days`) explicitly — the transport serializes them as strings and validation fails. Rely on server defaults.

## Batch 0 — Resolve

Resolve the symbol with `search_stocks` first; fall back to the conventions skill suffix table (plain `AAPL` → `AAPL.O`). Exchange suffix is load-bearing.

## Batch A — Core financials (parallel, 4 tokens)

| Tool | Parameters | Extracts |
|---|---|---|
| `get_financials` | statement="balance_sheet" | Total debt, equity, total assets, working capital |
| `get_financials` | statement="cash_flow" | Operating CF, capex, FCF |
| `get_financials` | statement="ratios" | D/E, Debt/EBITDA, interest coverage, margins, peer medians |
| `get_peer_snapshot` | `symbol` | D/E peer median, factor scores |
| `get_company_info` | `symbol` | Ground-truth name for cross-validation, sector, market cap |

**Cross-validation (non-bypassable).** After `get_peer_snapshot`, compare the top-level `target_company` against `get_company_info.name` — peer rows carry their own `name` and refer to each peer, not the target. On mismatch, halt: do not render scores or peer-relative flags from a mismatched mapping.

Derive: **Leverage** (Debt/EBITDA, Debt/Equity, Debt/Assets vs peer medians) · **Coverage** (interest coverage, EBITDA/interest) · **Liquidity** (current ratio, quick ratio) · **Profitability** (EBITDA, EBIT, FCF margins).

## Batch B — Solvency, trend, macro (parallel)

| Tool | Parameters | Purpose |
|---|---|---|
| `get_financial_analysis` | `symbol` | Solvency assessment — async, 2-5 min |
| `get_score_analysis` | `symbol` | Quality-score trajectory (52w server default) |
| `get_telemetry` | — | Market regime; no symbol parameter |

`get_financial_analysis` is async — never retry it, poll `check_job_status` per the async-jobs skill, and never let it block the rest of the report. On wait-cap expiry render "Analysis pending — service temporarily unavailable" in the Solvency section and continue with every other metric.

## Altman Z-Score

Compute the market-cap variant (public-company Z, not Z') from Batch A plus market cap:

```
Z = 1.2×X1 + 1.4×X2 + 3.3×X3 + 0.6×X4 + 1.0×X5

where:
  X1 = Working Capital / Total Assets
  X2 = Retained Earnings / Total Assets
  X3 = EBIT / Total Assets
  X4 = Market Cap / Total Liabilities   ← closing market cap from latest trading data
  X5 = Revenue / Total Assets

Thresholds:
  Z > 2.99   → Safe Zone (low distress probability)
  1.81–2.99  → Grey Zone (moderate risk)
  Z < 1.81   → Distress Zone (high distress probability)
```

If market cap is unavailable, substitute book equity for X4 (the **Z' variant**) and state the substitution in the output.

Altman thresholds are generic — they shift by industry (manufacturing vs retail vs financial). Note the caveat when the issuer's sector makes it material.

## Flagging Logic

Peer-relative traffic light:

| Signal | Condition |
|---|---|
| 🟢 GREEN | Better than peer median |
| 🟡 AMBER | Between peer median and 75th percentile |
| 🔴 RED | Worse than peer 75th percentile |

Also apply absolute credit thresholds. **Use the more conservative of peer-relative and absolute.**

| Metric | Amber | Red |
|---|---|---|
| Debt/EBITDA | > 3.5x | > 5.0x |
| Interest Coverage | < 3.0x | < 1.5x |
| Current Ratio | < 1.2x | < 1.0x |
| Altman Z | Grey Zone (1.81–2.99) | Distress Zone (< 1.81) |
| Quality Score Change (52w, 0-10 scale) | decline > 0.5 pts | decline > 1.5 pts |

Quality-score deterioration is a **primary** credit early-warning signal — a decline beyond 1.0 pt (0-10 scale) is RED even when every other metric looks healthy.

**Peer degradation:** if the peer group is too small for reliable medians, show absolute thresholds only and state that peer comparison is unavailable. Flag any significant size mismatch (mega-cap medians are not a meaningful yardstick for a small-cap).

## Render

Begin the response immediately with the rendered report — no preamble. Degraded-state notes render inside the affected section, never as a preamble.

## Output Format

**1. Header** — `## Credit Risk Assessment: [Company] ([RIC]) | Traffic-Light: 🟢/🟡/🔴`

Overall light is the majority color across flagged metrics. **If two or more colors tie for the highest count, render the most conservative tied color (Red > Amber > Green)** — a 2-2-2 split renders Red.

**2. Metrics Dashboard** — table: Category | Signal | Metric Value | Peer Median | Interpretation. One row each for Leverage, Coverage, Liquidity, Profitability, Altman Z, Quality Trend.

**2a. Verdict sensitivity** (one line) — state the Altman Z's nearest band boundary (2.99 Safe/Grey or 1.81 Grey/Distress) and the arithmetic flip condition. Example: "Altman Z = 2.85 sits in the Grey Zone, 0.14 below the 2.99 Safe threshold; a rise above 2.99 moves this leg to Safe." **Scope: the Altman band only** — the header traffic light is a multi-metric majority vote, not a single published numeric cutoff, and is out of scope for this line.

**3. Solvency Assessment** (narrative) — from `get_financial_analysis`, including accruals quality. High accruals (earnings not backed by cash) are a red flag independent of traditional credit metrics. If unavailable: `[Solvency assessment unavailable]`.

**4. Key Flags** (bullets) — every RED and AMBER flag with a one-line explanation citing the specific threshold breached.

**5. Quality Trend** (one sentence) — 52-week trajectory plus interpretation.

**6. Macro Context** (one sentence) — regime from `get_telemetry` plus its credit implication.

**7. Currency** (one line) — `Currency: figures as reported by source data; no base-currency conversion applied.`

Render the AI-interaction disclosure per the conventions skill §9.2 immediately above the disclaimer, then the standard disclaimer verbatim from the conventions skill §9.1.

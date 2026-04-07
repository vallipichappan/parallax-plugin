---
description: Macro outlook for any country or market — indicators, sectors, rates, FX, telemetry
argument-hint: "[country or market name]"
---

# Macro Outlook

Market names are case-sensitive. If unsure, call `list_macro_countries` first.

1. `macro_analyst` with market name only → overview (regime, headline signals)
2. Drill in with component as needed:

| Question | Component |
|---|---|
| Economic indicators | `macro_indicators` |
| Rates / bonds | `fixed_income` |
| Currency | `currency` |
| Sector positioning | `sectors` or `sector_positioning` |
| Short-term signal | `tactical` |
| Factor scores | `factors` |
| News | `news` |

3. For today's live market snapshot: `get_telemetry` (~15–30s async)

**Output:** Regime → Key signals → Sector implications → Rates/FX → Tactical bias.

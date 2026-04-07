---
description: Macro economic outlook for any country or market — indicators, sectors, fixed income, FX, and telemetry
argument-hint: "[country or market name, e.g. United States, Japan, Eurozone]"
---

# Macro Outlook Command

Get a structured macro view for a country or market — covering economic indicators, sector positioning, fixed income, currency, and daily market telemetry.

## Workflow

### Step 1: Find the right market name
Market names are case-sensitive. If unsure, call `list_macro_countries` first to get the exact name.

### Step 2: Get the overview
Call `macro_analyst` with just the market name (no component). This returns a concise overview — regime, headline risks, and key signals.

### Step 3: Drill into what the user needs
Based on the user's question, call `macro_analyst` again with specific components:

| User question | Component to request |
|---|---|
| "What are the economic indicators?" | `macro_indicators` |
| "How's the bond market / rates?" | `fixed_income` |
| "What's happening with the currency?" | `currency` |
| "Which sectors look good?" | `sectors` or `sector_positioning` |
| "What's the tactical signal?" | `tactical` |
| "What's in the news?" | `news` |
| "What do factor scores look like?" | `factors` |
| "How's liquidity?" | `liquidity` |

### Step 4: Daily telemetry (optional)
For today's live market snapshot — regime, baskets, signals across 400+ instruments — call `get_telemetry`. This takes 15-30 seconds.

### Step 5: Synthesize
Present the macro brief:
1. **Regime** — expansion/contraction, risk-on/off
2. **Key signals** — what's supportive, what's a headwind
3. **Sector implications** — what sectors this environment favors
4. **Fixed income / FX** — rates direction, currency trend
5. **Tactical view** — near-term positioning bias

## Tips
- Always start with the overview before drilling into components
- Telemetry is async (~15-30s) — let the user know it's processing
- If the user asks about a specific country and you're unsure of the name, call `list_macro_countries` first

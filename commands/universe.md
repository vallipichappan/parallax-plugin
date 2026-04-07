---
description: Build a thematic stock universe from a natural language investment idea
argument-hint: "[investment theme, e.g. 'AI infrastructure companies with strong balance sheets']"
---

# Universe Builder Command

Turn a natural language investment theme into a ranked list of matching stocks, screened from 65,000+ companies.

## Workflow

### Step 1: Clarify the theme (if vague)
If the user's description is broad (e.g. "tech stocks"), ask one clarifying question:
- "Any geographic or market cap constraints?"
- "Any factor preferences — e.g. quality bias, value tilt, momentum?"

### Step 2: Build the universe
Call `build_stock_universe` with the user's query. This searches company descriptions semantically and returns ranked results.

### Step 3: Score the candidates
For the top results, call `quick_portfolio_scores` to get instant factor scores across the shortlist. This helps triage quality vs momentum vs value names quickly.

### Step 4: Deep dive on standouts
For the most interesting names, call `get_peer_snapshot` to understand how each ranks within its own peer group.

### Step 5: Present the universe
Structure the output as:
1. **Theme summary** — what the search captured, coverage stats
2. **Ranked candidates** — top 10-15 names with sector, market cap, brief description
3. **Factor profile** — which names score best on quality, value, momentum
4. **Suggested portfolio** — a weighted starting point if the user wants to act on it
5. **What to watch** — key risks or gaps in the universe

## Tips
- More specific queries return better results: "profitable cloud infrastructure companies in the US" beats "tech"
- After building the universe, the user can pass the holdings to `/portfolio` for a full construction analysis
- If the user wants ETFs instead of individual stocks, redirect to `/etf` with a search query

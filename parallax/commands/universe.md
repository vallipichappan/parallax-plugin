---
description: Build a thematic stock universe from a natural language investment idea
argument-hint: "[investment theme, e.g. 'profitable AI infrastructure companies']"
---

# Universe Builder

1. `build_stock_universe` with the user's query (searches 65K+ company descriptions)
2. `quick_portfolio_scores` on top results for instant factor triage
3. `get_peer_snapshot` on standout names for peer-relative context

**Output:** Theme summary → Ranked candidates (top 10–15) → Factor profile → Suggested starting weights.

Tip: specific queries return better results. "Profitable cloud infrastructure US" beats "tech".
Pass the results to `/portfolio` for a full construction analysis.

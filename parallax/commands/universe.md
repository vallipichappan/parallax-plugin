---
description: Build a scored portfolio from a natural language investment thesis
argument-hint: "[investment theme, e.g. 'profitable AI infrastructure companies']"
---

# Universe Builder

## Step 1 — Build Universe

`build_stock_universe` with the user's thesis as query (searches 65K+ company descriptions).

## Step 2 — Score Top Picks

For top N results (default 10): call `get_peer_snapshot` for each in parallel to get factor scores.

## Step 3 — Rank & Select

Re-rank candidates by total score (universe tool ranks by relevance, not quality). Select top 5-8 for the portfolio.

## Step 4 — Redundancy Check

`check_portfolio_redundancy` on proposed equal-weight allocation. Identify sector concentration and industry overlap.

## Step 5 — Optimize Weights

Adjust weights based on scores, redundancy flags, and sector balance. Call `quick_portfolio_scores` on final allocation to verify factor profile.

## Step 6 — Validate (conditional)

`analyze_portfolio` on the final allocation to confirm it behaves as intended. If response is truncated (>180K chars), rely on Step 4-5 outputs for validation.

## Output

- **Investment Thesis** — restate and refine the user's intent
- **Universe Built** — how many candidates, key sectors
- **Selected Holdings** — table: symbol, name, sector, total score, weight, key factor strengths
- **Portfolio Factor Profile** — VALUE, QUALITY, MOMENTUM, DEFENSIVE scores
- **Redundancy Notes** — any overlap flagged and how resolved
- **Implementation Notes** — liquidity, position sizing, suggested rebalance frequency

Tip: specific queries return better results. "Profitable cloud infrastructure US" beats "tech".

After presenting results, ask: "Would you like me to run a portfolio health check on these holdings?" If yes, pass the final allocation to `/parallax:portfolio`.

*"These are analytical outputs based on Parallax factor scores, not investment advice."*

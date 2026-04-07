# Parallax Plugin for Claude

Institutional-grade investment research inside Claude. Powered by the [Parallax](https://chicago.global) platform.

## What it does

Connects Claude to the full Parallax data platform — stock analysis, portfolio construction, ETF intelligence, macro outlook, and thematic stock universe building — via MCP.

## Install

```bash
claude plugin install parallax
```

Or add the marketplace and install:

```bash
claude plugin marketplace add your-org/parallax-plugin
claude plugin install parallax@parallax-plugin
```

## Commands

| Command | What it does |
|---|---|
| `/stock [ticker]` | Full research brief — scores, peers, financials, news, analyst views |
| `/portfolio [holdings]` | Portfolio analysis — factor exposure, concentration, redundancy |
| `/etf [ticker or theme]` | ETF research, comparison, overlap, and search |
| `/macro [country]` | Macro outlook — indicators, sectors, fixed income, FX |
| `/universe [theme]` | Build a thematic stock universe from natural language |
| `/deep-dive [ticker]` | Deep fundamental + technical analysis |

## Skills (auto-applied)

Claude draws on these automatically — no command needed:

- **parallax-scoring** — Interprets factor scores (Quality, Value, Momentum, Defensive, Tactical)
- **symbol-format** — Ensures correct RIC format for stocks, plain tickers for ETFs
- **async-jobs** — Handles long-running analysis jobs gracefully
- **tool-selection** — Routes questions to the right tool

## Authentication

The MCP server requires a Parallax API key. Set it in your environment:

```bash
export PARALLAX_API_KEY=your_key_here
```

Or add it to your `.env.local` when running locally.

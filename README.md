# Parallax Plugin for Claude

Institutional-grade investment research inside Claude. Powered by the [Parallax](https://chicago.global) platform.

## Setup (one time)

```bash
export PARALLAX_API_KEY=your_key_here
claude plugin marketplace add vallipichappan/parallax-plugin
claude plugin install parallax@parallax-plugin
```

Then start Claude:

```bash
claude
```

## Commands

| Command | What it does |
|---|---|
| `/parallax:stock [ticker]` | Research brief — scores, peers, financials, news, analyst views |
| `/parallax:portfolio [holdings]` | Portfolio analysis — factor exposure, concentration, redundancy |
| `/parallax:etf [ticker or theme]` | ETF research, comparison, overlap, and search |
| `/parallax:macro [country]` | Macro outlook — indicators, sectors, rates, FX |
| `/parallax:universe [theme]` | Build a thematic stock universe from natural language |
| `/parallax:deep-dive [ticker]` | Deep fundamental + technical analysis |

## Examples

```
/parallax:stock AAPL
/parallax:portfolio AAPL 50%, MSFT 50%
/parallax:etf SPY QQQ
/parallax:etf high quality tech ETFs
/parallax:macro United States
/parallax:universe profitable AI infrastructure companies
/parallax:deep-dive TSLA
```

You can also ask naturally — skills fire automatically:

```
tell me about Microsoft
analyze my portfolio: AAPL 50%, GOOGL 50%
what ETFs overlap between VOO and VTI?
```

## Permissions

Claude will prompt for tool approval on first use. Press **a** to allow always for that tool, or run with auto-approval:

```bash
claude --allowedTools "mcp__parallax__*"
```

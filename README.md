# Parallax Plugin for Claude

Institutional-grade investment research inside Claude. Powered by the [Parallax](https://chicago.global) platform.

## Setup (one time)

**1. Add your API key** (get one at [chicago.global](https://chicago.global)):

```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc) for persistence:
export PARALLAX_API_KEY=your_key_here
```

**2. Install the plugin:**

```bash
claude plugin marketplace add vallipichappan/parallax-plugin
claude plugin install parallax@parallax-plugin
```

**3. Start Claude:**

```bash
claude
```

## Commands

| Command | What it does |
|---|---|
| `/parallax:stock [ticker]` | Research brief — scores, peers, financials, macro context, news, analyst views |
| `/parallax:portfolio [holdings]` | Portfolio analysis with health flags, drill-down, and advisor mode |
| `/parallax:etf [ticker or theme]` | ETF research, comparison, overlap, and search |
| `/parallax:macro [country]` | Macro outlook — regime, indicators, sectors, rates, FX, equity opportunities |
| `/parallax:universe [theme]` | Build a scored portfolio from a natural language investment thesis |
| `/parallax:deep-dive [ticker]` | Deep fundamental + technical analysis with AI assessment |
| `/parallax:screen [mode] [ticker]` | Shariah compliance screen (halal) or forensic earnings quality analysis |
| `/parallax:scenario [event] portfolio=[...]` | Event-driven exposure analysis — what's at risk, what to rotate into |
| `/parallax:rebalance [holdings]` | Prioritized trade recommendations with health flags and replacements |
| `/parallax:investor [profile] [ticker]` | AI investor profile — Buffett factor match, Greenblatt Magic Formula, Klarman margin of safety, Soros macro regime, or consensus across all four |

## Examples

```
/parallax:stock AAPL
/parallax:portfolio AAPL 50%, MSFT 50%
/parallax:etf SPY QQQ
/parallax:etf high quality tech ETFs
/parallax:macro United States
/parallax:macro compare US Japan Europe
/parallax:universe profitable AI infrastructure companies
/parallax:deep-dive TSLA "Is the robotaxi thesis priced in?"
/parallax:screen halal AAPL
/parallax:screen quality TSLA.O
/parallax:scenario "Fed cuts 50bps" portfolio=AAPL 30%, MSFT 20%, XOM 50%
/parallax:rebalance AAPL 40%, MSFT 40%, GOOGL 20% target="improve quality"
/parallax:rebalance AAPL MSFT GOOGL NVDA          (no weights = watchlist surveillance mode)
/parallax:investor AAPL                            (consensus across all 4 profiles)
/parallax:investor buffett AAPL                    (Buffett factor profile)
/parallax:investor greenblatt                      (Magic Formula universe screen)
/parallax:investor klarman BRKb.N                  (margin of safety check)
/parallax:investor soros                           (regime themes + trade ideas)
/parallax:investor consensus AAPL,MSFT,KO          (basket consensus)
```

You can also ask naturally — skills fire automatically:

```
tell me about Microsoft
analyze my portfolio: AAPL 50%, GOOGL 50%
what ETFs overlap between VOO and VTI?
is Apple stock halal?
what if China tariffs hit my portfolio?
check earnings quality of Tesla
compare Apple vs Microsoft
is Apple a Buffett stock?
what do the legends think about NVDA?
run the Magic Formula screen
margin of safety check on Tesla
```

## Permissions

Claude will prompt for tool approval on first use. Press **a** to allow always for that tool, or run with auto-approval:

```bash
claude --allowedTools "mcp__parallax__*"
```

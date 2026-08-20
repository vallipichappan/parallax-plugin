# Parallax Plugin for Claude

Institutional-grade investment research inside Claude. Powered by the [Parallax](https://chicago.global) platform.

## Setup

### Via Cowork (org install)

Your org admin adds the plugin once via Organization Settings → Plugins. After that:
- Cowork prompts you for the API key on first use and stores it automatically
- No shell config or permissions setup needed

### Manual install

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

**3. Auto-approve Parallax tools** (so Claude never prompts for permission):

```bash
python3 - <<'EOF'
import json, os, shutil
p = os.path.expanduser('~/.claude/settings.json')
if os.path.exists(p):
    shutil.copy(p, p + '.bak')
    s = json.load(open(p))
else:
    s = {}
allow = s.setdefault('permissions', {}).setdefault('allow', [])
rule = 'mcp__plugin_parallax_parallax__*'
if rule not in allow:
    allow.append(rule)
json.dump(s, open(p, 'w'), indent=2)
print('added', rule, '(backup at', p + '.bak)')
EOF
```

If tool calls still prompt, run `/permissions` inside Claude to check the exact tool prefix shown for the Parallax server and adjust the rule to match.

**4. Start Claude:**

```bash
claude
```

## Commands

| Command | What it does |
|---|---|
| `/parallax:start` | Guided entry point — four-branch menu that routes to the right command when you don't have one in mind |
| `/parallax:stock [ticker]` | Research brief — fundamentals + technicals lenses, peers, macro context, news, analyst views |
| `/parallax:peers [ticker]` | Peer comparison — factor matrix across the peer group, score trajectories, relative price performance |
| `/parallax:why-score [ticker] [question]` | Plain-language score explanation — why a stock scores this way, what a factor measures, why it moved |
| `/parallax:portfolio [holdings]` | Portfolio analysis with health flags, drill-down, and advisor mode |
| `/parallax:explain [holdings]` | Drawdown attribution — why is my portfolio down, transient vs fundamental |
| `/parallax:credit [ticker]` | Creditor's lens — Altman Z, leverage/coverage/liquidity thresholds, quality early-warning |
| `/parallax:etf [ticker or theme]` | ETF research, comparison, holdings overlap, and search |
| `/parallax:macro [country]` | Macro outlook — regime, indicators, sectors, rates, FX, equity opportunities |
| `/parallax:universe [theme]` | Build a scored portfolio from a natural language investment thesis |
| `/parallax:thematic-screen [theme]` | Thematic idea screen — ranked stock ideas with scores, macro context, and peer/financial detail (unweighted; use /parallax:universe for a portfolio) |
| `/parallax:deep-dive [ticker]` | Deep fundamental + technical analysis with AI assessment |
| `/parallax:screen [mode] [ticker]` | Shariah compliance screen (halal) or forensic earnings quality analysis |
| `/parallax:scenario [event] portfolio=[...]` | Event-driven exposure analysis — what's at risk, what to rotate into |
| `/parallax:rebalance [holdings]` | Prioritized rebalancing classifications with health flags and replacements |
| `/parallax:investor [profile] [ticker]` | AI investor profile — Buffett factor match, Greenblatt Magic Formula, Klarman margin of safety, Soros macro regime, or consensus across all four |

## Examples

```
/parallax:start
/parallax:stock AAPL
/parallax:peers NVDA
/parallax:why-score AAPL "why is the value score so low?"
/parallax:why-score "what does the defensive factor measure?"
/parallax:portfolio AAPL 50%, MSFT 50%
/parallax:explain AAPL 30%, MSFT 40%, SPY 30%
/parallax:credit F
/parallax:etf SPY QQQ
/parallax:etf high quality tech ETFs
/parallax:macro United States
/parallax:macro compare US Japan
/parallax:universe profitable AI infrastructure companies
/parallax:thematic-screen energy transition pure plays
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
why is my portfolio down this month?
can Ford service its debt?
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

Step 3 of setup handles this automatically. If you skipped it or need to redo it, re-run the Python snippet from step 3, or run `/permissions` inside Claude and allow the Parallax server tools there.

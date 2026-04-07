---
description: Analyze a portfolio — factor exposure, risk, concentration, redundancy
argument-hint: "[ticker weight, ticker weight, ... e.g. AAPL 30%, MSFT 20%, SPY 50%]"
---

# Portfolio Analysis

Parse holdings into `{symbol, weight}` pairs. Equal-weight if no weights given. Stocks need RIC format (AAPL.O); ETFs plain (SPY).

**Pick the right tool:**
- Stocks only → `analyze_portfolio` (lens: performance / risk / quality / concentration / holdings / attribution)
- Mixed stocks + ETFs → `analyze_mixed_portfolio` (expands ETFs to underlying for true factor exposure)
- Quick check → `quick_portfolio_scores` (instant weighted factor scores)

Then run `check_portfolio_redundancy` to flag sector concentration, industry duplicates, and factor clusters.

**Output:** Factor profile → Top contributors → Concentration risks → Redundancy → 2-3 construction suggestions.

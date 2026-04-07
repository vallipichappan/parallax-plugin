---
description: Analyze a portfolio — factor scores, risk, concentration, redundancy, and attribution
argument-hint: "[ticker weight, ticker weight, ... e.g. AAPL 30%, MSFT 20%, SPY 50%]"
---

# Portfolio Analysis Command

Analyze a portfolio of stocks and/or ETFs for factor exposure, risk, and construction quality.

## Workflow

### Step 1: Parse holdings
Extract tickers and weights from the user's input. If weights aren't given, assume equal weight.

Convert stock tickers to RIC format (AAPL → AAPL.O). Leave ETF tickers as-is (SPY, QQQ).

### Step 2: Choose the right tool
- **Stocks only** → `analyze_portfolio` (lens: performance, risk, quality, concentration, holdings, or attribution)
- **ETFs only or mixed stocks+ETFs** → `analyze_mixed_portfolio` (ETFs are expanded to underlying holdings for true factor exposure)
- **Quick factor check** → `quick_portfolio_scores` (instant, returns VALUE/QUALITY/MOMENTUM/DEFENSIVE)

### Step 3: Check construction quality
Call `check_portfolio_redundancy` to flag:
- Sector concentration
- Industry duplicates
- Factor clusters (holdings that move together)

### Step 4: Synthesize
Present the portfolio brief:
1. **Factor profile** — weighted scores and what they imply (growth tilt, defensive posture, etc.)
2. **Top contributors** — what's driving the overall character
3. **Concentration risks** — sectors, industries, or factors over-represented
4. **Redundancy** — overlapping names that add duplication without diversification
5. **Recommendations** — 2-3 actionable suggestions to improve construction

## Tips
- If the user has ETFs and wants true underlying exposure, always use `analyze_mixed_portfolio`
- For a quick sanity check before a meeting, `quick_portfolio_scores` is instant
- If the user asks about specific time periods, pass `start_date` to `analyze_portfolio`
- Benchmarks: SP500, NASDAQ, RUSSELL2000, or a custom RIC

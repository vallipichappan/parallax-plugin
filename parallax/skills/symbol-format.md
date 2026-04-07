---
name: symbol-format
description: Correct symbol format for Parallax API calls — RIC for stocks, plain ticker for ETFs.
---

# Symbol Format

**Stocks → RIC format** (exchange suffix required):
- NASDAQ: AAPL.O, MSFT.O, GOOGL.O, TSLA.O
- NYSE: JPM.N, BAC.N
- London: VOD.L · Tokyo: 9984.T · Hong Kong: 0700.HK

**ETFs → plain ticker** (no suffix): SPY, QQQ, IWM, ARKK, VTI

**Mixed portfolios** use both in the same holdings array:
`[{"symbol": "AAPL.O", "weight": 0.30}, {"symbol": "SPY", "weight": 0.70}]`

**When in doubt:** call `get_company_info` with a plain ticker or company name — it resolves to the correct RIC. Accepts comma-separated input for batches.

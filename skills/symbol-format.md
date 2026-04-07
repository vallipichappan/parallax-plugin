---
name: symbol-format
description: |
  Rules for formatting stock tickers and ETF symbols correctly for Parallax API calls.

  Use when: any tool call requires a symbol parameter to ensure the correct format is used.
---

# Symbol Format Guide

## Stock Symbols: RIC Format

Parallax stock tools require **Reuters Instrument Code (RIC)** format, not plain tickers.

### Common conversions

| Plain ticker | RIC format |
|---|---|
| AAPL | AAPL.O |
| MSFT | MSFT.O |
| GOOGL | GOOGL.O |
| TSLA | TSLA.O |
| JPM | JPM.N |
| BAC | BAC.N |
| 0700.HK | 0700.HK (already RIC) |
| 9984.T | 9984.T (already RIC) |

**Exchange suffixes:**
- `.O` — NASDAQ
- `.N` — NYSE
- `.L` — London Stock Exchange
- `.T` — Tokyo Stock Exchange
- `.HK` — Hong Kong Stock Exchange
- `.SS` / `.SZ` — Shanghai / Shenzhen

### How to resolve unknown symbols
Use `get_company_info` with a plain ticker (AAPL) or company name. It accepts both formats and returns the canonical RIC.

For multiple stocks: `get_company_info` accepts comma-separated tickers.

## ETF Symbols: Plain Format

ETF tools use **plain ticker format** — no exchange suffix.

✓ SPY, QQQ, IWM, ARKK, VTI, VOO
✗ SPY.O, QQQ.N (wrong — don't add suffix)

Tools that accept plain ETF format:
- `get_etf_snapshot`
- `get_etf_holdings`
- `search_etfs`
- `get_etf_price_history`
- `compare_etfs`
- `get_etf_overlap`

## Mixed Portfolios

When calling `analyze_mixed_portfolio`, stocks need RIC format and ETFs need plain format in the same holdings array.

```json
[
  {"symbol": "AAPL.O", "weight": 0.30},
  {"symbol": "MSFT.O", "weight": 0.20},
  {"symbol": "SPY", "weight": 0.50}
]
```

## When in Doubt
Call `get_company_info` first. It resolves ambiguous inputs and returns the correct RIC.

---
name: async-jobs
description: |
  How to handle async/long-running Parallax tools that return job IDs instead of immediate results.

  Use when: calling get_stock_report, get_technical_analysis, get_financial_analysis, get_assessment, or get_telemetry.
---

# Handling Async Jobs

Some Parallax tools are long-running and return a `job_id` instead of results immediately. Always handle these correctly.

## Async tools and their typical wait times

| Tool | Typical time | Notes |
|---|---|---|
| `get_technical_analysis` | 15-30s | Cached after first run |
| `get_telemetry` | 15-30s | Daily snapshot, cache by date |
| `get_financial_analysis` | 2-5 min | Deep Palepu framework analysis |
| `get_stock_report` | 1-2 min | Generates PDF + HTML report |
| `get_assessment` | ~3 min | Perplexity AI deep research |

## Polling pattern

1. Call the async tool — it returns `{"job_id": "abc123", "status": "pending"}`
2. Wait a moment, then call `check_job_status` with that job_id
3. Keep checking until `status` is `"completed"` or `"failed"`
4. On `completed`: the result is in the `result` field of the status response
5. On `failed`: report the error and offer to retry

## User communication

Always tell the user upfront when something is async:
- "This analysis takes about 2-3 minutes — I'll start it now and update you when it's ready."
- "The technical analysis is processing (~20 seconds)..."

Don't leave the user wondering why there's a delay.

## Parallelism

When doing a deep dive that requires multiple async calls, kick them all off before polling any of them. This minimises total wait time.

Example: start `get_financial_analysis` and `get_technical_analysis` simultaneously, then poll both.

## Cached results

Many async tools cache results. If the same symbol was analyzed recently, results return immediately (status already `completed`). Always check status before assuming a long wait.

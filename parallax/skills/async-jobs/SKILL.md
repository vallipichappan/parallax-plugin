---
name: async-jobs
description: How to handle Parallax tools that submit a job and wait for it server-side before returning.
---

# Async Jobs

Eight Parallax tools submit a job and the MCP server waits for it internally, returning the finished result in the same call. Callers normally do not poll at all.

| Tool | Server wait cap | Notes |
|---|---|---|
| `get_stock_report` | 300s | |
| `get_etf_report` | 300s | |
| `get_financial_analysis` | 300s | |
| `get_assessment` | 300s | Always the deep tier; typical wait ~3 min |
| `analyze_portfolio` | 180s | |
| `get_news_synthesis` | 150s | |
| `get_technical_analysis` | 120s | |
| `build_stock_universe` | 120s | Check the original job first; a narrower retry only after a failure, as a new billed query (5 credits) — see Failure and Timeout Handling |

`get_telemetry` also waits internally (120s cap), but it is billed and described as a normal tool: callers normally see an inline result. On its rare timeout it returns a "still running" reply with a `job_id` like the tools above; handle it the same way and do not re-call it.

## Pattern

Call the tool **once**. The server waits for the job and returns the finished result in that same call. Use the result directly.

## Failure and Timeout Handling

Any `success: false` reply from an async tool ends that section. **Never re-call the original async tool**: a re-call submits a brand-new job, which bills again if it completes. This covers every failure, not only timeouts.

| Reply | Action |
|---|---|
| `error` says "still running … check later with check_job_status (job_id: …)" | Call `check_job_status` with that `job_id`, never the original tool. Read its `status` field (next table). |
| Any other `success: false` (job failed, completed with no result, upstream error) | Render "Analysis unavailable" for that section. Do not re-call. |

`check_job_status` replies:

| Reply | Meaning | Action |
|---|---|---|
| `success: true`, `status: "completed"` | Done | Use the `result` field. |
| `success: true`, `status` is `pending`, `queued`, `running` or `processing` | Not done | A `success: true` reply here does NOT mean the result is ready. You may check once more after the other sections are rendered; if still not done, render "Analysis pending — ask me to check job <job_id> later." |
| `success: false`, `status: "failed"`, or "completed with no result" | Failed | Render "Analysis unavailable." |
| `success: false`, "not found or expired" | Expired | Render "Analysis unavailable — job expired." A later check cannot succeed. |

Use at most two `check_job_status` calls per job in one response. There is no way to sleep between calls, so space them by doing other work in between, not back to back.

**`build_stock_universe` is the one designed exception.** On a "still running" reply, run one `check_job_status` on the returned `job_id`. If it is still pending, report the `job_id` and offer to check later; never start a second job while the first runs. Only if the job failed, run one narrower query. That narrower query is a new billed call (5 credits); say so, and run it at most once.

`check_job_status`'s own description says the same: async tools already poll internally, and it should only be called if a tool returned a `job_id` without a result.

## Parallelism and Latency

Issue independent async calls in one parallel batch, so their server-side waits overlap. Never chain async calls serially; chaining adds the caps together.

A parallel batch returns only when its slowest call returns, up to that tool's cap (300s for reports, assessment and financial analysis). "Never blocks the rest of the output" therefore means: an async failure or timeout never stops the other sections from rendering. It does not mean instant results arrive before the async ones in the same batch. When a command says to start a later batch "without waiting" for an async tool, put that async tool in its own batch alongside the later work, not in the first batch with the instant identity calls.

## Caching

Many tools cache results. If the same symbol was run recently, the result returns immediately.

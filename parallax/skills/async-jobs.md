---
name: async-jobs
description: How to handle Parallax tools that return a job_id instead of immediate results.
---

# Async Jobs

Some tools are long-running and return `{"job_id": "...", "status": "pending"}` immediately.

| Tool | Typical wait |
|---|---|
| `get_technical_analysis` | 15–30s |
| `get_stock_report` | 1–2 min |
| `get_financial_analysis` | 2–5 min |
| `get_assessment` | ~3 min |

Note: `get_telemetry` is synchronous despite its size — it returns inline, no polling needed. Use the `fields` parameter to restrict the response (it's 60KB+ otherwise).

**Pattern:** call the tool → poll `check_job_status` until `completed` or `failed` → result is in the `result` field.

**Parallelism:** kick off multiple async jobs before polling any of them — minimises total wait.

**Caching:** many tools cache results; if the same symbol was run recently, status returns `completed` immediately.

Always tell the user upfront when something is async and approximately how long it will take.

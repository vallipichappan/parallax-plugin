# Parallax vs. Process Plugins: Positioning

## The Two-Column Comparison

| Dimension | Process Plugins (e.g., Anthropic financial-services) | Parallax Workflow Intelligence |
|---|---|---|
| **What it is** | Data connectors + Claude reasoning | Pre-computed scores + orchestrated workflows |
| **Session model** | Multi-session (5+ requests for coverage initiation) | Single-session (one command → structured verdict) |
| **Intelligence** | Claude derives analysis each time from raw data | Proprietary factor scores pre-computed across 65K+ companies |
| **Error handling** | Generic LLM retry | Cross-validation, fallback patterns, async-never-blocks |
| **Output** | Spreadsheets/docs the analyst interprets | Structured verdicts with health flags and prioritized actions |
| **Unique** | Comps, DCF, LBO (process tools) | Halal screening, scenario analysis, thematic universe, health flags |

## Why Single-Session Matters

Process-oriented plugins require multiple sessions: initiate coverage, wait for analysis, retrieve results, format output. Parallax delivers a structured verdict in one command — `/parallax:stock AAPL` fires 10 parallel MCP calls, resolves macro context, cross-validates company identity, applies fallback patterns, and returns a complete research brief. The user types one line and gets the answer. This is possible because the intelligence (factor scores across 65K+ companies) is pre-computed — Claude's job is orchestration and synthesis, not derivation.

## What Pre-Computed Scores Enable

Parallax scores are computed across 65,000+ companies before the session starts. This means: consistent scoring methodology across all companies, peer-relative rankings within sectors, historical score trajectories for trend analysis, and cross-validated data (company name checks, coverage thresholds). Claude doesn't need to derive quality or value metrics from raw financials each time — it gets them instantly and spends its reasoning budget on synthesis, macro context, and actionable recommendations.

## Unique Capabilities

| Capability | What it provides | Why it's unique |
|---|---|---|
| **Halal/Shariah screening** | AAOIFI/DJIM threshold compliance with purification ratios | No other Claude plugin offers Islamic finance screening |
| **Health flag system** | 5 binary flags with priority matrix for portfolio diagnostics | Structured triage, not ad-hoc analysis |
| **Event-driven scenario analysis** | Exposure ranking + rotation candidates + action plan | Forward-looking with transmission mechanism analysis |
| **Parallel batching** | 8-11 simultaneous MCP calls with explicit fallback patterns | Not generic retry — specific fallbacks per tool type |
| **Token-cost-aware routing** | Crossover points documented (e.g., `analyze_portfolio` becomes cheaper than `quick_portfolio_scores` at 6 holdings) | Cost discipline built into every workflow |

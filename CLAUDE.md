# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a **Claude Code plugin** (not an application) distributed via the plugin marketplace. It wraps the remote Parallax MCP server (`https://mcp.chicago.global/api/mcp`) with opinionated slash commands and skills so end users get structured investment-research verdicts from a single command.

There is **no build step, no test runner, and no package manager** — the repo is pure markdown + JSON config consumed directly by Claude Code.

## Layout

```
.claude-plugin/marketplace.json   Marketplace manifest (points at ./parallax)
parallax/
  .claude-plugin/plugin.json      Plugin manifest (name, version, user_config for PARALLAX_API_KEY)
  .mcp.json                       Remote MCP server config (HTTP + Bearer ${PARALLAX_API_KEY})
  commands/*.md                   12 slash commands (stock, portfolio, explain, credit, etf, macro, ...)
  skills/<name>/SKILL.md          8 shared skills commands rely on (subdirectory layout is REQUIRED —
                                  the plugin loader only discovers skills/<name>/SKILL.md, never flat files)
docs/positioning.md               Marketing/positioning reference
```

Installation for end users: `claude plugin marketplace add vallipichappan/parallax-plugin` then `claude plugin install parallax@parallax-plugin`. Requires `PARALLAX_API_KEY` env var (or Cowork-injected via `user_config`).

## Architecture: Commands Orchestrate, Skills Specify

The plugin's intelligence lives in the **interplay between commands and skills**, not in code.

- **Commands** (`parallax/commands/*.md`) are user-facing slash commands. Each one defines a workflow (tool batch, parallelism, output shape) but delegates *rules* to skills.
- **Skills** (`parallax/skills/*.md`) are non-user-facing reference documents that commands point to. They carry the cross-cutting behavior — RIC resolution, fallback policy, factor thresholds, health-flag math, token-cost routing, async polling patterns, investor-profile specs.

A command like `stock.md` will say "apply cross-validation per conventions skill" or "apply threshold per parallax-scoring skill" — so **the skill is the spec, the command is the pipeline**. When editing behavior that spans multiple commands (disclaimer text, fallback rules, RIC suffixes, verdict math), edit the skill, not the commands.

### Load-bearing skills

| Skill | Role |
|---|---|
| `conventions` | RIC resolution table, cross-validation gate, parallel vs dependent tools, fallback rules (instant/async), verbatim disclaimer. Applies to every command. |
| `tool-selection` | Decision table mapping user utterances → MCP tool or slash command. |
| `token-costs` | Per-tool token cost table + routing rules. `quick_portfolio_scores` is the default scoring path; `analyze_portfolio` is a performance-analytics product, preferred for scoring economy only at 15+ holdings. ETF tool costs are UNVERIFIED. |
| `async-jobs` | Polling pattern for `check_job_status`; which tools are async and their wait times. |
| `health-flags` | 5-flag portfolio health system, priority matrix, drill-down selection, mixed-exchange fallback. Used by `/parallax:portfolio` and `/parallax:rebalance`. |
| `parallax-scoring` | Factor definitions (Quality/Value/Momentum/Defensive/Tactical), score ranges, `explain_methodology` routing. |
| `investor-profiles` | Profile specs (Buffett/Greenblatt/Klarman/Soros), thresholds with citation DOIs, cross-validation gate, verbatim disclaimers, consensus super-majority math. |
| `asset-class-routing` | Asset-class × tool matrix (`etf_profile` as oracle), benchmark-ETF coverage table, multi-symbol fail-empty quirks, failure-handling contracts per workflow type. |

### Invariants to preserve when editing

- **Cross-validation gate is non-bypassable.** After any `get_peer_snapshot`, check the `target_company` (top-level, NOT peer-row `name` — that field is each peer's name) against `get_company_info.name`. Single-stock verdict flows refuse to render on mismatch; portfolio flows exclude the holding from aggregates and list it in a ⚠ MISMATCH table. `conventions` is the canonical statement; `investor-profiles` restates it.
- **Per-security scores are 0-10.** All thresholds (health flags, investor profiles) are 0-10 values; portfolio-aggregate surfaces may render 0-100 (score × 10). `parallax-scoring` is the canonical statement.
- **§9.2 AI-interaction disclosure is mandatory** on every output (EU AI Act Art 50, SFC/HKMA/MAS). Commands render it by reference to `conventions` §9.2 — never inline the banner text. §12 advice-boundary framing applies to every action-label table.
- **Asset-class routing precedes any price/scoring pull** over user-supplied holdings: `etf_profile` is the oracle; `export_price_series` is equity-only, `etf_daily_price` ETF-only, both fail empty. See `asset-class-routing`.
- **Disclaimers are verbatim.** `conventions` carries the general disclaimer; `investor-profiles` carries individual-profile and consensus disclaimers. When editing these, copy the existing text exactly — downstream outputs substitute investor names only.
- **Instant vs async tool policy differs.** Instant tools retry once on failure; async tools (`get_news_synthesis`, `get_assessment`, `get_technical_analysis`, `get_financial_analysis`, `get_stock_report`) never retry. Async calls must never block output.
- **MCP numeric params must not be passed explicitly.** The transport serializes `weeks`/`periods`/`limit`/`days` as strings and fails validation. Rely on server defaults (52 weeks, 4 periods). `investor-profiles` notes this; preserve the constraint when adding new workflows.
- **Soros Channel B caps verdict.** When telemetry is unavailable, `match` is unreachable — maximum is `partial_match`. Encode this in any new Soros-related flow.
- **Consensus math uses `ceil(0.75 × A)`** with `minimum_applicable_count = 3`. `M` counts full matches only, not partial_match. Do not weaken thresholds at small N.

## Authoring Changes

- **Adding a command:** create `parallax/commands/<name>.md` with frontmatter (`description`, `argument-hint`). Reference the existing skills rather than restating their rules. Update `README.md` command table and `parallax/skills/tool-selection/SKILL.md`. Bump `parallax/.claude-plugin/plugin.json` version.
- **Adding a skill:** create `parallax/skills/<name>/SKILL.md` with frontmatter (`name`, `description`) — the subdirectory layout is mandatory; flat `skills/*.md` files are never discovered by the plugin loader. Reference it from the commands that need it.
- **Changing thresholds or anchor tests** (e.g., Buffett factor cutoffs, Klarman check targets): update the skill spec, then re-verify the anchor tests listed in that skill section still hold per the tuning date noted (e.g., "Anchor tests (2026-04-06)").
- **Token-cost changes:** update `token-costs.md` table *and* the workflow cost estimates at the bottom, *and* per-command mentions if any.

## Manual Verification

There is no automated test suite. To verify a change:

1. Install the plugin locally: `claude plugin install parallax@parallax-plugin` (after `marketplace add` pointing at the local path).
2. Run the affected command against anchor tickers referenced in the skill (e.g., KO/AXP/BRKb/AAPL/NVDA for Buffett).
3. Confirm the cross-validation gate, fallback rules, and disclaimer text fire as specified.

## Releases

- Version lives in `parallax/.claude-plugin/plugin.json` (`version` field). Bump on any behavior change.
- Marketplace manifest at `.claude-plugin/marketplace.json` does not carry a version — it points at the plugin directory.
- Commits on `master` are the release trail (no tags in use as of 2026-04-24).

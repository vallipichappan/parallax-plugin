# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a **Claude Code plugin** (not an application) distributed via the plugin marketplace. It wraps the remote Parallax MCP server (`https://mcp.chicago.global/api/mcp`) with opinionated slash commands and skills so end users get structured investment-research verdicts from a single command.

There is **no build step and no package manager**. The product remains markdown and JSON consumed by Claude Code. Python standard-library tests validate the plugin contracts and perimeter scanner.

## Layout

```
.claude-plugin/marketplace.json   Marketplace manifest (points at ./parallax)
.github/workflows/validate.yml    PR gate: tests, public-safe perimeter scan, strict loader validation
parallax/
  .claude-plugin/plugin.json      Plugin manifest (name, version, userConfig for PARALLAX_API_KEY)
  .mcp.json                       Remote MCP server config (HTTP + Bearer ${PARALLAX_API_KEY})
  commands/*.md                   15 slash commands (start, stock, peers, why-score, portfolio, explain, ...)
  skills/<name>/SKILL.md          9 shared skills commands rely on (subdirectory layout is REQUIRED —
                                  the plugin loader only discovers skills/<name>/SKILL.md, never flat files)
scripts/perimeter-scan.py         Pre-push perimeter guard (see Porting, below)
tests/                            Standard-library regression and contract tests
docs/positioning.md               Marketing/positioning reference
```

Installation for end users: `claude plugin marketplace add vallipichappan/parallax-plugin` then `claude plugin install parallax@parallax-plugin`. Requires `PARALLAX_API_KEY` env var (or Cowork-injected via `userConfig`).

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
| `token-costs` | Per-tool token cost table + routing rules. `quick_portfolio_scores` is the default scoring path; `analyze_portfolio` is a performance-analytics product, preferred for scoring economy only at 15+ holdings. `etf_profile`/`etf_daily_price` priced at 1; only `etf_holdings` remains unverified. |
| `response-shapes` | Valid `fields` names for `analyze_portfolio` and `get_telemetry`. Both are **passthrough** params — an invalid name fails silently rather than erroring, so field names come from here, never from inference. |
| `async-jobs` | Polling pattern for `check_job_status`; which tools are async and their wait times. |
| `health-flags` | 5-flag portfolio health system, priority matrix, drill-down selection, mixed-exchange fallback. Used by `/parallax:portfolio` and `/parallax:rebalance`. |
| `parallax-scoring` | Factor definitions (Quality/Value/Momentum/Defensive/Tactical), score ranges, `explain_methodology` routing. |
| `investor-profiles` | Profile specs (Buffett/Greenblatt/Klarman/Soros), citation DOIs, cross-validation gate, verdict-sensitivity guard, verbatim disclaimers, consensus structure. Publishes no numeric calibration — see the invariant below. |
| `asset-class-routing` | Asset-class × tool matrix (`etf_profile` as oracle), benchmark-ETF coverage table, multi-symbol fail-empty quirks, failure-handling contracts per workflow type. |

### Invariants to preserve when editing

- **Cross-validation gate is non-bypassable.** After any `get_peer_snapshot`, check the `target_company` (top-level, NOT peer-row `name` — that field is each peer's name) against `get_company_info.name`. Single-stock verdict flows refuse to render on mismatch; portfolio flows exclude the holding from aggregates and list it in a ⚠ MISMATCH table. `conventions` is the canonical statement; `investor-profiles` restates it.
- **Per-security scores are 0-10.** Health-flag thresholds are 0-10 values; portfolio-aggregate surfaces may render 0-100 (score × 10). `parallax-scoring` is the canonical statement.
- **§9.2 AI-interaction disclosure is mandatory** on every output (EU AI Act Art 50, SFC/HKMA/MAS). Commands render it by reference to `conventions` §9.2 — never inline the banner text. §12 advice-boundary framing applies to every action-label table.
- **Asset-class routing precedes any price/scoring pull** over user-supplied holdings: `etf_profile` is the oracle; `export_price_series` is equity-only, `etf_daily_price` ETF-only, both fail empty. See `asset-class-routing`.
- **Disclaimers are verbatim.** `conventions` carries the general disclaimer; `investor-profiles` carries individual-profile and consensus disclaimers. When editing these, copy the existing text exactly — downstream outputs substitute investor names only.
- **Instant vs async tool policy differs.** Instant tools retry once on failure; async tools (`get_news_synthesis`, `get_assessment`, `get_technical_analysis`, `get_financial_analysis`, `get_stock_report`) never retry. Async calls must never block output.
- **MCP numeric params must not be passed explicitly.** The transport serializes `weeks`/`periods`/`limit`/`days` as strings and fails validation. Rely on server defaults (52 weeks, 4 periods). `investor-profiles` notes this; preserve the constraint when adding new workflows.
- **Incomplete data caps the verdict.** Any profile or workflow running on partial data is capped at `partial_match` and can never reach `match`. This is why an unavailable telemetry channel caps a Soros verdict — it is the general rule, not a Soros special case.
- **Investor-profile calibration is never published in this repo.** Scope is exactly the AI Investor Profile specs: per-profile factor cutoffs, percentile bands, anchor-test values, and the consensus super-majority constants. These are Parallax-calibrated against the engine's own score distribution, are not derivable from the cited literature, and are not part of this plugin's public surface. `/parallax:investor` expresses profile criteria by **direction** and reports **observed** values only — a target/threshold column in a profile output table means this invariant has been broken. This does **not** restrict numbers that are public by origin: health-flag cutoffs, AAOIFI Shariah ratios, published academic parameters, or analyst price targets returned by the API all stay. If a future change needs the calibration, it must be cleared upstream in `parallax-workflows`, flow through that repo's `build_bundle.py` redaction and term-scan gates, and be copied from its built `plugin/` output — never hand-authored here.

## Authoring Changes

- **Adding a command:** create `parallax/commands/<name>.md` with frontmatter (`description`, `argument-hint`). Reference the existing skills rather than restating their rules. Update `README.md` command table and `parallax/skills/tool-selection/SKILL.md`. Bump `parallax/.claude-plugin/plugin.json` version.
- **Adding a skill:** create `parallax/skills/<name>/SKILL.md` with frontmatter (`name`, `description`) — the subdirectory layout is mandatory; flat `skills/*.md` files are never discovered by the plugin loader. Reference it from the commands that need it.
- **Changing thresholds** (e.g., health-flag cutoffs, AAOIFI screen ratios): update the skill spec that owns them, then re-verify against the anchor tickers named in that section. Investor-profile cutoffs are out of scope here — see the calibration invariant above.
- **Token-cost changes:** update `token-costs.md` table *and* the workflow cost estimates at the bottom, *and* per-command mentions if any.

### Porting from `parallax-workflows`

Upstream is `github.com/bencharoenwong/parallax-workflows`. It classifies every skill in its `PERIMETER.md` and generates its own sanitized public bundle through `build_bundle.py`, which applies five protections this repo does not get for free: a tracked-files-only copy, content-anchored redaction transforms that fail the build when an anchor drifts, a fail-closed term scan, a reference-resolution gate, and an **allowlist** for shared content.

Consequences for anything ported here:

- **Copy from upstream's built `plugin/` output, never from its `skills/` sources.** The sources are pre-redaction. This is the single rule that would have prevented the calibration exposure.
- **Check `PERIMETER.md` first.** Skills marked `sanitize-required`, `internal-only`, or `claude-only` do not come across. A skill absent from that table defaults to `claude-only` by its own Process section — absence is not permission.
- **Translate, don't transplant.** Upstream calls tools as `mcp__claude_ai_Parallax__*` behind a `ToolSearch` preflight and JIT-loads `_parallax/…` by path. This plugin bundles its own `.mcp.json`, uses bare tool names, and references `parallax/skills/<name>/SKILL.md` from command prose. Ports that depend on house-view files or Python helpers cannot come across at all — this repo has no build step.
- **Upstream is not automatically right.** Several defects here were inherited by copying it. Where this repo is already correct — the `target_company` cross-validation field, 0-10 credit thresholds — do not "resync" backwards.
- **Run `python3 scripts/perimeter-scan.py` before every push.** Stage the release files first. The default scan reads their Git-index bytes, not worktree bytes. After committing, use `python3 scripts/perimeter-scan.py --source head`.

## Manual Verification

To verify a change:

1. Run `python3 -m unittest discover -s tests -p 'test_*.py'`.
2. Run `claude plugin validate --strict parallax` and validate `.claude-plugin/marketplace.json` separately.
3. Install the plugin locally: `claude plugin install parallax@parallax-plugin` after `marketplace add` points at the local path.
4. Run the affected command against a representative symbol and confirm the tool sequence fires as written.
5. Confirm the cross-validation gate, fallback rules, and disclaimer text fire as specified.
6. Stage the release candidate and run `python3 scripts/perimeter-scan.py` — exit 0 required.

**A referenced skill is a directive, not a guarantee.** Commands delegate rules by prose reference, and nothing enforces that the referenced skill was actually loaded and applied. When verifying, check that the *behavior* the skill specifies appears in the output — not merely that the command names the skill.

## Releases

- Version lives in `parallax/.claude-plugin/plugin.json` (`version` field). Bump on any behavior change.
- Marketplace manifest at `.claude-plugin/marketplace.json` does not carry a version — it points at the plugin directory.
- Commits on `master` are the release trail (no tags in use as of 2026-04-24).

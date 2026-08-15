# Codex Adversarial Review Plan

## Decision summary

The review should proceed. Two release-blocking risks already have direct code evidence:

1. `/parallax:start` applies the multi-ticker rule before portfolio, loss, and scenario rules. Weighted holdings can therefore route to `/parallax:peers`, which accepts one primary ticker.
2. `scripts/perimeter-scan.py` enumerates tracked paths and reads worktree bytes. A pre-push check must inspect the committed range or index content that will be pushed.

The current branch also has cross-validation gaps, advice-boundary conflicts, credit-input gaps, and avoidable paid calls. These are hypotheses until focused regression tests reproduce them.

**Plan quality score:** 9.4/10. The plan identifies each invariant, failure mode, fixture, assertion, resource cap, and rollback unit. Live MCP behavior remains outside the local baseline until separately authorized.

## Scope and baseline

- Repository: `/Users/bencharoenwong/parallax-plugin`
- Review target: the full plugin contract, with priority on `master...update/workflows-harmonization`
- Current branch: `update/workflows-harmonization`
- Base branch: `master`
- Branch divergence: 0 commits behind and 4 commits ahead of local `master`
- Initial worktree state: clean before this planbook was created
- Expected state after planning: only untracked `CODEX_REVIEW_PLAN.md`
- Pull request: PR 1 is open and has no reviews
- CI state: PR 1 has zero configured checks
- Repository shape: 15 command files, 9 skill files, 3 JSON manifests/configs, and one Python scanner
- Existing automation: `scripts/perimeter-scan.py`
- Existing test runner: none
- Existing build step: none
- Existing coverage configuration: none
- Existing project plans, `CONTEXT.md`, `DECISIONS.md`, `TODOS.md`, or project lessons: none found

### Review objectives

1. Prove that routing, identity checks, asset routing, fallbacks, field subsets, disclosures, and advice boundaries remain coherent.
2. Prove that the perimeter guard scans the content that can reach the remote repository.
3. Repair confirmed defects with the smallest responsible changes.
4. Reduce paid calls and serial waits without weakening output contracts.
5. Add a fast, deterministic local gate that matches this documentation-only repository.

### Explicit non-goals

- Do not change the remote Parallax MCP server or its schemas.
- Do not expose or reconstruct unpublished investor-profile calibration.
- Do not copy upstream pre-redaction source material.
- Do not change factor methodology, health thresholds, or regulatory language without separate approval.
- Do not install dependencies.
- Do not create commits, push, merge, or modify PR 1.
- Do not create or change branches without explicit branch approval.
- Do not call paid MCP tools during the local repair loop.
- Do not claim live workflow correctness from static tests alone.

## Applicable invariants

| ID | Public behavior that must hold |
|---|---|
| INV-01 | The concierge routes a payload to a command that accepts that payload shape. Specific portfolio and scenario shapes take precedence over generic ticker counts. |
| INV-02 | Every scoring result used in a verdict has an available identity oracle. A mismatch blocks a single-name verdict or excludes that holding from factor aggregates. |
| INV-03 | User-supplied holdings are classified before asset-specific price or score calls. Missing legs remain visible. |
| INV-04 | `analyze_portfolio` and `get_telemetry` use only canonical fields. Every portfolio response checks `result._meta.invalid_fields`. |
| INV-05 | Async tools are not retried. Independent async work starts as early as its actual dependencies allow. |
| INV-06 | Outputs preserve mismatch, degraded-coverage, missing-data, disclosure, and disclaimer surfaces. |
| INV-07 | Trade-related output uses analytical classifications. It contains no reader-directed trade instruction. |
| INV-08 | Numeric MCP parameters remain omitted where transport stringification breaks validation. |
| INV-09 | Token estimates reconcile with their printed call plans. Unknown costs remain labeled unknown. |
| INV-10 | The perimeter scan fails closed on incomplete configuration and scanner failures. It inspects the exact content being committed or pushed. |
| INV-11 | Plugin manifests, command frontmatter, skill frontmatter, command counts, and skill references remain loader-valid. |
| INV-12 | A performance change preserves returned sections, fallback behavior, and integrity gates. |

## Evidence-led risk matrix

| Risk class | Target and evidence | Boundary cases | Intended control |
|---|---|---|---|
| Inputs | Concierge payload precedence in `start.md:95-105` | one ticker, two tickers, weights, loss text, event plus holdings, investor name | Table-driven routing fixture |
| Inputs | Mandate and field names | empty fields, invalid field, mixed case, unknown constraint, malformed frontmatter | Static parser with explicit allowlists |
| Boundaries | Holding and fan-out caps | 0, 1, 5, 8, 10, 20, and 21 holdings | Fixture cases at each stated cutoff |
| Boundaries | Score and advice thresholds | exact cutoff, just inside, just outside, 0-10 versus 0-100 | Contract assertions against canonical skills |
| State | Perimeter source selection | clean worktree, staged secret then clean worktree, committed secret, staged deletion | Temporary Git repositories with distinct index and worktree bytes |
| State | Partial and repeated tool results | first-batch empty, instant retry, async timeout, partial portfolio response | Workflow contract fixtures with explicit end states |
| Concurrency | Async launch order | news pending, technicals pending, macro ready, assessment dependency | Dependency-graph assertions. No sleep timing. |
| Concurrency | Scanner invoked during worktree changes | index differs from worktree | Scanner reads an immutable Git object or index snapshot |
| Resources | Large portfolio and telemetry payloads | 20 holdings, combined field subsets, truncated response | Synthetic bounded payloads under 2 MB. No live large pull by default. |
| Resources | Scanner history and file set | 200 files, binary file, symlink, subprocess failure | Temporary fixtures capped at 200 files and 10 commits |
| Integration seams | Claude plugin loader | malformed JSON, missing frontmatter, flat skill path, unknown manifest field | `claude plugin validate --strict` after changes |
| Integration seams | MCP schema drift | absent `_meta`, non-empty `invalid_fields`, unavailable optional block | Recorded synthetic response shapes, then optional bounded live probe |
| Integration seams | GitHub release gate | no CI checks on PR 1 | Small standard-library test job if approved |

## Proposed tests

Each test has one distinct failure target. Tests will use Python's standard library unless the repository provides a better native mechanism.

| Test | Behavior protected | Unique failure mode | Fixture or control | Expected assertion | Why it is not redundant |
|---|---|---|---|---|---|
| T01 concierge route precedence | Specific payloads beat generic ticker counts | Weighted portfolios and loss statements route to peers | Table of representative invocations | Exact command per row | No existing test exercises routing order |
| T02 peers arity contract | `/parallax:peers` receives one primary ticker | Direct two-ticker shortcut reaches a one-ticker workflow | Extracted command metadata and route table | No route maps generic two-ticker input to incompatible arity | T01 tests outcomes; T02 tests route-target compatibility |
| T03 scoring identity coverage | Every verdict-bearing scoring path has an oracle | A command references cross-validation without scheduling `get_company_info` | Parsed command sections plus an explicit command policy map | Required oracle appears before render or exclusion | Detects missing operations in `stock`, `portfolio`, `rebalance`, and `scenario` |
| T04 portfolio mismatch semantics | Factor aggregates exclude mismatches while concentration retains original holdings | A shared exclusion rule removes weight from concentration | Canonical conventions text and command references | Both clauses remain present and non-conflicting | Protects the newly corrected denominator rule |
| T05 advice-boundary scan | Analytical commands avoid reader-directed trade instructions | `Hold or add`, `consider trim`, and `What To Do` bypass §12 | Approved-label allowlist plus targeted prohibited phrases | No direct trade instruction outside quoted source or allowed label definition | Disclosures do not detect actionable wording |
| T06 response-field contract | Every field subset uses canonical names | Silent success with omitted blocks from invalid fields | Parse literal field arrays from commands | Every field is in `response-shapes`; each portfolio call checks `_meta` | Directly targets the PR's historical defect class |
| T07 numeric-parameter guard | Broken numeric MCP arguments stay absent | A new command adds `weeks=52` or `limit=10` | Scan tool-call prose outside explanatory warnings | No forbidden explicit numeric argument | Separate from response fields and routing |
| T08 async policy contract | Async tools never retry and use wait caps | Generic instant retry text accidentally governs async calls | Canonical async set and command call sites | Each async call references poll, no retry, and fallback | Protects timeouts and duplicate paid calls |
| T09 terminal compliance order | Disclosure precedes the final disclaimer | A command omits, reverses, or renders content below terminal elements | All analytical command files | Ordered references exist exactly once | Advice wording tests do not prove disclosure order |
| T10 credit data sufficiency | Every Altman input has a named source | EBIT, revenue, retained earnings, liabilities, or market cap is unavailable | Required-variable-to-call mapping | All five X inputs map to scheduled fields or a stated halt | Cost arithmetic alone cannot detect missing accounting inputs |
| T11 token arithmetic | Printed subtotals equal listed paid calls | `credit` labels five one-token calls as four | Parsed explicit tables plus a small manual expectation map | Exact subtotal or declared range reconciles | Targets cost claims, not tool correctness |
| T12 perimeter index fidelity | Scanner checks push-bound content | Staged prohibited content passes because the worktree is clean | Temporary Git repo with divergent index and worktree | Scanner finds staged or committed content | Core release-guard regression |
| T13 perimeter fail-closed | Environmental failures return exit 2 | Empty extras, unreadable extras, failed Git subprocess, invalid repository | Temporary paths and mocked subprocess outcomes | Exit 2 with no clean claim | Distinguishes tool failure from a real finding |
| T14 perimeter pattern sensitivity | Structural checks catch supported leak shapes | Case, hyphen, prose comparator, or alternate table heading bypasses patterns | Positive and negative pattern fixtures | Positive fixtures fail; public health and AAOIFI thresholds pass | Measures scanner recall and false positives |
| T15 manifest and loader structure | Claude discovers every command and skill | Invalid JSON, missing metadata, flat skill, count drift | Repository tree and CLI validator | Strict validation passes; counts equal documentation | Loader validity is independent of workflow semantics |
| T16 reference resolution | Every command-to-skill reference resolves | Renamed or moved skill leaves prose dangling | Extract normalized skill names | Every reference maps to one `skills/<name>/SKILL.md` | Loader validation may not understand prose references |
| T17 speedup equivalence | Removed calls preserve required outputs | Call reduction drops an integrity or data section | Before-and-after dependency graph fixtures | Same required outputs and gates with fewer calls or shorter critical path | Prevents speed from weakening behavior |
| T18 bounded repeatability | Tests do not leak state or depend on timing | Temporary Git state or process output contaminates later tests | Fresh temporary directory per test; fixed environment | Three consecutive runs produce identical results | Specifically covers stateful scanner tests |

## High-priority defect hypotheses

### P0 release blockers

1. **Concierge precedence is unsafe.** `start.md:97-105` marks the rules as first-match-wins. The two-ticker rule precedes weighted holdings, drawdown, and scenario rules.
2. **The perimeter guard scans the wrong content source.** `perimeter-scan.py:60-65` lists tracked paths. Lines 139-142 and 171-174 read worktree files. A pre-push gate must inspect pushed commits or an explicitly selected index snapshot.

### P1 correctness and compliance risks

1. **Cross-validation lacks scheduled oracle calls.** `stock.md:18-28` needs `get_company_info.name`, but the main data batch omits `get_company_info`. `portfolio.md:18-22` and `rebalance.md:34-38` have the same risk for batch scoring.
2. **Scenario ground-truthing is underspecified.** `scenario.md:21-31` orders cross-validation before scoring, but it schedules neither `get_company_info` nor `get_peer_snapshot` for holdings.
3. **Explain conflicts with §12.** `explain.md:76-102` uses direct advice such as “Hold or add,” “consider trim,” and “What To Do.”
4. **Credit cannot prove every Altman input.** `credit.md:20-26` omits an income-statement call, while lines 49-54 require EBIT and revenue. The section also labels five one-token calls as four.
5. **Investor verdicts are underdetermined.** The public profile supplies directional tilts but asks the model to mark each criterion met. The decision rule needs a public, non-calibration definition or an explicit non-verdict outcome.
6. **Universe portfolio fields remain implicit.** `universe.md` requests an unspecified subset and does not state the `_meta.invalid_fields` check.
7. **Marketing counts have drifted.** `docs/positioning.md:16` says eight parallel stock calls, while `stock.md` lists nine calls before identity and asset-class probes.

## Performance and cost review

| Candidate | Classification | Current cost or delay | Proposed change | Proof required |
|---|---|---|---|---|
| Reuse detractor snapshots in `/explain` | Strict improvement | Up to three repeated one-token calls | Reuse Step 2 snapshots in Step 4 | T17 proves identical peer context and mismatch handling |
| Collapse two `/scenario` assessments | Likely strict improvement | Two ten-token async calls and two waits | Build deterministic exposure and candidates first, then call one final assessment | Confirm the first call has no unique output needed for candidate selection |
| Start credit async work after symbol resolution | Strict improvement | Financial analysis waits behind the core batch | Launch independent financial analysis, score trend, telemetry, and core financials together | Dependency graph shows no missing prerequisite |
| Start deep-dive macro work after company identity resolves | Strict improvement | Macro can wait behind unrelated async calls | Make macro depend only on company info and coverage | T17 preserves assessment inputs |
| Combine advisor-mode `analyze_portfolio` subsets | Trade-off | Two five-token calls | Test one combined valid subset | Accept only if payload stays under the cap for 5- and 20-holding fixtures |
| Combine rebalance `analyze_portfolio` subsets | Trade-off | Two five-token calls | Apply the same bounded experiment | Reject if truncation or response latency rises materially |
| Add a lightweight CI gate | Trade-off | No automated PR signal today | Run standard-library tests, strict plugin validation, and a partial public-safe scan | Keep runtime under two minutes and avoid secrets or paid services |
| Publish more investor calibration to make verdicts deterministic | Conflicts with architecture | Would simplify verdicts | Do not do this | Violates the explicit public-perimeter invariant |

## Likely weak or duplicative checks

- There are no existing test files to delete or consolidate.
- PR 1 lists manual checks, but the repository stores no reproducible result or command output.
- Disclaimer and render-discipline prose repeats across all 15 commands. Keep command references, and test the canonical terminal contract centrally.
- Cross-validation prose repeats with slight operational differences. Keep the canonical rule in `conventions`, then make each command state only its required call and mismatch action.
- Token estimates repeat in commands and `token-costs`. Keep `token-costs` canonical. Tests should flag command-local arithmetic drift.
- The two advisor `analyze_portfolio` calls duplicate transport setup. Consolidation needs payload evidence before adoption.

## Planned change list

### Phase 1: deterministic local gate

1. Add standard-library regression tests for `perimeter-scan.py`.
2. Add a small contract validator for manifests, frontmatter, references, field subsets, terminal compliance, routing precedence, and forbidden numeric parameters.
3. Add focused fixtures for routing, identity coverage, advice language, and cost arithmetic.

### Phase 2: confirmed correctness repairs

1. Reorder and narrow `/parallax:start` payload rules.
2. Add explicit identity-oracle calls where scoring output affects a verdict.
3. Define scenario classification, identity, and exclusion steps in executable order.
4. Replace direct trade instructions in `/parallax:explain` with §12 classifications and neutral status text.
5. Add the missing credit inputs or define a fail-loud path when source fields are absent.
6. Correct credit and positioning call counts.
7. Give `/parallax:universe` a canonical field subset and `_meta` check.
8. Resolve the investor-profile decision-rule gap without publishing calibration.

### Phase 3: measured speedups

1. Remove repeated peer snapshots in `/parallax:explain`.
2. Reduce `/parallax:scenario` to one assessment if dependency tests confirm equivalence.
3. Overlap credit and deep-dive independent work.
4. Benchmark combined portfolio subsets using synthetic responses first.
5. Use bounded live calls only after separate authorization for paid service use.

### Phase 4: release gate

1. Make the perimeter scanner inspect an explicit Git content source.
2. Return exit 2 for configuration, filesystem, decoding, and Git execution failures.
3. Reject an empty effective extras list in full-scan mode.
4. Add sensitivity tests before broadening structural patterns.
5. Add CI only if approved after the local gate stays fast and deterministic.

## Verification order after authorization

The repository currently documents these supported commands:

1. Focused unit target: `python3 -m unittest tests.test_perimeter_scan`
2. Contract target: `python3 -m unittest tests.test_contracts`
3. Full local suite: `python3 -m unittest discover -s tests -p 'test_*.py'`
4. Repeat state-sensitive tests three times with a shell loop that stops on first failure
5. Strict plugin validation: `claude plugin validate --strict /Users/bencharoenwong/parallax-plugin/parallax`
6. Marketplace validation: `claude plugin validate --strict /Users/bencharoenwong/parallax-plugin/.claude-plugin/marketplace.json`
7. Full perimeter scan: `python3 /Users/bencharoenwong/parallax-plugin/scripts/perimeter-scan.py`
8. Diff hygiene: `git -C /Users/bencharoenwong/parallax-plugin diff --check`
9. Final worktree review: `git -C /Users/bencharoenwong/parallax-plugin status --short`
10. Optional live workflow smoke tests only after separate paid-service authorization

No coverage threshold exists. The new suite should cover every branch in `perimeter-scan.py`. Coverage tooling will not be added solely to print a percentage.

## Execution risks and safe caps

| Risk | Control |
|---|---|
| Tests create temporary Git repositories | Use `tempfile.TemporaryDirectory`; verify cleanup after each test |
| Git configuration leaks from the host | Set local fixture identity and a minimal controlled environment |
| Scanner fixtures contain sensitive-looking strings | Use synthetic placeholders that do not match real proprietary terms |
| Tests inspect the real canary file | Point every test to a temporary extras file |
| Large payload tests consume memory | Cap each synthetic payload at 2 MB and each portfolio at 20 holdings |
| Concurrency tests become flaky | Assert dependency graphs. Do not use sleep or wall-clock thresholds |
| Repeated tests consume resources | Three runs maximum; one process per run |
| Strict validation writes caches | Check the worktree after each command and report any generated artifact |
| Live MCP validation consumes tokens | Skip by default. Use public tickers, fixed call counts, and a stated token cap after approval |
| CI introduces maintenance | Use one short workflow with pinned trusted actions and no secrets or paid calls |

## Scope challenge

1. **Existing reuse:** `response-shapes`, `conventions`, `asset-class-routing`, `async-jobs`, and `token-costs` already define most contracts. The validator should read those sources instead of creating parallel policy.
2. **Minimum diff:** Fix confirmed blockers first. Defer combined portfolio calls until payload evidence supports them.
3. **Complexity smell:** The likely repair touches more than eight files because the current contract is distributed across commands. The new validator reduces future spread. No new service or class is proposed.
4. **Distribution:** A local test suite alone will not protect PRs. CI is listed as a separate approval item because it adds repository infrastructure.
5. **Prior decisions:** No project `DECISIONS.md`, `TODOS.md`, prior review plan, or state document exists. The calibration invariant forbids the seemingly easy investor-profile fix of publishing thresholds.

## Rollback approach

- Keep each repair in a small, reviewable diff grouped by invariant.
- Revert a failed speedup independently from correctness fixes.
- Preserve current public text in Git history. Do not use destructive Git operations.
- If a contract test overreaches, narrow the test from observed false-positive evidence. Do not weaken the production invariant.
- If live behavior contradicts a static assumption, restore the prior command flow and record the exact response shape before redesign.

## Proposed branch

Recommended branch name: `review/v1.3-contract-hardening`, based on `update/workflows-harmonization`.

Branch creation is excluded until explicitly approved. Direct edits to the current PR branch also require explicit authorization under this review workflow.

## Authorization gate

Implementation requires explicit approval. Approval should state whether it includes:

1. creating `review/v1.3-contract-hardening`;
2. adding tests and repairing confirmed defects;
3. applying measured local speedups;
4. adding a GitHub Actions validation workflow; and
5. running bounded paid MCP smoke tests.

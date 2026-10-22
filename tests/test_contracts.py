from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMANDS = ROOT / "parallax" / "commands"
SKILLS = ROOT / "parallax" / "skills"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


class StructureTests(unittest.TestCase):
    def test_manifests_parse_and_inventory_matches(self) -> None:
        marketplace = json.loads(read(ROOT / ".claude-plugin" / "marketplace.json"))
        plugin = json.loads(read(ROOT / "parallax" / ".claude-plugin" / "plugin.json"))
        mcp = json.loads(read(ROOT / "parallax" / ".mcp.json"))
        command_files = sorted(COMMANDS.glob("*.md"))
        skill_files = sorted(SKILLS.glob("*/SKILL.md"))

        self.assertEqual(marketplace["plugins"][0]["source"], "./parallax")
        self.assertEqual(plugin["name"], "parallax")
        self.assertIn("userConfig", plugin)
        self.assertNotIn("user_config", plugin)
        self.assertIn("parallax", mcp["mcpServers"])
        self.assertEqual(len(command_files), 16)
        self.assertEqual(len(skill_files), 9)
        self.assertIn("16 commands", plugin["description"])

    def test_all_frontmatter_is_complete(self) -> None:
        for path in COMMANDS.glob("*.md"):
            text = read(path)
            self.assertRegex(text, r"\A---\n(?:.|\n)*?description:")
            self.assertRegex(text, r"\A---\n(?:.|\n)*?argument-hint:")
        for path in SKILLS.glob("*/SKILL.md"):
            text = read(path)
            self.assertRegex(text, rf"\A---\nname: {re.escape(path.parent.name)}\n")
            self.assertRegex(text, r"\A---\n(?:.|\n)*?description:")

    def test_named_skill_references_resolve(self) -> None:
        names = {path.parent.name for path in SKILLS.glob("*/SKILL.md")}
        command_text = "\n".join(read(path) for path in COMMANDS.glob("*.md"))
        referenced = set(
            re.findall(r"`([a-z][a-z0-9-]+)` skill", command_text)
        )
        unresolved = referenced - names

        self.assertTrue(referenced)
        self.assertEqual(unresolved, set())

    def test_ci_uses_pinned_actions_and_no_paid_services(self) -> None:
        workflow = read(ROOT / ".github" / "workflows" / "validate.yml")
        action_refs = re.findall(r"uses:\s*[^@\s]+@([^\s#]+)", workflow)

        self.assertTrue(action_refs)
        for ref in action_refs:
            self.assertRegex(ref, r"\A[0-9a-f]{40}\Z")
        self.assertRegex(workflow, r"fetch-depth:\s*0")
        self.assertIn("PARALLAX_ALLOW_PARTIAL_SCAN", workflow)
        self.assertNotIn("PARALLAX_API_KEY", workflow)
        self.assertNotIn("get_assessment", workflow)


class WorkflowContractTests(unittest.TestCase):
    def test_consensus_with_complete_profiles_still_withholds_signal(self) -> None:
        command = read(COMMANDS / "investor.md")
        skill = read(SKILLS / "investor-profiles" / "SKILL.md")
        for text in (command, skill):
            self.assertIn("Consensus unavailable — requires server-side calibration", text)
        aggregation = section(skill, "### Aggregation", "### Factor-Level Agreement")
        self.assertIn("even when every profile completed successfully", aggregation)
        self.assertNotIn("`YES` when", aggregation)
        self.assertNotIn("Consensus: YES / NO", command)

    def test_credit_fallback_uses_complete_model_and_matching_bands(self) -> None:
        text = read(COMMANDS / "credit.md")
        self.assertIn("Z' = 0.717×X1 + 0.847×X2 + 3.107×X3 + 0.420×X4 + 0.998×X5", text)
        self.assertIn("X4 = Book Equity / Total Liabilities", text)
        self.assertIn("Z' > 2.90", text)
        self.assertIn("Z' < 1.23", text)
        self.assertIn("boundaries inclusive", text)
        self.assertIn("model applicability not established", text)
        self.assertIn("Exclude an unavailable metric", text)
        self.assertIn("Z' uses 1.23/2.90", text)
        self.assertNotIn("substitute book equity for X4", text)

    def test_concierge_specific_routes_precede_generic_ticker_handling(self) -> None:
        text = read(COMMANDS / "start.md")
        loss = text.index("Holdings plus a loss statement")
        scenario = text.index("event description plus holdings")
        weighted = text.index("Holdings with weights")
        generic = text.index("Two or more unweighted tickers")

        self.assertLess(loss, generic)
        self.assertLess(scenario, generic)
        self.assertLess(weighted, generic)
        self.assertNotIn("Two or more tickers → `/parallax:peers`", text)

    def test_verdict_scoring_batches_schedule_identity_oracles(self) -> None:
        stock = section(read(COMMANDS / "stock.md"), "## Step 2", "## Step 3")
        portfolio = section(
            read(COMMANDS / "portfolio.md"),
            "### Batch A — Scoring + macro",
            "### Batch B",
        )
        rebalance = section(
            read(COMMANDS / "rebalance.md"),
            "### Batch A — Current state",
            "After Batch A completes",
        )
        scenario = section(
            read(COMMANDS / "scenario.md"),
            "## Phase 2a",
            "## Phase 2b",
        )

        for name, block in {
            "stock": stock,
            "portfolio": portfolio,
            "rebalance": rebalance,
            "scenario": scenario,
        }.items():
            with self.subTest(command=name):
                self.assertIn("`get_company_info`", block)
        self.assertIn("`get_peer_snapshot`", scenario)

    def test_cross_validation_names_the_wrapped_company_info_path(self) -> None:
        """The name oracle lives at get_company_info.data.name.

        The response wraps the company payload in a top-level `data` object, so
        there is no top-level `name` field. Verified live 2026-08-20 against
        https://mcp.chicago.global/api/mcp. A command that says
        `get_company_info.name` sends the reader looking for a field that does
        not exist, which silently weakens the non-bypassable cross-validation
        gate.
        """
        sources = sorted(COMMANDS.glob("*.md")) + sorted(SKILLS.glob("*/SKILL.md"))
        bare = re.compile(r"get_company_info\.name\b")
        cited = 0
        for path in sources:
            text = read(path)
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertIsNone(
                    bare.search(text),
                    "use get_company_info.data.name — there is no top-level name field",
                )
            if "get_company_info.data.name" in text:
                cited += 1
        self.assertGreaterEqual(cited, 8, "cross-validation field path lost its citations")

    def test_every_named_ric_suffix_is_classified_for_macro(self) -> None:
        """Each suffix the conventions skill names must be mapped or declared uncovered.

        A suffix that appears in the RIC Resolution table or the macro fallback
        line but in neither group of the macro-market table makes a candidate on
        that exchange silently lose its market tag. `.SI` and `.K` were in that
        state until 2026-08-20.

        Classification is read ONLY from the macro table's own rows and from the
        explicit "no currently-covered macro market" sentence. Surrounding prose
        does not count: an earlier version of this test read the whole section
        and was satisfied by a suffix merely being *mentioned* nearby, which
        made it unable to fail.
        """
        text = read(SKILLS / "conventions" / "SKILL.md")
        macro_table = section(
            text, "### RIC Suffix → Covered Macro Market", "## Render Discipline"
        )
        suffix = re.compile(r"`(\.[A-Z]{1,2})`")

        mapped: set[str] = set()
        for line in macro_table.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|") or stripped.startswith("|---"):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) != 2 or cells[1] in {"Market", ""}:
                continue
            mapped.update(suffix.findall(cells[0]))

        uncovered: set[str] = set()
        for line in macro_table.splitlines():
            if "no currently-covered macro market" in line:
                uncovered.update(suffix.findall(line))

        self.assertTrue(mapped, "macro-market table has no mapped suffix rows")
        self.assertTrue(uncovered, "macro-market table declares no uncovered suffixes")

        named = set(suffix.findall(text))
        self.assertGreaterEqual(len(named), 11, "suffix inventory shrank unexpectedly")
        unclassified = sorted(named - mapped - uncovered)
        self.assertEqual(
            unclassified,
            [],
            "suffixes named elsewhere but neither mapped nor declared uncovered",
        )

    def test_universe_reproducibility_is_documented_and_surfaced(self) -> None:
        """Every build_stock_universe caller must carry the point-in-time caveat.

        conventions states the requirement as "any command whose output is built
        on build_stock_universe must tell the user the result is a point-in-time
        sample". An earlier version of this test locked only thematic-screen.md,
        so six other callers silently violated a rule the canonical skill states
        — the exact drift CLAUDE.md's "the skill is the spec" rule exists to
        catch. Derive the caller list from the files themselves so a NEW caller
        cannot be added without complying.
        """
        conventions = read(SKILLS / "conventions" / "SKILL.md")
        self.assertIn("Universe Search Reproducibility", conventions)
        self.assertIn("not reproducible run-to-run", conventions)

        callers = [
            p for p in sorted(COMMANDS.glob("*.md"))
            if "build_stock_universe" in read(p)
        ]
        self.assertGreaterEqual(len(callers), 7, "caller inventory shrank unexpectedly")

        for path in callers:
            with self.subTest(command=path.name):
                self.assertIn(
                    "point-in-time",
                    read(path),
                    "calls build_stock_universe without the reproducibility caveat",
                )

        scope_note = [
            ln for ln in read(COMMANDS / "thematic-screen.md").splitlines()
            if "**Scope Note**" in ln
        ]
        self.assertEqual(len(scope_note), 1, "Scope Note line not found or duplicated")
        self.assertIn("Universe Search Reproducibility", scope_note[0])

    def test_universe_emptiness_is_decided_from_the_candidate_array(self) -> None:
        """total_matches is not a candidate count, and degraded is an integrity surface.

        Verified live 2026-08-20: build_stock_universe returned
        success=true, status="completed", total_matches=5, results_returned=0,
        companies=[], degraded=true, relaxed=["strict_theme",
        "default_liquidity_floor"]. A gate keyed on total_matches or success
        would have waved a zero-candidate result through to downstream tools.
        """
        conventions = read(SKILLS / "conventions" / "SKILL.md")
        self.assertIn("Emptiness and degradation are not what they look like", conventions)
        for token in ("`total_matches` is not a candidate count", "`degraded: true`", "`relaxed`"):
            with self.subTest(token=token):
                self.assertIn(token, conventions)

        screen = read(COMMANDS / "thematic-screen.md")
        gate = [ln for ln in screen.splitlines() if "Empty-universe gate" in ln]
        self.assertEqual(len(gate), 1, "empty-universe gate line not found or duplicated")
        self.assertIn("`companies` array only", gate[0])
        self.assertIn("never from `total_matches`", gate[0])
        self.assertIn("Degraded-universe note", screen)

    def test_thematic_screen_guards_every_downstream_call(self) -> None:
        """Steps 4 and 5 must not run with zero trusted candidates.

        Step 2 can legitimately exclude every candidate into the ⚠ MISMATCH
        table. Without this gate an all-mismatch run calls
        export_peer_comparison and get_financials with an undefined symbol.
        """
        screen = read(COMMANDS / "thematic-screen.md")
        self.assertIn("Zero-trusted-candidates gate", screen)
        gate = section(screen, "**Zero-trusted-candidates gate", "## Step 4")
        self.assertIn("skip Steps 4 and 5", gate)
        self.assertIn("undefined symbol", gate)

    def test_token_costs_asserts_no_redacted_candidate_cap(self) -> None:
        """Cost estimates must not restate a cap the profile spec no longer publishes.

        v1.3.0 redacted the Greenblatt percentile bands and its candidate cap
        from investor.md and investor-profiles. token-costs kept asserting a
        `×30` ratios pull, so the two skills disagreed on a number one of them
        is not allowed to publish. Per CLAUDE.md the calibration cannot be
        hand-authored back here, so the cost row must not name a count either.
        """
        costs = read(SKILLS / "token-costs" / "SKILL.md")
        greenblatt = [ln for ln in costs.splitlines() if "greenblatt" in ln.lower()]
        self.assertTrue(greenblatt, "greenblatt cost row missing")
        for line in greenblatt:
            with self.subTest(line=line):
                self.assertIsNone(
                    re.search(r"×\s*\d+", line),
                    "cost row names a candidate count the profile spec redacts",
                )

    def test_halal_screen_claims_no_named_standard(self) -> None:
        """The halal screen must not claim to follow a named index or standard.

        Its ratio set and cutoffs differ from published methodologies, and
        the server has no field for prohibited-activity revenue. A vendor
        label also uses a third party's mark to describe this product.
        """
        screen = read(COMMANDS / "screen.md")
        halal = section(screen, "## Halal Mode", "### Portfolio Mode")
        positioning = read(ROOT / "docs" / "positioning.md")
        for name, text in {"screen.md": screen, "positioning.md": positioning}.items():
            with self.subTest(file=name):
                self.assertNotRegex(text, r"(?i)\b(msci|aaoifi|djim)[- ]style")
                self.assertNotRegex(text, r"(?i)ratios follow the")
        self.assertIn("not a claim of conformance to any named standard", halal)
        self.assertIn('statement="income"', halal)
        self.assertNotIn('`get_financials` (statement="ratios")', halal)

    def test_greenblatt_costs_are_formulas_not_totals(self) -> None:
        """A numeric total lets a reader back-solve the redacted candidate count.

        The Greenblatt rows and the consensus rows that include them state
        formulas or sums only, never a credit total.
        """
        costs = read(SKILLS / "token-costs" / "SKILL.md")
        rows = [ln for ln in costs.splitlines() if ln.startswith("| `/parallax:investor` (greenblatt")]
        consensus = [ln for ln in costs.splitlines() if ln.startswith("| `/parallax:investor` (consensus")]
        self.assertEqual(len(consensus), 2)
        for line in consensus:
            with self.subTest(line=line):
                self.assertIsNone(re.search(r"~\s*\d", line), "a consensus total includes Greenblatt")
        profiles = read(SKILLS / "investor-profiles" / "SKILL.md")
        sequences = [ln for ln in section(profiles, "## Greenblatt Profile", "## Klarman Profile").splitlines()
                     if ln.startswith("**Tool sequence")]
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(sequences), 2)
        for line in rows + sequences:
            with self.subTest(line=line):
                self.assertIn("0.05 per candidate", line)
                self.assertIsNone(re.search(r"~\s*\d", line), "a total lets the cap be inferred")

    def test_peer_snapshot_misleading_fields_are_documented(self) -> None:
        """peer_count excludes the target and target_score is a string.

        Verified live 2026-08-20 on OXB.L: peer_count=5 while the comparison
        array held 6 rows, and target_score was "0.9/10 (Poor)". A workflow
        that trusts either field renders a wrong peer count or a string where
        a number belongs. Nothing reads them today; this locks the warning
        before something does.
        """
        conventions = read(SKILLS / "conventions" / "SKILL.md")
        self.assertIn("`peer_count` **excludes the target**", conventions)
        self.assertIn("is_target", conventions)
        self.assertIn("formatted **string**", conventions)

    def test_readme_states_how_to_save_the_key_and_the_401_symptom(self) -> None:
        """The key must be saved before first use, and the failure is silent.

        If the plugin connects with no saved key, the server answers 401 and
        Claude Code registers `authenticate` / `complete_authentication`
        placeholders instead of the real tools. That state survives a restart
        and surfaces no error naming the key. The key is a userConfig option,
        so the README must show how to save it at install and afterwards.
        """
        readme = read(ROOT / "README.md")

        self.assertIn("--config PARALLAX_API_KEY=", readme)
        self.assertIn("/plugin configure parallax@parallax-plugin", readme)

        self.assertIn("The order matters", readme)
        for token in ("401", "authenticate", "complete_authentication", "/mcp"):
            with self.subTest(token=token):
                self.assertIn(token, readme)
        self.assertIn("Troubleshooting", readme)
        self.assertIn("survive", readme.lower().replace("survives", "survive"))

    def test_mcp_header_reads_the_declared_user_config_key(self) -> None:
        """A bare ${PARALLAX_API_KEY} reads the shell env and ignores userConfig.

        Claude Code substitutes a saved userConfig value into MCP config only
        as ${user_config.KEY}. Any other form sends the user's entered key
        nowhere and the server answers 401.
        """
        plugin = json.loads(read(ROOT / "parallax" / ".claude-plugin" / "plugin.json"))
        mcp = json.loads(read(ROOT / "parallax" / ".mcp.json"))
        self.assertIn("PARALLAX_API_KEY", plugin["userConfig"])
        header = mcp["mcpServers"]["parallax"]["headers"]["Authorization"]
        self.assertEqual(header, "Bearer ${user_config.PARALLAX_API_KEY}")

    def test_explain_uses_neutral_classifications(self) -> None:
        text = read(COMMANDS / "explain.md")
        for phrase in ("Hold or add", "consider trim", "What To Do"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)
        self.assertIn("analytical classification", text)

    def test_analyze_portfolio_fields_match_the_server_enum(self) -> None:
        """analyze_portfolio `fields` is a validated enum on the MCP server.

        The list below is the server's enum at parallax-mcp f61709d
        (2026-10-22). An invalid name fails the tool call. `turnover_analysis`
        and `benchmark_prices` are not in it, though older docs listed both.
        When the server enum changes, update SERVER_FIELDS from the server.
        """
        server_fields = {
            "portfolio_parameters", "portfolio_input", "data_quality", "portfolio_summary",
            "performance_metrics", "rolling_metrics", "drawdown_analysis", "portfolio_scores",
            "concentration_metrics", "transactions", "company_info", "latest_holdings",
            "market_allocation", "sector_allocation", "currency_allocation", "company_contribution",
            "sector_contribution", "market_contribution", "time_period_returns", "monthly_returns",
            "annual_returns", "daily_summary",
        }
        response_shapes = read(SKILLS / "response-shapes" / "SKILL.md")
        valid_table = section(response_shapes, "### Valid field names", "### Names that do NOT exist")
        table_rows = "\n".join(ln for ln in valid_table.splitlines() if ln.startswith("|"))
        self.assertEqual(set(re.findall(r"`([a-z_]+)`", table_rows)), server_fields)
        before_telemetry = response_shapes.split("## `get_telemetry`", 1)[0]
        self.assertNotIn("direct passthrough", before_telemetry)
        self.assertIn("validated enum", before_telemetry)

        expected_calls = {"portfolio.md": 2, "rebalance.md": 2, "scenario.md": 1, "universe.md": 1}
        pattern = re.compile(r"fields=\[(.*?)\]", re.DOTALL)
        for filename, expected_count in expected_calls.items():
            arrays = pattern.findall(read(COMMANDS / filename))
            self.assertEqual(len(arrays), expected_count, filename)
            for array in arrays:
                fields = set(re.findall(r'"([a-z_]+)"', array))
                self.assertTrue(fields)
                self.assertTrue(fields.issubset(server_fields), (filename, fields - server_fields))

    def test_async_set_matches_the_server(self) -> None:
        """Eight tools wait server-side and return a job_id only on timeout.

        Re-calling one after a timeout submits and bills a new job, so every
        async list must name all eight, and no command may tell the model to
        poll as the normal path.
        """
        async_tools = (
            "get_stock_report", "get_etf_report", "get_financial_analysis", "get_assessment",
            "analyze_portfolio", "get_news_synthesis", "get_technical_analysis", "build_stock_universe",
        )
        async_jobs = read(SKILLS / "async-jobs" / "SKILL.md")
        fallback = section(read(SKILLS / "conventions" / "SKILL.md"), "**Async tools**", "\n\n")
        invariant = [ln for ln in read(ROOT / "CLAUDE.md").splitlines() if "Instant vs async tool policy" in ln]
        self.assertEqual(len(invariant), 1)
        for name, text in {"async-jobs": async_jobs, "conventions": fallback, "CLAUDE.md": invariant[0]}.items():
            for tool in async_tools:
                with self.subTest(source=name, tool=tool):
                    self.assertIn(f"`{tool}`", text)
        for path in COMMANDS.glob("*.md"):
            with self.subTest(command=path.name):
                self.assertNotRegex(read(path), r"(?i)\bpoll(s|ed|ing)?\b")

    def test_scores_are_not_called_sector_relative(self) -> None:
        """Scores rank a stock across all covered stocks (explain_methodology, 2026-10-22)."""
        for path in (*COMMANDS.glob("*.md"), *SKILLS.glob("*/SKILL.md"), ROOT / "docs" / "positioning.md"):
            with self.subTest(path=path.name):
                self.assertNotRegex(read(path), r"(?i)sector-relative (0-10|score)|peer-relative within the stock's sector")

    def test_telemetry_calls_use_the_standard_subset(self) -> None:
        required = {
            "regime_tag",
            "signals",
            "commentary.headline",
            "commentary.mechanism",
            "divergences",
        }
        for path in COMMANDS.glob("*.md"):
            text = read(path)
            if "`get_telemetry`" not in text:
                continue
            with self.subTest(command=path.name):
                for field in required:
                    self.assertIn(field, text)

    def test_forbidden_numeric_tool_arguments_are_absent(self) -> None:
        pattern = re.compile(r"\b(?:weeks|periods|limit|days)\s*[:=]\s*[\"']?\d")
        paths = [*COMMANDS.glob("*.md"), *SKILLS.glob("*/SKILL.md")]
        for path in paths:
            self.assertIsNone(pattern.search(read(path)), path.name)

    def test_search_etfs_is_called_with_schema_params_only(self) -> None:
        # The server schema accepts query, limit, market, currency. Anything
        # else is silently ignored, so a factor filter returns unfiltered
        # results (verified live 2026-10-16).
        paths = [*COMMANDS.glob("*.md"), *SKILLS.glob("*/SKILL.md")]
        for path in paths:
            self.assertNotRegex(read(path), r"\bmin_(?:quality|value|momentum|defensive|tactical)\b", path.name)
        routing = read(SKILLS / "asset-class-routing" / "SKILL.md")
        row = next(line for line in routing.splitlines() if line.startswith("| `search_etfs`"))
        self.assertNotRegex(row.lower(), r"discovery by[^.|]*\bscore")
        self.assertIn("has_scores: true", read(COMMANDS / "etf.md"))

    def test_token_costs_prices_every_tool_and_every_command(self) -> None:
        costs = read(SKILLS / "token-costs" / "SKILL.md")
        self.assertNotIn("UNVERIFIED", costs)
        self.assertNotRegex(costs, r"(?i)unpriced")
        self.assertNotRegex(read(COMMANDS / "etf.md"), r"(?i)unpriced")
        # Prices follow the served Cost: markers (credit contract of 2026-10-18).
        rows = {line.split("|")[1].strip(): line for line in costs.splitlines() if line.startswith("| **")}
        expected = {
            "**0 (free)**": ("search_stocks", "search_etfs", "list_macro_countries", "check_macro_health"),
            "**0.05 per symbol**": ("get_company_info", "export_price_series", "etf_daily_price", "get_financials"),
            "**0.1 per call**": ("get_peer_snapshot", "get_score_analysis", "etf_profile", "etf_holdings"),
            "**0.1 per holding**": ("quick_portfolio_scores", "check_portfolio_redundancy"),
            "**5 per call**": ("build_stock_universe", "macro_analyst", "analyze_portfolio"),
            "**10 per call**": ("get_stock_report", "get_assessment", "get_etf_report"),
        }
        for label, tools in expected.items():
            for tool in tools:
                with self.subTest(price=label, tool=tool):
                    self.assertIn(f"`{tool}`", rows[label])
        # The server bills in credits; integer token prices are the pre-2026-10-18 table.
        for path in (*COMMANDS.glob("*.md"), *SKILLS.glob("*/SKILL.md")):
            with self.subTest(unit=path.name):
                self.assertNotRegex(read(path), r"(?i)\b\d+(?:-\d+)? tokens?\b")
        workflows = costs.split("## Workflow Cost Estimates", 1)[1]
        for path in COMMANDS.glob("*.md"):
            with self.subTest(command=path.stem):
                self.assertIn(f"`/parallax:{path.stem}`", workflows)

    def test_ci_validates_with_a_cli_that_checks_user_config(self) -> None:
        # ${user_config.*} in .mcp.json is validated only from 2.1.281.
        workflow = read(ROOT / ".github" / "workflows" / "validate.yml")
        pins = re.findall(r"@anthropic-ai/claude-code@(\d+)\.(\d+)\.(\d+)", workflow)
        self.assertEqual(len(pins), 2)
        for pin in pins:
            self.assertGreaterEqual(tuple(int(part) for part in pin), (2, 1, 281))

    def test_terminal_compliance_order_is_explicit(self) -> None:
        for path in COMMANDS.glob("*.md"):
            text = read(path)
            with self.subTest(command=path.name):
                self.assertGreaterEqual(text.rfind("§9.2"), 0)
                self.assertGreater(text.rfind("§9.1"), text.rfind("§9.2"))

    def test_credit_has_all_altman_sources_and_correct_batch_cost(self) -> None:
        text = read(COMMANDS / "credit.md")
        batch = section(text, "## Batch A", "## Batch B")
        for statement in ("income", "balance_sheet", "cash_flow", "ratios"):
            self.assertIn(f'statement="{statement}"', batch)
        self.assertIn("parallel, 0.35 credits", text)
        for variable in (
            "Working Capital",
            "Retained Earnings",
            "EBIT",
            "Market Cap",
            "Total Liabilities",
            "Revenue",
        ):
            self.assertIn(variable.lower(), batch.lower())

    def test_explain_reuses_existing_peer_snapshots(self) -> None:
        step = section(read(COMMANDS / "explain.md"), "## Step 4", "## Step 5")
        self.assertIn("Reuse", step)
        self.assertNotIn("`get_peer_snapshot` and", step)

    def test_scenario_uses_one_assessment_call(self) -> None:
        text = read(COMMANDS / "scenario.md")
        self.assertEqual(text.count("`get_assessment`"), 1)

    def test_rebalance_has_atomic_sizing_gate(self) -> None:
        text = read(COMMANDS / "rebalance.md")
        self.assertIn("Atomic sizing gate", text)
        self.assertIn("do not render proposed weights", text)

    def test_investor_verdict_does_not_reconstruct_hidden_cutoffs(self) -> None:
        text = read(COMMANDS / "investor.md")
        self.assertIn("without reconstructing a cutoff", text)
        self.assertIn("render `partial_match`", text)

    def test_thematic_screen_is_not_a_portfolio_builder(self) -> None:
        text = read(COMMANDS / "thematic-screen.md")
        ranked_ideas = section(text, "**Ranked Ideas**", "- **Peer Comparison**")
        columns = section(ranked_ideas, "then table: ", ".")
        self.assertIn(
            "This is a ranked idea list, not a weighted or validated portfolio "
            "— no weights, redundancy check, or portfolio validation has been "
            "run.",
            text,
        )
        self.assertNotIn("weight", columns.lower())
        self.assertNotIn("`check_portfolio_redundancy`", text)
        self.assertNotIn("`analyze_portfolio`", text)

    def test_marketing_stock_call_count_matches_command(self) -> None:
        positioning = read(ROOT / "docs" / "positioning.md")
        step2 = section(read(COMMANDS / "stock.md"), "## Step 2", "## Step 3")
        calls = [ln for ln in step2.splitlines() if ln.startswith("| `")]
        async_tools = ("get_technical_analysis", "get_news_synthesis", "get_stock_report", "get_assessment")
        for tool in async_tools:
            with self.subTest(async_tool=tool):
                self.assertFalse(any(ln.startswith(f"| `{tool}`") for ln in calls), "async tool back in the pre-gate batch")
        self.assertIn(f"fires {len(calls)} parallel MCP calls", positioning)
        # 0.1 credits per holding against 5 flat: parity at 50 holdings.
        self.assertIn("cost the same at 50 holdings", positioning)
        self.assertNotIn("at 6 holdings", positioning)


if __name__ == "__main__":
    unittest.main()

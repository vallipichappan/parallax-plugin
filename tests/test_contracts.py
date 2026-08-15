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
        self.assertEqual(len(command_files), 15)
        self.assertEqual(len(skill_files), 9)
        self.assertIn("15 commands", plugin["description"])

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

    def test_explain_uses_neutral_classifications(self) -> None:
        text = read(COMMANDS / "explain.md")
        for phrase in ("Hold or add", "consider trim", "What To Do"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)
        self.assertIn("analytical classification", text)

    def test_analyze_portfolio_calls_use_literal_valid_fields_and_meta_check(self) -> None:
        response_shapes = read(SKILLS / "response-shapes" / "SKILL.md")
        valid_table = section(
            response_shapes,
            "### Valid field names",
            "### Names that do NOT exist",
        )
        valid = set(re.findall(r"`([a-z_]+)`", valid_table))
        expected_calls = {
            "portfolio.md": 2,
            "rebalance.md": 2,
            "scenario.md": 1,
            "universe.md": 1,
        }
        pattern = re.compile(r"fields=\[(.*?)\]", re.DOTALL)

        for filename, expected_count in expected_calls.items():
            text = read(COMMANDS / filename)
            arrays = pattern.findall(text)
            self.assertEqual(len(arrays), expected_count, filename)
            for array in arrays:
                fields = set(re.findall(r'"([a-z_]+)"', array))
                self.assertTrue(fields)
                self.assertTrue(fields.issubset(valid), (filename, fields - valid))
            self.assertIn("invalid_fields", text)

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
        pattern = re.compile(r"\b(?:weeks|periods|limit|days)\s*=\s*\d+")
        for path in COMMANDS.glob("*.md"):
            self.assertIsNone(pattern.search(read(path)), path.name)

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
        self.assertIn("parallel, 6 tokens", text)
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

    def test_marketing_stock_call_count_matches_command(self) -> None:
        positioning = read(ROOT / "docs" / "positioning.md")
        self.assertIn("fires 10 parallel MCP calls", positioning)
        self.assertIn("becomes cheaper", positioning)
        self.assertIn("at 6 holdings", positioning)


if __name__ == "__main__":
    unittest.main()

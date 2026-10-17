from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCANNER = ROOT / "scripts" / "perimeter-scan.py"
MARKER = "synthetic-private-marker"


class PerimeterScanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.repo = Path(self.tempdir.name) / "repo"
        self.repo.mkdir()
        self.extras = Path(self.tempdir.name) / "extras.txt"
        self.extras.write_text(f"{MARKER}\n", encoding="utf-8")
        self.git("init", "--quiet")
        self.git("config", "user.name", "Test User")
        self.git("config", "user.email", "test@example.invalid")
        self.write("README.md", "safe\n")
        self.git("add", "README.md")
        self.git("commit", "--quiet", "-m", "initial")

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def write(self, relative_path: str, content: str) -> None:
        path = self.repo / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def scan(
        self,
        *extra_args: str,
        extras: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.pop("PARALLAX_ALLOW_PARTIAL_SCAN", None)
        env["PARALLAX_CANARY_EXTRA"] = str(extras or self.extras)
        return subprocess.run(
            [
                sys.executable,
                str(SCANNER),
                "--repo",
                str(self.repo),
                *extra_args,
            ],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

    def test_clean_index_passes(self) -> None:
        result = self.scan()
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("from index", result.stdout)

    def test_default_scan_reads_staged_content_not_worktree(self) -> None:
        self.write("README.md", f"{MARKER}\n")
        self.git("add", "README.md")
        self.write("README.md", "safe worktree\n")

        index_result = self.scan()
        worktree_result = self.scan("--source", "worktree")

        self.assertEqual(index_result.returncode, 1)
        self.assertIn("local canary hit", index_result.stdout)
        self.assertEqual(
            worktree_result.returncode,
            0,
            worktree_result.stderr + worktree_result.stdout,
        )

    def test_head_source_reads_committed_content(self) -> None:
        self.write("README.md", f"{MARKER}\n")
        self.git("add", "README.md")
        self.git("commit", "--quiet", "-m", "fixture update")

        result = self.scan("--source", "head")

        self.assertEqual(result.returncode, 1)
        self.assertIn("local canary hit", result.stdout)

    def test_empty_extras_fail_closed(self) -> None:
        empty = Path(self.tempdir.name) / "empty-extras.txt"
        empty.write_text("# comments only\n", encoding="utf-8")

        result = self.scan(extras=empty)

        self.assertEqual(result.returncode, 2)
        self.assertIn("not found or empty", result.stderr)
        self.assertNotIn("clean", result.stdout)

    def test_invalid_repository_returns_operational_error(self) -> None:
        missing = Path(self.tempdir.name) / "missing"
        env = os.environ.copy()
        env["PARALLAX_CANARY_EXTRA"] = str(self.extras)

        result = subprocess.run(
            [sys.executable, str(SCANNER), "--repo", str(missing)],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("could not scan", result.stderr)

    def test_anchor_test_phrase_is_detected(self) -> None:
        phrase = "Anchor " + "test result for a named fixture\n"
        self.write("notes.md", phrase)
        self.git("add", "notes.md")

        result = self.scan()

        self.assertEqual(result.returncode, 1)
        self.assertIn("anchor-test", result.stdout)

    def test_target_heading_check_is_case_insensitive(self) -> None:
        self.write("investor-notes.md", "| observed | target |\n|---|---|\n")
        self.git("add", "investor-notes.md")

        result = self.scan()

        self.assertEqual(result.returncode, 1)
        self.assertIn("target-column", result.stdout)

    def test_reviewed_calibration_leak_shapes_are_detected(self) -> None:
        # Each line once scanned clean (ship-check review, 2026-10-16). The
        # literals are split so this file does not trip the scan itself.
        cases = [
            ("factor-comparison", "Quality " + "> 7.0 and Value " + "> 6\n"),
            ("factor-score-comparison", "Quality " + "score > 7\n"),
            ("target-column", "| Factor | " + "Threshold |\n|---|---|\n"),
            ("anchor" + "-test", "anchor-" + "test: XYZ scored 8.1\n"),
            ("anchor" + "-test", "anchor-" + "tested on AAPL.O at 8.1\n"),
            ("percentile-band", "at least 70" + "th percentile\n"),
            ("consensus-constant", "super-" + "majority: 3 of 4\n"),
        ]
        for check, line in cases:
            with self.subTest(line=line):
                self.write("parallax/skills/investor-profiles/SKILL.md", line)
                self.git("add", "-A")
                result = self.scan()
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(check, result.stdout)

    def test_factor_cutoff_restated_outside_investor_files_is_detected(self) -> None:
        self.write("README.md", "Buffett match needs Quality " + ">= 7\n")
        self.git("add", "README.md")

        result = self.scan()

        self.assertEqual(result.returncode, 1)
        self.assertIn("factor-comparison", result.stdout)

    def test_factor_cutoff_written_as_percent_is_detected(self) -> None:
        self.write("README.md", "Quality " + "> 15% of peers\n")
        self.git("add", "README.md")

        result = self.scan()

        self.assertEqual(result.returncode, 1)
        self.assertIn("factor-comparison", result.stdout)

    def test_worded_and_variant_calibration_shapes_are_detected(self) -> None:
        # Most lines scanned clean before the 2026-10-16 deferred-debt pass; the
        # rest lock in existing coverage (Unicode operators, supermajority).
        # Literals are split so this file does not trip the scan itself.
        global_cases = [
            ("factor-comparison", "A match needs Quality " + "above 7\n"),
            ("factor-comparison", "Value at " + "least 7.0\n"),
            ("factor-comparison", "Quality must " + "exceed 7\n"),
            ("factor-comparison", "Quality " + "7+ only\n"),
            ("factor-comparison", "Quality " + "≥ 7\n"),
            ("factor-comparison", "Quality " + "> -1\n"),
            ("factor-comparison", "quality" + ">.7\n"),
            ("factor-comparison", "min_" + "quality=7\n"),
            ("consensus-constant", "match when 3 of 4 " + "profiles agree\n"),
            ("consensus-constant", "a 2/3 " + "majority\n"),
            ("consensus-constant", "super" + "majority of 3\n"),
        ]
        investor_cases = [
            ("percentile-band", "top 70" + "th-percentile\n"),
            ("percentile-band", "top 30% " + "of peer universe\n"),
            ("target-column", "| Factor | " + "Floor |\n|---|---|\n"),
            ("target-column", "| Factor | " + "Required |\n|---|---|\n"),
            ("target-column", "| Factor | " + "Min score |\n|---|---|\n"),
            ("target-column", "| Factor | " + "Thresholds |\n|---|---|\n"),
            ("percentile-band", "bottom 30% " + "of its peers\n"),
            ("threshold-comparison", "Quality " + "≥7\n"),
        ]
        for path, cases in (
            ("README.md", global_cases),
            ("parallax/skills/investor-profiles/SKILL.md", investor_cases),
        ):
            for check, line in cases:
                with self.subTest(line=line):
                    self.write(path, line)
                    self.git("add", "-A")
                    result = self.scan()
                    self.assertEqual(result.returncode, 1, result.stdout)
                    self.assertIn(check, result.stdout)

    def test_public_health_flag_cutoffs_stay_clean(self) -> None:
        # health-flags states public cutoffs as "<factor> score <op> N"; the
        # global checks must not flag that phrasing.
        lines = (
            "| **Value Trap** | Portfolio value score is low | `quick_portfolio_scores` | Portfolio value score <= 3.0 |\n"
            "| **Low Score** | Portfolio overall score is weak | `quick_portfolio_scores` | Overall <= 5.0 |\n"
            "Flag when the value score is below 3.0 for the book.\n"
            "Momentum under 3 months tends to reverse; value over 10 years compounds.\n"
        )
        self.write("parallax/skills/health-flags/SKILL.md", lines)
        self.git("add", "-A")

        result = self.scan()

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_local_canary_in_the_scanner_itself_is_detected(self) -> None:
        # The scanner is exempt from structural checks only. A partner name
        # pasted into it ships publicly like any other file.
        self.write("scripts/perimeter-scan.py", f"# {MARKER}\n")
        self.git("add", "-A")

        result = self.scan()

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("local canary hit", result.stdout)

    def test_public_percentile_band_outside_investor_files_is_allowed(self) -> None:
        self.write("parallax/commands/credit.md", "Worse than peer 75" + "th percentile\n")
        self.git("add", "-A")

        result = self.scan()

        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()

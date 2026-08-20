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


if __name__ == "__main__":
    unittest.main()

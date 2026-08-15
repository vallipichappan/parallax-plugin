#!/usr/bin/env python3
"""Perimeter scan for the public parallax-plugin repo.

Run before any push:

    git add <release files>
    python3 scripts/perimeter-scan.py

The default source is the Git index. This makes the scan inspect the staged
release candidate rather than unrelated or cleaner worktree bytes. Use
``--source head`` after committing. ``--source worktree`` is diagnostic only;
it still limits the file list to paths tracked by the index.

Exit 0 = clean. Exit 1 = findings. Exit 2 = incomplete or failed scan.

WHY THIS EXISTS
---------------
Content in this repo is hand-authored rather than generated. The upstream
parallax-workflows repo builds its public bundle through a script that applies
five protections: a tracked-files-only copy, content-anchored redaction
transforms that fail the build when their anchor drifts, a fail-closed term
scan, a reference-resolution gate, and an allowlist (not a denylist) for shared
content. Hand-porting bypasses all five. This script restores the cheapest and
most load-bearing of them — the term scan — and adds structural checks for the
one class of leak a term scan cannot catch.

That class matters. Proprietary calibration carries no distinctive vocabulary:
it is ordinary numbers in ordinary tables. A clean term scan is necessary, not
sufficient, which is why the structural checks below look for the *shape* of a
published threshold rather than its value.

THIS FILE IS TRACKED AND PUBLIC. It must never contain a canary term, a held
numeric value, or an internal identifier in literal form. Branding canaries are
assembled from Unicode codepoints at runtime; genuinely sensitive terms live
only in the untracked local extras file.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

DEFAULT_REPO = Path(__file__).resolve().parent.parent
EXTRAS_ENV = "PARALLAX_CANARY_EXTRA"
DEFAULT_EXTRAS = Path.home() / ".claude" / "parallax-canary-extra.txt"

# This scanner names the patterns it hunts for, so it is the one file exempt
# from its own checks. Nothing else is blanket-exempt — in particular CLAUDE.md
# is scanned, because repo-guidance files are a real carrier for calibration
# restated as an "invariant" and they ship on the same push as everything else.
SELF_REFERENTIAL = {
    "scripts/perimeter-scan.py",
}


def branding_canaries() -> list[str]:
    """Assemble branding canaries from codepoints so this file never carries them."""
    glyphs = [chr(c) for c in (0x03A9, 0x03A6, 0x039E, 0x03A8)]
    framework = "".join(chr(c) for c in (0x50, 0x52, 0x49, 0x53, 0x4D))
    return glyphs + [framework]


def git(repo: Path, *args: str) -> bytes:
    """Run Git without inheriting locale-dependent decoding behavior."""
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        check=True,
    ).stdout


def tracked_files(repo: Path, source: str) -> list[str]:
    """Return paths from the selected immutable or working content source."""
    if source == "head":
        out = git(repo, "ls-tree", "-r", "--name-only", "-z", "HEAD")
    else:
        out = git(repo, "ls-files", "--cached", "-z")
    return [
        path.decode("utf-8", errors="surrogateescape")
        for path in out.split(b"\0")
        if path
    ]


def file_text(repo: Path, rel: str, source: str) -> str:
    """Read a tracked path from the selected Git source."""
    if source == "index":
        raw = git(repo, "show", f":{rel}")
    elif source == "head":
        raw = git(repo, "show", f"HEAD:{rel}")
    else:
        raw = (repo / rel).read_bytes()
    return raw.decode("utf-8", errors="replace")


def commit_messages(repo: Path) -> str:
    return git(repo, "log", "--all", "--format=%B").decode(
        "utf-8", errors="replace"
    )


def load_extras(default_path: Path) -> list[str] | None:
    """Return local canary terms, or None when the file is absent."""
    path = Path(os.environ.get(EXTRAS_ENV, str(default_path)))
    if not path.is_file():
        return None
    terms = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            terms.append(line)
    return terms


# Structural tells that published calibration has re-entered the repo. These
# match the SHAPE of a threshold spec, not any particular value.
#
# GLOBAL checks run over every tracked file. Their patterns are specific enough
# that a hit anywhere is worth a look — and calibration restated in a README or
# a guidance file is published just as surely as calibration in a skill.
STRUCTURAL_GLOBAL = [
    (
        "anchor-test",
        re.compile(r"anchor test", re.IGNORECASE),
        "an anchor-test reference — these are engine outputs on named tickers",
    ),
    (
        "tuning-date",
        re.compile(r"tuned\s+\d{4}-\d{2}-\d{2}"),
        "a calibration tuning date",
    ),
    (
        "consensus-constant",
        re.compile(r"ceil\s*\(|minimum_applicable_count"),
        "a consensus aggregation constant",
    ),
]

# SCOPED checks would false-positive on legitimate public numbers elsewhere
# (health-flag cutoffs, AAOIFI screen ratios), so they run only where
# investor-profile calibration would land.
STRUCTURAL_SCOPED = [
    (
        "threshold-comparison",
        re.compile(r"(?:>=|<=|≥|≤)\s*\d"),
        "a numeric comparison — investor-profile criteria are expressed by direction, not cutoff",
    ),
    (
        "target-column",
        re.compile(r"\|\s*target\s*\|", re.IGNORECASE),
        "a 'Target' table column — profile outputs report observed values only",
    ),
]

STRUCTURAL_SCOPE = re.compile(r"investor", re.IGNORECASE)


def parse_args() -> Namespace:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        type=Path,
        default=DEFAULT_REPO,
        help="repository to scan",
    )
    parser.add_argument(
        "--source",
        choices=("index", "head", "worktree"),
        default="index",
        help="content source to scan; index matches the staged release candidate",
    )
    return parser.parse_args()


def scan(repo: Path, source: str) -> int:
    findings: list[str] = []
    notices: list[str] = []

    files = tracked_files(repo, source)
    texts = {
        rel: file_text(repo, rel, source)
        for rel in files
        if rel not in SELF_REFERENTIAL
    }

    # --- 1. Branding canaries over files and commit messages -----------------
    canaries = branding_canaries()
    for rel, text in texts.items():
        for term in canaries:
            if term.lower() in text.lower():
                for n, line in enumerate(text.splitlines(), 1):
                    if term.lower() in line.lower():
                        findings.append(f"{rel}:{n}: branding canary hit")
    msgs = commit_messages(repo)
    for term in canaries:
        if term.lower() in msgs.lower():
            findings.append("commit messages: branding canary hit")

    # --- 2. Local extras, fail-closed ---------------------------------------
    extras = load_extras(DEFAULT_EXTRAS)
    if not extras:
        if os.environ.get("PARALLAX_ALLOW_PARTIAL_SCAN") == "1":
            notices.append(
                "NOTICE: local canary file absent or empty; built-in checks only. "
                "This scan did NOT cover partner names or internal identifiers."
            )
        else:
            print(
                f"perimeter-scan: local canary file not found or empty "
                f"(default {DEFAULT_EXTRAS}, override with {EXTRAS_ENV}).\n"
                "Refusing to report a clean scan on a partial term set.\n"
                "Set PARALLAX_ALLOW_PARTIAL_SCAN=1 to run built-in checks only.",
                file=sys.stderr,
            )
            return 2
    else:
        for rel, file_content in texts.items():
            text = file_content.lower()
            for i, term in enumerate(extras):
                if term.lower() in text:
                    # Never echo the term — naming it to prove presence publishes it.
                    findings.append(f"{rel}: local canary hit (term #{i + 1})")
        low = msgs.lower()
        for i, term in enumerate(extras):
            if term.lower() in low:
                findings.append(f"commit messages: local canary hit (term #{i + 1})")

    # --- 3. Structural calibration tells -------------------------------------
    for rel, text in texts.items():
        checks = list(STRUCTURAL_GLOBAL)
        if STRUCTURAL_SCOPE.search(rel):
            checks += STRUCTURAL_SCOPED
        for n, line in enumerate(text.splitlines(), 1):
            for name, pat, why in checks:
                if pat.search(line):
                    findings.append(f"{rel}:{n}: {name} — {why}")

    for notice in notices:
        print(notice)

    if findings:
        print(f"\nperimeter-scan: {len(findings)} finding(s)\n")
        for f in findings:
            print(f"  {f}")
        print(
            "\nA hit is not automatically a leak — review each. If a match is "
            "legitimate, narrow the pattern or add the path to SELF_REFERENTIAL "
            "with a comment saying why."
        )
        return 1

    print(f"perimeter-scan: clean ({len(files)} tracked files from {source})")
    return 0


def main() -> int:
    args = parse_args()
    try:
        return scan(args.repo.resolve(), args.source)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"perimeter-scan: could not scan: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

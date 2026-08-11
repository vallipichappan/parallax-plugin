#!/usr/bin/env python3
"""Perimeter scan for the public parallax-plugin repo.

Run before any push:

    python3 scripts/perimeter-scan.py

Exit 0 = clean. Exit 1 = findings. Exit 2 = could not scan (see below).

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
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
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


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [p for p in out.splitlines() if p.strip()]


def commit_messages() -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), "log", "--all", "--format=%B"],
        capture_output=True, text=True, check=True,
    ).stdout


def load_extras() -> list[str] | None:
    """Return local canary terms, or None when the file is absent."""
    path = Path(os.environ.get(EXTRAS_ENV, DEFAULT_EXTRAS))
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
        re.compile(r"[Aa]nchor test"),
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
        re.compile(r"\|\s*Target\s*\|"),
        "a 'Target' table column — profile outputs report observed values only",
    ),
]

STRUCTURAL_SCOPE = re.compile(r"investor", re.IGNORECASE)


def main() -> int:
    findings: list[str] = []
    notices: list[str] = []

    files = tracked_files()

    # --- 1. Branding canaries over files and commit messages -----------------
    canaries = branding_canaries()
    for rel in files:
        if rel in SELF_REFERENTIAL:
            continue
        text = (REPO / rel).read_text(encoding="utf-8", errors="replace")
        for term in canaries:
            if term.lower() in text.lower():
                for n, line in enumerate(text.splitlines(), 1):
                    if term.lower() in line.lower():
                        findings.append(f"{rel}:{n}: branding canary hit")
    msgs = commit_messages()
    for term in canaries:
        if term.lower() in msgs.lower():
            findings.append("commit messages: branding canary hit")

    # --- 2. Local extras, fail-closed ---------------------------------------
    extras = load_extras()
    if extras is None:
        if os.environ.get("PARALLAX_ALLOW_PARTIAL_SCAN") == "1":
            notices.append(
                "NOTICE: local canary file absent; built-in checks only. "
                "This scan did NOT cover partner names or internal identifiers."
            )
        else:
            print(
                f"perimeter-scan: local canary file not found "
                f"(looked for {DEFAULT_EXTRAS}, override with {EXTRAS_ENV}).\n"
                "Refusing to report a clean scan on a partial term set.\n"
                "Set PARALLAX_ALLOW_PARTIAL_SCAN=1 to run built-in checks only.",
                file=sys.stderr,
            )
            return 2
    else:
        for rel in files:
            if rel in SELF_REFERENTIAL:
                continue
            text = (REPO / rel).read_text(encoding="utf-8", errors="replace").lower()
            for i, term in enumerate(extras):
                if term.lower() in text:
                    # Never echo the term — naming it to prove presence publishes it.
                    findings.append(f"{rel}: local canary hit (term #{i + 1})")
        low = msgs.lower()
        for i, term in enumerate(extras):
            if term.lower() in low:
                findings.append(f"commit messages: local canary hit (term #{i + 1})")

    # --- 3. Structural calibration tells -------------------------------------
    for rel in files:
        if rel in SELF_REFERENTIAL:
            continue
        checks = list(STRUCTURAL_GLOBAL)
        if STRUCTURAL_SCOPE.search(rel):
            checks += STRUCTURAL_SCOPED
        text = (REPO / rel).read_text(encoding="utf-8", errors="replace")
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

    print(f"perimeter-scan: clean ({len(files)} tracked files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

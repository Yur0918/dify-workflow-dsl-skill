#!/usr/bin/env python3
"""Fixture tests for scripts/validate_dsl.py.

Each fixture in tests/fixtures/ encodes one contract of the validator:
valid-*.yml must exit 0 with a clean "OK" report; invalid-*.yml must exit
non-zero and print the expected ERROR lines. The validator is invoked as a
subprocess so these tests exercise the real CLI contract (arguments, exit
codes, stdout), not an imported API.

Stdlib only. Run from anywhere:

    python3 tests/run_tests.py

Exits non-zero if any fixture fails.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validate_dsl.py"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"

# fixture file -> (expected exit code, required stdout substrings)
CASES: dict[str, tuple[int, list[str]]] = {
    "valid-translate.yml": (0, ["OK"]),
    "valid-chatflow.yml": (0, ["OK"]),
    "invalid-missing-structure.yml": (
        1,
        [
            "ERROR: workflow.graph.nodes is missing or empty.",
            "ERROR: workflow.graph.edges is missing.",
        ],
    ),
    "invalid-broken-references.yml": (
        1,
        [
            "ERROR: Edge",
            "target does not exist",
            "sourceType 'llm' does not match node 3000001 type 'start'",
        ],
    ),
    "invalid-code-node.yml": (
        1,
        [
            "ERROR: Code node",
            "missing code_language",
            "missing code string",
            "missing outputs mapping",
        ],
    ),
    "invalid-tool-sql.yml": (
        1,
        [
            "ERROR: Tool node",
            "trailing comma",
            "two-part [node_id, field] selector",
        ],
    ),
}


def run_case(name: str, expected_exit: int, expected_parts: list[str]) -> list[str]:
    """Run one fixture. Returns a list of problems (empty means pass)."""
    path = FIXTURE_DIR / name
    if not path.exists():
        return [f"fixture not found: {path}"]

    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), str(path)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    output = proc.stdout + proc.stderr
    lines = [line.strip() for line in output.splitlines()]

    problems: list[str] = []
    if proc.returncode != expected_exit:
        problems.append(f"exit code {proc.returncode}, expected {expected_exit}")
    for part in expected_parts:
        if part not in output:
            problems.append(f"missing output: {part!r}")
    # A fully clean report prints the standalone line "OK"; anything with
    # errors or warnings does not.
    has_ok_line = "OK" in lines
    if expected_exit == 0 and not has_ok_line:
        problems.append("expected a clean 'OK' report, got warnings/errors instead")
    if expected_exit != 0 and has_ok_line:
        problems.append("invalid fixture reported a clean 'OK'")
    return problems


def main() -> int:
    failures = 0
    names = sorted(CASES)
    for name in names:
        expected_exit, expected_parts = CASES[name]
        problems = run_case(name, expected_exit, expected_parts)
        if problems:
            failures += 1
            print(f"FAILED {name}")
            for problem in problems:
                print(f"       - {problem}")
        else:
            print(f"OK     {name} (exit {expected_exit})")

    print(f"\n{len(names) - failures}/{len(names)} fixture(s) passed.")
    if failures:
        print(f"{failures} fixture(s) FAILED.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

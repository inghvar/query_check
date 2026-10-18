#!/usr/bin/env python3
"""Diff-scoped GitHub Actions annotations from a django-query-doctor log.

Parses the plain-text report produced by query_doctor's "log" reporter
(see LogReporter._log_prescription), keeps only the findings whose
callsite falls on a line actually changed in this PR, and prints them as
native GitHub Actions annotations (::error / ::warning) so they show up
inline in the PR's "Files changed" tab.

Usage:
    python scripts/query_doctor_annotate.py \
        --log query_doctor.log \
        --base-sha <base_sha> \
        --head-sha <head_sha> \
        [--fail-on warning]   # warning (default) or critical

Exit code is 1 if any matching finding is found at or above --fail-on
severity, 0 otherwise (including when nothing matches or the log is
missing/empty).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass

_LOG_LINE_RE = re.compile(
    r"^\[(?P<severity>CRITICAL|WARNING|INFO)\]\s+"
    r"(?P<description>.*?)\s+"
    r"at\s+(?P<file>\S+):(?P<line>\d+)\s+in\s+(?P<function>\S+)\s+"
    r"\|\s+Fix:\s+(?P<fix>.*)$"
)

_SEVERITY_ORDER = {"info": 0, "warning": 1, "critical": 2}

_ANNOTATION_LEVEL = {
    "critical": "error",
    "warning": "warning",
    "info": "notice",
}


@dataclass
class Finding:
    severity: str
    description: str
    file: str
    line: int
    function: str
    fix: str


def parse_log(path: str) -> list[Finding]:
    findings: list[Finding] = []
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"::warning::query-doctor log not found at {path}; nothing to annotate", file=sys.stderr)
        return findings

    for raw_line in lines:
        match = _LOG_LINE_RE.match(raw_line.strip())
        if not match:
            continue
        findings.append(
            Finding(
                severity=match.group("severity").lower(),
                description=match.group("description"),
                file=match.group("file"),
                line=int(match.group("line")),
                function=match.group("function"),
                fix=match.group("fix"),
            )
        )
    return findings


def get_changed_lines(base_sha: str, head_sha: str) -> dict[str, set[int]]:
    """Return {repo-relative file path: {changed line numbers in new file}}.

    Uses `git diff --unified=0` and parses the `@@ -a,b +c,d @@` hunk
    headers, same mechanism git itself uses, so added/modified lines are
    reported with their exact new-file line numbers (not just "file touched").
    """
    result = subprocess.run(
        ["git", "diff", "--unified=0", f"{base_sha}", f"{head_sha}"],
        capture_output=True,
        text=True,
        check=True,
    )

    changed: dict[str, set[int]] = {}
    current_file: str | None = None
    hunk_re = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
    file_re = re.compile(r"^\+\+\+ b/(.+)$")

    for line in result.stdout.splitlines():
        file_match = file_re.match(line)
        if file_match:
            current_file = file_match.group(1)
            changed.setdefault(current_file, set())
            continue

        hunk_match = hunk_re.match(line)
        if hunk_match and current_file is not None:
            start = int(hunk_match.group(1))
            count = int(hunk_match.group(2)) if hunk_match.group(2) is not None else 1
            if count == 0:
                # Pure deletion hunk; nothing added on the new-file side.
                continue
            changed[current_file].update(range(start, start + count))

    return changed


def matches_changed_lines(finding: Finding, changed: dict[str, set[int]]) -> bool:
    for changed_file, line_numbers in changed.items():
        if finding.file.endswith(changed_file) or changed_file.endswith(finding.file):
            if finding.line in line_numbers:
                return True
    return False


def emit_annotation(finding: Finding) -> None:
    level = _ANNOTATION_LEVEL.get(finding.severity, "warning")
    message = f"{finding.description} | Fix: {finding.fix}".replace("\n", " ")
    print(f"::{level} file={finding.file},line={finding.line}::{message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", default="query_doctor.log")
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--fail-on", default="warning", choices=["info", "warning", "critical"])
    args = parser.parse_args()

    findings = parse_log(args.log)
    changed = get_changed_lines(args.base_sha, args.head_sha)

    matched = [f for f in findings if matches_changed_lines(f, changed)]

    if not matched:
        print("Query Doctor: no findings on changed lines of this PR.")
        return 0

    fail_threshold = _SEVERITY_ORDER[args.fail_on]
    should_fail = False
    for finding in matched:
        emit_annotation(finding)
        if _SEVERITY_ORDER[finding.severity] >= fail_threshold:
            should_fail = True

    print(f"Query Doctor: {len(matched)} finding(s) on changed lines of this PR.")
    return 1 if should_fail else 0


if __name__ == "__main__":
    sys.exit(main())

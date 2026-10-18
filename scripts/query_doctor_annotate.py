#!/usr/bin/env python3
"""GitHub Actions annotations from a django-query-doctor log (baseline mode).

Parses the plain-text report produced by query_doctor's "log" reporter
(see LogReporter._log_prescription) and prints every finding as a native
GitHub Actions annotation (::error / ::warning) so it shows up inline in
the PR's "Files changed" tab.

This relies on a *clean baseline*: the repository is kept at zero
query_doctor findings on its default branch (fix real issues, add known
third-party-library limitations to .queryignore). Under that invariant,
any finding present in a push's query_doctor.log is new by definition --
introduced by that push's own code -- so no git-diff/line-matching is
needed at all to tell "pre-existing" apart from "new".

Usage:
    python scripts/query_doctor_annotate.py \
        --log query_doctor.log \
        [--fail-on warning]   # info, warning (default), or critical

Exit code is 1 if any finding is found at or above --fail-on severity,
0 otherwise (including when the log is empty/missing).
"""

from __future__ import annotations

import argparse
import os
import re
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


def to_repo_relative(path: str) -> str:
    """Best-effort conversion of an absolute callsite path to a repo-relative one.

    query_doctor logs the absolute filesystem path of the callsite. GitHub's
    annotation `file=` field resolves an absolute path under GITHUB_WORKSPACE
    on its own, but the *message text* does not get that treatment, so we
    convert it ourselves to keep the location readable wherever the message
    is displayed (raw job log, PR comment, etc.), not only in the "Files
    changed" tab.
    """
    cwd = os.getcwd()
    if path.startswith(cwd + os.sep):
        return path[len(cwd) + 1:]
    return path


def emit_annotation(finding: Finding) -> None:
    level = _ANNOTATION_LEVEL.get(finding.severity, "warning")
    rel_file = to_repo_relative(finding.file)
    # Location is embedded directly in the message text (not just in the
    # file=/line= annotation metadata) so it is visible in every GitHub
    # surface that renders this text, including the raw job log.
    message = (
        f"{rel_file}:{finding.line} in {finding.function}() -- "
        f"{finding.description} | Fix: {finding.fix}"
    ).replace("\n", " ")
    print(f"::{level} file={rel_file},line={finding.line}::{message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", default="query_doctor.log")
    parser.add_argument("--fail-on", default="warning", choices=["info", "warning", "critical"])
    args = parser.parse_args()

    findings = parse_log(args.log)

    if not findings:
        print("Query Doctor: baseline is clean, no findings.")
        return 0

    fail_threshold = _SEVERITY_ORDER[args.fail_on]
    should_fail = False
    for finding in findings:
        emit_annotation(finding)
        if _SEVERITY_ORDER[finding.severity] >= fail_threshold:
            should_fail = True

    print(f"Query Doctor: {len(findings)} finding(s) -- baseline is supposed to be clean, these are new.")
    return 1 if should_fail else 0


if __name__ == "__main__":
    sys.exit(main())

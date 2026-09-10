#!/usr/bin/env bash
# ensure-run-state-ignored.sh — install veri's run-state rule into a target repo's .gitignore.
#
# veri writes leaf logs, .rc markers, .prompt files and the blind spec into the target repo's
# .tdd/; only the ledger (.tdd/issue-<n>.md) belongs in history. This writes the three-line,
# order-sensitive rule that makes git agree: ignore .tdd/*, un-ignore the ledger, re-ignore
# the spec (which would otherwise be caught by the ledger's negation).
#
# Usage:   ensure-run-state-ignored.sh [repo-root]      (default: the current directory)
set -euo pipefail

root="${1:-.}"

cat >> "$root/.gitignore" <<'RULE'
.tdd/*
!.tdd/issue-*.md
.tdd/issue-*-spec.md
RULE

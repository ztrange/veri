#!/usr/bin/env bash
# Unit tests for scripts/tests/lib/fenced-lines.sh — the lines inside ``` fences of a file that
# match a pattern, optionally only those under one heading, sourced, not run.
# Fast tier: no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/fenced-lines.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../lib/fenced-lines.sh"
source "$HERE/../lib/harness.sh"

name="fenced_lines restricted to one heading prints only the fenced lines under that heading"
md="$(scratch_dir)/doc.md"
printf '%s\n' '## A' '```' 'a fenced' '```' '### B' 'b prose' '```' 'b fenced' '```' '## C' '```' 'c fenced' '```' > "$md"
actual="$(
  # shellcheck disable=SC1090
  source "$LIB"
  fenced_lines "$md" 'fenced' '### B'
)"
expect_eq "$name" "$(printf '8\tb fenced')" "$actual"

finish

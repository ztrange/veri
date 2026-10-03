#!/usr/bin/env bash
# Unit tests for scripts/tests/lib/section-end.sh — the last line of the section a heading opens,
# the line before the next heading or the file's last line, sourced, not run.
# Fast tier: no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/section-end.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../lib/section-end.sh"
source "$HERE/../lib/harness.sh"

name="a section ends the line before the next heading, and the last section at the file's last line"
md="$(scratch_dir)/doc.md"
printf '%s\n' 'intro' '## A' 'a one' 'a two' '### B' 'b one' > "$md"
actual="$(
  # shellcheck disable=SC1090
  source "$LIB"
  printf '%s %s' "$(section_end "$md" 2)" "$(section_end "$md" 5)"
)"
expect_eq "$name" "4 6" "$actual"

finish

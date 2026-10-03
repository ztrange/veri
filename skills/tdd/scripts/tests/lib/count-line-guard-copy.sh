#!/usr/bin/env bash
# Sourced by suites that plant a repository tree: copy_count_line_guard copies
# skills/tdd/scripts/lib/count-line-guard.sh into <tree>/skills/tdd/scripts/lib/, which must exist.
# Usage: source "$HERE/lib/count-line-guard-copy.sh"; copy_count_line_guard <tree>

COUNT_LINE_GUARD_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../lib" && pwd)/count-line-guard.sh"

copy_count_line_guard() {
  cp "$COUNT_LINE_GUARD_LIB" "$1/skills/tdd/scripts/lib/"
}

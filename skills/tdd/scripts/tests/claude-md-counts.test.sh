#!/usr/bin/env bash
# Unit test for what CLAUDE.md says about this skill's scripts.
#
# Contract under test:
#   1. The opening paragraph names invisible-work.sh, the script the procedure does not call.
#
# Run: scripts/tests/claude-md-counts.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"

source "$HERE/lib/harness.sh"

present() {
  if [[ ! -f "$ROOT/$1" ]]; then
    problems+=("$1 is not in the tree whose count $claude_md states")
  fi
}

preamble() { awk '/^## / { exit } { print }' "$claude_path"; }

flatten() { tr '\n' ' '; }

intro="$(preamble | flatten)"

finish

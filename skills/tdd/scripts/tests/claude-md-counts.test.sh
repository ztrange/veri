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

name="$claude_md's prose names invisible-work.sh, the script the procedure does not call"
problems=()

present "skills/tdd/scripts/invisible-work.sh"
if [[ "${#problems[@]}" -eq 0 ]]; then
  if [[ -n "${intro// /}" && "$intro" != *"invisible-work.sh"* ]]; then
    problems+=("$claude_md's opening paragraph counts '<n> bash scripts it calls' without naming invisible-work.sh, a script the procedure never calls")
  fi
fi

report "$name"

finish

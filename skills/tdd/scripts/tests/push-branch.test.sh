#!/usr/bin/env bash
# Unit tests for scripts/push-branch.sh — the push the conductor makes after each step's
# green commit and after each verify-refactor PASS clears the mark.
#
# Contract under test:
#   push-branch.sh, run from the worktree with an origin that cannot be reached
#                       → exit 0, the exit status the conductor branches on.
#                       → HEAD, the commit count and the ledger file are exactly what they
#                         were before the call.
#                       → one line appended to `.tdd/events.jsonl` whose `event` says the
#                         push failed.
#   push-branch.sh, run from the worktree with an origin it can reach
#                       → the run's branch is on that remote, at the commit HEAD is on.
#
# Run: scripts/tests/push-branch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
PUSH="$HERE/../push-branch.sh"

finish

#!/usr/bin/env bash
# Unit tests for scripts/tier-usual.sh — what one tier's test-command run usually costs,
# computed from the `test-run` lines timed-test-run.sh writes.
#
# Contract under test:
#   tier-usual.sh <tier>  → exit 0, and on stdout the median of the `seconds` on the last 10
#                           `test-run` lines of `.tdd/events.jsonl` whose `tier` is <tier>.
#   the log               → `.tdd/events.jsonl`, read relative to the directory the script
#                           runs in.
#
# Run: skills/tdd/scripts/tests/tier-usual.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
USUAL="$HERE/../tier-usual.sh"

source "$HERE/lib/harness.sh"

ev() {
  printf '{"ts": 1700000000, "issue": "342", "actor": "developer", "phase": "green", "step": "1", "event": "%s", "attempt": "1", "skill_commit": "abc1234", "tier": "%s", "suites": "one.test.sh", "seconds": "%s"}\n' \
    "$1" "$2" "$3"
}

finish

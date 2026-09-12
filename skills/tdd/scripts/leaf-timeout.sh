#!/usr/bin/env bash
# leaf-timeout.sh — size the run's hard timeout from the green-baseline run's wall time,
# so a repo whose suite takes minutes does not have every leaf killed as stuck while it is
# working (issue #121: a 900 s timeout against a 140-250 s `make docs-test`).
#
# Given the baseline's wall time in seconds as $1, print the timeout every leaf of the run
# should get: the larger of 900 (today's fixed default, which a quick suite keeps) and
# 6 × the baseline, as a whole number of seconds.
#
# A baseline that is not a whole number >= 0 is a broken measurement, not a decision: fail
# closed like refactor-budget.sh does on a bad budget — a diagnostic on stderr and exit 2,
# with nothing on stdout, so a conductor capturing stdout in a command substitution cannot
# mistake a malformed call for a real timeout and run the whole issue on it.
#
# Usage:   leaf-timeout.sh <baseline-seconds>   # a whole number >= 0
set -euo pipefail

baseline="${1:-}"

if [[ ! "$baseline" =~ ^[0-9]+$ ]]; then
  echo "leaf-timeout: <baseline-seconds> must be a whole number >= 0: $baseline" >&2
  exit 2
fi

# The floor is named once rather than written into both branches: it is one decision —
# today's fixed default, which a quick suite keeps — and the comparison and the value
# printed when it wins must never drift apart.
floor=900
derived=$((baseline * 6))

if [[ "$derived" -gt "$floor" ]]; then
  echo "$derived"
else
  echo "$floor"
fi

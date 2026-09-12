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
# An explicit VERI_TIMEOUT is the answer, not an input: it is printed as given whatever the
# baseline measured, so the liveness axis stays the operator's to set (CLAUDE.md's three
# budgets on three axes). It is held to >= 1, not >= 0: a zero timeout kills every leaf the
# instant it starts, which costs a stuck retry and a reverted step each time, so a typo
# fails closed here rather than burning the issue looking like model failure.
#
# Usage:   leaf-timeout.sh <baseline-seconds>   # a whole number >= 0
#          VERI_TIMEOUT=<n> leaf-timeout.sh …   # <n> a whole number >= 1, used as given
set -euo pipefail

baseline="${1:-}"
# `override`, not `timeout`: both branches print a timeout, so the name has to say which of
# the two this one is. It is the value VERI_TIMEOUT arrived with — checked and printed back
# as the answer, never mixed with the floor and scaled baseline the other branch derives
# from — which is what keeps the liveness axis the operator's to set.
override="${VERI_TIMEOUT:-}"

if [[ -n "$override" ]]; then
  if [[ ! "$override" =~ ^[0-9]+$ ]] || [[ "$override" -lt 1 ]]; then
    echo "leaf-timeout: VERI_TIMEOUT must be a whole number >= 1: $override" >&2
    exit 2
  fi
  echo "$override"
  exit 0
fi

if [[ ! "$baseline" =~ ^[0-9]+$ ]]; then
  echo "leaf-timeout: <baseline-seconds> must be a whole number >= 0: $baseline" >&2
  exit 2
fi

# The floor is named once rather than written into both branches: it is one decision —
# today's fixed default, which a quick suite keeps — and the comparison and the value
# printed when it wins must never drift apart.
floor=900
# `scaled`, not `derived`: the derived timeout is whichever of the two wins, so naming the
# 6 × half after the whole answer made the else branch read as printing something other
# than a derived timeout. The pair the comparison is between is floor and scaled baseline.
scaled=$((baseline * 6))

if [[ "$scaled" -gt "$floor" ]]; then
  echo "$scaled"
else
  echo "$floor"
fi

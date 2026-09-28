#!/usr/bin/env bash
# leaf-timeout.sh — size the run's hard timeout from the green-baseline run's wall time,
# so a repo whose suite takes minutes does not have every leaf killed as stuck while it is
# working.
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
# The refactor leaf is the one exception to "every leaf of the run gets the same timeout":
# it applies the whole step's transforms itself rather than one per leaf, so
# it is asked for as many leaves' worth of work as the budget it may spend, and its cap is
# the run's derived timeout times that budget. An explicit VERI_TIMEOUT stays unmultiplied
# — the budget is the cost axis, and it must not move a cap the operator set on liveness.
#
# Preflight measures the FAST tier — `make unit` on this repo, a few seconds —
# but no leaf runs it: a developer leaf runs the suites covering the files it touched and a
# verifier runs the full tier. Sizing from the fast measurement therefore bounded work
# nobody does, and a green leaf was killed at the floor twice over while working. So a
# caller that has both measurements hands in both, and the derivation runs over the full
# one; the fast argument stays first and stays validated, because it is still the baseline
# a caller with only one measurement has. The full one is validated the same way and for a
# sharper reason: it is the number the whole run's timeout is sized from, so an unreadable
# one — a word, a decimal, a negative, a `--full` with nothing behind it — must refuse here
# rather than either die in the arithmetic with bash's own exit 1 (a clean negative, which
# tells a conductor the plumbing is fine) or fall back to the fast measurement and print a
# floor value that looks like a real timeout.
#
# Usage:   leaf-timeout.sh <baseline-seconds>              # a whole number >= 0
#          leaf-timeout.sh <baseline-seconds> refactor     # × max(1, VERI_REFACTOR_BUDGET)
#          leaf-timeout.sh <fast-seconds> --full <full-seconds>
#          VERI_TIMEOUT=<n> leaf-timeout.sh …   # <n> a whole number >= 1, used as given
set -euo pipefail

baseline="${1:-}"
role="${2:-}"
full_given=0
full=""
if [[ "$role" == --full ]]; then
  full_given=1
  full="${3:-}"
  role=""
fi
override="${VERI_TIMEOUT:-}"

if [[ -n "$override" ]]; then
  if [[ ! "$override" =~ ^[0-9]+$ ]] || [[ "$override" -lt 1 ]]; then
    echo "leaf-timeout: VERI_TIMEOUT must be a whole number >= 1: $override" >&2
    exit 2
  fi
  echo "$override"
  exit 0
fi

require_seconds() {
  local name="$1" value="$2"
  if [[ ! "$value" =~ ^[0-9]+$ ]]; then
    echo "leaf-timeout: <$name> must be a whole number >= 0: $value" >&2
    exit 2
  fi
}

require_seconds baseline-seconds "$baseline"

if [[ "$full_given" == 1 ]]; then
  require_seconds full-seconds "$full"
  baseline="$full"
fi

floor=900
scaled=$((baseline * 6))

if [[ "$scaled" -gt "$floor" ]]; then
  derived="$scaled"
else
  derived="$floor"
fi

if [[ "$role" == refactor ]]; then
  budget="${VERI_REFACTOR_BUDGET:-5}"
  if [[ "$budget" -lt 1 ]]; then
    budget=1
  fi
  derived=$((derived * budget))
fi

echo "$derived"

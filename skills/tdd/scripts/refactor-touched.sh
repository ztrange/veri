#!/usr/bin/env bash
# refactor-touched.sh — print the files a step's green commit touched, as the bounds of that
# step's refactor (issue #167).
#
# The green commit is the atomic tick-and-commit, so it always carries the ledger under `.tdd/`.
# The ledger is run state, not code a refactor may tidy, so it is left out here, once, for both
# the cycle loop and Resume.
#
# Usage:   refactor-touched.sh <commit>
#          refactor-touched.sh --issue <base>
#
# Prints the touched files comma-joined, in `git diff --name-only` order: those <commit>
# touched, or with `--issue` every file changed between <base> and HEAD.
set -euo pipefail

usage="usage: refactor-touched.sh <commit> | --issue <base>"
rev="${1:-}"; from="$rev^"; to="$rev"
if [[ "$rev" == --issue ]]; then
  rev="${2:-}"; from="$rev"; to=HEAD
fi
[[ -n "$rev" ]] || { echo "$usage" >&2; exit 2; }

# A commit the repository cannot resolve is a plumbing failure, not an empty answer: without
# this check `git diff` fails, `grep -v` then reads no input and returns 1 under `pipefail`,
# and the refactor prompt reads that 1 as a clean "nothing touched".
git rev-parse --verify --quiet "$rev^{commit}" >/dev/null ||
  { echo "refactor-touched: cannot resolve commit '$rev'" >&2; exit 2; }

# A commit whose files are all under `.tdd/` leaves a refactor nothing to tidy. That is an
# answer, not a failure, so it is the "nothing to do" code with an empty stdout: `grep`
# finding no line exits 1, and under `pipefail` that 1 would otherwise be the script's.
touched="$(git diff --name-only "$from" "$to" | grep -v '^\.tdd/' || true)"
[[ -n "$touched" ]] || exit 3

printf '%s\n' "$touched" | paste -sd, -

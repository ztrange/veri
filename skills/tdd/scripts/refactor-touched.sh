#!/usr/bin/env bash
# refactor-touched.sh — print the files a step's green commit touched, as the bounds of that
# step's refactor (issue #167).
#
# The green commit is the atomic tick-and-commit, so it always carries the ledger under `.tdd/`.
# The ledger is run state, not code a refactor may tidy, so it is left out here, once, for both
# the cycle loop and Resume.
#
# Usage:   refactor-touched.sh <commit>
#
# Prints the touched files comma-joined, in `git diff --name-only` order.
set -euo pipefail

commit="${1:?usage: refactor-touched.sh <commit>}"

# A commit the repository cannot resolve is a plumbing failure, not an empty answer: without
# this check `git diff` fails, `grep -v` then reads no input and returns 1 under `pipefail`,
# and the refactor prompt reads that 1 as a clean "nothing touched".
git rev-parse --verify --quiet "$commit^{commit}" >/dev/null ||
  { echo "refactor-touched: cannot resolve commit '$commit'" >&2; exit 2; }

git diff --name-only "$commit^" "$commit" | grep -v '^\.tdd/' | paste -sd, -

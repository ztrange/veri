#!/usr/bin/env bash
# transform-touches-tests.sh — reject a refactor-kind transform whose commits change a test
# file (issue #499).
#
# A transform moves structure and must leave the tests that pin the behaviour alone, or a
# green suite stops meaning the behaviour is unchanged. A long refactor has no green commit,
# so the range read is the step's base sha to HEAD — every commit in it, not HEAD's own diff.
# A test file is one under a `tests/` directory or named `*.test.*`, this repository's layout.
#
# Usage:   transform-touches-tests.sh <base-sha>
#
# Exit: 1 naming each test file the range changed, 0 when it changed none.
set -euo pipefail

[[ -n "${1:-}" ]] || { echo "usage: transform-touches-tests.sh <base-sha>" >&2; exit 2; }
base="$1"

touched="$(git log --format= --name-only "$base..HEAD" | grep -E '(^|/)tests/|\.test\.' | sort -u || true)"
[[ -z "$touched" ]] && exit 0

printf 'transform changed a test file: %s\n' "$touched"
exit 1

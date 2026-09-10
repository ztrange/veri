#!/usr/bin/env bash
# Unit tests for scripts/ensure-run-state-ignored.sh — installs veri's run-state rule into
# a target repo's .gitignore, so the first `git add -A` cannot sweep run scratch (leaf logs,
# .rc markers, .prompt files, the blind spec) into history while still committing the ledger.
#
# Contract under test (issue #27):
#   ensure-run-state-ignored.sh [repo-root]   (default: the current directory)
#   afterwards, in that repo, `git check-ignore` says
#     .tdd/develop-red.log  IS ignored      (exit 0)
#     .tdd/issue-7.md       is NOT ignored  (exit 1)
#
# The assertion is on git's own ignore decision, not on the text of .gitignore: the rule is
# order-sensitive (`.tdd/*`, then a negation, then a re-ignore) and grepping for lines would
# pass on an ordering git rejects.
#
# Run: scripts/tests/ensure-run-state-ignored.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ENSURE="$HERE/../ensure-run-state-ignored.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0

# ignored <repo> <path> — git's verdict on one path, as an exit code we can assert on.
# 0 = ignored, 1 = not ignored, anything else = git errored (a broken test, not a verdict).
ignored() {
  git -C "$1" check-ignore -q "$2" >/dev/null 2>&1
}

# 1. a repo with no .gitignore at all gets one that separates run scratch from the ledger
repo="$work/fresh"
mkdir -p "$repo"
git init -q "$repo" >/dev/null 2>&1

"$ENSURE" "$repo" >/dev/null 2>&1

ignored "$repo" .tdd/develop-red.log && log_code=0 || log_code=$?
ignored "$repo" .tdd/issue-7.md && ledger_code=0 || ledger_code=$?

if [[ "$log_code" == 0 && "$ledger_code" == 1 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - no .gitignore: creates one ignoring .tdd/develop-red.log but not .tdd/issue-7.md"
  echo "    .tdd/develop-red.log: want check-ignore exit 0 (ignored), got $log_code"
  echo "    .tdd/issue-7.md:      want check-ignore exit 1 (not ignored), got $ledger_code"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

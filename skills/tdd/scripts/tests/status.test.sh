#!/usr/bin/env bash
# Unit tests for scripts/status.sh — the aggregation layer over every run in a repository.
# Run from a target repo, it discovers runs from `.tdd/wt/*` under the repository's MAIN
# working tree (resolved as solvable-issues.sh does, #166) and renders each one.
#
# Contract under test (issue #109):
#   status.sh            print every run under .tdd/wt/*, exit 0;
#                        print "no runs" and exit 3 when there are none.
#
# Run: scripts/tests/status.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STATUS="$HERE/../status.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# A repository of the case's own, so the answer never depends on the runs live in the
# repository `make test` was typed in. A `git init` with no commit is enough: `git worktree
# list` prints it as the main tree.
repo() {  # repo <name> -> path
  local dir="$work/$1"
  git init -q -b main "$dir" >/dev/null 2>&1
  echo "$dir"
}

# Run the script from inside <dir>, leaving stdout in $out and the exit code in $code.
run_in() {  # run_in <dir> [script args…]; sets $out and $code
  local dir="$1"; shift
  out="$(cd "$dir" && "$STATUS" "$@" 2>/dev/null)" && code=0 || code=$?
}

# --- no .tdd/wt/* runs under the main working tree: "no runs", exit 3 ---
empty="$(repo empty)"
run_in "$empty"
if [[ "$out" == "no runs" && "$code" -eq 3 ]]; then ok; else
  no "no runs under the main working tree prints 'no runs' and exits 3"
  diff <(printf 'no runs\nexit 3\n') <(printf '%s\nexit %s\n' "$out" "$code")
fi

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

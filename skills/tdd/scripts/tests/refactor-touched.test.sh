#!/usr/bin/env bash
# Unit tests for scripts/refactor-touched.sh — prints the files a step's green commit
# touched, as the bounds of that step's refactor (issue #167).
#
# The green commit is the atomic tick-and-commit, so it always carries the ledger
# `.tdd/issue-<n>.md`. The ledger is run state, not code the refactor may tidy: a leaf that
# rewords a step line breaks the substring clear-refactor-pending.sh matches on. So the
# bounds name the commit's production and test files and never the ledger.
#
# Contract under test:
#   refactor-touched.sh <commit>, run inside the repository
#                       → exit 0, and the commit's touched files in `git diff --name-only`
#                         order, with `.tdd/issue-<n>.md` left out.
#
# The separator is read as either a comma or a newline: the conductor hands the list to
# build-develop-prompt.sh comma-joined, but which of the two the script prints is the green
# phase's choice, and this case pins the list, not its punctuation.
#
# Run: scripts/tests/refactor-touched.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TOUCHED="$HERE/../refactor-touched.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# git_q <repo> <args…> — git with a fixed identity, so a commit does not depend on the
# user.name/user.email of the machine running the suite (CI carries none).
git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

# 1. a green commit touching the ledger and two source files → exactly the two source files,
#    in git diff order. The source files are written zeta-first so creation order and diff
#    order disagree, and the ledger sorts first so a list that kept it would lead with it.
repo="$work/green"
git init -q -b main "$repo" >/dev/null 2>&1
mkdir -p "$repo/.tdd" "$repo/lib" "$repo/src"
printf -- '- [ ] a step\n' > "$repo/.tdd/issue-7.md"
git_q "$repo" add -A >/dev/null 2>&1
git_q "$repo" commit -q -m "plan: scope #7" >/dev/null 2>&1
printf 'zeta\n' > "$repo/src/zeta.sh"
printf 'alpha\n' > "$repo/lib/alpha.test.sh"
printf -- '- [x] a step ⟂ refactor pending\n' > "$repo/.tdd/issue-7.md"
git_q "$repo" add -A >/dev/null 2>&1
git_q "$repo" commit -q -m "feat: a step (#7)" >/dev/null 2>&1
green="$(git -C "$repo" rev-parse HEAD)"
expected="$(printf 'lib/alpha.test.sh\nsrc/zeta.sh')"
out="$(cd "$repo" && "$TOUCHED" "$green" 2>&1)"; code=$?
got="$(printf '%s' "$out" | tr ',' '\n' | sed '/^$/d')"
if [[ "$code" == 0 && "$got" == "$expected" ]]; then ok; else
  no "green commit with ledger + two source files → only the two, in diff order (code=$code)"
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$got") | sed 's/^/    /'
fi

# 2. a commit name the repository cannot resolve → exit 2, the code for "no answer could be
#    obtained", and a stderr diagnostic naming the commit. The failure is the plumbing's, not
#    the methodology's: a 1 here would reach the refactor prompt as a clean empty answer.
repo="$work/unresolvable"
git init -q -b main "$repo" >/dev/null 2>&1
printf 'alpha\n' > "$repo/alpha.sh"
git_q "$repo" add -A >/dev/null 2>&1
git_q "$repo" commit -q -m "feat: alpha" >/dev/null 2>&1
missing="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
err="$(cd "$repo" && "$TOUCHED" "$missing" 2>&1 >/dev/null)"; code=$?
if [[ "$code" == 2 && "$err" == *"$missing"* ]]; then ok; else
  no "unresolvable commit → exit 2 with a stderr diagnostic naming it (code=$code, stderr=$err)"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

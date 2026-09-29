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

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

commit_all() {
  git_q "$1" add -A >/dev/null 2>&1
  git_q "$1" commit -q -m "$2" >/dev/null 2>&1
}

new_repo() {
  local dir="$work/$1"
  git init -q -b main "$dir" >/dev/null 2>&1
  echo "$dir"
}

repo="$(new_repo green)"
mkdir -p "$repo/.tdd" "$repo/lib" "$repo/src"
printf -- '- [ ] a step\n' > "$repo/.tdd/issue-7.md"
commit_all "$repo" "plan: scope #7"
printf 'zeta\n' > "$repo/src/zeta.sh"
printf 'alpha\n' > "$repo/lib/alpha.test.sh"
printf -- '- [x] a step ⟂ refactor pending\n' > "$repo/.tdd/issue-7.md"
commit_all "$repo" "feat: a step (#7)"
green="$(git -C "$repo" rev-parse HEAD)"
expected="$(printf 'lib/alpha.test.sh\nsrc/zeta.sh')"
out="$(cd "$repo" && "$TOUCHED" "$green" 2>&1)"; code=$?
got="$(printf '%s' "$out" | tr ',' '\n' | sed '/^$/d')"
if [[ "$code" == 0 && "$got" == "$expected" ]]; then ok; else
  no "green commit with ledger + two source files → only the two, in diff order (code=$code)"
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$got") | sed 's/^/    /'
fi

repo="$(new_repo unresolvable)"
printf 'alpha\n' > "$repo/alpha.sh"
commit_all "$repo" "feat: alpha"
missing="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
err="$(cd "$repo" && "$TOUCHED" "$missing" 2>&1 >/dev/null)"; code=$?
if [[ "$code" == 2 && "$err" == *"$missing"* ]]; then ok; else
  no "unresolvable commit → exit 2 with a stderr diagnostic naming it (code=$code, stderr=$err)"
fi

repo="$(new_repo ledger-only)"
mkdir -p "$repo/.tdd"
printf 'alpha\n' > "$repo/alpha.sh"
commit_all "$repo" "feat: alpha"
printf -- '- [x] a step ⟂ refactor pending\n' > "$repo/.tdd/issue-9.md"
commit_all "$repo" "chore: tick the ledger (#9)"
ledger_only="$(git -C "$repo" rev-parse HEAD)"
out="$(cd "$repo" && "$TOUCHED" "$ledger_only" 2>/dev/null)"; code=$?
if [[ "$code" == 3 && -z "$out" ]]; then ok; else
  no "commit touching only .tdd/ → exit 3 and nothing on stdout (code=$code, stdout=$out)"
fi

repo="$(new_repo issue-range)"
mkdir -p "$repo/.tdd" "$repo/lib" "$repo/src"
printf -- '- [ ] a step\n' > "$repo/.tdd/issue-11.md"
commit_all "$repo" "plan: scope #11"
base="$(git -C "$repo" rev-parse HEAD)"
printf 'zeta\n' > "$repo/src/zeta.sh"
printf -- '- [x] a step\n' > "$repo/.tdd/issue-11.md"
commit_all "$repo" "feat: a step (#11)"
printf 'alpha\n' > "$repo/lib/alpha.test.sh"
commit_all "$repo" "refactor: alpha (#11)"
last_code="$(git -C "$repo" rev-parse HEAD)"
printf -- '- [x] a step ⟂ done\n' > "$repo/.tdd/issue-11.md"
commit_all "$repo" "chore: tick the ledger (#11)"
out="$(cd "$repo" && "$TOUCHED" --issue "$base" 2>&1)"; code=$?
none_out="$(cd "$repo" && "$TOUCHED" --issue "$last_code" 2>/dev/null)"; none_code=$?
missing="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
bad_err="$(cd "$repo" && "$TOUCHED" --issue "$missing" 2>&1 >/dev/null)"; bad_code=$?
if [[ "$code" == 0 && "$out" == "lib/alpha.test.sh,src/zeta.sh" \
   && "$none_code" == 3 && -z "$none_out" \
   && "$bad_code" == 2 && "$bad_err" == *"$missing"* ]]; then ok; else
  no "--issue <base> → base..HEAD files outside .tdd/ comma-joined, 3 when none, 2 when unresolvable (code=$code, stdout=$out; none_code=$none_code, none_out=$none_out; bad_code=$bad_code, bad_err=$bad_err)"
fi

out="$(cd "$repo" && "$TOUCHED" --issue 2>/dev/null)"; code=$?
err="$(cd "$repo" && "$TOUCHED" --issue 2>&1 >/dev/null)"
if [[ "$code" == 2 && -z "$out" && "$err" == *"usage: refactor-touched.sh"* ]]; then ok; else
  no "--issue with no base → exit 2 with the usage (code=$code, stdout=$out, stderr=$err)"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

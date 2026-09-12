#!/usr/bin/env bash
# Unit tests for docs/merge-gates.sh — the merge-time decision about which docs gates a
# branch owes. Zero-dependency plain-shell asserts, same idiom as the other suites.
#
# The gates themselves are slow (the guards ~2 min, the freshness check ~2 s), so every
# decision case runs with VERI_GATES_PLAN=1, which prints what would run and runs nothing:
# the thing under test here is the decision, and the decision is a function of the
# diff. One case at the end lets a gate actually run, against a hand-edited page, so the
# failure path — exit 1 and the fix printed — has been watched to fire.
#
# Each case builds a disposable repository: a base branch standing in for origin/main,
# and a branch with one change on top. VERI_GATES_BASE points at the local base.
#
# Run: docs/tests/merge-gates.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
pass=0 fail=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# repo — a copy of the docs pipeline, the scripts, SKILL.md and the Makefile, committed
# once on `base`, with `work` checked out on top. The page is built once so docs-fresh
# has a committed file to compare against.
repo() {
  local d; d="$(mktemp -d "$WORK/case.XXXXXX")"
  mkdir -p "$d/docs" "$d/skills/tdd"
  cp "$ROOT/docs/build-walkthrough.py" "$ROOT/docs/check-walkthrough.py" "$ROOT/docs/merge-gates.sh" "$d/docs/"
  cp -R "$ROOT/docs/wt" "$d/docs/wt"; rm -rf "$d/docs/wt/__pycache__"
  cp -R "$ROOT/docs/tests" "$d/docs/tests"
  cp -R "$ROOT/skills/tdd/scripts" "$d/skills/tdd/scripts"
  cp "$ROOT/skills/tdd/SKILL.md" "$d/skills/tdd/"
  cp "$ROOT/Makefile" "$d/"
  ( cd "$d" && python3 docs/build-walkthrough.py >/dev/null 2>&1 )
  git -C "$d" -c init.defaultBranch=base init -q
  git -C "$d" config user.email veri@example.invalid
  git -C "$d" config user.name veri
  git -C "$d" config commit.gpgsign false
  git -C "$d" add -A
  git -C "$d" commit -qm 'feat: the tree (#1)'
  git -C "$d" checkout -qb work
  printf '%s' "$d"
}

touch_file() { printf '\n# touched\n' >> "$1"; }
export -f touch_file

# plans <name> <expected-substring> <unexpected-substring> <mutator...>
# The mutator runs in the repo and commits; merge-gates then runs in plan mode and its
# stdout must contain the first string and not the second. GATES (default auto) is the
# VERI_GATES value handed to the script, so one case can assert on `all`.
GATES=auto
plans() {
  local name="$1" want="$2" unwanted="$3"; shift 3
  local d out code; d="$(repo)"
  ( cd "$d" && "$@" && git add -A && git commit -qm 'work' --allow-empty )
  out="$(cd "$d" && VERI_GATES="$GATES" VERI_GATES_PLAN=1 VERI_GATES_BASE=base docs/merge-gates.sh 2>&1)" && code=0 || code=$?
  if [[ "$code" == 0 && "$out" == *"$want"* && ( -z "$unwanted" || "$out" != *"$unwanted"* ) ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want:     $want"
    [[ -n "$unwanted" ]] && echo "    not:      $unwanted"
    echo "$out" | sed 's/^/    | /'
  fi
}

# 1. a branch that changed nothing the page reads owes nothing — and says so, rather
#    than silently exiting 0.
plans "no page input changed: nothing runs" 'nothing to run' 'docs-fresh' \
  bash -c 'echo x > README.md'

# 2. a script changed: the page may be stale, the build is not suspect. Fresh only.
plans "a script changed: freshness only" 'docs-fresh' 'docs-test' \
  bash -c 'touch_file skills/tdd/scripts/classify-bail.sh'

# 3. SKILL.md changed: the page cross-checks its revise budget. Fresh only.
plans "SKILL.md changed: freshness only" 'docs-fresh' 'docs-test' \
  bash -c 'touch_file skills/tdd/SKILL.md'

# 4. the page itself changed by hand: freshness catches a hand edit. Fresh only.
plans "the page was edited: freshness only" 'docs-fresh' 'docs-test' \
  bash -c 'touch_file docs/walkthrough.html'

# 5. the pipeline changed: the guards must fire too, and the reason names the file.
plans "commentary changed: guards and freshness" 'docs-test  (build guards' '' \
  bash -c 'touch_file docs/wt/commentary.py'

# 6. so does a change to the guard suite itself.
plans "the guard suite changed: guards and freshness" 'docs-test' '' \
  bash -c 'touch_file docs/tests/build-guards.test.sh'

# 7. uncommitted work counts: a gate that ignored the working tree would pass a dirty
#    merge. The mutator leaves the change unstaged (no commit of it — the commit is empty).
plans "an uncommitted script change still counts" 'docs-fresh' '' \
  bash -c 'touch_file skills/tdd/scripts/verify.sh; git stash -q; git stash pop -q; git reset -q'

# 8. VERI_GATES=all runs both whatever the diff says — here, a diff that owes nothing.
GATES=all plans "VERI_GATES=all overrides the diff" 'docs-test' '' \
  bash -c 'echo x > README.md'
GATES=auto

# 8b. and a value that is neither is refused with exit 2, not treated as auto.
d="$(repo)"
out="$(cd "$d" && VERI_GATES=sometimes VERI_GATES_PLAN=1 VERI_GATES_BASE=base docs/merge-gates.sh 2>&1)" && code=0 || code=$?
if [[ "$code" == 2 && "$out" == *"must be auto or all"* ]]; then pass=$((pass + 1)); else
  fail=$((fail + 1)); echo "FAIL - a bad VERI_GATES is exit 2 (exit $code)"; echo "$out" | sed 's/^/    | /'; fi

# 9. a base that does not resolve is exit 2, not a silent "nothing changed".
d="$(repo)"
( cd "$d" && echo x > README.md && git add -A && git commit -qm work )
out="$(cd "$d" && VERI_GATES_PLAN=1 VERI_GATES_BASE=no-such-ref docs/merge-gates.sh 2>&1)" && code=0 || code=$?
if [[ "$code" == 2 && "$out" == *"does not resolve"* ]]; then pass=$((pass + 1)); else
  fail=$((fail + 1)); echo "FAIL - unresolvable base is exit 2 (exit $code)"; echo "$out" | sed 's/^/    | /'; fi

# 10. the failure path, for real: a hand-edited page makes docs-fresh fail, merge-gates
#     exits 1 and prints the regen fix. This one rebuilds the page (~2 s).
d="$(repo)"
( cd "$d" && printf '\n<!-- hand edit -->\n' >> docs/walkthrough.html && git add -A && git commit -qm 'hand edit' )
out="$(cd "$d" && VERI_GATES_BASE=base docs/merge-gates.sh 2>&1)" && code=0 || code=$?
if [[ "$code" == 1 && "$out" == *"stale"* && "$out" == *"make docs && git add docs/walkthrough.html"* ]]; then pass=$((pass + 1)); else
  fail=$((fail + 1)); echo "FAIL - a stale page fails with the fix printed (exit $code)"; echo "$out" | tail -6 | sed 's/^/    | /'; fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

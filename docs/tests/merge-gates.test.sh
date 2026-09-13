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
  cp "$ROOT/docs/build-walkthrough.py" "$ROOT/docs/check-walkthrough.py" "$ROOT/docs/merge-gates.sh" \
     "$ROOT/docs/docs-owed.sh" "$d/docs/"
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

# plans <name> <expected-substrings> <unexpected-substring> <mutator...>
# The mutator runs in the repo and commits; merge-gates then runs in plan mode and its
# stdout must contain every expected string and not the unexpected one. The expected
# argument is one substring per line, because a case that owes both gates asserts on both
# lines of the plan and on the reason each names. GATES (default auto) is the VERI_GATES
# value handed to the script, so one case can assert on `all`.
GATES=auto
plans() {
  local name="$1" want="$2" unwanted="$3"; shift 3
  local d out code w missing=""; d="$(repo)"
  ( cd "$d" && "$@" && git add -A && git commit -qm 'work' --allow-empty )
  out="$(cd "$d" && VERI_GATES="$GATES" VERI_GATES_PLAN=1 VERI_GATES_BASE=base docs/merge-gates.sh 2>&1)" && code=0 || code=$?
  # one pass over the wants, collecting the unmet ones as the report lines they become: what
  # decides the case is exactly what the failure needs to print, so it is gathered once
  # rather than the list walked again. Empty means every want was found.
  while IFS= read -r w; do
    [[ -z "$w" || "$out" == *"$w"* ]] || missing+="    missing:  $w"$'\n'
  done <<< "$want"
  if [[ "$code" == 0 && -z "$missing" && ( -z "$unwanted" || "$out" != *"$unwanted"* ) ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    printf '%s' "$missing"
    [[ -n "$unwanted" ]] && echo "    not:      $unwanted"
    echo "$out" | sed 's/^/    | /'
  fi
}

# 1. a branch that changed nothing the page reads owes nothing — and says so, rather
#    than silently exiting 0.
plans "no page input changed: nothing runs" 'nothing to run' 'docs-fresh' \
  bash -c 'echo x > README.md'

# 2. #125: a change under skills/ owes no gate at all. Until #125 a script owed docs-fresh
#    and SKILL.md owed it too (the page cross-checks its revise budget); those two paths are
#    the whole of what an ordinary development PR touches, and owing them a fresh page is
#    what put the `make docs` regen commit — plus the prose the build refused to build
#    without — on the critical path of every script change. The page is allowed to lag now:
#    the build carries an uncovered line as debt and docs/docs-owed.sh files it, so the merge
#    no longer has to collect it. One case for both paths, because "nothing under skills/" is
#    one rule and not two: the branch changes a script and SKILL.md together and still owes
#    nothing.
plans "a change under skills/ owes nothing" 'nothing to run' 'docs-fresh' \
  bash -c 'touch_file skills/tdd/scripts/classify-bail.sh; touch_file skills/tdd/SKILL.md'

# 3. the page itself changed by hand: freshness catches a hand edit. Fresh only.
plans "the page was edited: freshness only" 'docs-fresh' 'docs-test' \
  bash -c 'touch_file docs/walkthrough.html'

# 4. the pipeline changed: the docs suites must fire too, and the reason names the file.
plans "commentary changed: docs-test and freshness" 'docs-test  (every docs suite' '' \
  bash -c 'touch_file docs/wt/commentary.py'

# 5. so does a change to the guard suite itself.
plans "the guard suite changed: docs-test and freshness" 'docs-test' '' \
  bash -c 'touch_file docs/tests/build-guards.test.sh'

# 5b. #137: so does anything else under docs/. Before this, the pipeline pattern named
#     docs/wt/, the two python scripts and docs/tests/ one by one, so docs/docs-owed.sh and
#     docs/merge-gates.sh matched neither pattern and a change to either got no gate at
#     all — and since the docs suites left `make test`, two of them ran in no gate
#     anywhere. The rule is the directory now, minus the page on its own (case 3): a branch
#     that changes only docs/docs-owed.sh owes every docs suite plus the freshness check,
#     and the reason names the file.
plans "a change under docs/ outside the page owes every docs suite and freshness" \
  $'docs-test\ndocs-fresh\ndocs/docs-owed.sh' '' \
  bash -c 'touch_file docs/docs-owed.sh'

# 6. uncommitted work counts: a gate that ignored the working tree would pass a dirty
#    merge. The mutator leaves the change unstaged (no commit of it — the commit is empty).
#    It edits the docs pipeline rather than a script because since #125 a script owes no
#    gate, so a script here would be indistinguishable from the working tree being ignored.
plans "an uncommitted pipeline change still counts" 'docs-test' '' \
  bash -c 'touch_file docs/wt/commentary.py; git stash -q; git stash pop -q; git reset -q'

# 7. VERI_GATES=all runs both whatever the diff says — here, a diff that owes nothing.
GATES=all plans "VERI_GATES=all overrides the diff" 'docs-test' '' \
  bash -c 'echo x > README.md'
GATES=auto

# 7b. and a value that is neither is refused with exit 2, not treated as auto.
d="$(repo)"
out="$(cd "$d" && VERI_GATES=sometimes VERI_GATES_PLAN=1 VERI_GATES_BASE=base docs/merge-gates.sh 2>&1)" && code=0 || code=$?
if [[ "$code" == 2 && "$out" == *"must be auto or all"* ]]; then pass=$((pass + 1)); else
  fail=$((fail + 1)); echo "FAIL - a bad VERI_GATES is exit 2 (exit $code)"; echo "$out" | sed 's/^/    | /'; fi

# 8. a base that does not resolve is exit 2, not a silent "nothing changed".
d="$(repo)"
( cd "$d" && echo x > README.md && git add -A && git commit -qm work )
out="$(cd "$d" && VERI_GATES_PLAN=1 VERI_GATES_BASE=no-such-ref docs/merge-gates.sh 2>&1)" && code=0 || code=$?
if [[ "$code" == 2 && "$out" == *"does not resolve"* ]]; then pass=$((pass + 1)); else
  fail=$((fail + 1)); echo "FAIL - unresolvable base is exit 2 (exit $code)"; echo "$out" | sed 's/^/    | /'; fi

# 9. the failure path, for real: a hand-edited page makes docs-fresh fail, merge-gates
#    exits 1 and prints the regen fix. This one rebuilds the page (~2 s).
d="$(repo)"
( cd "$d" && printf '\n<!-- hand edit -->\n' >> docs/walkthrough.html && git add -A && git commit -qm 'hand edit' )
out="$(cd "$d" && VERI_GATES_BASE=base docs/merge-gates.sh 2>&1)" && code=0 || code=$?
if [[ "$code" == 1 && "$out" == *"stale"* && "$out" == *"make docs && git add docs/walkthrough.html"* ]]; then pass=$((pass + 1)); else
  fail=$((fail + 1)); echo "FAIL - a stale page fails with the fix printed (exit $code)"; echo "$out" | tail -6 | sed 's/^/    | /'; fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

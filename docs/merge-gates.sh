#!/usr/bin/env bash
# merge-gates.sh — run the docs gates CI does not, and only the ones this branch's
# changes warrant. Meant to run once, at merge time, in the PR's worktree on the
# rebased tip: `make merge-gates`.
#
# WHY NOT CI, WHY NOT A PUSH HOOK: the walkthrough's guards (docs/tests/build-guards.test.sh)
# rebuild the page thirty-odd times and take ~140 s; even the freshness check
# (docs/check-walkthrough.py) rebuilds it once, ~20 s, because `make docs` shells out to
# git blame per script for the hunk marks. On a runner billed by the minute that was the
# bulk of the bill; on a pre-push hook it fires on pushes that touched nothing the page
# reads. The merge is the one moment the check is owed, and it is owed exactly to the
# extent the branch changed an input. So: diff against the base, decide, run.
#
# WHAT THE PAGE READS, AND SO WHAT WARRANTS WHICH GATE:
#   pipeline  docs/wt/*, docs/build-walkthrough.py, docs/check-walkthrough.py, docs/tests/
#             → the guards (docs-test) AND the freshness check (docs-fresh). Changing how
#               the page is built is the only way to break the guards.
#   inputs    skills/tdd/scripts/*.sh, skills/tdd/SKILL.md (the revise
#             budget the page cross-checks), docs/walkthrough.html itself (a hand edit),
#             Makefile → the freshness check only: the page may now be stale, but the
#               build that makes it has not changed.
#   anything else → nothing. A test-only or README PR owes no page.
# Tags are NOT a file, so a tag cut since the page was built is not seen here; that is
# docs/hooks/reference-transaction's job, and docs-fresh names the missing tag if it runs.
#
# EXIT CODES, the repo-wide four: 0 = every gate that ran passed (or none was owed);
# 1 = a gate ran and failed — check-walkthrough's own output says which and, for a stale
# page, the fix; 2 = no answer could be obtained (the base ref does not resolve, a bad
# VERI_GATES value).
#
# TUNABLES, all ${VAR:-default} so the test suite can inject:
#   VERI_GATES_BASE  the ref the branch is compared against (default origin/main)
#   VERI_GATES       auto (default) decide from the diff; all = run both regardless
#   VERI_GATES_PLAN  1 = print the decision and run nothing (what the tests assert on)
set -uo pipefail

base="${VERI_GATES_BASE:-origin/main}"
mode="${VERI_GATES:-auto}"
plan="${VERI_GATES_PLAN:-0}"
root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "merge-gates: not a git repository" >&2; exit 2; }
cd "$root" || exit 2

case "$mode" in auto|all) ;; *)
  echo "merge-gates: VERI_GATES must be auto or all — got '$mode'" >&2; exit 2;; esac

mb="$(git merge-base HEAD "$base" 2>/dev/null)" || {
  echo "merge-gates: base ref '$base' does not resolve (set VERI_GATES_BASE)" >&2; exit 2; }

# Committed on the branch since it left the base, plus anything uncommitted — a merge
# should never see the latter, but a gate that ignored it would pass a dirty tree.
changed="$( { git diff --name-only "$mb" HEAD; git diff --name-only HEAD; git ls-files --others --exclude-standard; } | sort -u)"

pipeline_re='^docs/(wt/|build-walkthrough\.py$|check-walkthrough\.py$|tests/)'
inputs_re='^(skills/tdd/scripts/[^/]+\.sh|skills/tdd/SKILL\.md|docs/walkthrough\.html|Makefile)$'

run_test=0 run_fresh=0 why_test="" why_fresh=""
if [ "$mode" = all ]; then
  run_test=1 run_fresh=1 why_test="VERI_GATES=all" why_fresh="VERI_GATES=all"
else
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    if [[ "$f" =~ $pipeline_re ]]; then
      run_test=1 run_fresh=1; why_test="${why_test:-$f}"; why_fresh="${why_fresh:-$f}"
    elif [[ "$f" =~ $inputs_re ]]; then
      run_fresh=1; why_fresh="${why_fresh:-$f}"
    fi
  done <<< "$changed"
fi

if [ $run_test -eq 0 ] && [ $run_fresh -eq 0 ]; then
  echo "merge-gates: nothing to run — no page input changed against $base"
  exit 0
fi
[ $run_test  -eq 1 ] && echo "merge-gates: docs-test  (build guards, ~140 s) — $why_test"
[ $run_fresh -eq 1 ] && echo "merge-gates: docs-fresh (rebuild + compare, ~20 s) — $why_fresh"
[ "$plan" = 1 ] && exit 0

rc=0
if [ $run_test -eq 1 ]; then
  docs/tests/build-guards.test.sh || rc=1
fi
if [ $run_fresh -eq 1 ]; then
  python3 docs/check-walkthrough.py || {
    rc=1
    echo "merge-gates: if the page is merely stale, regenerate it as its own commit on the branch:" >&2
    echo "             make docs && git add docs/walkthrough.html && git commit -m 'docs: regenerate walkthrough'" >&2
  }
fi
[ $rc -eq 0 ] && echo "merge-gates: all gates passed" || echo "merge-gates: a gate FAILED" >&2
exit $rc

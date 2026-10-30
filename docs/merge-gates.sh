#!/usr/bin/env bash
# merge-gates.sh — run the docs gates CI does not, and only the ones this branch's
# changes warrant. Meant to run once, at merge time, in the PR's worktree on the
# rebased tip: `make merge-gates`.
#
# WHY NOT CI, WHY NOT A PUSH HOOK: the walkthrough's guards (docs/tests/build-guards.test.sh)
# rebuild the page thirty-odd times and take minutes; even the freshness check
# (docs/check-walkthrough.py) rebuilds it once — ~20 s when this was decided, ~2 s since
# gitmeta.py asks git once per tag instead of once per commit. On a billed runner it was the
# bulk of the bill; on a pre-push hook it fires on pushes that touched nothing the page
# reads. The merge is the one moment the check is owed, and it is owed exactly to the
# extent the branch changed an input. So: diff against the base, decide, run.
#
# WHAT THE PAGE READS, AND SO WHAT WARRANTS WHICH GATE:
#   pipeline  anything under docs/ except the page itself → every suite under docs/tests/
#             (docs-test) AND the freshness check (docs-fresh). The rule is the directory,
#             not a list of its parts (#137): docs/docs-owed.sh and this script matched no
#             listed part and so got no gate at all, and since the docs suites left
#             `make test` two of them ran in no gate anywhere.
#   stale     docs/walkthrough.html itself (a hand edit) → the freshness check only: the
#             page is the one thing under docs/ that is output, not input, so a hand edit
#             to it can only make it stale — the build that makes it is unchanged.
#   anything else → nothing. A README or test-only PR owes no page, and since #125 neither
#             does anything under skills/ — a script or SKILL.md change included — nor,
#             since #146, anything under docs/adr/, nor, since #164, the Makefile.
# Tags are NOT a file, so a tag cut since the page was built is not seen here; that is
# docs/hooks/reference-transaction's job, and docs-fresh names the missing tag if it runs.
#
# WHY skills/ OWES NOTHING (#125): a script change does leave the page stale. That
# staleness is now debt the page carries openly — an uncovered line renders marked
# `commentary owed` — and docs/docs-owed.sh files, rather than a bill collected at merge.
# Owing a fresh page put the `make docs` regen commit, and the prose the build used to
# refuse to build without, on the critical path of every development PR. Prose is allowed
# to lag; the page's promise is that the source it shows is verbatim, not that it is
# explained.
#
# WHY docs/adr/ OWES NOTHING (#146): an ADR is a record of a decision, and the page build
# reads none of them — `grep -n adr docs/build-walkthrough.py docs/wt/gitmeta.py
# docs/check-walkthrough.py` finds nothing — so an ADR can neither make the page stale nor
# move a guard. Under the directory rule above it nevertheless matched ^docs/, and since
# development issues record their decisions there (#125 committed ADR 0016 that way), every
# development PR carrying one paid the whole docs lane — the suites plus the freshness
# check, ~5 min — for a file the lane does not read. It is carved back out the same way
# skills/ is. The docs lane's own runs still cover it: every suite under docs/tests/ runs
# by existing under the docs-test glob, whatever this decision says.
#
# WHY Makefile OWES NOTHING (#164): a Makefile change can break a docs target, but it does
# not make the committed page stale — the page goes stale by design on every tag and every
# script change (#125). So the check on a development branch failed for what the base did
# while the branch was open, whatever the recipe edit was: #160 changed only the `test`
# recipe and still had to choose between regenerating the page on a development branch and
# merging past a red gate. A Makefile change that breaks a docs target is the docs lane's
# to catch on its own cadence (`make docs-check`, docs/docs-owed.sh) — not this merge's.
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

# Declared in the order they are applied below: exempt drops a path (#146) before either of
# the two rules under it judges it; then stale, then pipeline.
exempt_re='^docs/adr/'
stale_re='^docs/walkthrough\.html$'
pipeline_re='^docs/'

run_test=0 run_fresh=0 why_test="" why_fresh=""
if [ "$mode" = all ]; then
  run_test=1 run_fresh=1 why_test="VERI_GATES=all" why_fresh="VERI_GATES=all"
else
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    # a second guard, not a third rule: a path under docs/ the build does not read owes
    # nothing (#146), so it is dropped here rather than reaching the chain below, where it
    # would match the pipeline rule.
    [[ "$f" =~ $exempt_re ]] && continue
    # stale first: the page is the one thing under docs/ that is output, not input.
    if [[ "$f" =~ $stale_re ]]; then
      run_fresh=1; why_fresh="${why_fresh:-$f}"
    elif [[ "$f" =~ $pipeline_re ]]; then
      run_test=1 run_fresh=1; why_test="${why_test:-$f}"; why_fresh="${why_fresh:-$f}"
    fi
  done <<< "$changed"
fi

if [ $run_test -eq 0 ] && [ $run_fresh -eq 0 ]; then
  echo "merge-gates: nothing to run — no page input changed against $base"
  exit 0
fi
[ $run_test  -eq 1 ] && echo "merge-gates: docs-test  (every docs suite, ~2 min) — $why_test"
[ $run_fresh -eq 1 ] && echo "merge-gates: docs-fresh (rebuild + compare, ~2 s) — $why_fresh"
[ "$plan" = 1 ] && exit 0

rc=0
if [ $run_test -eq 1 ]; then
  # every suite under docs/tests/, via the target that globs them — naming one here would
  # leave the suites added since out of the only gate that runs them. This script's own
  # tunables are unset first: one of those suites tests this script, and an ambient
  # VERI_GATES=all or VERI_GATES_PLAN=1 would reach the cases that set neither and fail them.
  env -u VERI_GATES -u VERI_GATES_PLAN -u VERI_GATES_BASE make docs-test || rc=1
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

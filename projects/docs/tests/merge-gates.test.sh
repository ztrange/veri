#!/usr/bin/env bash
# Unit tests for projects/docs/merge-gates.sh — the merge-time decision about which docs gates a
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
# Run: projects/docs/tests/merge-gates.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
pass=0 fail=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# repo — a copy of the docs pipeline, the scripts, SKILL.md and the Makefile, committed
# once on `base`, with `work` checked out on top. The page is built once so docs-fresh
# has a committed file to compare against.
#
# The top-level docs scripts come in by glob, not by name: every one of them is a file a
# case may touch now that the rule is the directory (#137), and a roster here is the same
# debt the Makefile's one-line-per-suite recipe was — it puts an edit between adding a
# docs script and a case being able to name it. The page is excluded because it is built
# below, not copied.
repo() {
  local d; d="$(mktemp -d "$WORK/case.XXXXXX")"
  mkdir -p "$d/projects/docs" "$d/skills/tdd"
  cp "$ROOT"/projects/docs/*.py "$ROOT"/projects/docs/*.sh "$d/projects/docs/"
  cp -R "$ROOT/projects/docs/wt" "$d/projects/docs/wt"; rm -rf "$d/projects/docs/wt/__pycache__"
  cp -R "$ROOT/projects/docs/tests" "$d/projects/docs/tests"
  cp -R "$ROOT/skills/tdd/scripts" "$d/skills/tdd/scripts"
  cp "$ROOT/skills/tdd/SKILL.md" "$d/skills/tdd/"
  cp "$ROOT/Makefile" "$d/"
  ( cd "$d" && python3 projects/docs/build-walkthrough.py >/dev/null 2>&1 )
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
  out="$(cd "$d" && VERI_GATES="$GATES" VERI_GATES_PLAN=1 VERI_GATES_BASE=base projects/docs/merge-gates.sh 2>&1)" && code=0 || code=$?
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
#    the build carries an uncovered line as debt and projects/docs/docs-owed.sh files it, so the merge
#    no longer has to collect it. One case for both paths, because "nothing under skills/" is
#    one rule and not two: the branch changes a script and SKILL.md together and still owes
#    nothing.
plans "a change under skills/ owes nothing" 'nothing to run' 'docs-fresh' \
  bash -c 'touch_file skills/tdd/scripts/classify-bail.sh; touch_file skills/tdd/SKILL.md'

# 2b. #146: and neither does an ADR travelling with it. A development issue records its
#     decisions under docs/adr/ — #125 committed ADR 0016 that way — and the page build
#     reads nothing there: `grep -n adr projects/docs/build-walkthrough.py projects/docs/wt/gitmeta.py
#     projects/docs/check-walkthrough.py` finds nothing, so an ADR can neither make the page stale
#     nor move a guard. Under the directory rule (case 5b) it nevertheless matched ^projects/docs/
#     and billed every development PR carrying one the whole docs lane — the suites plus the
#     freshness check, ~5 min — for a file the lane does not read. docs/adr/ is carved back
#     out, the same way skills/ is: a branch whose changes outside the owed-nothing set are
#     only under docs/adr/ owes no gate. One case for both paths because it is one rule and
#     not two — the branch touches a script and an ADR together and still owes nothing.
#     The sandbox carries no docs/adr — nothing in the pipeline reads one — so the case
#     makes the directory and then changes the ADR the way every other case changes its
#     file. What the decision reads is the path; the content is never opened, so there is
#     none to write.
plans "a change under skills/ and docs/adr/ owes nothing" 'nothing to run' 'docs-fresh' \
  bash -c 'touch_file skills/tdd/scripts/classify-bail.sh
           mkdir -p docs/adr && touch_file docs/adr/0017-a-decision.md'

# 3. the page itself changed by hand: freshness catches a hand edit. Fresh only.
plans "the page was edited: freshness only" 'docs-fresh' 'docs-test' \
  bash -c 'touch_file projects/docs/walkthrough.html'

# 4. the pipeline changed: the docs suites must fire too, and the reason names the file.
plans "commentary changed: docs-test and freshness" 'docs-test  (every docs suite' '' \
  bash -c 'touch_file projects/docs/wt/commentary.py'

# 4b. #146: and the exemption case 2b carves out stops at docs/adr/. projects/docs/wt/ is the
#     directory the build actually reads — every module the page is assembled from lives
#     there — so a change to one is the clearest thing there is that owes both gates: the
#     suites, because a guard can move, and the freshness check, because the page the
#     module builds is now a different page. An exemption written one character too wide
#     (`^projects/docs/(adr|wt)/`, `^projects/docs/a`) takes this with it and the whole docs lane goes quiet
#     on its own pipeline, which is why the boundary gets a case of its own rather than
#     being left implied by case 4. Asserts on both plan lines and on the reason naming the
#     file, and touches gitmeta.py rather than commentary.py so it pins the directory and
#     not the one file another case already stands on.
plans "a change under projects/docs/wt/ owes every docs suite and freshness" \
  $'docs-test\ndocs-fresh\nprojects/docs/wt/gitmeta.py' '' \
  bash -c 'touch_file projects/docs/wt/gitmeta.py'

# 5. so does a change to the guard suite itself.
plans "the guard suite changed: docs-test and freshness" 'docs-test' '' \
  bash -c 'touch_file projects/docs/tests/build-guards.test.sh'

# 5b. #137: so does anything else under projects/docs/. Before this, the pipeline pattern named
#     projects/docs/wt/, the two python scripts and projects/docs/tests/ one by one, so projects/docs/docs-owed.sh and
#     projects/docs/merge-gates.sh matched neither pattern and a change to either got no gate at
#     all — and since the docs suites left `make test`, two of them ran in no gate
#     anywhere. The rule is the directory now, minus the page on its own (case 3): a branch
#     that changes only projects/docs/docs-owed.sh owes every docs suite plus the freshness check,
#     and the reason names the file.
plans "a change under projects/docs/ outside the page owes every docs suite and freshness" \
  $'docs-test\ndocs-fresh\nprojects/docs/docs-owed.sh' '' \
  bash -c 'touch_file projects/docs/docs-owed.sh'

# 6. uncommitted work counts: a gate that ignored the working tree would pass a dirty
#    merge. The mutator leaves the change unstaged (no commit of it — the commit is empty).
#    It edits the docs pipeline rather than a script because since #125 a script owes no
#    gate, so a script here would be indistinguishable from the working tree being ignored.
plans "an uncommitted pipeline change still counts" 'docs-test' '' \
  bash -c 'touch_file projects/docs/wt/commentary.py; git stash -q; git stash pop -q; git reset -q'

# 7. VERI_GATES=all runs both whatever the diff says — here, a diff that owes nothing.
GATES=all plans "VERI_GATES=all overrides the diff" 'docs-test' '' \
  bash -c 'echo x > README.md'
GATES=auto

# 7b. and a value that is neither is refused with exit 2, not treated as auto.
d="$(repo)"
out="$(cd "$d" && VERI_GATES=sometimes VERI_GATES_PLAN=1 VERI_GATES_BASE=base projects/docs/merge-gates.sh 2>&1)" && code=0 || code=$?
if [[ "$code" == 2 && "$out" == *"must be auto or all"* ]]; then pass=$((pass + 1)); else
  fail=$((fail + 1)); echo "FAIL - a bad VERI_GATES is exit 2 (exit $code)"; echo "$out" | sed 's/^/    | /'; fi

# 8. a base that does not resolve is exit 2, not a silent "nothing changed".
d="$(repo)"
( cd "$d" && echo x > README.md && git add -A && git commit -qm work )
out="$(cd "$d" && VERI_GATES_PLAN=1 VERI_GATES_BASE=no-such-ref projects/docs/merge-gates.sh 2>&1)" && code=0 || code=$?
if [[ "$code" == 2 && "$out" == *"does not resolve"* ]]; then pass=$((pass + 1)); else
  fail=$((fail + 1)); echo "FAIL - unresolvable base is exit 2 (exit $code)"; echo "$out" | sed 's/^/    | /'; fi

# 9. the failure path, for real: a hand-edited page makes docs-fresh fail, merge-gates
#    exits 1 and prints the regen fix. This one rebuilds the page (~2 s).
d="$(repo)"
( cd "$d" && printf '\n<!-- hand edit -->\n' >> projects/docs/walkthrough.html && git add -A && git commit -qm 'hand edit' )
out="$(cd "$d" && VERI_GATES_BASE=base projects/docs/merge-gates.sh 2>&1)" && code=0 || code=$?
if [[ "$code" == 1 && "$out" == *"stale"* && "$out" == *"make docs && git add projects/docs/walkthrough.html"* ]]; then pass=$((pass + 1)); else
  fail=$((fail + 1)); echo "FAIL - a stale page fails with the fix printed (exit $code)"; echo "$out" | tail -6 | sed 's/^/    | /'; fi

# 10. #137: a stale page still fails the merge after the guards stopped judging it.
#     build-guards.test.sh dropped page_is_current and page_checks_out so that a tag or a
#     script commit no longer turns `make docs-test` red; the fact they held — a merge
#     cannot land a stale page — is docs-fresh's alone now, and this is where it is
#     watched. The branch edits projects/docs/wt/style.css, which the build inlines into the page,
#     so the staleness comes from a pipeline change rather than the hand edit case 9 uses.
#
#     `make` is stubbed to a no-op for the docs-test half. This is a real run, and the
#     sandbox carries a copy of projects/docs/tests/, so letting docs-test run would run this suite
#     inside itself — and the nested copy would do it again, without bound. The stub takes
#     that half out and leaves docs-fresh, the half under test, running for real (~2 s).
d="$(repo)"
stub="$(mktemp -d "$WORK/stub.XXXXXX")"
cat > "$stub/make" <<'STUB'
#!/usr/bin/env bash
echo "stub make: $*"
STUB
chmod +x "$stub/make"
( cd "$d" && touch_file projects/docs/wt/style.css && git add -A && git commit -qm 'style: a pipeline change' )
out="$(cd "$d" && env PATH="$stub:$PATH" VERI_GATES_BASE=base projects/docs/merge-gates.sh 2>&1)" && code=0 || code=$?
if [[ "$code" == 1 && "$out" == *"projects/docs/wt/style.css"* && "$out" == *"stale"* && "$out" == *"make docs && git add projects/docs/walkthrough.html"* ]]; then pass=$((pass + 1)); else
  fail=$((fail + 1)); echo "FAIL - a projects/docs/wt/ change that leaves the page stale still fails (exit $code)"; echo "$out" | tail -8 | sed 's/^/    | /'; fi

# 11. #164: a branch whose only change is the Makefile owes nothing, and owes it even when
#     the committed page is stale. The Makefile sat in the stale pattern beside the page
#     itself, so every branch that edited a recipe — #160 changed only `test:` — was billed
#     a docs-fresh; and the page goes stale by design on every tag and every script commit,
#     so that gate failed for a reason the branch had nothing to do with. Development does
#     not wait on the docs lane (#125, #137, #146) and the Makefile is not a page input: a
#     recipe that breaks a docs target is the docs lane's to catch on its own cadence.
#
#     A real run, not a plan: what went wrong was a gate that ran, so the pin has to be that
#     none does. The staleness is committed on `base`, not on the branch — a hand edit on
#     the branch would owe docs-fresh on its own (case 3) and the case would be asserting on
#     the wrong file. On base it stands in for what actually happens: main moved, nobody
#     regenerated the page, and this branch touched a recipe.
d="$(repo)"
( cd "$d" \
  && git checkout -q base \
  && printf '\n<!-- a page nobody regenerated -->\n' >> projects/docs/walkthrough.html \
  && git add -A && git commit -qm 'docs: a page left stale on the base' \
  && git checkout -q -B work base \
  && touch_file Makefile \
  && git add -A && git commit -qm 'chore: a recipe change (#164)' )
out="$(cd "$d" && VERI_GATES_BASE=base projects/docs/merge-gates.sh 2>&1)" && code=0 || code=$?
if [[ "$code" == 0 && "$out" == *"nothing to run"* && "$out" != *"docs-fresh"* ]]; then pass=$((pass + 1)); else
  fail=$((fail + 1)); echo "FAIL - a Makefile-only branch runs no gate even against a stale page (exit $code)"; echo "$out" | sed 's/^/    | /'; fi

# 11b. #164: and the carve-out case 11 makes stops at the Makefile itself. A branch that
#      edits a recipe *and* a script under projects/docs/ still owes the whole docs lane — the
#      suites and the freshness check — because the docs script is a page input whatever
#      travels with it. A carve-out written one step too wide (dropping every path once a
#      Makefile change is seen, or exempting the branch rather than the file) takes this
#      with it and a real pipeline change merges ungated, which is why the boundary gets a
#      case of its own rather than being left implied by case 5b. Plan mode: the decision
#      is the thing under test, and the reason must name the docs script, not the Makefile.
plans "the Makefile plus a projects/docs/ script still owes every docs suite and freshness" \
  $'docs-test\ndocs-fresh\nprojects/docs/docs-owed.sh' '' \
  bash -c 'touch_file Makefile; touch_file projects/docs/docs-owed.sh'

# 11c. #164: and the page keeps its own gate whatever travels with it. Case 3 pins the hand
#      edit alone; what the carve-out puts at risk is the hand edit arriving on a branch that
#      also touched the Makefile — the file that used to share the stale rule with it. A
#      carve-out written at branch scope rather than at file scope (nothing runs once a
#      Makefile change is seen) takes the page's own freshness check with it, and a hand
#      edit — the one staleness a rebuild is guaranteed to catch, because the build that
#      makes the page is unchanged — would merge unnoticed. Still docs-fresh only, and the
#      reason still names the page rather than the Makefile: the Makefile now matches no
#      rule, so it neither adds a gate nor removes one.
plans "a hand-edited page travelling with a Makefile still owes freshness" \
  $'docs-fresh\nprojects/docs/walkthrough.html' 'docs-test' \
  bash -c 'touch_file Makefile; touch_file projects/docs/walkthrough.html'

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells a refactor-kind run — an issue whose spec
# carries the `## Refactor` section capture-spec.sh writes for the `refactor` label. Like
# skill-bug-fix-subject.test.sh this suite belongs to no single script: its subject is the
# procedure document, read as text, the way the session that follows it reads it. Picked up
# by `make test`'s glob by existing. Zero-dependency plain-shell asserts, same idiom.
#
# Why this exists (issue #499): a refactor changes no behaviour, so it has no failing test
# to write, and a Red/Green plan for it is a plan with nothing to be red. Its Red is the
# smell being present, stated as a shell command in the step's criterion — false before the
# step, true after — and each step is one named refactoring, so its verifier can judge one
# transform. The plan verifier already REJECTs a plan that does not do this; a procedure
# that never tells the planner to write one would have every refactor run pay for a REJECT
# before its first step.
#
# Contract under test:
#   1. SKILL.md's Scope & plan section tells a refactor-kind run to plan each step as one named
#      refactoring whose criterion is a shell predicate false before the step and true after it.
#   2. The develop-cover prompt and SKILL.md's Cover step — see case 2's comment.
#   3. SKILL.md's Cover step on `COVERED: no` — see case 3's comment.
#   4. SKILL.md's refactor-kind cycle, transform rejection and abandonment — see case 4's comment.
#   5. SKILL.md's Draft PR step titles a refactor-labelled run's PR refactor: — see case 5's comment.
#
# Run: skills/tdd/scripts/tests/skill-refactor-kind.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

section() {
  awk -v h="$1" \
    'index($0, h) == 1 { inside = 1; next } inside && /^###? / { exit } inside' "$skill_path" |
    plain
}

plan_heading='### 2. Scope & plan'

skill_text="$(plain < "$skill_path")"

# hazard: BSD grep refuses an interval bound over 255.
window() {
  head -1 < <(grep -oE ".{0,250}$2.{0,250}" <<<"$1")
}

name="$skill_md tells a refactor-kind run to plan each step as one named refactoring whose criterion is a shell predicate false before the step and true after it"
problems=()

text="$(section "$plan_heading")"
if [[ -z "${text// /}" ]]; then
  problems+=("$skill_md has no '$plan_heading' section to read — how a refactor-kind run plans its steps could not be established")
else
  grep -E 'refactor[- ]kind|## refactor section|label(l)?ed refactor' <<<"$text" > /dev/null ||
    problems+=("$skill_md's '$plan_heading' section never names the refactor run kind, so a run on a refactor issue is planned as Red/Green steps with nothing to be red")
  if ! grep -E 'predicate' <<<"$text" > /dev/null; then
    problems+=("$skill_md's '$plan_heading' section never says a refactor step's criterion is a shell predicate, so the smell a step removes is never stated as something runnable")
  else
    near="$(window "$text" 'predicate')"
    grep -E '(one|named) refactoring' <<<"$near" > /dev/null ||
      problems+=("$skill_md's '$plan_heading' section names a predicate without saying each step is one named refactoring")
    grep -E 'false before' <<<"$near" > /dev/null ||
      problems+=("$skill_md's '$plan_heading' section never says the predicate is false before the step")
    grep -E 'true after' <<<"$near" > /dev/null ||
      problems+=("$skill_md's '$plan_heading' section never says the predicate is true after the step")
  fi
fi
report "$name"

name="the develop-cover prompt tells the leaf to mutate, run the suite, expect red, restore and prove the tree unchanged, ending in COVERED: and CAUGHT_BY:; $skill_md refuses to continue past Cover on a non-empty git status --porcelain"
problems=()

cover_spec="$(mktemp)"
printf 'QWIXTLE spec\n' > "$cover_spec"
cover_raw="$("$HERE/../build-develop-prompt.sh" cover "$cover_spec" 'Extract Function QWIXTLE' 'make test' 2>/dev/null)"
rm -f "$cover_spec"
if [[ -z "$cover_raw" ]]; then
  problems+=("build-develop-prompt.sh cover printed no prompt to read")
else
  cover="$(plain <<<"$cover_raw")"
  grep -E 'mutat|break' <<<"$cover" > /dev/null || problems+=("the cover prompt never tells the leaf to mutate the code the step will move")
  grep -E 'run the suite|run the (affected )?suites' <<<"$cover" > /dev/null || problems+=("the cover prompt never tells the leaf to run the suite")
  grep -E 'expect red' <<<"$cover" > /dev/null || problems+=("the cover prompt never tells the leaf to expect red")
  grep -E 'restore' <<<"$cover" > /dev/null || problems+=("the cover prompt never tells the leaf to restore the edit")
  grep -E 'git diff --exit-code|git status --porcelain' <<<"$cover" > /dev/null || problems+=("the cover prompt never tells the leaf to prove the tree unchanged")
  cover_tail="$(sed '/^[[:space:]]*$/d' <<<"$cover_raw" | tail -n 3)"
  grep -E '^COVERED:' <<<"$cover_tail" > /dev/null || problems+=("the cover prompt's closing lines carry no COVERED: line")
  grep -E '^CAUGHT_BY:' <<<"$cover_tail" > /dev/null || problems+=("the cover prompt's closing lines carry no CAUGHT_BY: line")
fi

cover_near="$(window "$skill_text" '(develop-cover|cover (phase|step|leaf))')"
if ! grep -F 'git status --porcelain' <<<"$cover_near" | grep -E 'refus|stop|bail|(not|never) (go on|continue)' > /dev/null; then
  problems+=("$skill_md never refuses to continue past Cover when git status --porcelain is non-empty afterwards, so a mutation the cover leaf left behind reaches the transform")
fi
report "$name"

name="$skill_md's Cover step on COVERED: no bails with cause uncovered, narrates the remedy (find a seam, surround the behaviour) and runs coverage-blocker.sh"
problems=()

uncovered_near="$(window "$skill_text" 'covered: no')"
if [[ -z "$uncovered_near" ]]; then
  problems+=("$skill_md never says what a run does when Cover answers COVERED: no, so an uncovered refactor step goes on to transform code no test watches")
else
  grep -E 'bail[^.]*cause uncovered|cause uncovered' <<<"$uncovered_near" > /dev/null ||
    problems+=("$skill_md's COVERED: no handling never bails with cause uncovered")
  grep -E 'seam' <<<"$uncovered_near" > /dev/null ||
    problems+=("$skill_md's COVERED: no handling never narrates the remedy of finding a seam")
  grep -E 'surround' <<<"$uncovered_near" > /dev/null ||
    problems+=("$skill_md's COVERED: no handling never narrates the remedy of surrounding the behaviour")
  grep -F 'coverage-blocker.sh' <<<"$uncovered_near" > /dev/null ||
    problems+=("$skill_md's COVERED: no handling never runs coverage-blocker.sh, so the refactor issue stays in the queue to be retaken and refused again")
fi
report "$name"

name="$skill_md's refactor-kind cycle runs Cover → Transform → Verify, rejects a transform whose commits touch a test file via transform-touches-tests.sh, and abandons a step by resetting to its base sha"
problems=()

grep -E 'cover (→|->|, then|then) transform (→|->|, then|then) verify' <<<"$skill_text" > /dev/null ||
  problems+=("$skill_md never states the refactor-kind cycle as Cover → Transform → Verify, so a refactor step is run as Red → Green → Refactor")
touches_near="$(window "$skill_text" 'transform-touches-tests\.sh')"
if [[ -z "$touches_near" ]]; then
  problems+=("$skill_md never runs transform-touches-tests.sh, so a transform that edits a test file is accepted as a refactoring")
else
  grep -E 'reject|refus' <<<"$touches_near" > /dev/null ||
    problems+=("$skill_md runs transform-touches-tests.sh without saying a transform touching a test file is rejected")
fi
grep -E 'git reset --hard <base-sha>|reset(ting)? (it )?to (its|the step.s) base sha' <<<"$skill_text" > /dev/null ||
  problems+=("$skill_md never abandons a refactor-kind step by resetting to its base sha, so an abandoned transform's commits stay on the branch")
report "$name"

pr_heading='### 4. Draft PR'
name="$skill_md's Draft PR step titles a run on an issue labelled refactor with the refactor: prefix, beside fix: and feat:"
problems=()

text="$(section "$pr_heading")"
if [[ -z "${text// /}" ]]; then
  problems+=("$skill_md has no '$pr_heading' section to read — what prefix a refactor run's PR title takes could not be established")
elif ! grep -F 'refactor:' <<<"$text" > /dev/null; then
  problems+=("$skill_md's '$pr_heading' section never names the refactor: prefix, so a refactor run's PR is titled feat: and announces a capability the run did not add")
else
  near="$(window "$text" 'refactor:')"
  grep -E 'label' <<<"$near" > /dev/null ||
    problems+=("$skill_md's '$pr_heading' section names the refactor: prefix without tying it to the refactor label")
  grep -E 'fix' <<<"$near" > /dev/null && grep -E 'feat' <<<"$near" > /dev/null ||
    problems+=("$skill_md's '$pr_heading' section names the refactor: prefix away from the fix: and feat: branches it sits beside")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

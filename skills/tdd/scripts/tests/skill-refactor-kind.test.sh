#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells a refactor-kind run — an issue whose spec
# carries the `## Refactor` section capture-spec.sh writes for the `refactor` label — read
# as text.
#
# Contract under test:
#   1. SKILL.md's Scope & plan section tells a refactor-kind run to plan each step as one named
#      refactoring whose criterion is a shell predicate false before the step and true after it.
#   2. The develop-cover prompt and SKILL.md's Cover step — see case 2's comment.
#   3. SKILL.md's Cover step on `COVERED: no` — see case 3's comment.
#   4. SKILL.md's refactor-kind cycle, transform rejection and abandonment — see case 4's comment.
#   5. SKILL.md's Draft PR step titles a refactor-labelled run's PR refactor: — see case 5's comment.
#   6. A step no test can observe never bails `uncovered`: the cover prompt allows COVERED:
#      unreachable (only deletes code no caller reaches) and COVERED: type-only (changes only
#      types) with a PROOF: line, and never for a step that moves or reshapes runtime code;
#      SKILL.md reads it through cover-outcome.sh, goes on to Transform on exit 3 without a
#      bail or coverage-blocker.sh, and reruns a type-only step's type-check command after the
#      transform.
#
# Run: skills/tdd/scripts/tests/skill-refactor-kind.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"

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
  grep -E 'git diff[^.]{0,120}before[^.]{0,40}mutat|git status --porcelain' <<<"$cover" > /dev/null || problems+=("the cover prompt never tells the leaf to prove the tree unchanged")
  cover_tail="$(sed '/^[[:space:]]*$/d' <<<"$cover_raw" | tail -n 4)"
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

name="the develop-cover prompt allows COVERED: unreachable and type-only, each with a PROOF:, only for a step no test can observe; $skill_md's Cover step goes on to Transform on cover-outcome.sh exit 3 and reruns a type-only proof after the transform"
problems=()

if [[ -z "$cover_raw" ]]; then
  problems+=("build-develop-prompt.sh cover printed no prompt to read")
else
  near="$(window "$cover" 'covered: unreachable')"
  if [[ -z "$near" ]]; then
    problems+=("the cover prompt never offers COVERED: unreachable, so a step deleting dead code can only answer COVERED: no and bail")
  else
    grep -E 'only delet|deletes? only|deletion[- ]only' <<<"$near" > /dev/null ||
      problems+=("the cover prompt offers COVERED: unreachable without restricting it to a step that only deletes code")
    grep -E 'every caller|no caller' <<<"$near" > /dev/null ||
      problems+=("the cover prompt's COVERED: unreachable asks for no proof naming every caller")
  fi
  near="$(window "$cover" 'covered: type-only')"
  if [[ -z "$near" ]]; then
    problems+=("the cover prompt never offers COVERED: type-only, so a step changing only a type can only answer COVERED: no and bail")
  else
    grep -E 'only types' <<<"$near" > /dev/null ||
      problems+=("the cover prompt offers COVERED: type-only without restricting it to a step that changes only types")
    grep -E 'type checker|type-check' <<<"$near" > /dev/null ||
      problems+=("the cover prompt's COVERED: type-only never asks for the type-check command as its proof")
  fi
  grep -E '(mov|reshap)[^.]{0,160}never[^.]{0,40}unreachable[^.]{0,20}type-only' <<<"$cover" > /dev/null ||
    problems+=("the cover prompt never says a step that moves or reshapes runtime code is neither unreachable nor type-only, so the gate loosens for every step")
  cover_tail="$(sed '/^[[:space:]]*$/d' <<<"$cover_raw" | tail -n 4)"
  grep -E '^PROOF:' <<<"$cover_tail" > /dev/null ||
    problems+=("the cover prompt's closing lines carry no PROOF: line")
fi

near="$(window "$skill_text" 'covered: unreachable')"
if [[ -z "$near" ]]; then
  problems+=("$skill_md never says what a run does when Cover answers COVERED: unreachable or type-only")
else
  grep -F 'type-only' <<<"$near" > /dev/null ||
    problems+=("$skill_md's handling of a step no test can observe never names COVERED: type-only")
  grep -E 'exits? 3[^.]{0,200}transform|transform[^.]{0,200}exits? 3' <<<"$near" > /dev/null ||
    problems+=("$skill_md's COVERED: unreachable handling never goes on to Transform on exit 3")
  grep -E '(not|never|no)[^.]{0,80}(bail|coverage-blocker)' <<<"$near" > /dev/null ||
    problems+=("$skill_md's COVERED: unreachable handling never says it neither bails nor files a coverage blocker")
fi
near="$(window "$skill_text" 'for type-only')"
grep -E 'type-check command[^.]{0,120}(run|rerun)[^.]{0,80}transform[^.]{0,160}reject' <<<"$near" > /dev/null ||
  problems+=("$skill_md never reruns a type-only step's type-check command after the transform and rejects it on failure, so the proof is only ever checked before the change")
report "$name"

finish

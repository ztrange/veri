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
#   6. SKILL.md's Cover step reads the report through cover-outcome.sh — see case 6's name.
#   7. SKILL.md reruns a type-only step's proof command after its transform — see case 7's name.
#   8. SKILL.md keeps a type-only step's proof command in a run file the conductor reruns — see
#      case 8's name.
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

name="#679 $skill_md's Cover step reads the cover report through cover-outcome.sh: exit 3 goes on to Transform posting the proof in the Cover comment without bailing or running coverage-blocker.sh, exit 2 bails as no-verdict"
problems=()

outcome_near="$(window "$skill_text" 'cover-outcome\.sh')"
if [[ -z "$outcome_near" ]]; then
  problems+=("$skill_md never reads the cover leaf's report through cover-outcome.sh, so a COVERED: unreachable or type-only answer with its PROOF: is read as COVERED: no and bails uncovered")
else
  exit3_near="$(window "$outcome_near" 'exit 3')"
  if [[ -z "$exit3_near" ]]; then
    problems+=("$skill_md runs cover-outcome.sh without saying what its exit 3 does")
  else
    grep -E 'transform' <<<"$exit3_near" > /dev/null ||
      problems+=("$skill_md's cover-outcome.sh exit 3 never goes on to Transform")
    grep -E 'proof' <<<"$exit3_near" > /dev/null && grep -E 'cover comment|comment' <<<"$exit3_near" > /dev/null ||
      problems+=("$skill_md's cover-outcome.sh exit 3 never posts the proof in the step's Cover comment")
    grep -E '(without|not|never|no) [^.]{0,60}(bail|coverage-blocker\.sh)' <<<"$exit3_near" > /dev/null ||
      problems+=("$skill_md's cover-outcome.sh exit 3 never says it neither bails nor runs coverage-blocker.sh")
  fi
  grep -E 'exit 2[^.]{0,120}no-verdict' <<<"$outcome_near" > /dev/null ||
    problems+=("$skill_md's cover-outcome.sh exit 2 never bails as no-verdict")
fi
report "$name"

name="#679 $skill_md reruns a type-only step's proof command after its transform commits, a non-zero exit rejecting the transform as transform-touches-tests.sh exit 1 does"
problems=()

rerun_near="$(window "$skill_text" '(rerun|re-run|runs? again)[^.]{0,80}proof')"
if [[ -z "$rerun_near" ]]; then
  problems+=("$skill_md never reruns a type-only step's proof command after its transform, so a transform that breaks the type check is accepted as a refactoring")
else
  grep -F 'type-only' <<<"$rerun_near" > /dev/null ||
    problems+=("$skill_md reruns a proof command without tying it to a type-only step")
  grep -E 'after[^.]{0,60}transform[^.]{0,40}commit|transform[^.]{0,40}commit[^.]{0,60}(then|after)' <<<"$rerun_near" > /dev/null ||
    problems+=("$skill_md never says the proof command reruns after the transform commits")
  grep -E '(non-zero|nonzero)[^.]{0,80}reject' <<<"$rerun_near" > /dev/null ||
    problems+=("$skill_md never says a non-zero exit of the rerun proof command rejects the transform")
  grep -E 'transform-touches-tests\.sh[^.]{0,40}exit 1' <<<"$rerun_near" > /dev/null ||
    problems+=("$skill_md never says the rejection is the one transform-touches-tests.sh exit 1 makes")
fi
report "$name"

name="#679 $skill_md keeps a type-only step's proof command — the text cover-outcome.sh printed after 'type-only: ' — in a run file between Cover and Transform, and the conductor itself reruns that saved command"
problems=()

kept_near="$(window "$skill_text" 'type-only: ')"
if [[ -z "$kept_near" ]]; then
  problems+=("$skill_md never names the text cover-outcome.sh prints after 'type-only: ', so where the proof command comes from between Cover and Transform is unsaid")
else
  grep -F 'cover-outcome.sh' <<<"$kept_near" > /dev/null ||
    problems+=("$skill_md names 'type-only: ' without saying cover-outcome.sh printed it")
  grep -E '(save|write|keep|store)[^.]{0,80}\.tdd/[a-z0-9<>_.-]+' <<<"$kept_near" > /dev/null ||
    problems+=("$skill_md never says the proof command is saved to a run file under .tdd/")
fi
grep -E 'conductor[^.]{0,40}(rerun|re-run|runs? again)[^.]{0,80}(saved|\.tdd/)' <<<"$skill_text" > /dev/null ||
  problems+=("$skill_md never says the conductor itself reruns the saved proof command")
report "$name"

finish

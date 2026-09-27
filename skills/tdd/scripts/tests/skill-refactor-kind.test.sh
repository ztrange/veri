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
#
# Run: skills/tdd/scripts/tests/skill-refactor-kind.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice: the path as every failure message spells it, and the same path
# resolved for the probes to read, so a message can never name a file the probes did not
# open.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
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

# plain — stdin with emphasis marks and backticks dropped, the case folded and the lines
# joined onto one, so a sentence that wraps across two lines is still one sentence.
plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

# section <heading-prefix> — the lines after the first heading STARTING WITH that literal,
# up to the next heading of level two or three, normalised through `plain`. Not "any level":
# the Scope & plan section quotes a ledger in a code block whose first line is `# Plan for`,
# and a level-one match there would end the section inside its own example.
section() {
  awk -v h="$1" \
    'index($0, h) == 1 { inside = 1; next } inside && /^###? / { exit } inside' "$skill_path" |
    plain
}

plan_heading='### 2. Scope & plan'

# window <text> <extended-regex> — the text within 250 characters either side of the first
# match, or the empty string when there is none. 250 because BSD grep refuses an interval
# bound over 255.
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

# 2. Cover (criterion 4). Before a refactoring moves code, a cover leaf proves some test
#    catches that code breaking: it mutates the code by hand, runs the suite, expects red,
#    restores the edit and proves the tree is as it found it, then reports `COVERED:` and
#    `CAUGHT_BY:`. A leaf that forgets to restore leaves its mutation for the transform to
#    commit as a "refactoring", so SKILL.md does not take its word for it: a non-empty
#    `git status --porcelain` after Cover refuses the run rather than continuing.
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

skill_text="$(plain < "$skill_path")"
cover_near="$(window "$skill_text" '(develop-cover|cover (phase|step|leaf))')"
if ! grep -F 'git status --porcelain' <<<"$cover_near" | grep -E 'refus|stop|bail|(not|never) (go on|continue)' > /dev/null; then
  problems+=("$skill_md never refuses to continue past Cover when git status --porcelain is non-empty afterwards, so a mutation the cover leaf left behind reaches the transform")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

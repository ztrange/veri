#!/usr/bin/env bash
# Unit test for how skills/tdd/SKILL.md carries a step's structural leftovers out of its
# refactor loop, read as text.
#
# Contract under test — one criterion, one case:
#   SKILL.md's Refactor section runs `refactor-owed.sh append` on the refactor leaf's own
#   report, into the run's owed file and under the step, and the file rides the commit that
#   clears that step's refactor-pending mark.
#   Its `append` call passes the step's refactor bounds, a structural candidate of an
#   all-test-file step is recorded test-only, and the Draft PR's structural pass never lists
#   such a candidate, so it launches no predicate or transform leaf for it.
#
# Run: scripts/tests/skill-refactor-owed.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"
source "$HERE/lib/window.sh"


refactor_section() {
  awk -v h='#### Refactor' \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" |
    plain --join
}
section="$(refactor_section)"

name="$skill_md's Refactor section appends the step's structural leftovers to the run's owed file and commits that file with the step's refactor-pending clear"
problems=()

if [[ -z "${section// /}" ]]; then
  problems+=("$skill_md has no '#### Refactor' section to read — whether a step's structural leftovers are recorded anywhere could not be established")
else
  append="$(window "$section" 'refactor-owed\.sh append')"
  if [[ -z "$append" ]]; then
    problems+=("$skill_md's Refactor section never runs refactor-owed.sh append, so a step's structural leftovers live only in .tdd/develop-refactor.out and are gone as soon as the next step overwrites it")
  else
    grep -qE 'issue-[^ ]*refactor-owed\.md' <<<"$append" ||
      problems+=("$skill_md's Refactor section runs refactor-owed.sh append without naming the run's .tdd/issue-<n>-refactor-owed.md file, so where a resumed run should find the leftovers it already recorded is left to judgement")
    grep -qE 'develop-refactor\.out' <<<"$append" ||
      problems+=("$skill_md's Refactor section runs refactor-owed.sh append without feeding it the refactor leaf's report, so the candidates it is supposed to record have no source")
    grep -qE '<step>' <<<"$append" ||
      problems+=("$skill_md's Refactor section runs refactor-owed.sh append without the step, so a run's leftovers pile up with nothing saying which step owes which")
  fi

  cleared="$(window "$section" 'clear-refactor-pending\.sh')"
  if [[ -z "$cleared" ]]; then
    problems+=("$skill_md's Refactor section never clears the refactor-pending mark, so the commit the owed file is supposed to ride does not exist to be read for")
  else
    grep -qE 'refactor-owed' <<<"$cleared" ||
      problems+=("$skill_md's Refactor section commits the cleared ledger without saying the owed file goes with it, so what append wrote stays uncommitted and dies with the worktree")
    grep -qE 'commit' <<<"$cleared" ||
      problems+=("$skill_md's Refactor section clears the refactor-pending mark without committing anything there, so neither the clear nor the owed file survives a resume")
  fi
fi

report "$name"

draft_pr_pass() {
  awk -v h='### 4. Draft PR' \
    'index($0, h) == 1 { inside = 1; next } inside && /^### / { exit } inside' "$skill_path" |
    plain --join
}
draft_pr="$(draft_pr_pass)"
pass_text="${draft_pr#*one structural pass}"

name="#756: $skill_md's refactor loop passes the step's refactor bounds to refactor-owed.sh append and records an all-test-file step's structural candidate test-only, which the structural pass never lists and so launches no predicate or transform leaf for"
problems=()

append="$(window "$section" 'refactor-owed\.sh append')"
if [[ -z "$append" ]]; then
  problems+=("$skill_md's Refactor section never runs refactor-owed.sh append — whether it is handed the step's bounds could not be established")
else
  grep -E 'refactor-owed\.sh append .*<step>"? +"?(\$touched|<touched-files>)' > /dev/null <<<"$append" ||
    problems+=("$skill_md's Refactor section runs refactor-owed.sh append without the step's refactor bounds (\$touched) after the step, so append cannot tell an all-test-file step's structural candidate from any other")
  grep -F 'test-only' > /dev/null <<<"$append" ||
    problems+=("$skill_md's Refactor section never says append records a structural candidate of a step whose bounds are all test files as test-only")
fi
if [[ "$pass_text" == "$draft_pr" ]]; then
  problems+=("$skill_md's Draft PR step has no 'one structural pass' — whether a test-only candidate is listed could not be established")
else
  test_only="$(window "$pass_text" 'test-only')"
  if [[ -z "$test_only" ]]; then
    problems+=("$skill_md's structural pass never says a candidate recorded test-only is not listed, so nothing says it launches no predicate or transform leaf")
  else
    for word in 'never listed' 'predicate' 'transform leaf'; do
      grep -F "$word" > /dev/null <<<"$test_only" ||
        problems+=("$skill_md's structural pass mentions test-only without saying such a candidate is never listed and launches no predicate or transform leaf — '$word' is missing near it")
    done
  fi
fi

report "$name"

finish

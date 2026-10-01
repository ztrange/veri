#!/usr/bin/env bash
# Unit test for how skills/tdd/SKILL.md carries a step's structural leftovers out of its
# refactor loop, read as text.
#
# Contract under test — one criterion, one case:
#   SKILL.md's Refactor section runs `refactor-owed.sh append` on the refactor leaf's own
#   report, into the run's owed file and under the step, and the file rides the commit that
#   clears that step's refactor-pending mark.
#
# Run: scripts/tests/skill-refactor-owed.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"

plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

refactor_section() {
  awk -v h='#### Refactor' \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" |
    plain | tr '\n' ' '
}
section="$(refactor_section)"

# hazard: BSD grep refuses an interval bound over 255.
win() {
  head -1 < <(grep -oE ".{0,250}$1.{0,250}" <<<"$section")
}

name="$skill_md's Refactor section appends the step's structural leftovers to the run's owed file and commits that file with the step's refactor-pending clear"
problems=()

if [[ -z "${section// /}" ]]; then
  problems+=("$skill_md has no '#### Refactor' section to read — whether a step's structural leftovers are recorded anywhere could not be established")
else
  append="$(win 'refactor-owed\.sh append')"
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

  cleared="$(win 'clear-refactor-pending\.sh')"
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

finish

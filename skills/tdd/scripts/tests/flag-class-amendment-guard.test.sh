#!/usr/bin/env bash
# Unit test for the guard that keeps a plan amendment tied to the one flag class that earns
# one — case 7 of skills/tdd/scripts/tests/skill-refactor-leaf.test.sh, run against a planted
# copy of SKILL.md's Refactor section.
#
# Contract under test:
#   Over a copy of this tree whose Refactor section grants the plan amendment to a flag class
#   other than `uncovered-spec` — every mention of that class renamed to `off-spec` —
#   skill-refactor-leaf.test.sh fails, its own count line says so, and the case it names is the
#   one about which class grows the plan and no other case. Over the same tree with the document
#   unplanted it passes.
#
# Run: skills/tdd/scripts/tests/flag-class-amendment-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
source "$HERE/lib/guard-plant.sh"
ROOT="$(cd "$HERE/../../../.." && pwd)"

GUARD='skills/tdd/scripts/tests/skill-refactor-leaf.test.sh'
GUARD_PATH="$ROOT/$GUARD"

SKILL='skills/tdd/SKILL.md'
SKILL_PATH="$ROOT/$SKILL"

COMPANIONS=(CONTEXT.md CLAUDE.md)

CLASS='uncovered-spec'
OTHER_CLASS='off-spec'

scratch="$(scratch_dir)"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

plant() {
  planted_skill="$scratch/planted-SKILL.md"
  FROM="$CLASS" TO="$OTHER_CLASS" awk '
    {
      out = ""
      rest = $0
      while ((i = index(rest, ENVIRON["FROM"])) > 0) {
        out = out substr(rest, 1, i - 1) ENVIRON["TO"]
        rest = substr(rest, i + length(ENVIRON["FROM"]))
      }
      print out rest
    }
  ' "$SKILL_PATH" > "$planted_skill"
}

probe_skill_does_not_already_name_other_class() {
  grep -F "$OTHER_CLASS" "$SKILL_PATH" > /dev/null &&
    problems+=("$SKILL already names $OTHER_CLASS, so renaming $CLASS to it leaves the two classes indistinguishable and the guard is asked a different question")
  return 0
}

probe_guard_names_the_routing_case() {
  local failures failed_cases
  run_guard_over "$planted_skill"
  planted_out="$guard_out"
  failures="$(failures_in "$guard_out")"
  [[ "$guard_code" != 0 ]] ||
    problems+=("want ${GUARD##*/} to fail over a $SKILL whose Refactor section amends the plan from $OTHER_CLASS rather than $CLASS; it exited 0 and said: $(flat "$guard_out")")
  [[ "$failures" == 1 ]] ||
    problems+=("want ${GUARD##*/}'s own count line to state exactly 1 failed over that document — the other six criteria it reads out of that section are untouched by the plant; it stated '$failures': $(flat "$guard_out")")
  failed_cases="$(grep '^FAIL - ' <<< "$guard_out")"
  if [[ -z "$failed_cases" ]]; then
    problems+=("${GUARD##*/} named no failing case over that document, so nothing tells the next author which rule the section broke; it said: $(flat "$guard_out")")
  else
    grep -qF "$CLASS" <<< "$failed_cases" ||
      problems+=("${GUARD##*/} failed over that document without naming the $CLASS class in the case it failed, so its red is about something other than which flag class grows the plan; the cases it named were: $(flat "$failed_cases")")
  fi
}

name="${GUARD##*/} fails over a $SKILL whose Refactor section amends the plan from a flag class other than $CLASS, naming that case and no other, and passes over the document as committed"
problems=()
tree=""
guard_copy=""
planted_skill=""
guard_out=""
guard_code=0
planted_out=""

run_plant_sequence tree plant "$CLASS" "$OTHER_CLASS" probe_skill_does_not_already_name_other_class probe_guard_names_the_routing_case
report "$name"

name="${GUARD##*/}'s one-call-per-criterion case passes over a $SKILL whose plan-growing flag class is named $OTHER_CLASS rather than $CLASS, since that case asks how many add-ledger-step.sh calls sub-step 4 makes, not which class grows the plan (#1292)"
problems=()

if [[ -z "$planted_out" ]]; then
  problems+=("${GUARD##*/} was never run over the planted $SKILL, so whether its one-call-per-criterion case depends on the class name went unasked")
else
  per_criterion_failed="$(grep '^FAIL - .*one call per criterion' <<< "$planted_out")"
  [[ -z "$per_criterion_failed" ]] ||
    problems+=("${GUARD##*/} failed its one-call-per-criterion case over a $SKILL that only renamed $CLASS to $OTHER_CLASS, so that case reads the class name rather than the per-criterion calls: $(flat "$per_criterion_failed")")
fi

report "$name"

finish

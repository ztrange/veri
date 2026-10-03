#!/usr/bin/env bash
# Unit test for the guard that keeps a `beyond-spec` flag out of the plan — case 8 of
# skills/tdd/scripts/tests/skill-refactor-leaf.test.sh, run against a planted document.
#
# Contract under test:
#   Over a copy of this tree whose Refactor section plans and builds a `beyond-spec` flag
#   instead of only narrating it, skill-refactor-leaf.test.sh fails, its own count line says
#   so, and the case it names is the one about where a beyond-spec flag goes and no other
#   case. Over the same tree with the document unplanted it passes.
#
# Run: skills/tdd/scripts/tests/beyond-spec-narration-guard.test.sh
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

CLASS='beyond-spec'

DENIAL='is not planned and not built in this run'
GRANT='is planned and built in this run'

scratch="$(scratch_dir)"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

plant() {
  planted_skill="$scratch/planted-SKILL.md"
  FROM="$DENIAL" TO="$GRANT" awk '
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

probe_skill_does_not_already_grant() {
  grep -F "$GRANT" "$SKILL_PATH" > /dev/null &&
    problems+=("$SKILL already says a $CLASS flag $GRANT, so the planted document is the committed one on the clause this plant is about")
  return 0
}

probe_guard_names_the_narration_case() {
  local failures failed_cases
  run_guard_over "$planted_skill"
  failures="$(failures_in "$guard_out")"
  [[ "$guard_code" != 0 ]] ||
    problems+=("want ${GUARD##*/} to fail over a $SKILL whose Refactor section says a $CLASS flag $GRANT; it exited 0 and said: $(flat "$guard_out")")
  [[ "$failures" == 1 ]] ||
    problems+=("want ${GUARD##*/}'s own count line to state exactly 1 failed over that document — the other seven criteria it reads out of that section are untouched by the plant; it stated '$failures': $(flat "$guard_out")")
  failed_cases="$(grep '^FAIL - ' <<< "$guard_out")"
  if [[ -z "$failed_cases" ]]; then
    problems+=("${GUARD##*/} named no failing case over that document, so nothing tells the next author which rule the section broke; it said: $(flat "$guard_out")")
  else
    grep -qF "$CLASS" <<< "$failed_cases" ||
      problems+=("${GUARD##*/} failed over that document without naming the $CLASS class in the case it failed, so its red is about something other than where a $CLASS flag goes; the cases it named were: $(flat "$failed_cases")")
  fi
}

name="${GUARD##*/} fails over a $SKILL whose Refactor section plans and builds a $CLASS flag instead of only narrating it, naming that case and no other, and passes over the document as committed"
problems=()
tree=""
guard_copy=""
planted_skill=""
guard_out=""
guard_code=0

run_plant_sequence tree plant "$DENIAL" "$GRANT" probe_skill_does_not_already_grant probe_guard_names_the_narration_case
report "$name"

finish

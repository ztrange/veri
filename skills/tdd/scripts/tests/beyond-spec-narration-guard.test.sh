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

failures_in() {
  local line
  line="$(grep -E '^[0-9]+ passed, [0-9]+ failed$' <<< "$1" | tail -1)"
  [[ -n "$line" ]] || { printf '%s' '<none>'; return; }
  line="${line#*, }"
  printf '%s' "${line% failed}"
}

plant() {
  local companion
  tree="$scratch/tree"
  mkdir -p "$tree/${SKILL%/*}" "$tree/${GUARD%/*}" || {
    problems+=("could not make a scratch tree to plant the document in, so the criterion went unasked")
    return 1
  }
  guard_copy="$tree/$GUARD"
  cp "$GUARD_PATH" "$guard_copy" || return 1
  mkdir -p "${guard_copy%/*}/lib" && cp "$HERE/lib/harness.sh" "${guard_copy%/*}/lib/" || return 1
  for companion in "${COMPANIONS[@]}"; do
    cp "$ROOT/$companion" "$tree/$companion" || {
      problems+=("$companion could not be copied into the scratch tree, so the guard would be red for a reason that is not the plant")
      return 1
    }
  done

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
  return 0
}

probe_guard_is_there() {
  [[ -f "$GUARD_PATH" ]] || {
    problems+=("there is no guard suite at $GUARD, so nothing checks that $SKILL's Refactor section keeps a $CLASS flag out of the plan")
    return 1
  }
  [[ -x "$GUARD_PATH" ]] || {
    problems+=("$GUARD is not executable, so \`make test\`'s runner cannot run it")
    return 1
  }
}

probe_plant_is_what_it_claims() {
  local carriers changed
  carriers="$(grep -cF "$DENIAL" "$SKILL_PATH")"
  [[ "$carriers" -gt 0 ]] || {
    problems+=("no line of $SKILL says a $CLASS flag $DENIAL, so there is no denial to turn into a grant and the criterion cannot be asked")
    return 1
  }
  grep -F "$GRANT" "$SKILL_PATH" > /dev/null &&
    problems+=("$SKILL already says a $CLASS flag $GRANT, so the planted document is the committed one on the clause this plant is about")
  grep -F "$DENIAL" "$planted_skill" > /dev/null &&
    problems+=("the planted $SKILL still says a $CLASS flag $DENIAL, so nothing was planted")
  grep -F "$GRANT" "$planted_skill" > /dev/null ||
    problems+=("the planted $SKILL nowhere says a $CLASS flag $GRANT, so its Refactor section denies the planning in some other words rather than granting it")
  changed="$(diff "$SKILL_PATH" "$planted_skill" | grep -c '^[<>]')"
  [[ "$changed" == "$((carriers * 2))" ]] ||
    problems+=("the plant rewrote lines adding up to $changed diff lines of $SKILL, want $((carriers * 2)) — the $carriers lines that carried the denial and no other; a red over a document changed elsewhere is not about where a $CLASS flag goes")
  return 0
}

run_guard_over() {
  cp "$1" "$tree/$SKILL"
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
}

probe_guard_is_green_unplanted() {
  local failures
  run_guard_over "$SKILL_PATH"
  failures="$(failures_in "$guard_out")"
  [[ "$guard_code" == 0 ]] ||
    problems+=("want ${GUARD##*/} to pass over $SKILL as committed — red there says nothing about the plant; it exited $guard_code and said: $(flat "$guard_out")")
  [[ "$failures" == 0 ]] ||
    problems+=("want ${GUARD##*/}'s own count line to state 0 failed over $SKILL as committed; it stated '$failures': $(flat "$guard_out")")
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

if probe_guard_is_there && plant; then
  if probe_plant_is_what_it_claims; then
    probe_guard_is_green_unplanted
    probe_guard_names_the_narration_case
  fi
fi
report "$name"

finish

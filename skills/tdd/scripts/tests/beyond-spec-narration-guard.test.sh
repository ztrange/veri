#!/usr/bin/env bash
# Unit test for the guard that keeps a `beyond-spec` flag out of the plan — case 8 of
# skills/tdd/scripts/tests/skill-refactor-leaf.test.sh, which reads SKILL.md's Refactor section
# and refuses a document that narrates that class without also saying it is neither planned nor
# built in this run. Like flag-class-amendment-guard.test.sh, verifier-launch-guard.test.sh and
# docs-read-guard.test.sh this suite has no script as its subject: its subject is what another
# suite reports about the document it is run against. Zero-dependency plain-shell asserts, same
# idiom as flag-class-amendment-guard.test.sh.
#
# Why this exists (issue #175): `beyond-spec` is the one flag class that is not this run's work
# at all — it names an input class or an edge the issue's spec never asked for, so a step made
# from it would build behaviour no criterion states and the blind verifier, which is given the
# spec, could not judge it. Narration is the whole of what it earns. The document says so today
# in one clause, and a clause is exactly what the next author rewrites: "and is not planned and
# not built in this run" reads like emphasis rather than the rule, and dropping it puts back the
# six `plan: amend` commits #175 counted.
#
# The guard is what is supposed to stop that, and a guard that has never been watched to fail is
# not tested. Asking case 8 about a planted document is the only thing that answers whether it
# guards the clause at all, and over this tree the answer is that it does not: probe c reads
# `denial(plan|built|build)` within one clause of a `beyond-spec` window, and the bullet's own
# rationale — "without costing it a step: one made from a `beyond-spec` flag would build
# behaviour no criterion of the issue states" — matches that with no sentence boundary in
# between. So the probe is answered by the sentence explaining WHY the class is not planned,
# never by the clause saying that it is not, and a document that turns the denial into a grant
# still passes case 8. This suite is therefore red until probe c is narrowed to the denial
# itself, which is the behaviour the step that follows builds.
#
# Contract under test:
#   Over a copy of this tree whose Refactor section plans and builds a `beyond-spec` flag
#   instead of only narrating it — the clause denying both turned into the grant it denies, so
#   the section still names the class and still narrates it in both places, and only what the
#   narration costs the run has changed — skill-refactor-leaf.test.sh fails, its own count line
#   says so, and the case it names is the one about where a beyond-spec flag goes and no other
#   case. Over the same tree with the document unplanted it passes.
#
# Both halves are the case, and the green half is not decoration: red over a tree is worth
# nothing unless the same guard is green over the same tree before the plant. A guard broken so
# that it fails on everything would satisfy the red half alone.
#
# Naming the case, rather than merely failing, is the criterion too — and naming ONLY that case.
# The guard reads eight criteria out of that one section, and the other seven are still correct
# over the plant; a red that listed them too would send the next author to eight places, seven of
# which are right.
#
# The plant carries the three documents the guard resolves against its own repo root — SKILL.md,
# CONTEXT.md and CLAUDE.md — and the guard itself, and nothing else. In particular the generated
# tree is not copied, and no line below names a path in it, which is what no-docs-reads.test.sh
# asks of every suite in this directory.
#
# Run: skills/tdd/scripts/tests/beyond-spec-narration-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

GUARD='skills/tdd/scripts/tests/skill-refactor-leaf.test.sh'
GUARD_PATH="$ROOT/$GUARD"

SKILL='skills/tdd/SKILL.md'
SKILL_PATH="$ROOT/$SKILL"

COMPANIONS=(CONTEXT.md CLAUDE.md)

CLASS='beyond-spec'

DENIAL='is not planned and not built in this run'
GRANT='is planned and built in this run'

pass=0 fail=0
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

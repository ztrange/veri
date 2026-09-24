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
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The guard, twice, and neither name substitutes for the other: repo-relative is what a failure
# message quotes and what the plant rebuilds the path from, absolute is what copying it into the
# plant needs. Same pairing flag-class-amendment-guard.test.sh uses on its own guard.
GUARD='skills/tdd/scripts/tests/skill-refactor-leaf.test.sh'
GUARD_PATH="$ROOT/$GUARD"

# The document the plant rewrites, the same way twice and for the same reason.
SKILL='skills/tdd/SKILL.md'
SKILL_PATH="$ROOT/$SKILL"

# The other two documents the guard opens — its case 2 reads CONTEXT.md's Cycle entry and
# CLAUDE.md's budget invariant — copied into the tree untouched. They are not what this plant is
# about, but a tree missing them would make the guard red for a reason that is not the plant, and
# the red half below would then say nothing.
COMPANIONS=(CONTEXT.md CLAUDE.md)

# The class this plant is about, named once so a message can never be about another one.
CLASS='beyond-spec'

# The clause the document denies the planning with, and what the plant turns it into: the same
# sentence granting what it used to refuse. A grant rather than a deletion because the criterion
# is a section that PLANS and BUILDS the class, and a section with the clause merely cut would be
# a section that says nothing either way — a weaker document than the one the rule is against.
DENIAL='is not planned and not built in this run'
GRANT='is planned and built in this run'

pass=0 fail=0
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

# report <name> — close a case whose probes collected into the `problems` array: an empty array
# is a pass, otherwise one FAIL line for the case and one indented line per problem, so the
# output says which half of the contract broke rather than just that the case did.
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

# flat <text> — one line of it, for a failure message: newlines become slashes so a guard's whole
# output quoted inside an indented problem line stays one line.
flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

# failures_in <output> — the number a suite's own count line states it failed, or '<none>' when
# it printed no count line at all. A suite's exit code alone is not trusted (#157: a suite that
# dies partway routinely comes back 0), so both probes below read the verdict the guard printed
# as well as the status it exited with — the same pair the `test` recipe reads.
failures_in() {
  local line
  line="$(grep -E '^[0-9]+ passed, [0-9]+ failed$' <<< "$1" | tail -1)"
  [[ -n "$line" ]] || { printf '%s' '<none>'; return; }
  line="${line#*, }"
  printf '%s' "${line% failed}"
}

# plant — the scratch tree the guard runs inside, and the rewritten document it is asked about.
# Leaves the tree in `tree`, the guard's copy in `guard_copy` and the planted document in
# `planted_skill`. Non-zero when the tree cannot be made, so the caller stops rather than
# reporting on a tree it never built.
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
  # One literal substitution per occurrence, done with awk's `index`/`substr` rather than sed so
  # that nothing in either clause has to be escaped into a pattern.
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

# probe_guard_is_there — the premise every probe below rests on, and the one that answers while
# the guard does not exist yet: there is a suite at that path and it can be run.
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

# probe_plant_is_what_it_claims — the plant's premises, asserted rather than assumed. The
# committed document has to deny the planning at all, or there is nothing to turn into a grant
# and the red below would be about a document that never routed the class; it must not already
# carry the grant, or the planted document is indistinguishable from the committed one on the
# very clause the plant is about; and the planted document has to differ from the committed one
# on exactly the lines that carried the denial and no other, since a red over a document changed
# twice is not about where a beyond-spec flag goes.
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

# run_guard_over <document> — put <document> in the tree as the document the guard reads, run the
# guard there once, and leave what it said in `guard_out` and how it exited in `guard_code`. A
# step of its own because both halves below ask about one such run over the same tree.
run_guard_over() {
  cp "$1" "$tree/$SKILL"
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
}

# probe_guard_is_green_unplanted — the half that makes the other half mean something. The guard is
# run over the tree with the document exactly as committed: it has to pass, and its own count
# line has to say nothing failed. A guard red over this tree is red over every tree, and the
# plant below would prove nothing about it.
probe_guard_is_green_unplanted() {
  local failures
  run_guard_over "$SKILL_PATH"
  failures="$(failures_in "$guard_out")"
  [[ "$guard_code" == 0 ]] ||
    problems+=("want ${GUARD##*/} to pass over $SKILL as committed — red there says nothing about the plant; it exited $guard_code and said: $(flat "$guard_out")")
  [[ "$failures" == 0 ]] ||
    problems+=("want ${GUARD##*/}'s own count line to state 0 failed over $SKILL as committed; it stated '$failures': $(flat "$guard_out")")
}

# probe_guard_names_the_narration_case — the criterion. Not "the guard fails" — a guard deleted
# down to `exit 1` would satisfy that, and so would one whose other seven cases broke on the copy
# — but a failure whose count line says one case failed, and whose `FAIL -` line is the one about
# where a beyond-spec flag goes, naming that class.
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

# 1. One criterion — the narration guard is known to go red over a section that plans and builds
#    a $CLASS flag, and green without it — and so one case: both runs are of the same guard over
#    the same tree, and a case that asked only about the planted one would pass over a guard that
#    refuses everything.
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

#!/usr/bin/env bash
# Unit test for the guard that keeps a plan amendment tied to the one flag class that earns
# one — case 7 of skills/tdd/scripts/tests/skill-refactor-leaf.test.sh, which reads SKILL.md's
# Refactor section and refuses a document that grows the plan from a flag without saying it is
# the `uncovered-spec` class doing it. Like verifier-launch-guard.test.sh, docs-read-guard.test.sh
# and hermetic-suites.test.sh this suite has no script as its subject: its subject is what
# another suite reports about the document it is run against. Zero-dependency plain-shell
# asserts, same idiom as verifier-launch-guard.test.sh.
#
# Why this exists (issue #175): a refactor leaf's `FLAGS:` line used to carry no class, and the
# conductors that read it turned flags into ledger steps — six `plan: amend` commits on
# `origin/main`, #107's three of them running from 01:31 to past 03:06 for three one-line `fix:`
# commits and seventeen `refactor:` ones, because a step made from a flag has a refactor loop of
# its own and that loop flagged the next sibling. The routing rule now says which class buys an
# amendment and that no other does, and a rule written into prose is exactly the kind that comes
# back: the next author spelling the classes out from the shape above them, or reaching for the
# nearest name when a new class arrives, puts the six commits back as one plausible sentence.
#
# The guard is what stops that, and a guard that has never been watched to fail is not tested:
# the document routes the amendment correctly today, so case 7 passes over this tree whether it
# still checks anything or not. Deleting its `problems+=` lines, or widening the text it reads,
# would leave `make test` green and the routing unguarded. So the contradiction is planted
# instead, and the guard is asked about the planted document.
#
# Contract under test:
#   Over a copy of this tree whose Refactor section grants the plan amendment to a flag class
#   other than `uncovered-spec` — every mention of that class renamed to `off-spec`, so the
#   section still amends the plan and still names a class, just the wrong one —
#   skill-refactor-leaf.test.sh fails, its own count line says so, and the case it names is the
#   one about which class grows the plan and no other case. Over the same tree with the document
#   unplanted it passes.
#
# Both halves are the case, and the green half is not decoration: red over a tree is worth
# nothing unless the same guard is green over the same tree before the plant. A guard broken so
# that it fails on everything would satisfy the red half alone.
#
# Naming the case, rather than merely failing, is the criterion too — and naming ONLY that case.
# The guard reads seven criteria out of that one section, and the other six are still correct
# over the plant; a red that listed them too would send the next author to seven places, six of
# which are right.
#
# The plant carries the three documents the guard resolves against its own repo root — SKILL.md,
# CONTEXT.md and CLAUDE.md — and the guard itself, and nothing else. In particular the generated
# tree is not copied, and no line below names a path in it, which is what no-docs-reads.test.sh
# asks of every suite in this directory.
#
# Run: skills/tdd/scripts/tests/flag-class-amendment-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The guard, twice, and neither name substitutes for the other: repo-relative is what a failure
# message quotes and what the plant rebuilds the path from, absolute is what copying it into the
# plant needs. Same pairing verifier-launch-guard.test.sh uses on its own guard.
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

# The class the routing rule grants the amendment to, and the class the plant hands it to
# instead. The plant renames every mention of the granted class, so the class it renames to has
# to be one the document does not already name — otherwise the planted document names the wrong
# class in the routing rule and the right one everywhere else, the two are indistinguishable, and
# the guard would be answering a different question. None of the other two classes the leaf
# reports can serve: the document names `overfit` at the bullet that answers one inside the step
# and `beyond-spec` at the bullet that narrates one as a follow-up, both of them rules this same
# section owes. So the plant hands the amendment to a fourth name — a document naming a class the
# protocol never defined is a document somebody could write, and a routing rule granted to it is
# as wrong as one granted to a real class that has not earned it.
CLASS='uncovered-spec'
OTHER_CLASS='off-spec'

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
# `planted_skill`. The rewrite renames every mention of the class rather than one of them: the
# criterion is a section that routes the amendment to another class, and a section naming both
# would be a section that still names the right one. Non-zero when the tree cannot be made, so
# the caller stops rather than reporting on a tree it never built.
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
  # that nothing in either class name has to be escaped into a pattern.
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
  return 0
}

# probe_guard_is_there — the premise every probe below rests on, and the one that answers while
# the guard does not exist yet: there is a suite at that path and it can be run.
probe_guard_is_there() {
  [[ -f "$GUARD_PATH" ]] || {
    problems+=("there is no guard suite at $GUARD, so nothing checks which flag class $SKILL's Refactor section grows the plan from")
    return 1
  }
  [[ -x "$GUARD_PATH" ]] || {
    problems+=("$GUARD is not executable, so \`make test\`'s runner cannot run it")
    return 1
  }
}

# probe_plant_is_what_it_claims — the plant's premises, asserted rather than assumed. The
# committed document has to name the class at all, or there is nothing to rename and the red
# below would be about a document that never routed anything; it must not already name the class
# the plant hands the amendment to, or the planted document still names the right one somewhere
# and the guard would be answering a different question; and the planted document has to differ
# from the committed one on exactly the lines that carried the class and no other, since a red
# over a document changed twice is not about the routing.
probe_plant_is_what_it_claims() {
  local carriers changed
  carriers="$(grep -cF "$CLASS" "$SKILL_PATH")"
  [[ "$carriers" -gt 0 ]] || {
    problems+=("no line of $SKILL names the $CLASS class, so there is no routing rule to hand to $OTHER_CLASS and the criterion cannot be asked")
    return 1
  }
  grep -F "$OTHER_CLASS" "$SKILL_PATH" > /dev/null &&
    problems+=("$SKILL already names $OTHER_CLASS, so renaming $CLASS to it leaves the two classes indistinguishable and the guard is asked a different question")
  grep -F "$CLASS" "$planted_skill" > /dev/null &&
    problems+=("the planted $SKILL still names the $CLASS class, so nothing was planted")
  grep -F "$OTHER_CLASS" "$planted_skill" > /dev/null ||
    problems+=("the planted $SKILL names no $OTHER_CLASS class, so its Refactor section routes the amendment to nothing rather than to the wrong class")
  changed="$(diff "$SKILL_PATH" "$planted_skill" | grep -c '^[<>]')"
  [[ "$changed" == "$((carriers * 2))" ]] ||
    problems+=("the plant rewrote lines adding up to $changed diff lines of $SKILL, want $((carriers * 2)) — the $carriers lines that named $CLASS and no other; a red over a document changed elsewhere is not about the routing")
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

# probe_guard_names_the_routing_case — the criterion. Not "the guard fails" — a guard deleted down
# to `exit 1` would satisfy that, and so would one whose other six cases broke on the copy — but
# a failure whose count line says one case failed, and whose `FAIL -` line is the one about which
# flag class grows the plan, quoting the class the section stopped naming.
probe_guard_names_the_routing_case() {
  local failures failed_cases
  run_guard_over "$planted_skill"
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

# 1. One criterion — the routing guard is known to go red over a section that amends the plan from
#    a flag class other than $CLASS, and green without it — and so one case: both runs are of the
#    same guard over the same tree, and a case that asked only about the planted one would pass
#    over a guard that refuses everything.
name="${GUARD##*/} fails over a $SKILL whose Refactor section amends the plan from a flag class other than $CLASS, naming that case and no other, and passes over the document as committed"
problems=()
tree=""
guard_copy=""
planted_skill=""
guard_out=""
guard_code=0

if probe_guard_is_there && plant; then
  if probe_plant_is_what_it_claims; then
    probe_guard_is_green_unplanted
    probe_guard_names_the_routing_case
  fi
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

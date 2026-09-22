#!/usr/bin/env bash
# Unit tests for what the conductor's Green section does with a developer leaf that answered
# `SPLIT:` instead of an implementation — like skill-red-untestable.test.sh and
# skill-refactor-leaf.test.sh this suite belongs to no single script: its subject is
# skills/tdd/SKILL.md, read as text, the way the session that follows it reads it.
# Zero-dependency plain-shell asserts, same idiom as skill-red-untestable.test.sh, picked up
# by `make test`'s glob by existing.
#
# Why this exists (issue #363, part of #354): a step too big for one green had no way out but
# a bail — SKILL.md notes sizing when the plan is scoped and never gates on it again, and a
# revise leaf may only answer the verifier's objection. develop-green.md and develop-revise.md
# now offer Beck's Child Test as a third answer: one to three `SPLIT: <behaviour-level
# criterion>` lines instead of an implementation, with no production code changed. That report
# reaches a conductor that has not been told what to do with it, and this suite pins what it
# now does.
#
# Contract under test:
#   1. SKILL.md's Green section, on `SPLIT:`, restores the tree to `HEAD` — the red test is
#      uncommitted, so leaving it on disk would poison the first split step — passes the
#      split criteria to ONE `add-ledger-step.sh … before '<STEP>'` call, commits the grown
#      ledger, emits `step-split`, and loops back to `next-unchecked.sh`, which hands over
#      the first split step.
#   2. On the over-budget end of that branch — `add-ledger-step.sh` exits 1, so the criteria
#      are already filed under `## Owed steps` and the step has no plan to go on with — the
#      run bails with cause `step-too-big`, which SKILL.md's Bailing causes list classifies
#      as a **process** failure, the way skill-red-untestable.test.sh pins the same thing for
#      `untestable-criterion`.
#
# Run: scripts/tests/skill-green-split.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice: the path as every failure message spells it, and the same path resolved
# for the probes to read, so a message can never name a file the probes did not open. Same
# pairing skill-red-untestable.test.sh uses.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem, so
# the output says which part of the branch is missing rather than just that it is.
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
# joined onto one, because `SPLIT:` and **split** are the same word and a claim that wraps
# across two lines is still one claim. The probes' regexes are then written one way, match
# however the author chose to mark the words up, and none of them is about order.
plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

# The heading the section is found by, spelled once: the probes look for it and the
# fail-closed message names it, so a suite re-pointed at a renamed heading cannot go on
# telling a reader it searched for the old one.
green_heading='#### Green'

# green_section — the lines after the first heading starting `$green_heading`, up to the next
# heading of any level, normalised through `plain`.
green_section() {
  awk -v h="$green_heading" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" |
    plain
}
section="$(green_section)"

# unreadable — empty unless the Green section could not be read at all, in which case it is
# the half of the failure message both cases share: what was searched for and not found. Fail
# closed on it rather than probing an empty string, which would let "the phase is gone" read
# as "the phase is right"; each case appends what it could not establish.
unreadable=""
[[ -n "${section// /}" ]] ||
  unreadable="$skill_md has no '$green_heading' section to read —"

# win <extended-regex> — the section text within 250 characters either side of the first
# match, or the empty string when there is none: the text a reader meets while working out
# what to do about that answer. 250 rather than a rounder, larger number because BSD grep —
# the one on the development machine this repository holds itself portable to — refuses an
# interval whose bound is over 255.
win() {
  head -1 < <(grep -oE ".{0,250}$1.{0,250}" <<<"$section")
}

# The invocation the plan's growth is found by, spelled once for the probes that count it and
# read the window around it. `$s` and not `$S` because `plain` folds the section's case; the
# `$` and the `.` are escaped because this is an extended regex and not a path.
add_ledger_step='\$s/add-ledger-step\.sh'

# bailing_causes — the Bailing section's causes list, from the `killed-stuck` bullet to the
# end of the section, normalised the same way `green_section` is. The list and not
# the whole section, for the reason skill-red-untestable.test.sh gives about the same text: a
# "process failure" written anywhere else in the procedure must not stand in for the list
# actually carrying the token.
bailing_causes() {
  awk '
    !in_s && index($0, "## Bailing") == 1 { in_s = 1; next }
    in_s && /^#/ { exit }
    in_s {
      if (!want && $0 ~ /killed-stuck/) want = 1
      if (want) print
    }' "$skill_path" | plain
}

name="$skill_md's Green section, on SPLIT:, restores the tree to HEAD, adds the split steps before STEP in one add-ledger-step.sh call, commits the ledger, emits step-split and returns to next-unchecked.sh"
problems=()

if [[ -n "$unreadable" ]]; then
  problems+=("$unreadable what the conductor does with a SPLIT: report could not be established")
else
  # 1. The branch itself. A leaf that reports SPLIT: has written no implementation and no
  #    `SUITE:` line, so a conductor with no branch for it reads the report as a malformed
  #    one and bails on a step the methodology just handled.
  grep -qE 'split' <<<"$section" ||
    problems+=("$skill_md's Green section never branches on the leaf's SPLIT: report, so the answer develop-green.md now offers reaches a conductor with nothing to do with it")

  # 2. The tree. Red's test is uncommitted at this point and the leaf changed no production
  #    code, so what is on disk is a failing test for a step about to be put back in the
  #    plan — it would be the first split step's inherited red.
  grep -qE 'git (restore|checkout|reset)[^.]{0,60}head|restore[^.]{0,60}(the tree|to) head' <<<"$section" ||
    problems+=("$skill_md's Green section never restores the tree to HEAD on a SPLIT:, so the uncommitted red test stays on disk and the first split step starts against a failing case nobody wrote for it")

  # 3. The insertion, and that there is exactly one of it, for the reason
  #    skill-refactor-leaf.test.sh gives about the same script: it takes every text at once
  #    and reads the growth budget per call, so a call per criterion refuses the third SPLIT:
  #    line of a step under the default VERI_STEP_GROWTH while one call either fits them all
  #    or files them all as owed. A mention that is not an invocation carries no `$S/` and is
  #    not counted.
  calls="$(grep -oE "$add_ledger_step" <<<"$section" | grep -c '')"
  if [[ "$calls" -eq 0 ]]; then
    problems+=("$skill_md's Green section never runs add-ledger-step.sh on a SPLIT:, so the criteria the leaf named are narrated and the plan the run reads is unchanged")
  elif [[ "$calls" -gt 1 ]]; then
    problems+=("$skill_md's Green section runs add-ledger-step.sh $calls times, so a step's SPLIT: criteria are inserted a call at a time and the growth budget is read once per criterion rather than once for the split")
  else
    added="$(win "$add_ledger_step")"
    grep -qE "before '?<step>" <<<"$added" ||
      problems+=("$skill_md's Green section runs add-ledger-step.sh without anchoring the insertion before the step being split, so the smaller steps land after the step they were supposed to come first")
    grep -qE 'commit' <<<"$added" ||
      problems+=("$skill_md's Green section grows the ledger on a SPLIT: without committing it, so the split steps are lost the moment the run is resumed from the committed ledger")
  fi

  # 4. The mark. A split is the one thing that changes a step's plan without a green commit
  #    of its own, so a run log with no `step-split` shows a step that simply started again.
  grep -qE 'step-split' <<<"$section" ||
    problems+=("$skill_md's Green section never emits step-split, so nothing in the run log says the step was split rather than silently restarted")

  # 5. And where it goes next: the first split step is now the first unchecked one, so the
  #    loop is re-entered at its head rather than carried on into verify-green.
  grep -qE 'next-unchecked' <<<"$section" ||
    problems+=("$skill_md's Green section never loops back to next-unchecked.sh after a split, so the conductor goes on into verify-green with no implementation for it to judge")
fi

report "$name"

# The over-budget end of the same branch: `add-ledger-step.sh` exits 1 when the insertion
# would take the ledger past `VERI_STEP_GROWTH`, and it has already filed the criteria under
# `## Owed steps` by then. The step cannot go on without them — its own red is discarded and
# the smaller steps it needs are not in the plan — so the run stops, and it stops as a
# process failure: the methodology said this step is too big, nothing in the plumbing broke.
name="$skill_md's Green section bails with cause step-too-big when add-ledger-step.sh exits 1 on a split, and its Bailing section lists that cause as a process failure"
problems=()

if [[ -n "$unreadable" ]]; then
  problems+=("$unreadable what the conductor does when a split is over budget could not be established")
elif ! grep -qE 'step-too-big' <<<"$section"; then
  problems+=("$skill_md's Green section never names the step-too-big cause, so a split refused for growth budget leaves the conductor to invent a stop for a step whose criteria are already filed as owed")
else
  over="$(win 'step-too-big')"
  grep -qE 'exits? 1' <<<"$over" ||
    problems+=("$skill_md's Green section names step-too-big without saying it is add-ledger-step.sh's exit 1 that causes it, so the conductor cannot tell the over-budget refusal from a call that worked")
  grep -qE 'bail' <<<"$over" ||
    problems+=("$skill_md's Green section names step-too-big without bailing on it, so a run whose split was refused carries on into a step it has no plan for")
fi

causes="$(bailing_causes)"
if [[ -z "${causes// /}" ]]; then
  problems+=("$skill_md's Bailing section has no causes list starting at killed-stuck — the classification of step-too-big could not be read")
else
  grep -qE 'step-too-big[^.]{0,220}process' <<<"$causes" ||
    problems+=("$skill_md's Bailing causes list never classifies step-too-big as a process failure, so the label a human reads calls a methodology verdict a broken pipe")
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

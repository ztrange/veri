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
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

source "$HERE/lib/harness.sh"

plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

green_heading='#### Green'

green_section() {
  awk -v h="$green_heading" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" |
    plain
}
section="$(green_section)"

unreadable=""
[[ -n "${section// /}" ]] ||
  unreadable="$skill_md has no '$green_heading' section to read —"

# hazard: BSD grep refuses an interval bound over 255.
win() {
  head -1 < <(grep -oE ".{0,250}$1.{0,250}" <<<"$section")
}

add_ledger_step='\$s/add-ledger-step\.sh'

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
  grep -qE 'split' <<<"$section" ||
    problems+=("$skill_md's Green section never branches on the leaf's SPLIT: report, so the answer develop-green.md now offers reaches a conductor with nothing to do with it")

  grep -qE 'git (restore|checkout|reset)[^.]{0,60}head|restore[^.]{0,60}(the tree|to) head' <<<"$section" ||
    problems+=("$skill_md's Green section never restores the tree to HEAD on a SPLIT:, so the uncommitted red test stays on disk and the first split step starts against a failing case nobody wrote for it")

  calls="$(grep -oE "$add_ledger_step" <<<"$section" | grep -c '')"
  if [[ "$calls" -eq 0 ]]; then
    problems+=("$skill_md's Green section never runs add-ledger-step.sh on a SPLIT:, so the criteria the leaf named are narrated and the plan the run reads is unchanged")
  elif [[ "$calls" -gt 1 ]]; then
    problems+=("$skill_md's Green section runs add-ledger-step.sh $calls times, so a step's SPLIT: criteria are inserted a call at a time and the growth budget is read once per criterion rather than once for the split")
  else
    added="$(win "$add_ledger_step")"
    grep -qE "before ['\"]?(<step>|\\$\\(\\\$s/next-unchecked\\.sh)" <<<"$added" ||
      problems+=("$skill_md's Green section runs add-ledger-step.sh without anchoring the insertion before the step being split, so the smaller steps land after the step they were supposed to come first")
    grep -qE 'commit' <<<"$added" ||
      problems+=("$skill_md's Green section grows the ledger on a SPLIT: without committing it, so the split steps are lost the moment the run is resumed from the committed ledger")
  fi

  grep -qE 'step-split' <<<"$section" ||
    problems+=("$skill_md's Green section never emits step-split, so nothing in the run log says the step was split rather than silently restarted")

  grep -qE 'next-unchecked' <<<"$section" ||
    problems+=("$skill_md's Green section never loops back to next-unchecked.sh after a split, so the conductor goes on into verify-green with no implementation for it to judge")
fi

report "$name"

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


step_too_big_cause() {
  awk '
    !in_s && index($0, "## Bailing") == 1 { in_s = 1; next }
    in_s && /^#/ { exit }
    in_s && inside && (/^- / || /^$/) { exit }
    in_s && /^- `step-too-big`/ { inside = 1 }
    inside' "$skill_path" | plain
}

name="$skill_md's Bailing entry for step-too-big names all three splits that lead to it: a Green leaf's SPLIT:, the revise-exhausted split and the over-budget split"
problems=()

bullet="$(step_too_big_cause)"
if [[ -z "${bullet// /}" ]]; then
  problems+=("$skill_md's Bailing causes list has no step-too-big bullet — which splits lead to it could not be read")
else
  grep -E 'green[^.]*split:|split:[^.]*green' <<<"$bullet" > /dev/null ||
    problems+=("$skill_md's step-too-big entry does not name a Green leaf's SPLIT:")
  grep -E 'exhausted' <<<"$bullet" > /dev/null ||
    problems+=("$skill_md's step-too-big entry does not name the revise-exhausted split")
  grep -E 'over-budget' <<<"$bullet" > /dev/null ||
    problems+=("$skill_md's step-too-big entry does not name the over-budget split")
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

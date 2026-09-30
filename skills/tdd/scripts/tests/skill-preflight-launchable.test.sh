#!/usr/bin/env bash
# Unit test for where skills/tdd/SKILL.md's preflight runs `leaf-launchable.sh`. Like
# skill-timeout.test.sh and skill-test-command.test.sh this suite belongs to no single
# script: its subject is the procedure read as text, the way the conductor session that
# follows it reads it. Zero-dependency plain-shell asserts, same idiom, picked up by
# `make test`'s glob by existing.
#
# Why this exists (issue #187): `leaf-launchable.sh` is the check the earlier steps of this
# issue built. What fault it catches, and what a run that misses it has already paid for by
# the time its first leaf dies, are said in its header (leaf-launchable.sh:4-22), once — and
# a script nobody calls changes none of it. There is no script that calls the conductor — the
# conductor is prose — so the wiring can only be pinned as prose, the way
# skill-test-command.test.sh pins preflight's call to `detect-test-command.sh`.
#
# Contract under test (this step only — the check's own behaviour is
# leaf-launchable.test.sh's, and what the document tells an OPERATOR to type instead is
# skill-conductor-launch.test.sh's):
#   Some preflight check names `leaf-launchable.sh`, and it comes before the check that runs
#   the baseline suite.
#
# A second case (issue #360) holds the same section to refusing a bad `VERI_STEP_GROWTH`, the
# fifth budget axis: the check belongs where item 5 already refuses a bad
# `VERI_REFACTOR_BUDGET`, since a budget that cannot be read is a misconfigured run either way
# and preflight is the one place a run is still free to stop. Its behaviour as a script is
# add-ledger-step.test.sh's; that the document orders a run to make the check is prose, and so
# is pinned here.
#
# A third case (issue #451) holds the same item to calling `step-budget.sh`, the resolver for
# the two money budgets (#449), beside `refactor-budget.sh 0`: a step or run budget that cannot
# be read is the same misconfigured run, refused at the same point, and its exit 2 is spelled in
# the paragraph that makes the call rather than borrowed from the refactor budget's.
#
# Before the baseline is the whole point of the position, not a tidiness: the baseline is the
# expensive half of preflight — minutes on a slow repo — and it is wasted either way when no
# leaf can launch. A launchability check placed after it would still refuse the run, but only
# once the run had paid for the answer it could have had for free.
#
# The two checks are located by the SCRIPT each one calls rather than by its number or its
# wording: preflight's items are renumbered whenever one is inserted, and which sentence
# announces a check is the author's. Where the call is written is what "before" is read off,
# so moving a check within an item counts as moving it. `detect-test-command.sh` is what identifies the baseline
# item because that is the call the baseline run is made from (SKILL.md preflight step 3), and
# skill-test-command.test.sh already holds it to living in this section.
#
# Fail closed twice over: a preflight section that cannot be found, and a baseline item that
# names no detection, are each reported as themselves rather than left to read as "nothing is
# out of order".
#
# Not asked here: that CLAUDE.md's suite count moved when this file landed.
# claude-md-counts.test.sh is the case that holds every count in that document to the files on
# disk, and this suite arriving in the tree is what makes it answer.
#
# Run: scripts/tests/skill-preflight-launchable.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
md="$ROOT/$skill_md"

launchable="leaf-launchable.sh"
detector="detect-test-command.sh"
growth='VERI_STEP_GROWTH'
step_budget='step-budget.sh'
refactor_budget='refactor-budget.sh 0'
refusal='exits? 2'
preflight='### 0. Preflight'

pass=0 fail=0

source "$HERE/lib/harness.sh"

sec_start=0 sec_end=0
section() {
  sec_start="$(awk -v h="$1" 'index($0, h) == 1 { print NR; exit }' "$md")"
  [[ -n "$sec_start" ]] || { sec_end=0; return 1; }
  local next
  next="$(head -1 < <(tail -n "+$((sec_start + 1))" "$md" | grep -nE '^#') | cut -d: -f1)"
  if [[ -n "$next" ]]; then
    sec_end=$((sec_start + next - 1))
  else
    sec_end=$(($(wc -l < "$md")))
  fi
  return 0
}

call_at() {
  awk -v s="$sec_start" -v e="$sec_end" -v want="$1" \
    'NR >= s && NR <= e && index($0, want) { print NR; exit }' "$md"
}

item_around() {
  local at="$1" start end next
  start="$(awk -v s="$sec_start" -v at="$at" 'NR >= s && NR <= at && /^[0-9]+\./ { n = NR } END { print n + 0 }' "$md")"
  [[ "$start" -gt 0 ]] || start="$sec_start"
  next="$(awk -v s="$((at + 1))" -v e="$sec_end" 'NR >= s && NR <= e && /^[0-9]+\./ { print NR; exit }' "$md")"
  if [[ -n "$next" ]]; then end=$((next - 1)); else end="$sec_end"; fi
  sed -n "${start},${end}p" "$md"
}

paragraph_around() {
  awk -v at="$1" '
    NR <= at { if ($0 ~ /^[[:space:]]*$/) buf = ""; else if ($0 ~ /^[0-9]+\./) buf = $0 "\n"; else buf = buf $0 "\n"; next }
    $0 ~ /^[[:space:]]*$/ || $0 ~ /^[0-9]+\./ { exit }
    { buf = buf $0 "\n" }
    END { printf "%s", buf }' "$md"
}

preflight_or_problem() {
  section "$preflight" && return 0
  problems+=("$skill_md has no '$preflight' section — where $1 would sit could not be read")
  return 1
}

name="$skill_md's preflight runs $launchable before the baseline suite"
problems=()

if preflight_or_problem "a launchability check"; then
  launch_at="$(call_at "$launchable")"
  baseline_at="$(call_at "$detector")"
  [[ -n "$launch_at" ]] ||
    problems+=("$skill_md's '$preflight' section never names $launchable, so a run performs no launchability check and still dies at its first leaf")
  if [[ -z "$baseline_at" ]]; then
    problems+=("$skill_md's '$preflight' section has no item naming $detector, so which check runs the baseline — the one a launchability check has to precede — could not be read")
  elif [[ -n "$launch_at" ]] && [[ "$launch_at" -gt "$baseline_at" ]]; then
    problems+=("$skill_md:$launch_at calls $launchable after the baseline's $detector call at line $baseline_at, so a run that cannot launch a leaf still pays the whole baseline suite first")
  fi
fi

report "$name"

name="$skill_md's preflight refuses to start on a bad $growth"
problems=()

if preflight_or_problem "a $growth check"; then
  growth_at="$(call_at "$growth")"
  if [[ -z "$growth_at" ]]; then
    problems+=("$skill_md's '$preflight' section never names $growth, so a run whose plan-growth budget cannot be read starts anyway and only finds out when a leaf first tries to grow the plan")
  elif ! grep -qiE "$refusal" < <(item_around "$growth_at"); then
    problems+=("$skill_md:$growth_at names $growth in a preflight item that spells no exit 2, so the document mentions the budget without refusing a run that cannot read it — the way item 5 refuses a bad VERI_REFACTOR_BUDGET")
  fi
fi

report "$name"

name="$skill_md's preflight calls $step_budget beside $refactor_budget and stops on its exit 2"
problems=()

if preflight_or_problem "a $step_budget check"; then
  sb_at="$(call_at "$step_budget")"
  if [[ -z "$sb_at" ]]; then
    problems+=("$skill_md's '$preflight' section never names $step_budget, so a run whose step or run budget cannot be read starts anyway and launches leaves it cannot price")
  else
    grep -F -- "$refactor_budget" > /dev/null < <(item_around "$sb_at") ||
      problems+=("$skill_md:$sb_at calls $step_budget outside the preflight item that runs $refactor_budget")
    grep -iE "$refusal" > /dev/null < <(paragraph_around "$sb_at") ||
      problems+=("$skill_md:$sb_at calls $step_budget in a paragraph that spells no exit 2, so nothing says a budget it cannot read stops the run before a leaf launches")
  fi
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

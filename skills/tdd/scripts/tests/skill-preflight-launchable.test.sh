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
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice — the path as every failure message spells it, and the same path
# resolved for the probes to read — so a message can never name a file the probes did not
# open. The pairing skill-test-command.test.sh and skill-conductor-launch.test.sh both use.
skill_md="skills/tdd/SKILL.md"
md="$ROOT/$skill_md"

# The two scripts an item is recognised by, and the heading the items live under, each
# written down once: every one of them is both a pattern a probe searches for and a string a
# failure message spells, so a message can never name something the probe never looked for.
launchable="leaf-launchable.sh"
detector="detect-test-command.sh"
growth='VERI_STEP_GROWTH'
step_budget='step-budget.sh'
refactor_budget='refactor-budget.sh 0'
refusal='exits? 2'
preflight='### 0. Preflight'

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem, so
# the output says which half of the wiring is wrong rather than just that one is.
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

# section <heading> — the lines under the first heading STARTING WITH the literal <heading>,
# up to the line before the next heading of any level, into `sec_start`/`sec_end`. Non-zero
# when no such heading exists, so a renamed section is reported rather than probed as an
# empty range. A line RANGE rather than the text, because the claim below is about order and
# line numbers are what make "before" answerable. Same shape as skill-test-command.test.sh's.
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

# call_at <script> — the line number the first mention of <script> inside the current
# section is on, empty when the section never names it. A LINE, not the numbered item that
# contains it: preflight's items are prose paragraphs and one of them can hold two calls, so
# an item-granular position would read a launchability check buried in the baseline item's
# last sentence as coming *before* the baseline call in that same item's first. The line is
# also the position a reader sent to the failure message wants.
#
# One pattern rule and no END block, so `exit` cannot print twice: awk runs END after `exit`
# as well as after the last record, and a two-line answer here would reach `-gt` below as a
# bash syntax error — the ordering check would go quiet exactly when an item moved.
call_at() {
  awk -v s="$sec_start" -v e="$sec_end" -v want="$1" \
    'NR >= s && NR <= e && index($0, want) { print NR; exit }' "$md"
}

# item_around <line> — the text of the numbered preflight item that contains <line>: from the
# last `N.` item opener at or before it to the line before the next opener, or the section's
# end when it is the last item. The item rather than the line, because a check is announced on
# one line and its refusal spelled on the next; the opener rather than blank lines, because an
# item's continuation lines are indented prose with blank lines of their own.
item_around() {
  local at="$1" start end next
  start="$(awk -v s="$sec_start" -v at="$at" 'NR >= s && NR <= at && /^[0-9]+\./ { n = NR } END { print n + 0 }' "$md")"
  [[ "$start" -gt 0 ]] || start="$sec_start"
  next="$(awk -v s="$((at + 1))" -v e="$sec_end" 'NR >= s && NR <= e && /^[0-9]+\./ { print NR; exit }' "$md")"
  if [[ -n "$next" ]]; then end=$((next - 1)); else end="$sec_end"; fi
  sed -n "${start},${end}p" "$md"
}

# paragraph_around <line> — the paragraph that contains <line>, bounded by blank lines and by
# numbered item openers, since preflight's items follow one another with no blank line. Narrower
# than item_around: item 5 already spells exit 2 for the refactor budget, so a check that read
# the whole item would find that sentence and never ask whether the money budgets' call has one
# of its own.
paragraph_around() {
  awk -v at="$1" '
    NR <= at { if ($0 ~ /^[[:space:]]*$/) buf = ""; else if ($0 ~ /^[0-9]+\./) buf = $0 "\n"; else buf = buf $0 "\n"; next }
    $0 ~ /^[[:space:]]*$/ || $0 ~ /^[0-9]+\./ { exit }
    { buf = buf $0 "\n" }
    END { printf "%s", buf }' "$md"
}

# preflight_or_problem <what> — enter the preflight section, or record the one problem that
# says the case could not be read at all. Non-zero when the heading is gone, so each case
# below is a probe run inside the section rather than a probe and its own missing-section
# branch: both cases ask the same question first and would otherwise spell the same
# fail-closed message twice, once per case.
preflight_or_problem() {
  section "$preflight" && return 0
  problems+=("$skill_md has no '$preflight' section — where $1 would sit could not be read")
  return 1
}

# 1. One criterion, one case: the check the earlier steps built is the one a real run
#    performs, and it runs before the run has paid for anything.
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

# 2. The fifth budget is checked where the third one is: a value that cannot be read stops the
#    run before it starts, rather than surfacing when a leaf first tries to grow the plan.
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

# 3. The money budgets are checked where the refactor budget is: `step-budget.sh` is called in
#    the preflight item that runs `refactor-budget.sh 0`, and its exit 2 stops the run there,
#    before any leaf is launched.
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

#!/usr/bin/env bash
# Unit tests for scripts/over-budget.sh — the check that turns a recorded test-command run
# into a yes or no (issue #342, part of PRD #335). timed-test-run.sh records a tier and its
# seconds, tier-usual.sh says what that tier usually costs and time-budget.sh resolves the
# two tunables; this is the one that compares them, so that the conductor's narration has
# something to say a word about.
#
# Contract under test:
#   over-budget.sh <tier> <seconds> <usual>
#       → exit 0 when the run is over budget, exit 1 when it is not. Exit 1 is the clean
#         negative CLAUDE.md's "Exit codes are the API" table reserves for a real answer:
#         the check ran and said no.
#   A unit-tier run is over budget when its seconds exceed VERI_UNIT_BUDGET (default 10);
#   at or under that figure it is not. A run of any tier is over budget when its seconds
#   exceed VERI_TIME_WARN_RATIO (default 1.5) times that tier's usual; at or under that
#   product it is not.
#   An over-budget run also prints exactly one line, carrying the ⏱ the conductor pastes
#   into that phase's narration; a run that is not over budget prints nothing. SKILL.md is
#   where the conductor is told to paste that line and to branch on nothing, so this suite
#   reads it too — the line and the instruction to use it are one fact in two files.
#
# Every number here is fabricated and passed in as an argument, so nothing waits on a clock
# and the case costs one process per invocation (CLAUDE.md, "Testing idiom" — the seconds a
# run really took are recorded, never asserted on). Each case picks its `usual` so that only
# the rule it is about can answer: case 1's is 100, far enough above its seconds that the
# ratio cannot be what said yes, and case 2's keeps its seconds under the unit tier's own
# ceiling — so neither passes because some other comparison happened to agree.
#
# Run: skills/tdd/scripts/tests/over-budget.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CHECK="$HERE/../over-budget.sh"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root. The
# document is held twice: the path every failure message spells, and the same path resolved
# for the probes to read, so a message can never name a file the probes did not open.
skill_md="skills/tdd/SKILL.md"
skill_path="$(cd "$HERE/../../../.." && pwd)/$skill_md"
pass=0 fail=0

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

# `probe <var> <value> <tier> <seconds> <usual> <want>` runs the check on a fabricated run
# of <tier> lasting <seconds> against a fabricated <usual>, with the tunable <var> set to
# <value>, and records a problem unless the check exits <want>. An empty <value> clears
# <var> with `env -u` so the script's own default answers — cleared rather than merely left
# unset by the caller, which hermetic-suites.test.sh requires of every suite here.
#
# One helper rather than one per rule: the two rules differ only in which tunable a case
# pins and which tier and usual it picks, so the invocation, the exit-code capture and the
# diagnostic are the same work either way.
probe() {
  local var="$1" value="$2" tier="$3" seconds="$4" usual="$5" want="$6" code verdict against
  if [[ -n "$value" ]]; then
    env "$var=$value" "$CHECK" "$tier" "$seconds" "$usual" && code=0 || code=$?
    against="$var=$value"
  else
    env -u "$var" "$CHECK" "$tier" "$seconds" "$usual" && code=0 || code=$?
    against="$var unset, so the script's own default"
  fi
  [[ "$want" == 0 ]] && verdict="over budget" || verdict="not over budget"
  [[ "$code" == "$want" ]] ||
    problems+=("$tier $seconds s against usual $usual and $against: want exit $want ($verdict), got $code")
}

# 1. The whole of the unit tier's own ceiling, as one case: three fabricated unit-tier runs
#    against the default budget of 10 s — one over it, one exactly at it, one under — and a
#    fourth against a budget set low by the environment, so that a check which had hardcoded
#    10 rather than reading VERI_UNIT_BUDGET is not a pass.
name="over-budget.sh: a unit-tier run over VERI_UNIT_BUDGET is over budget, at or under it is not"
problems=()

probe VERI_UNIT_BUDGET "" unit 12 100 0
probe VERI_UNIT_BUDGET "" unit 10 100 1
probe VERI_UNIT_BUDGET "" unit 4  100 1
probe VERI_UNIT_BUDGET 3  unit 4  100 0

report "$name"

# 2. The ratio rule, which is every tier's: a run whose seconds exceed the ratio times its
#    tier's usual is over budget, and at or under that product it is not. Three fabricated
#    runs of the `all` tier against a usual of 100 and the default ratio — one over 150 s,
#    one exactly at it, one well under — then the same 160 s against a ratio of 2 set in the
#    environment, so a check that hardcoded 1.5 is not a pass. The last is a `unit` run of
#    8 s against a usual of 4: under the unit tier's own 10 s ceiling, so only the ratio can
#    answer it, which is what makes this "any tier" rather than "every tier but unit".
name="over-budget.sh: a run over VERI_TIME_WARN_RATIO x its usual is over budget, at or under it is not"
problems=()

probe VERI_TIME_WARN_RATIO "" all 160 100 0
probe VERI_TIME_WARN_RATIO "" all 150 100 1
probe VERI_TIME_WARN_RATIO "" all 100 100 1
probe VERI_TIME_WARN_RATIO 2  all 160 100 1
probe VERI_TIME_WARN_RATIO "" unit 8   4   0

report "$name"

# 3. What the check says out loud, and what the conductor is told to do with it. The two
#    halves are one criterion: the ⏱ line only exists to be pasted into a phase's narration,
#    and a line nobody is instructed to paste — or one a conductor reads as a verdict — is
#    the same defect as no line at all. So one case, with the script's own output probed
#    first and SKILL.md's instruction after it.
#
#    The line's wording is the writer's; what is pinned is that an over-budget run prints
#    exactly one line and that the line carries the ⏱ the narration is recognised by, and
#    that a run which is not over budget prints nothing at all — a conductor that pastes
#    whatever it got would otherwise narrate a blank warning on every green run.
name="over-budget.sh: one ⏱ line for a run over budget and nothing for one that is not, and $skill_md says to paste it and branch on nothing"
problems=()

# `lines <text>` — how many lines a captured stdout held; empty output is 0 rather than the
# 1 `wc -l` would count for a string command substitution has already stripped.
lines() {
  [[ -z "$1" ]] && { echo 0; return; }
  printf '%s\n' "$1" | wc -l | tr -d ' '
}

# Both fabricated runs are unit-tier against a usual of 100: 12 s is over the default 10 s
# ceiling and 4 s is under it, and the usual is far enough above both that the ratio rule
# cannot be what answered either one.
over="$("$CHECK" unit 12 100 2>/dev/null)" || true
under="$("$CHECK" unit 4 100 2>/dev/null)" || true

[[ "$(lines "$over")" == 1 ]] ||
  problems+=("unit 12 s against usual 100, over budget: want exactly one line of output, got $(lines "$over") lines: $(printf '%q' "$over")")
[[ "$over" == *⏱* ]] ||
  problems+=("unit 12 s against usual 100, over budget: want the line to carry ⏱, got: $(printf '%q' "$over")")
[[ -z "$under" ]] ||
  problems+=("unit 4 s against usual 100, not over budget: want no output at all, got: $(printf '%q' "$under")")

# SKILL.md's side of the same criterion: the text that names the script, joined onto one
# line and normalised, so a sentence that wraps still reads as one and `**never**` matches
# "never". The block is delimited by a top-level bullet or a blank line, not by a blank
# line alone: the script roster here is one unbroken run of bullets, so a paragraph-mode
# read would hand every assertion below the whole roster and each would then be satisfied
# by some *other* script's bullet — a bullet for this one saying "bail the run when it
# does" would pass. Fail closed — a document that never names the script is reported as
# that, rather than probed as an empty string in which nothing matches for its own reason.
instruction="$(awk '
  /^[-*] / || /^[[:space:]]*$/ {
    if (block ~ /over-budget\.sh/) print block
    block = ""
  }
  { block = block " " $0 }
  END { if (block ~ /over-budget\.sh/) print block }
' "$skill_path" | tr -d '*`' | tr '[:upper:]' '[:lower:]')"

if [[ -z "${instruction// /}" ]]; then
  problems+=("$skill_md never names over-budget.sh, so the conductor is never told what the ⏱ line is or what to do with it")
else
  [[ "$instruction" == *⏱* ]] ||
    problems+=("$skill_md names over-budget.sh but never the ⏱ line, so what the conductor is to paste is not stated")
  [[ "$instruction" =~ narrat|issue\ thread|comment ]] ||
    problems+=("$skill_md never says the ⏱ line goes into the phase's narration, so the one place it is meant to appear is unstated")
  [[ "$instruction" =~ (never|not|nothing|no)[^.]{0,80}(branch|gate|verdict|outcome|bail|retr) ]] ||
    problems+=("$skill_md never says the check is branched on by nothing, so a conductor may read an over-budget run as a verdict")
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

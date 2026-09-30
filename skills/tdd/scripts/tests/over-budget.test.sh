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
skill_md="skills/tdd/SKILL.md"
skill_path="$(cd "$HERE/../../../.." && pwd)/$skill_md"
pass=0 fail=0

source "$HERE/lib/harness.sh"

probe() {
  local var="$1" value="$2" tier="$3" seconds="$4" usual="$5" want="$6" code verdict against
  if [[ -n "$value" ]]; then
    env "$var=$value" "$CHECK" "$tier" "$seconds" "$usual" >/dev/null 2>&1 && code=0 || code=$?
    against="$var=$value"
  else
    env -u "$var" "$CHECK" "$tier" "$seconds" "$usual" >/dev/null 2>&1 && code=0 || code=$?
    against="$var unset, so the script's own default"
  fi
  [[ "$want" == 0 ]] && verdict="over budget" || verdict="not over budget"
  [[ "$code" == "$want" ]] ||
    problems+=("$tier $seconds s against usual $usual and $against: want exit $want ($verdict), got $code")
}

name="over-budget.sh: a unit-tier run over VERI_UNIT_BUDGET is over budget, at or under it is not"
problems=()

probe VERI_UNIT_BUDGET "" unit 12 100 0
probe VERI_UNIT_BUDGET "" unit 10 100 1
probe VERI_UNIT_BUDGET "" unit 4  100 1
probe VERI_UNIT_BUDGET 3  unit 4  100 0

report "$name"

name="over-budget.sh: a run over VERI_TIME_WARN_RATIO x its usual is over budget, at or under it is not"
problems=()

probe VERI_TIME_WARN_RATIO "" all 160 100 0
probe VERI_TIME_WARN_RATIO "" all 150 100 1
probe VERI_TIME_WARN_RATIO "" all 100 100 1
probe VERI_TIME_WARN_RATIO 2  all 160 100 1
probe VERI_TIME_WARN_RATIO "" unit 8   4   0

report "$name"

name="over-budget.sh: one ⏱ line for a run over budget and nothing for one that is not, and $skill_md says to paste it and branch on nothing"
problems=()

lines() {
  [[ -z "$1" ]] && { echo 0; return; }
  printf '%s\n' "$1" | wc -l | tr -d ' '
}

over="$("$CHECK" unit 12 100 2>/dev/null)" || true
under="$("$CHECK" unit 4 100 2>/dev/null)" || true

[[ "$(lines "$over")" == 1 ]] ||
  problems+=("unit 12 s against usual 100, over budget: want exactly one line of output, got $(lines "$over") lines: $(printf '%q' "$over")")
[[ "$over" == *⏱* ]] ||
  problems+=("unit 12 s against usual 100, over budget: want the line to carry ⏱, got: $(printf '%q' "$over")")
[[ -z "$under" ]] ||
  problems+=("unit 4 s against usual 100, not over budget: want no output at all, got: $(printf '%q' "$under")")

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

name="over-budget.sh: a run over budget still ends on its leaf's own verdict, with no retry and no bail"
problems=()

fixture="$(mktemp -d)"
trap 'rm -rf "$fixture"' EXIT

over_seconds=40
mkdir -p "$fixture/.tdd"
{
  for _ in {1..10}; do
    printf '{"ts": 1, "issue": "342", "actor": "", "phase": "", "step": "", "event": "test-run", "attempt": "1", "skill_commit": "", "tier": "unit", "suites": "make unit", "seconds": "1"}\n'
  done
  printf '{"ts": 2, "issue": "342", "actor": "", "phase": "", "step": "", "event": "test-run", "attempt": "1", "skill_commit": "", "tier": "unit", "suites": "make unit", "seconds": "%s"}\n' "$over_seconds"
} > "$fixture/.tdd/events.jsonl"

printf 'slugify must lowercase the title and join words with hyphens.\n' > "$fixture/spec.md"

cat > "$fixture/claude" <<'STUB'
#!/bin/sh
printf 'VERDICT: PASS\nREASON: the new case fails for the reason the step names.\n'
STUB
chmod +x "$fixture/claude"

usual="$(cd "$fixture" && "$HERE/../tier-usual.sh" unit)"
( cd "$fixture" && "$CHECK" unit "$over_seconds" "$usual" ) >/dev/null 2>&1 && tripped=0 || tripped=$?
[[ "$tripped" == 0 ]] ||
  problems+=("the run the fixture log records last (unit, $over_seconds s, usual $usual) is not over budget: the check exited $tripped, so nothing below is a statement about an over-budget run")

before="$(wc -l < "$fixture/.tdd/events.jsonl" | tr -d ' ')"
out="$( cd "$fixture" && env -u VERI_MODEL -u VERI_MODEL_VERIFIER -u VERI_MODEL_DEVELOPER \
          -u VERIFY_LEAF_ARGS CLAUDE_BIN="$fixture/claude" VERI_POLL=0.02 \
          VERI_STUCK_RETRIES=0 VERI_NO_VERDICT_RETRIES=0 \
          "$HERE/../verify.sh" red "$fixture/spec.md" tests/test_slugify.py test_lowercases 2>/dev/null )" \
  && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("the stub leaf said PASS on an over-budget run: want verify.sh exit 0, got $code")
[[ "$out" == *"the reason the step names"* ]] ||
  problems+=("want the stub leaf's own reason on stdout, got: $(printf '%q' "$out")")

after="$(sed -n "$((before + 1)),\$p" "$fixture/.tdd/events.jsonl")"
[[ "$after" == *'"event": "verdict"'*'"verdict": "PASS"'* ]] ||
  problems+=("want one verdict event carrying PASS in the log, got: $(printf '%q' "$after")")
[[ "$after" != *'"event": "relaunch"'* ]] ||
  problems+=("the over-budget run was retried: a relaunch event was logged: $(printf '%q' "$after")")
[[ "$after" != *'"event": "bail"'* ]] ||
  problems+=("the over-budget run bailed: a bail event was logged: $(printf '%q' "$after")")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

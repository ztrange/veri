#!/usr/bin/env bash
# Tests for scripts/step-cost.sh — the reader over the run's `usage` events (#448): what one
# step, or the whole run, has spent on leaves so far. Run from the run's worktree, it reads
# .tdd/events.jsonl relative to it, the way event.sh and supervise.sh spell their own paths.
# Every fixture here is a hand-written events.jsonl, so nothing a leaf does is needed.
#
# Fast tier (#336): no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/step-cost.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STEP_COST="$HERE/../../step-cost.sh"
source "$HERE/../lib/harness.sh"
problems=""

work="$(scratch_dir)"
mkdir -p "$work/.tdd"

run_cost() {
  out="$(cd "$work" && "$STEP_COST" "$@" 2>"$work/stderr")" && code=0 || code=$?
  err="$(cat "$work/stderr")"
}

expect() {
  if [[ "$code" != "$1" || "$out" != "$2" ]]; then
    problems+="    want exit $1 and stdout '$2', got exit $code and stdout '$out' (stderr '$err')"$'\n'
  fi
}

refused() {
  expect 2 ""
  [[ "$err" == step-cost.sh:* ]] || problems+="    $1: stderr '$err' is not step-cost.sh's own diagnostic"$'\n'
}

verdict() {
  if [[ -z "$problems" ]]; then
    ok
  else
    no "$1"
    printf '%s' "$problems"
  fi
  problems=""
}

cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30134540000000004"}
{"ts": 2, "issue": "448", "actor": "developer", "phase": "green", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}
{"ts": 3, "issue": "448", "actor": "verifier", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.12"}
EOF
run_cost "step one"
expect 0 "0.42"
verdict "a step's usage events are summed to two decimals, exit 0"

cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30"}
EOF
run_cost "step two"
expect 3 ""
verdict "a step no usage event carries prints nothing, exit 3"

cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30134540000000004"}
{"ts": 2, "issue": "448", "actor": "developer", "phase": "green", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}
{"ts": 3, "issue": "448", "actor": "conductor", "phase": "scope", "step": "", "event": "usage", "total_cost_usd": "0.25"}
EOF
run_cost --run
expect 0 "1.55"
verdict "--run sums every usage event, step-less ones included, exit 0"

cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "verifier", "phase": "red", "step": "step one", "event": "verdict", "verdict": "PASS"}
{"ts": 2, "issue": "448", "actor": "developer", "phase": "green", "step": "step one", "event": "test-run", "exit": "0"}
EOF
run_cost --run
expect 3 ""
verdict "--run against a log with no usage event prints nothing, exit 3"

cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}
{"ts": 2, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30134540000000004"}
{"ts": 3, "issue": "448", "actor": "verifier", "phase": "red", "step": "step two", "event": "usage", "total_cost_usd": "0.5"}
{"ts": 4, "issue": "448", "actor": "verifier", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.12"}
{"ts": 5, "issue": "448", "actor": "developer", "phase": "green", "step": "step two", "event": "usage", "total_cost_usd": "0.25"}
EOF
run_cost --steps
expect 0 $'1.75 3\n0.42 2'
cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "verifier", "phase": "red", "step": "step one", "event": "verdict", "verdict": "PASS"}
EOF
run_cost --steps
expect 3 ""
verdict "--steps prints one dollars-and-leaves line per step in first-mention order, exit 0; none is exit 3"

cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30"}
{"ts": 2, "issue": "448", "actor": "verifier", "phase": "red", "step": "step one", "event": "usage"}
{"ts": 3, "issue": "448", "actor": "developer", "phase": "green", "step": "step one", "event": "usage", "total_cost_usd": ""}
{"ts": 4, "issue": "448", "actor": "developer", "phase": "red", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}
EOF
run_cost --steps
expect 0 $'0.30 3\n1.00 1'
run_cost "step one"
expect 0 "0.30"
run_cost --run
expect 0 "1.30"
verdict "a usage event with an absent or empty total_cost_usd contributes zero and still counts as a leaf"

cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "verifier", "phase": "red", "step": "step three", "event": "verdict", "verdict": "PASS"}
{"ts": 2, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30"}
{"ts": 3, "issue": "448", "actor": "developer", "phase": "green", "step": "step one", "event": "test-run", "exit": "0", "total_cost_usd": "5.0"}
{"ts": 4, "issue": "448", "actor": "verifier", "phase": "green", "step": "step one", "event": "usage", "total_cost_usd": "0.20"}
{"ts": 5, "issue": "448", "actor": "verifier", "phase": "green", "step": "step one", "event": "verdict", "verdict": "PASS"}
EOF
run_cost --steps
expect 0 "0.50 2"
run_cost "step one"
expect 0 "0.50"
run_cost "step three"
expect 3 ""
run_cost --run
expect 0 "0.50"
verdict "events that are not usage events create no step and add no cost in any of the three calls"

cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30"}
EOF
run_cost
refused "no argument"
run_cost --bogus
refused "--bogus"
run_cost --run "step one"
refused "--run with a step text"
run_cost --steps "step one"
refused "--steps with a step text"
rm "$work/.tdd/events.jsonl"
run_cost "step one"
refused "missing .tdd/events.jsonl"
verdict "no argument, an unknown option, --run or --steps with a step text, and a missing log each exit 2 with stderr only"

header="$(sed -n '2,$p' "$HERE/step-cost.test.sh" | sed '/^#/!q' | grep '^#')"
for part in 'no git' 'no network' 'no servers' 'no real sleep' 'no nested suites'; do
  grep -F "$part" <<< "$header" > /dev/null || problems+="    the header comment does not state '$part'"$'\n'
done
cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30"}
EOF
PATH="$HERE/../unit-guard:$HERE/../offline:$PATH" run_cost "step one"
expect 0 "0.30"
[[ -z "$err" ]] || problems+="    under make unit's shims stderr said '$err', want nothing"$'\n'
verdict "the header states the fast-tier bar and the script answers under make unit's git, python3, gh and curl shims"

header="$(sed -n '2,$p' "$STEP_COST" | sed '/^#/!q' | grep '^#' | sed 's/^# *//' | tr '\n' ' ')"
for part in 'leaf spend only' "conductor's own spending is in no \`usage\` event"; do
  grep -F "$part" <<< "$header" > /dev/null || problems+="    the header comment does not state '$part'"$'\n'
done
verdict "step-cost.sh's header says it reports leaf spend only and the conductor's spending is in no usage event"

cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "521", "actor": "developer", "phase": "red", "step": "cost a step \u2014 its title \u27e6criterion 1\u27e7", "event": "usage", "total_cost_usd": "0.30"}
{"ts": 2, "issue": "521", "actor": "verifier", "phase": "red", "step": "cost a step \u2014 its title \u27e6criterion 1\u27e7", "event": "usage", "total_cost_usd": "0.12"}
{"ts": 3, "issue": "521", "actor": "developer", "phase": "red", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}
EOF
run_cost --steps
expect 0 $'0.42 2\n1.00 1'
run_cost "cost a step — its title ⟦criterion 1⟧"
expect 0 "0.42"
verdict "#521: a step title carrying an em dash and ⟦criterion k⟧ is summed to the figure --steps prints for it"

finish

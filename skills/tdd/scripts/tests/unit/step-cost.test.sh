#!/usr/bin/env bash
# Tests for scripts/step-cost.sh — the reader over the run's `usage` events: what one
# step, or the whole run, has spent on leaves so far. Run from the run's worktree, it reads
# .tdd/events.jsonl relative to it. Every fixture here is a hand-written events.jsonl.
# Fast tier: no git, no network, no servers, no real sleep, no nested suites —
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

cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "721", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30"}
EOF
ln -s "$(cd "$HERE/../../.." && pwd)" "$work/linked-skill"
mkdir -p "$work/elsewhere/.tdd"
cp "$work/.tdd/events.jsonl" "$work/elsewhere/.tdd/events.jsonl"
run_cost "step one"
in_place="$out" in_place_code="$code"
linked="$(cd "$work/elsewhere" && "$work/linked-skill/scripts/step-cost.sh" "step one" 2>&1)" && linked_code=0 || linked_code=$?
if [[ "$in_place" != "0.30" || "$in_place_code" != 0 || "$linked" != "$in_place" || "$linked_code" != "$in_place_code" ]]; then
  problems+="    in place: exit $in_place_code, stdout '$in_place'; through the symlink from elsewhere: exit $linked_code, output '$linked'"$'\n'
fi
verdict "step-cost.sh run through a symlink to the skill directory and from another working directory prints the same figure and exit code as when run in place"

finish

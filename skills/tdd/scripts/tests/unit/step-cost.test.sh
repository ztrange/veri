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
pass=0 fail=0

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/.tdd"

# run_cost [args…] — run the script from the run's worktree with the arguments given,
# leaving its stdout in `out`, its exit code in `code` and its stderr in `err`.
run_cost() {
  out="$(cd "$work" && "$STEP_COST" "$@" 2>"$work/stderr")" && code=0 || code=$?
  err="$(cat "$work/stderr")"
}

# verdict <name> — report one case from the `problems` the case just filled: empty is a
# pass, otherwise a FAIL line naming the case and the indented lines it collected. Same
# accounting idiom as stop-requested.test.sh's verdict().
verdict() {
  if [[ -z "$problems" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1)); echo "FAIL - $1"
    printf '%s' "$problems"
  fi
}

# 1. a step's `usage` events are summed and printed to two decimals, exit 0. The fixture
#    carries the cost as harvest-usage.sh writes it — a JSON string with a float's full
#    tail — and a second step's event besides, so a sum over the whole log (1.42) and a sum
#    of the named step's events (0.42) come out different.
cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30134540000000004"}
{"ts": 2, "issue": "448", "actor": "developer", "phase": "green", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}
{"ts": 3, "issue": "448", "actor": "verifier", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.12"}
EOF
run_cost "step one"
problems=""
if [[ "$code" != 0 || "$out" != "0.42" ]]; then
  problems="    want exit 0 and stdout '0.42', got exit $code and stdout '$out' (stderr '$err')"$'\n'
fi
verdict "a step's usage events are summed to two decimals, exit 0"

# 2. a step no `usage` event carries yet — the state a step is in before its first leaf has
#    exited — is nothing to do, not an error: nothing on stdout, exit 3. The log still holds
#    other steps' events, so an empty log is not what makes the answer.
cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30"}
EOF
run_cost "step two"
problems=""
if [[ "$code" != 3 || -n "$out" ]]; then
  problems="    want exit 3 and empty stdout, got exit $code and stdout '$out' (stderr '$err')"$'\n'
fi
verdict "a step no usage event carries prints nothing, exit 3"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

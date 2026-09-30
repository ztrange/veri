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

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/.tdd"

# run_cost [args…] — run the script from the run's worktree with the arguments given,
# leaving its stdout in `out`, its exit code in `code` and its stderr in `err`.
run_cost() {
  out="$(cd "$work" && "$STEP_COST" "$@" 2>"$work/stderr")" && code=0 || code=$?
  err="$(cat "$work/stderr")"
}

# expect <code> <stdout> — add to the case's `problems` for the run just made: nothing when it
# exited <code> with exactly <stdout>, otherwise one indented line saying what it did instead.
expect() {
  if [[ "$code" != "$1" || "$out" != "$2" ]]; then
    problems+="    want exit $1 and stdout '$2', got exit $code and stdout '$out' (stderr '$err')"$'\n'
  fi
}

# refused <call> — add to `problems` unless the run just made exited 2, silent on stdout,
# with a diagnostic of the script's own on stderr; <call> names it in the line.
refused() {
  expect 2 ""
  [[ "$err" == step-cost.sh:* ]] || problems+="    $1: stderr '$err' is not step-cost.sh's own diagnostic"$'\n'
}

# verdict <name> — report one case from the `problems` the case just filled: empty is a
# pass, otherwise a FAIL line naming the case and the indented lines it collected. Then
# empty it for the next case. Same accounting idiom as stop-requested.test.sh's verdict().
verdict() {
  if [[ -z "$problems" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1)); echo "FAIL - $1"
    printf '%s' "$problems"
  fi
  problems=""
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
expect 0 "0.42"
verdict "a step's usage events are summed to two decimals, exit 0"

# 2. a step no `usage` event carries yet — the state a step is in before its first leaf has
#    exited — is nothing to do, not an error: nothing on stdout, exit 3. The log still holds
#    other steps' events, so an empty log is not what makes the answer.
cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30"}
EOF
run_cost "step two"
expect 3 ""
verdict "a step no usage event carries prints nothing, exit 3"

# 3. --run sums every `usage` event in the log, whatever step it carries — including one
#    carrying none, which event.sh writes as `"step": ""` — to two decimals, exit 0. Without
#    the step-less event the sum is 1.30, so a reader that skips it comes out different.
cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30134540000000004"}
{"ts": 2, "issue": "448", "actor": "developer", "phase": "green", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}
{"ts": 3, "issue": "448", "actor": "conductor", "phase": "scope", "step": "", "event": "usage", "total_cost_usd": "0.25"}
EOF
run_cost --run
expect 0 "1.55"
verdict "--run sums every usage event, step-less ones included, exit 0"

# 4. --run against a log holding no `usage` event is nothing to do: nothing on stdout, exit
#    3. The log is not empty — it holds a verdict and a test-run event, both carrying a step
#    — so an empty file is not what makes the answer; the absence of `usage` events is.
cat > "$work/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "448", "actor": "verifier", "phase": "red", "step": "step one", "event": "verdict", "verdict": "PASS"}
{"ts": 2, "issue": "448", "actor": "developer", "phase": "green", "step": "step one", "event": "test-run", "exit": "0"}
EOF
run_cost --run
expect 3 ""
verdict "--run against a log with no usage event prints nothing, exit 3"

# 5. --steps prints one `<dollars> <leaves>` line per step that has a `usage` event, in the
#    order the log first mentions each, exit 0. "step two" is mentioned first although "step
#    one" sorts first, and the two steps' leaf counts differ, so neither a sorted nor a
#    count-blind reader comes out the same. Then a log with no `usage` event is nothing to
#    do: nothing on stdout, exit 3.
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

# 6. a `usage` event whose `total_cost_usd` is absent, or empty, contributes zero and still
#    counts as a leaf, rather than aborting the read — one malformed leaf record must not
#    blind the budget. "step one" holds one well-formed event, one with no cost key and one
#    with an empty cost, so it is 0.30 over three leaves; the well-formed event of "step
#    two" comes after both malformed ones, so a read that stopped at them would miss it.
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

# 7. events that are not `usage` events are ignored by all three calls: a `verdict` or
#    `test-run` line carrying a step creates no step and adds no cost. "step three" is
#    mentioned only by a verdict, and first, so a reader that took it for a step would list
#    it ahead of "step one"; the test-run line on "step one" carries a cost, so a reader that
#    summed it would come out 5.00 higher.
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

# 8. a call that cannot be answered — no argument, an unknown option, `--run` or `--steps`
#    with a step text besides, and a missing .tdd/events.jsonl — exits 2 with a diagnostic
#    on stderr and nothing on stdout, so a conductor capturing stdout never reads a
#    diagnostic as a figure. The log holds a `usage` event, so `--run extra` or `--steps
#    extra` read as if the extra word were not there would print a figure and exit 0. The
#    diagnostic is the script's own, opening `step-cost.sh:`, so a missing log is refused by
#    the script and not left to whatever the tool reading it happens to print.
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

# 9. the suite belongs in the fast tier and says so: its header comment states each part of
#    the bar — no git, no network, no servers, no real sleep, no nested suites — and the
#    script answers with `make unit`'s shims first on PATH (unit-guard's git and python3,
#    offline's gh and curl), each of which refuses on stderr when run for real. So a
#    step-cost.sh that shelled out to any of them would print that refusal here, whatever
#    `make test` — which adds no such shim — made of it.
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

# 10. step-cost.sh's own header says the figure is leaf spend only, and why: the conductor's
#     own spending is in no `usage` event. A figure that reads as "what this step cost" and
#     silently leaves the conductor out gets quoted wrongly later, so the caveat sits where
#     a reader of the script meets it. The header is read as one line — the comment marks
#     stripped, its lines joined by spaces — so a rewrap of the sentence is not a failure.
header="$(sed -n '2,$p' "$STEP_COST" | sed '/^#/!q' | grep '^#' | sed 's/^# *//' | tr '\n' ' ')"
for part in 'leaf spend only' "conductor's own spending is in no \`usage\` event"; do
  grep -F "$part" <<< "$header" > /dev/null || problems+="    the header comment does not state '$part'"$'\n'
done
verdict "step-cost.sh's header says it reports leaf spend only and the conductor's spending is in no usage event"

# 11. a step whose title carries an em dash and ⟦criterion k⟧ is summed like any other
#     (#521). event.sh writes the step as JSON with ensure_ascii, so the log holds `\u2014`,
#     `\u27e6` and `\u27e7` where the ledger — and so the argument — holds the UTF-8
#     characters. The step-cost.sh call must print the same figure --steps prints for it.
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

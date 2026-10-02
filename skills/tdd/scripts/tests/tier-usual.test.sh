#!/usr/bin/env bash
# Unit tests for scripts/tier-usual.sh — what one tier's test-command run usually costs,
# computed from the `test-run` lines timed-test-run.sh writes.
#
# Contract under test:
#   tier-usual.sh <tier>  → exit 0, and on stdout the median of the `seconds` on the last 10
#                           `test-run` lines of `.tdd/events.jsonl` whose `tier` is <tier>.
#   the log               → `.tdd/events.jsonl`, read relative to the directory the script
#                           runs in.
#
# Run: skills/tdd/scripts/tests/tier-usual.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
USUAL="$HERE/../tier-usual.sh"

source "$HERE/lib/harness.sh"

ev() {
  printf '{"ts": 1700000000, "issue": "342", "actor": "developer", "phase": "green", "step": "1", "event": "%s", "attempt": "1", "skill_commit": "abc1234", "tier": "%s", "suites": "one.test.sh", "seconds": "%s"}\n' \
    "$1" "$2" "$3"
}

name="tier-usual.sh <tier>: the usual is the median of that tier's last 10 test-run events' seconds"
problems=()
work="$(scratch_dir)"
mkdir -p "$work/.tdd"
{
  ev test-run fast 100
  ev test-run fast 200
  ev test-run fast 7
  ev test-run fast 3
  ev test-run all 900
  ev test-run fast 10
  ev test-run fast 1
  ev leaf-exit fast 900
  ev test-run fast 9
  ev test-run fast 5
  ev test-run fast 2
  ev test-run fast 8
  ev test-run fast 4
  ev test-run fast 6
} > "$work/.tdd/events.jsonl"

out="$( cd "$work" && "$USUAL" fast 2>/dev/null )" && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want tier-usual.sh to exit 0, it exited $code")

[[ "$out" == 5.5 ]] ||
  problems+=("usual for tier fast: want 5.5, got $(printf '%q' "$out")")

rm -rf "$work"
report "$name"

name="tier-usual.sh and metrics.sh read the event log through veri/event_log.py: each, run through its entry point against a stand-in veri/event_log.py, reports the stand-in figures"
problems=()
work="$(scratch_dir)"
pkg="$work/pkg"
mkdir -p "$pkg/lib" "$pkg/veri" "$work/run/.tdd"
cp "$HERE/../tier-usual.sh" "$HERE/../metrics.sh" "$HERE/../ledger-steps.sh" "$pkg/"
cp "$HERE"/../lib/*.sh "$pkg/lib/"
cat > "$pkg/veri/event_log.py" <<'PY'
def read_events(path):
    return [{"ts": 1000, "event": "launch", "step": "decoy step", "phase": "red",
             "actor": "developer", "name": "decoy-leaf"},
            {"ts": 1077, "event": "usage"},
            {"ts": 1078, "event": "test-run", "tier": "decoy-tier", "seconds": "42"}]


def usage_totals(events):
    return 3.0, 1234
PY
printf '# Plan for #9 \xe2\x80\x94 cogs mesh\n\n- [x] a cog exists\n- [ ] two cogs mesh\n' > "$work/run/.tdd/issue-9.md"
ev test-run fast 100 > "$work/run/.tdd/events.jsonl"

usual="$( cd "$work/run" && "$pkg/tier-usual.sh" decoy-tier 2>&1 )" && code=0 || code=$?
[[ "$usual" == "42.0" ]] ||
  problems+=("tier-usual.sh beside a stand-in veri/event_log.py: printed $(printf '%q' "$usual") (exit $code), want 42.0")

metrics="$( cd "$work/run" && "$pkg/metrics.sh" 9 2>&1 )" && code=0 || code=$?
for want in "| decoy step |" "| decoy-tier | 42 |"; do
  [[ "$metrics" == *"$want"* ]] ||
    problems+=("metrics.sh beside a stand-in veri/event_log.py: report lacks '$want' (exit $code): $(printf '%s' "$metrics" | tail -n 1)")
done

rm -rf "$work"
report "$name"

finish

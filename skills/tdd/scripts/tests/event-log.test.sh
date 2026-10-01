#!/usr/bin/env bash
# Unit tests for scripts/lib/event_log.py — the one per-line parse of a run's events.jsonl and
# the one dollar/token sum over its `usage` events.
#
# Contract under test:
#   lib/event_log.py   read_events(<path>)  → the log's events, one dict per non-blank line
#                      usage_totals(<events>) → (dollars, tokens) summed over the usage events
#   status.sh          text and --json figures read through those two, and unchanged by them
#
# Run: scripts/tests/event-log.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
SCRIPTS="$HERE/.."
work="$(scratch_dir)"

repo="$work/repo"
new_repo -b main "$repo" >/dev/null 2>&1
run="$repo/.tdd/wt/9"
new_repo -b tdd/9-cogs-mesh "$run" >/dev/null 2>&1
mkdir -p "$run/.tdd"
printf '# Plan for #9 — cogs mesh\n\n- [x] a cog exists\n- [ ] two cogs mesh\n' > "$run/.tdd/issue-9.md"
now="$(date +%s)"
cat > "$run/.tdd/events.jsonl" <<EOF

{"ts": $((now - 300)), "issue": "9", "actor": "developer", "phase": "red", "step": "a cog exists", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}
{"ts": $((now - 250)), "issue": "9", "actor": "developer", "phase": "red", "step": "a cog exists", "event": "usage", "attempt": "1", "skill_commit": "abc", "total_cost_usd": "0.50", "input_tokens": "1000", "output_tokens": "200", "cache_read_input_tokens": "3000", "cache_creation_input_tokens": "500"}


{"ts": $((now - 200)), "issue": "9", "actor": "developer", "phase": "green", "step": "two cogs mesh", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-green"}
{"ts": $((now - 100)), "issue": "9", "actor": "developer", "phase": "green", "step": "two cogs mesh", "event": "usage", "attempt": "1", "skill_commit": "abc", "total_cost_usd": "1.25", "input_tokens": "2000", "output_tokens": "300", "cache_read_input_tokens": "4000", "cache_creation_input_tokens": "0"}

EOF
gh_json="$work/gh"
mkdir -p "$gh_json"
echo '[]' > "$gh_json/issues.json"
echo '[]' > "$gh_json/prs.json"

status() {
  local script="$1"; shift
  out="$(cd "$repo" && env -u VERI_LABEL VERI_GH_JSON="$gh_json" VERI_TIMEOUT=600 \
    "$script" --scope cogs-label "$@" 2>/dev/null)" && code=0 || code=$?
  run_line="$(printf '%s\n' "$out" | grep '^#9 ' || true)"
  scope_line="$(printf '%s\n' "$out" | grep '^scope ' || true)"
}

problems=()

status "$SCRIPTS/status.sh"
for want in "develop-green" "attempt 1" '$1.75' "11000 tokens"; do
  [[ "$run_line" == *"$want"* ]] || problems+=("status.sh run line lacks '$want': '$run_line' (exit $code)")
done
for want in "attempted 1" "done 0" "bailed 0" "wall 200s" '$1.75'; do
  [[ "$scope_line" == *"$want"* ]] || problems+=("status.sh scope line lacks '$want': '$scope_line' (exit $code)")
done
status "$SCRIPTS/status.sh" --json
figures="$(printf '%s' "$out" | python3 -c '
import json, sys
try:
    doc = json.loads(sys.stdin.read())
    run, scope = doc["runs"][0], doc["scope"]
    print("leaf=%s attempts=%r dollars=%r tokens=%r scope_dollars=%r wall=%r attempted=%r" % (
        run["leaf"], run["attempts"], run["dollars"], run["tokens"], scope["dollars"],
        scope["wall_seconds"], scope["attempted"]))
except (ValueError, KeyError, TypeError, IndexError) as err:
    print("no run and scope figures: %r" % err)
')"
want_figures="leaf=develop-green attempts=1 dollars=1.75 tokens=11000 scope_dollars=1.75 wall=200 attempted=1"
[[ "$figures" == "$want_figures" ]] \
  || problems+=("status.sh --json figures: '$figures' (exit $code), want '$want_figures'")

copy="$work/scripts"
mkdir -p "$copy/lib"
cp "$SCRIPTS/status.sh" "$SCRIPTS/solvable-issues.sh" "$copy/"
cp "$SCRIPTS/lib/main-working-tree.sh" "$copy/lib/"
cat > "$copy/lib/event_log.py" <<'PY'
def read_events(path):
    return [{"ts": 1000, "event": "launch", "step": "decoy step", "phase": "red",
             "actor": "developer", "name": "decoy-leaf"},
            {"ts": 1077, "event": "usage"}]


def usage_totals(events):
    return 3.0, 1234
PY
status "$copy/status.sh"
for want in "decoy-leaf" '$3.00' "1234 tokens"; do
  [[ "$run_line" == *"$want"* ]] \
    || problems+=("status.sh beside a stand-in event_log.py: run line lacks '$want': '$run_line' (exit $code)")
done
for want in "wall 77s" '$3.00'; do
  [[ "$scope_line" == *"$want"* ]] \
    || problems+=("status.sh beside a stand-in event_log.py: scope line lacks '$want': '$scope_line' (exit $code)")
done

report "run_activity and scope_totals read the event log through lib/event_log.py's one parse and one dollar/token sum, with status.sh's text and --json figures unchanged over a log with blank lines and usage events"

finish

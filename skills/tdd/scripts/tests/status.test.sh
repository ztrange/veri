#!/usr/bin/env bash
# Unit tests for scripts/status.sh — the aggregation layer over every run in a repository.
# Run from a target repo, it discovers runs from `.tdd/wt/*` under the repository's MAIN
# working tree (resolved as solvable-issues.sh does, #166) and renders each one.
#
# Contract under test (issue #109):
#   status.sh            print every run under .tdd/wt/*, exit 0;
#                        print "no runs" and exit 3 when there are none.
#
# Run: scripts/tests/status.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STATUS="$HERE/../status.sh"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

repo() {  # repo <name> -> path
  local dir="$work/$1"
  new_repo -b main "$dir" >/dev/null 2>&1
  echo "$dir"
}

fabricate_run() {  # fabricate_run <repo> <n> <branch> -> path
  local dir="$1/.tdd/wt/$2"
  new_repo -b "$3" "$dir" >/dev/null 2>&1
  mkdir -p "$dir/.tdd"
  echo "$dir"
}

run_in() {  # run_in <dir> [script args…]; sets $out and $code
  local dir="$1"; shift
  out="$(cd "$dir" && "$STATUS" "$@" 2>/dev/null)" && code=0 || code=$?
}

expect_nothing_missing() {  # expect_nothing_missing <case name>; reads $missing, $out, $code
  if [[ ${#missing[@]} -eq 0 && "$code" -eq 0 ]]; then ok; else
    no "$1"
    printf 'missing: %s\n' "${missing[@]:-}"
    printf 'output:\n%s\nexit %s\n' "$out" "$code"
  fi
}

empty="$(repo empty)"
run_in "$empty"
if [[ "$out" == "no runs" && "$code" -eq 3 ]]; then ok; else
  no "no runs under the main working tree prints 'no runs' and exits 3"
  diff <(printf 'no runs\nexit 3\n') <(printf '%s\nexit %s\n' "$out" "$code")
fi

one="$(repo one)"
run="$(fabricate_run "$one" 7 tdd/7-widgets-spin)"
cat > "$run/.tdd/issue-7.md" <<'EOF'
# Plan for #7 — widgets spin when clicked

- [x] a widget exists
- [ ] a clicked widget spins
- [ ] a spinning widget stops
EOF
run_in "$one"
missing=()
for want in "#7" "widgets spin when clicked" "tdd/7-widgets-spin" "step 2 of 3"; do
  [[ "$out" == *"$want"* ]] || missing+=("$want")
done
expect_nothing_missing "a run under .tdd/wt/* is listed with its issue number, title, branch and step n of m"

live="$(repo live)"
run="$(fabricate_run "$live" 8 tdd/8-gears-turn)"
cat > "$run/.tdd/issue-8.md" <<'EOF'
# Plan for #8 — gears turn

- [x] a gear exists
- [ ] a gear turns
EOF
now="$(date +%s)"
ev() {  # ev <ts> <actor> <phase> <step> <event> <attempt> [name]
  printf '{"ts": %s, "issue": "8", "actor": "%s", "phase": "%s", "step": "%s", "event": "%s", "attempt": "%s", "skill_commit": "abc"%s}\n' \
    "$1" "$2" "$3" "$4" "$5" "$6" "${7:+, \"name\": \"$7\"}"
}
{
  ev $((now - 900)) conductor ""     "a gear exists" step-start ""
  ev $((now - 890)) developer red    "a gear exists" launch     1 develop-red
  ev $((now - 800)) developer green  "a gear exists" launch     1 develop-green
  ev $((now - 700)) verifier  green  "a gear exists" launch     1 verify-green
  ev $((now - 600)) conductor ""     "a gear exists" step-done  ""
  ev $((now - 500)) conductor ""     "a gear turns"  step-start ""
  ev $((now - 400)) developer green  "a gear turns"  launch     1 develop-green
  ev $((now - 100)) developer green  "a gear turns"  launch     2 develop-green
} > "$run/.tdd/events.jsonl"
run_in "$live"
missing=()
for want in "green" "developer" "develop-green" "attempt 2"; do
  [[ "$out" == *"$want"* ]] || missing+=("$want")
done
[[ "$out" =~ (^|[^0-9])10[0-5]s([^0-9a-z]|$) ]] || missing+=("elapsed 100s-105s")
expect_nothing_missing "a run shows its current phase, actor, leaf name, leaf elapsed seconds and attempts in the step, from its event log"

spent="$(repo spent)"
run="$(fabricate_run "$spent" 9 tdd/9-cogs-mesh)"
cat > "$run/.tdd/issue-9.md" <<'EOF'
# Plan for #9 — cogs mesh

- [x] a cog exists
- [ ] two cogs mesh
EOF
now="$(date +%s)"
cat > "$run/.tdd/events.jsonl" <<EOF
{"ts": $((now - 300)), "issue": "9", "actor": "developer", "phase": "red", "step": "a cog exists", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}
{"ts": $((now - 250)), "issue": "9", "actor": "developer", "phase": "red", "step": "a cog exists", "event": "usage", "attempt": "1", "skill_commit": "abc", "duration_ms": "50000", "duration_api_ms": "40000", "num_turns": "7", "total_cost_usd": "0.50", "input_tokens": "1000", "output_tokens": "200", "cache_read_input_tokens": "3000", "cache_creation_input_tokens": "500"}
{"ts": $((now - 200)), "issue": "9", "actor": "developer", "phase": "green", "step": "two cogs mesh", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-green"}
{"ts": $((now - 100)), "issue": "9", "actor": "developer", "phase": "green", "step": "two cogs mesh", "event": "usage", "attempt": "1", "skill_commit": "abc", "duration_ms": "90000", "duration_api_ms": "80000", "num_turns": "9", "total_cost_usd": "1.25", "input_tokens": "2000", "output_tokens": "300", "cache_read_input_tokens": "4000", "cache_creation_input_tokens": "0"}
EOF
run_in "$spent"
missing=()
[[ "$out" == *'$1.75'* ]] || missing+=('$1.75')
[[ "$out" =~ (^|[^0-9])11,?000\ tokens ]] || missing+=("11000 tokens")
expect_nothing_missing "a run shows its cost so far in dollars and tokens, summed from its event log"

states="$(repo states)"
now="$(date +%s)"
sleep 0 & dead_pid=$!
wait "$dead_pid" 2>/dev/null
launched_run() {  # launched_run <repo> <n> <ts> -> path; a one-step ledger and one develop-red launch at <ts>
  local dir
  dir="$(fabricate_run "$1" "$2" "tdd/$2-lamps")"
  printf '# Plan for #%s — lamps glow\n\n- [ ] a lamp glows\n' "$2" > "$dir/.tdd/issue-$2.md"
  printf '{"ts": %s, "issue": "%s", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}\n' \
    "$3" "$2" > "$dir/.tdd/events.jsonl"
  echo "$dir"
}
state_run() { launched_run "$states" "$@"; }  # state_run <n> <ts> -> path
run="$(state_run 11 $((now - 10)))"
echo "$$" > "$run/.tdd/conductor.pid"
run="$(state_run 12 $((now - 20)))"
printf '{"ts": %s, "issue": "12", "actor": "conductor", "phase": "", "step": "", "event": "done", "attempt": "", "skill_commit": "abc", "pr": "https://github.com/o/r/pull/12"}\n' \
  "$((now - 15))" >> "$run/.tdd/events.jsonl"
run="$(state_run 13 $((now - 30)))"
printf '{"ts": %s, "issue": "13", "actor": "conductor", "phase": "green", "step": "a lamp glows", "event": "bail", "attempt": "", "skill_commit": "abc", "cause": "stuck", "classification": "system"}\n' \
  "$((now - 25))" >> "$run/.tdd/events.jsonl"
run="$(state_run 14 $((now - 1000)))"
echo "$dead_pid" > "$run/.tdd/conductor.pid"
VERI_TIMEOUT=600 run_in "$states"
line_of() { printf '%s\n' "$out" | grep "^#$1 " || true; }
missing=()
for want in "11 running" "12 done" "12 https://github.com/o/r/pull/12" "13 bailed" "13 green" \
    "13 system" "14 stale"; do
  [[ "$(line_of "${want%% *}")" == *"${want#* }"* ]] || missing+=("#$want")
done
expect_nothing_missing "a run shows its state: running, done with its PR url, bailed with phase and classification, or stale"

finished="$(repo finished)"
now="$(date +%s)"
run="$(launched_run "$finished" 15 $((now - 40)))"
printf '{"ts": %s, "issue": "15", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "launch", "attempt": "2", "skill_commit": "abc", "name": "develop-red"}\n' \
  "$((now - 30))" >> "$run/.tdd/events.jsonl"
printf '{"ts": %s, "issue": "15", "actor": "conductor", "phase": "", "step": "", "event": "done", "attempt": "", "skill_commit": "abc", "pr": "https://github.com/o/r/pull/15"}\n' \
  "$((now - 20))" >> "$run/.tdd/events.jsonl"
run_in "$finished"
missing=()
[[ "$out" == *"attempt 2 "* ]] || missing+=("attempt 2")
expect_nothing_missing "a finished run's line reports its last step's attempt count, not attempt 0, when the done event carries an empty step"

stop_mark() {  # stop_mark <run> <n> <ts>
  printf '{"ts": %s, "issue": "%s", "actor": "conductor", "phase": "", "step": "a lamp glows", "event": "stop", "attempt": "", "skill_commit": "abc", "mode": "at-leaf", "at": "planned"}\n' \
    "$3" "$2" >> "$1/.tdd/events.jsonl"
}

paused="$(repo paused)"
now="$(date +%s)"
run="$(launched_run "$paused" 16 $((now - 20)))"
stop_mark "$run" 16 "$((now - 10))"
missing=()
run_in "$paused"
[[ "$out" == *"stopped at-leaf"* ]] || missing+=("stopped at-leaf")
run_in "$paused" --json
stopped="$(printf '%s' "$out" | python3 -c '
import json, sys
try:
    run = json.loads(sys.stdin.read())["runs"][0]
    print("%s %s" % (run["state"], run.get("stop_mode", "(no stop_mode)")))
except (ValueError, KeyError, IndexError, TypeError) as err:
    print("no run with a state: %r" % err)
')"
[[ "$stopped" == "stopped at-leaf" ]] || missing+=("--json state and stop_mode \"stopped at-leaf\", got: $stopped")
expect_nothing_missing "a run whose log ends with a stop mark reads stopped <mode>, and --json reports state stopped with the mode in stop_mode"

resumed="$(repo resumed)"
now="$(date +%s)"
run="$(launched_run "$resumed" 17 $((now - 30)))"
stop_mark "$run" 17 "$((now - 20))"
printf '{"ts": %s, "issue": "17", "actor": "conductor", "phase": "", "step": "a lamp glows", "event": "resume", "attempt": "", "skill_commit": "abc"}\n' \
  "$((now - 10))" >> "$run/.tdd/events.jsonl"
missing=()
run_in "$resumed"
[[ "$out" == *"running"* ]] || missing+=("running, got: $out")
[[ "$out" != *"stopped"* ]] || missing+=("no stopped")
expect_nothing_missing "a resume mark after a stop mark makes the run read running again"

scoped="$(repo scoped)"
now="$(date +%s)"
scope_run() {  # scope_run <n> <launch ts> <usage ts> <dollars> -> path
  local dir
  dir="$(launched_run "$scoped" "$1" "$2")"
  printf '{"ts": %s, "issue": "%s", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "usage", "attempt": "1", "skill_commit": "abc", "total_cost_usd": "%s", "input_tokens": "10", "output_tokens": "0", "cache_read_input_tokens": "0", "cache_creation_input_tokens": "0"}\n' \
    "$3" "$1" "$4" >> "$dir/.tdd/events.jsonl"
  echo "$dir"
}
run="$(scope_run 21 $((now - 100)) $((now - 40)) 0.25)"
echo "$$" > "$run/.tdd/conductor.pid"
run="$(scope_run 22 $((now - 500)) $((now - 350)) 1.50)"
printf '{"ts": %s, "issue": "22", "actor": "conductor", "phase": "", "step": "", "event": "done", "attempt": "", "skill_commit": "abc", "pr": "https://github.com/o/r/pull/22"}\n' \
  "$((now - 300))" >> "$run/.tdd/events.jsonl"
run="$(scope_run 23 $((now - 1000)) $((now - 950)) 0.50)"
printf '{"ts": %s, "issue": "23", "actor": "conductor", "phase": "red", "step": "a lamp glows", "event": "bail", "attempt": "", "skill_commit": "abc", "cause": "stuck", "classification": "system"}\n' \
  "$((now - 900))" >> "$run/.tdd/events.jsonl"
gh_json="$work/scoped-gh"
mkdir -p "$gh_json"
echo '[]' > "$gh_json/issues.json"
echo '[]' > "$gh_json/prs.json"
lamps_scope_line() { printf '%s\n' "$out" | grep 'lamps-label' || true; }
expect_lamps_totals() {  # expect_lamps_totals <case name>; reads $out, $code
  local scope_line want
  scope_line="$(lamps_scope_line)"
  missing=()
  for want in "scope lamps-label" "attempted 3" "done 1" "bailed 1" "wall 360s" '$2.25'; do
    [[ "$scope_line" == *"$want"* ]] || missing+=("$want")
  done
  expect_nothing_missing "$1"
}
VERI_GH_JSON="$gh_json" VERI_TIMEOUT=600 run_in "$scoped" --scope lamps-label
expect_lamps_totals "--scope <name> adds the scope's totals: issues attempted, done, bailed, total wall time and dollars"

VERI_GH_JSON="$gh_json" VERI_TIMEOUT=600 VERI_LABEL=lamps-label run_in "$scoped"
expect_lamps_totals "with no --scope, VERI_LABEL names the scope and adds the same totals line"

solvable_gh="$work/solvable-gh"
mkdir -p "$solvable_gh"
cat > "$solvable_gh/issues.json" <<'JSON'
[
  {"number": 31, "title": "a lamp dims", "labels": [{"name": "lamps-label"}], "state": "OPEN", "body": "## Blocked by\n\nNone.\n"},
  {"number": 32, "title": "a lamp flickers", "labels": [{"name": "lamps-label"}], "state": "OPEN", "body": "## Blocked by\n\nNone.\n"},
  {"number": 33, "title": "a gear slips", "labels": [{"name": "other-label"}], "state": "OPEN", "body": "## Blocked by\n\nNone.\n"}
]
JSON
echo '[]' > "$solvable_gh/prs.json"
VERI_GH_JSON="$solvable_gh" VERI_TIMEOUT=600 run_in "$scoped" --scope lamps-label
missing=()
[[ "$(lamps_scope_line)" == *"solvable 2"* ]] || missing+=("solvable 2")
expect_nothing_missing "--scope <name> totals include the count still solvable, from solvable-issues.sh for that scope"

VERI_GH_JSON="$solvable_gh" VERI_TIMEOUT=600 run_in "$scoped" --json --scope lamps-label
missing=()
while IFS= read -r want; do
  [[ -n "$want" ]] && missing+=("$want")
done < <(printf '%s' "$out" | python3 -c '
import json, sys
wanted = ["21", "22", "23", "lamps glow", "tdd/21-lamps", "tdd/22-lamps", "tdd/23-lamps",
          "https://github.com/o/r/pull/22", "system", "lamps-label", "360", "2.25", "2"]
try:
    doc = json.loads(sys.stdin.read())
except ValueError:
    print("one JSON document")
    sys.exit()
leaves = set()
def walk(node):
    if isinstance(node, dict):
        for value in node.values():
            walk(value)
    elif isinstance(node, list):
        for value in node:
            walk(value)
    elif isinstance(node, float) and node.is_integer():
        leaves.add(str(int(node)))
    else:
        leaves.add(str(node))
walk(doc)
for want in wanted:
    if want not in leaves:
        print(want)
')
expect_nothing_missing "--json emits the same per-run and scope data as one JSON document"

VERI_GH_JSON="$solvable_gh" VERI_TIMEOUT=600 run_in "$scoped" --json --scope lamps-label
solvable="$(printf '%s' "$out" | python3 -c '
import json, sys
try:
    print(repr(json.loads(sys.stdin.read())["scope"]["solvable"]))
except (ValueError, KeyError, TypeError) as err:
    print("no scope.solvable: %r" % err)
')"
if [[ "$solvable" == "2" && "$code" -eq 0 ]]; then ok; else
  no "--json emits scope.solvable as a JSON number, like every other numeric field"
  diff <(printf '2\nexit 0\n') <(printf '%s\nexit %s\n' "$solvable" "$code")
fi

broken_gh="$work/broken-gh"
mkdir -p "$broken_gh"
echo 'not json' > "$broken_gh/issues.json"
echo '[]' > "$broken_gh/prs.json"
missing=()
VERI_GH_JSON="$broken_gh" VERI_TIMEOUT=600 run_in "$scoped" --scope lamps-label
text_out="$out" text_code="$code"
[[ "$(lamps_scope_line)" == *"solvable ?"* ]] || missing+=("solvable ?")
VERI_GH_JSON="$broken_gh" VERI_TIMEOUT=600 run_in "$scoped" --json --scope lamps-label
solvable="$(printf '%s' "$out" | python3 -c '
import json, sys
try:
    print(json.dumps(json.loads(sys.stdin.read())["scope"]["solvable"]))
except (ValueError, KeyError, TypeError) as err:
    print("no scope.solvable: %r" % err)
')"
[[ "$solvable" == '"?"' ]] || missing+=('"solvable": "?"')
out="$text_out"$'\n'"$out"
[[ "$text_code" -eq 0 ]] || code="$text_code"
expect_nothing_missing "solvable-issues.sh exiting other than 0 or 3 renders the solvable count as ?, in text and JSON"

VERI_TIMEOUT=600 run_in "$states" --json
phases="$(printf '%s' "$out" | python3 -c '
import json, sys
try:
    run = [r for r in json.loads(sys.stdin.read())["runs"] if r["issue"] == "13"][0]
    print("phase=%s bail_phase=%s" % (run["phase"], run["bail_phase"]))
except (ValueError, KeyError, TypeError, IndexError) as err:
    print("no run #13 with phase and bail_phase: %r" % err)
')"
if [[ "$phases" == "phase=red bail_phase=green" && "$code" -eq 0 ]]; then ok; else
  no "--json reports bail_phase from the bail event's own phase, not the last launch's"
  diff <(printf 'phase=red bail_phase=green\nexit 0\n') <(printf '%s\nexit %s\n' "$phases" "$code")
fi

# --- a run directory's own ledger is its run, not every committed ledger beside it (#343) ---
own="$(repo own)"
run="$(fabricate_run "$own" 7 tdd/7-widgets-spin)"
cat > "$run/.tdd/issue-7.md" <<'EOF'
# Plan for #7 — widgets spin when clicked

- [ ] a widget exists
EOF
cat > "$run/.tdd/issue-3.md" <<'EOF'
# Plan for #3 — gears turn

- [ ] a gear exists
EOF
cat > "$run/.tdd/issue-5.md" <<'EOF'
# Plan for #5 — lamps glow

- [ ] a lamp exists
EOF
missing=()
run_in "$own"
lines="$(printf '%s\n' "$out" | grep -c '^#' || true)"
[[ "$lines" == "1" ]] || missing+=("exactly one run line, got $lines")
[[ "$out" == *"#7"* ]] || missing+=("#7")
[[ "$out" != *"#3"* ]] || missing+=("no line for #3")
[[ "$out" != *"#5"* ]] || missing+=("no line for #5")
run_in "$own" --json
issues="$(printf '%s' "$out" | python3 -c '
import json, sys
try:
    print(" ".join(r["issue"] for r in json.loads(sys.stdin.read())["runs"]))
except (ValueError, KeyError, TypeError) as err:
    print("no runs: %r" % err)
')"
[[ "$issues" == "7" ]] || missing+=("--json runs exactly [7], got: $issues")
expect_nothing_missing "a run directory is one run, its own issue's ledger, not every committed ledger beside it"

pair="$(repo pair)"
pair_run() {  # pair_run <n> <dollars> -> path; own ledger, two committed ones beside it, one usage line
  local dir other
  dir="$(fabricate_run "$pair" "$1" "tdd/$1-lamps")"
  for other in "$1" 4 "$2"; do
    printf '# Plan for #%s — lamps glow\n\n- [ ] a lamp glows\n' "$other" > "$dir/.tdd/issue-$other.md"
  done
  printf '{"ts": %s, "issue": "%s", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}\n' \
    "$(date +%s)" "$1" > "$dir/.tdd/events.jsonl"
  printf '{"ts": %s, "issue": "%s", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "usage", "attempt": "1", "skill_commit": "abc", "total_cost_usd": "%s", "input_tokens": "10", "output_tokens": "0", "cache_read_input_tokens": "0", "cache_creation_input_tokens": "0"}\n' \
    "$(date +%s)" "$1" "$3" >> "$dir/.tdd/events.jsonl"
  echo "$dir"
}
pair_run 7 9 0.25 > /dev/null
pair_run 9 7 1.50 > /dev/null
run_in "$pair" --json
pairs="$(printf '%s' "$out" | python3 -c '
import json, sys
try:
    runs = json.loads(sys.stdin.read())["runs"]
    print(" ".join(sorted("%s=%.2f" % (r["issue"], r["dollars"]) for r in runs)))
except (ValueError, KeyError, TypeError) as err:
    print("no runs with issue and dollars: %r" % err)
')"
if [[ "$pairs" == "7=0.25 9=1.50" && "$code" -eq 0 ]]; then ok; else
  no "two run directories each holding the other's committed ledger print exactly two runs, each with only its own directory's totals"
  diff <(printf '7=0.25 9=1.50\nexit 0\n') <(printf '%s\nexit %s\n' "$pairs" "$code")
fi

unborn="$(repo unborn)"
run="$(fabricate_run "$unborn" 8 tdd/8-lamps-glow)"
cat > "$run/.tdd/issue-3.md" <<'EOF'
# Plan for #3 — gears turn

- [ ] a gear exists
EOF
cat > "$run/.tdd/issue-5.md" <<'EOF'
# Plan for #5 — lamps glow

- [ ] a lamp exists
EOF
missing=()
run_in "$unborn"
lines="$(printf '%s\n' "$out" | grep -c '^#' || true)"
[[ "$lines" == "0" ]] || missing+=("no run line, got $lines")
run_in "$unborn" --json
issues="$(printf '%s' "$out" | python3 -c '
import json, sys
try:
    print(" ".join(r["issue"] for r in json.loads(sys.stdin.read())["runs"]) or "(none)")
except (ValueError, KeyError, TypeError) as err:
    print("no runs array: %r" % err)
')"
[[ "$issues" == "(none)" ]] || missing+=("--json runs empty, got: $issues")
expect_nothing_missing "a run directory with no ledger of its own contributes no run and is not an error"

watched="$(repo watched)"
now="$(date +%s)"
run="$(launched_run "$watched" 41 $((now - 10)))"
echo "$$" > "$run/.tdd/conductor.pid"
watch_out="$work/watch.out"
(cd "$watched" && exec "$STATUS" --watch 0 > "$watch_out" 2>/dev/null) &
watch_pid=$!
wait_for() {  # wait_for <text>; polls $watch_out for up to 5 s
  local i
  for i in $(seq 50); do
    grep -q -- "$1" "$watch_out" 2>/dev/null && return 0
    sleep 0.1
  done
  return 1
}
missing=()
wait_for "#41" || missing+=("a first render listing #41")
printf '{"ts": %s, "issue": "41", "actor": "conductor", "phase": "", "step": "", "event": "done", "attempt": "", "skill_commit": "abc", "pr": "https://github.com/o/r/pull/41"}\n' \
  "$(date +%s)" >> "$run/.tdd/events.jsonl"
wait_for "done https://github.com/o/r/pull/41" || true
kill -0 "$watch_pid" 2>/dev/null || missing+=("still watching after its first render")
kill "$watch_pid" 2>/dev/null
wait "$watch_pid" 2>/dev/null
out="$(cat "$watch_out")"
code=0
[[ "$out" == *$'\e['* || "$out" == *$'\ec'* ]] || missing+=("a redraw-in-place escape")
[[ "$out" == *"done https://github.com/o/r/pull/41"* ]] || missing+=("#41 done after its event log changed")
expect_nothing_missing "--watch [seconds] redraws in place, recomputing every run from disk on each render"

counted="$(repo counted)"
run="$(fabricate_run "$counted" 31 tdd/31-lamps)"
printf '# Plan for #31 — lamps glow\n\n- [ ] a lamp glows\n' > "$run/.tdd/issue-31.md"
stub="$work/stub"
mkdir -p "$stub"
cp "$STATUS" "$stub/status.sh"
cp -R "$HERE/../lib" "$stub/lib"
cat > "$stub/lib/ledger.sh" <<'EOF'
ledger_steps() {
  cat >/dev/null
  printf '1\tdone\tstep\t0\t0\t\ta lamp exists\n'
  printf '2\topen\tstep\t0\t0\t\ta lamp glows\n'
  printf '3\topen\tstep\t0\t0\t\ta lamp dims\n'
}
EOF
STATUS="$stub/status.sh" run_in "$counted"
missing=()
[[ "$out" == *"step 2 of 3"* ]] || missing+=("step 2 of 3")
expect_nothing_missing "finds the step through lib/ledger.sh's ledger_steps, counting no checkbox of its own"

finish

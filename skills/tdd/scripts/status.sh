#!/usr/bin/env bash
# status.sh — render every veri run under the repository's main working tree.
#
# Runs are discovered from `.tdd/wt/*` under the MAIN working tree, resolved through
# lib/main-working-tree.sh (#166), never the checkout this script was called from.
#
# Usage:   status.sh [--json] [--scope <name>] [--watch [seconds]]   (no --scope: VERI_LABEL, when set, names the scope)
#          --json prints the same runs and scope totals as one JSON document.
#          --watch redraws in place every <seconds> (default 2), each render a fresh run of this
#          script without --watch, so everything is recomputed from disk and nothing is kept.
# Exit:    0 one or more runs printed; 3 nothing to do — "no runs"
set -euo pipefail

lib="$(dirname "$0")/lib"
# shellcheck source=lib/main-working-tree.sh
source "$lib/main-working-tree.sh"

# Step n is the first unticked step; m is every step the ledger has.
ledger_step() {  # ledger_step <ledger> -> "<n> of <m>"
  local line total=0 step=0
  while IFS= read -r line; do
    case "$line" in
      "- [x] "*) total=$((total + 1)) ;;
      "- [ ] "*) total=$((total + 1)); [[ "$step" -eq 0 ]] && step="$total" ;;
    esac
  done < "$1"
  [[ "$step" -eq 0 ]] && step="$total"
  printf '%s of %s\n' "$step" "$total"
}

# The latest leaf launch in the event log, how many launches the current step has had, and the
# run's cost so far: every `usage` line's dollars and its four token kinds, summed — and the
# run's state. A `done` or `bail` event ends a run and a `stop` event reads `stopped <mode>`;
# otherwise it is stale when its newest event is older than <timeout> seconds and
# <conductor.pid> does not answer `kill -0`, else running.
# With STATUS_JSON=1 the same fields print as one JSON object instead.
run_activity() {  # run_activity <events.jsonl> <conductor.pid> <timeout> -> "<phase>  <actor>  <leaf> <n>s  attempt <k>  $<d>  <t> tokens  <state>"
  PYTHONPATH="$lib" python3 - "$1" "$2" "$3" <<'PY'
import json, os, sys, time
from event_log import read_events, usage_totals
last, attempts = None, 0
newest, ended = None, None
events = read_events(sys.argv[1])
dollars, tokens = usage_totals(events)
for line in events:
    newest = line
    if line.get("event") == "launch":
        if line.get("step") != (last or {}).get("step"):
            attempts = 0
        last = line
        attempts += 1
    elif line.get("event") in ("done", "bail", "stop"):
        ended = line


def conductor_answers(pid_file):
    try:
        with open(pid_file) as f:
            os.kill(int(f.read().strip()), 0)
        return True
    except (OSError, ValueError):
        return False


now = int(time.time())
if ended is not None and ended.get("event") == "done":
    state = "done %s" % ended.get("pr", "")
elif ended is not None and ended.get("event") == "stop":
    state = "stopped %s" % ended.get("mode", "")
elif ended is not None:
    state = "bailed %s %s" % (ended.get("phase", ""), ended.get("classification", ""))
elif newest is not None and now - int(newest["ts"]) > int(sys.argv[3]) \
        and not conductor_answers(sys.argv[2]):
    state = "stale"
else:
    state = "running"
if last is None:
    sys.exit()
if os.environ.get("STATUS_JSON") == "1":
    end = ended or {}
    print(json.dumps({"phase": last.get("phase", ""), "actor": last.get("actor", ""),
                      "leaf": last.get("name", ""), "elapsed_seconds": now - int(last["ts"]),
                      "attempts": attempts, "dollars": round(dollars, 2), "tokens": tokens,
                      "state": state.split(" ")[0], "pr": end.get("pr", ""),
                      "bail_phase": end.get("phase", ""),
                      "classification": end.get("classification", ""),
                      "stop_mode": end.get("mode", "")}))
else:
    print("%s  %s  %s %ds  attempt %d  $%.2f  %d tokens  %s" % (last.get("phase", ""),
          last.get("actor", ""), last.get("name", ""), now - int(last["ts"]),
          attempts, dollars, tokens, state))
PY
}

# A scope's totals over every run's event log: runs attempted, how many ended done and how many
# bailed, wall time as each run's first-to-last event span summed, and every usage line's dollars.
# The solvable count is solvable_count's, passed in. With STATUS_JSON=1 the same totals print
# as one JSON object instead, the count a number like the rest.
scope_totals() {  # scope_totals <name> <solvable> <events.jsonl>... -> "scope <name>  attempted <a>  done <d>  bailed <b>  wall <w>s  $<x>  solvable <s>"
  PYTHONPATH="$lib" python3 - "$@" <<'PY'
import json, os, sys
from event_log import read_events, usage_totals
solvable = sys.argv[2]
attempted = done = bailed = wall = 0
dollars = 0.0
for path in sys.argv[3:]:
    attempted += 1
    events = read_events(path)
    dollars += usage_totals(events)[0]
    done += sum(1 for line in events if line.get("event") == "done")
    bailed += sum(1 for line in events if line.get("event") == "bail")
    if events:
        wall += int(events[-1]["ts"]) - int(events[0]["ts"])
if os.environ.get("STATUS_JSON") == "1":
    print(json.dumps({"name": sys.argv[1], "attempted": attempted, "done": done,
                      "bailed": bailed, "wall_seconds": wall, "dollars": round(dollars, 2),
                      "solvable": int(solvable) if solvable.isdigit() else solvable}))
    sys.exit()
print("scope %s  attempted %d  done %d  bailed %d  wall %ds  $%.2f  solvable %s"
      % (sys.argv[1], attempted, done, bailed, wall, dollars, solvable))
PY
}

# The count still solvable is solvable-issues.sh's for the scope's label, so the same four
# conditions; its exit 3 (nothing takeable) is a count of 0, and any other failure is no answer.
solvable_count() {  # solvable_count <name> -> "<count>", or "?" when solvable-issues.sh gave no answer
  local listed code=0
  listed="$(VERI_LABEL="$1" "$(dirname "$0")/solvable-issues.sh")" || code=$?
  case "$code" in
    0) printf '%s\n' "$listed" | grep -c . ;;
    3) echo 0 ;;
    *) echo "?" ;;
  esac
}

scope="${VERI_LABEL:-}"
json=0
watch=""
render_args=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --watch)
      watch=2; shift
      if [[ "${1:-}" =~ ^[0-9]+$ ]]; then watch="$1"; shift; fi ;;
    --json) json=1; render_args+=("$1"); shift ;;
    --scope) scope="${2:-}"; render_args+=("$1" "$scope"); shift $(( $# > 1 ? 2 : 1 )) ;;
    *) render_args+=("$1"); shift ;;
  esac
done

if [[ -n "$watch" ]]; then
  while :; do
    # ESC[H moves the cursor home and ESC[2J clears the screen, so each render replaces the last.
    rendered="$("$0" ${render_args[@]+"${render_args[@]}"})" || true
    printf '\033[H\033[2J%s\n' "$rendered"
    sleep "$watch"
  done
fi
export STATUS_JSON="$json"

timeout="${VERI_TIMEOUT:-900}"
main_tree="$(main_working_tree)"

shopt -s nullglob
runs=()
if [[ -n "$main_tree" ]]; then
  runs=("$main_tree"/.tdd/wt/*/)
fi

if [[ ${#runs[@]} -eq 0 ]]; then
  echo "no runs"
  exit 3
fi

events=()
run_objects=()
for run in "${runs[@]}"; do
  run="${run%/}"
  branch="$(git -C "$run" symbolic-ref --short HEAD 2>/dev/null || true)"
  activity=""
  if [[ -f "$run/.tdd/events.jsonl" ]]; then
    events+=("$run/.tdd/events.jsonl")
    activity="$(run_activity "$run/.tdd/events.jsonl" "$run/.tdd/conductor.pid" "$timeout")"
    [[ "$json" -eq 1 ]] || activity="  $activity"
  fi
  # A run directory is .tdd/wt/<n>/, so its own ledger is issue-<n>.md. Every other
  # issue-*.md beside it is an earlier issue's committed plan, not a run of this tree.
  ledger="$run/.tdd/issue-${run##*/}.md"
  [[ -f "$ledger" ]] || continue
  # The heading is `# Plan for #<n> — <title>`.
  heading="$(head -n 1 "$ledger")"
  heading="${heading#\# Plan for #}"
  issue="${heading%% — *}"
  title="${heading#* — }"
  step="$(ledger_step "$ledger")"
  if [[ "$json" -eq 1 ]]; then
    # One object per run: the ledger's fields, merged with run_activity's object when there is one.
    run_objects+=("$(python3 -c '
import json, sys
run = {"issue": sys.argv[1], "title": sys.argv[2], "branch": sys.argv[3], "step": sys.argv[4]}
run.update(json.loads(sys.argv[5]) if sys.argv[5] else {})
print(json.dumps(run))' "$issue" "$title" "$branch" "$step" "$activity")")
    continue
  fi
  printf '#%s  %s  %s  step %s%s\n' "$issue" "$title" "$branch" "$step" "$activity"
done

if [[ "$json" -eq 1 ]]; then
  scope_object="null"
  if [[ -n "$scope" ]]; then
    scope_object="$(scope_totals "$scope" "$(solvable_count "$scope")" ${events[@]+"${events[@]}"})"
  fi
  runs_array="$(IFS=,; printf '%s' "${run_objects[*]:-}")"
  printf '{"runs": [%s], "scope": %s}\n' "$runs_array" "$scope_object"
  exit 0
fi

if [[ -n "$scope" ]]; then
  scope_totals "$scope" "$(solvable_count "$scope")" ${events[@]+"${events[@]}"}
fi

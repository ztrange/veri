#!/usr/bin/env bash
# status.sh — render every veri run under the repository's main working tree.
#
# Runs are discovered from `.tdd/wt/*` under the MAIN working tree, resolved through
# lib/main-working-tree.sh, never the checkout this script was called from.
#
# Usage:   status.sh [--json] [--scope <name>] [--watch [seconds]]   (no --scope: VERI_LABEL, when set, names the scope)
#          --json prints the same runs and scope totals as one JSON document.
#          --watch redraws in place every <seconds> (default 2), each render a fresh run of this
#          script without --watch, so everything is recomputed from disk and nothing is kept.
# Exit:    0 one or more runs printed; 3 nothing to do — "no runs"
set -euo pipefail

lib="$(dirname "$0")/lib"
source "$lib/main-working-tree.sh"
[[ ! -f "$lib/ledger.sh" ]] || source "$lib/ledger.sh"

step_of_total() {  # step_of_total <ledger> -> "<n> of <m>"
  local index state rest total=0 step=0
  while IFS=$'\t' read -r index state rest; do
    total="$index"
    [[ "$state" == open && "$step" -eq 0 ]] && step="$index"
  done < <(ledger_steps < "$1")
  [[ "$step" -eq 0 ]] && step="$total"
  printf '%s of %s\n' "$step" "$total"
}

run_activity() {  # run_activity <events.jsonl> <conductor.pid> <timeout> -> "<phase>  <actor>  <leaf> <n>s  attempt <k>  $<d>  <t> tokens  <state>"
  PYTHONPATH="$lib" python3 - "$1" "$2" "$3" <<'PY'
import json, os, sys, time
from event_log import read_events, usage_totals
last, attempts = None, 0
newest, end = None, {}
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
        end = line
    elif line.get("event") == "resume":
        end = {}


def conductor_answers(pid_file):
    try:
        with open(pid_file) as f:
            os.kill(int(f.read().strip()), 0)
        return True
    except (OSError, ValueError):
        return False


now = int(time.time())
if end.get("event") == "done":
    state = "done %s" % end.get("pr", "")
elif end.get("event") == "stop":
    state = "stopped %s" % end.get("mode", "")
elif end.get("event") == "bail":
    state = "bailed %s %s" % (end.get("phase", ""), end.get("classification", ""))
elif newest is not None and now - int(newest["ts"]) > int(sys.argv[3]) \
        and not conductor_answers(sys.argv[2]):
    state = "stale"
else:
    state = "running"
if last is None:
    sys.exit()
if os.environ.get("STATUS_JSON") == "1":
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
  ledger="$run/.tdd/issue-${run##*/}.md"
  [[ -f "$ledger" ]] || continue
  heading="$(head -n 1 "$ledger")"
  heading="${heading#\# Plan for #}"
  issue="${heading%% — *}"
  title="${heading#* — }"
  step="$(step_of_total "$ledger")"
  if [[ "$json" -eq 1 ]]; then
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

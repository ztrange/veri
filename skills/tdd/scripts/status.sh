#!/usr/bin/env bash
# status.sh — render every veri run under the repository's main working tree.
#
# Runs are discovered from `.tdd/wt/*` under the MAIN working tree, resolved the way
# solvable-issues.sh resolves it (#166): the first `worktree <path>` line of git's registry,
# never the checkout this script was called from.
#
# Usage:   status.sh [--scope <name>]
# Exit:    0 one or more runs printed; 3 nothing to do — "no runs"
set -euo pipefail

main_working_tree() {
  local first_line
  first_line="$(git worktree list --porcelain 2>/dev/null | head -n 1 || true)"
  printf '%s\n' "${first_line#worktree }"
}

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
# run's state. A `done` or `bail` event ends a run; otherwise it is stale when its newest event
# is older than <timeout> seconds and <conductor.pid> does not answer `kill -0`, else running.
run_activity() {  # run_activity <events.jsonl> <conductor.pid> <timeout> -> "<phase>  <actor>  <leaf> <n>s  attempt <k>  $<d>  <t> tokens  <state>"
  python3 - "$1" "$2" "$3" <<'PY'
import json, os, sys, time
last, attempts, step = None, 0, None
newest, ended = None, None
dollars, tokens = 0.0, 0
TOKEN_KINDS = ("input_tokens", "output_tokens", "cache_read_input_tokens",
               "cache_creation_input_tokens")
with open(sys.argv[1]) as f:
    for raw in f:
        raw = raw.strip()
        if not raw:
            continue
        line = json.loads(raw)
        newest = line
        if line.get("step") != step:
            step, attempts = line.get("step"), 0
        if line.get("event") == "launch":
            last = line
            attempts += 1
        elif line.get("event") == "usage":
            dollars += float(line.get("total_cost_usd") or 0)
            tokens += sum(int(line.get(kind) or 0) for kind in TOKEN_KINDS)
        elif line.get("event") in ("done", "bail"):
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
elif ended is not None:
    state = "bailed %s %s" % (ended.get("phase", ""), ended.get("classification", ""))
elif newest is not None and now - int(newest["ts"]) > int(sys.argv[3]) \
        and not conductor_answers(sys.argv[2]):
    state = "stale"
else:
    state = "running"
if last is not None:
    print("%s  %s  %s %ds  attempt %d  $%.2f  %d tokens  %s" % (last.get("phase", ""),
          last.get("actor", ""), last.get("name", ""), now - int(last["ts"]),
          attempts, dollars, tokens, state))
PY
}

# A scope's totals over every run's event log: runs attempted, how many ended done and how many
# bailed, wall time as each run's first-to-last event span summed, and every usage line's dollars.
scope_totals() {  # scope_totals <name> <events.jsonl>... -> "scope <name>  attempted <a>  done <d>  bailed <b>  wall <w>s  $<x>"
  python3 - "$@" <<'PY'
import json, sys
attempted = done = bailed = wall = 0
dollars = 0.0
for path in sys.argv[2:]:
    attempted += 1
    first = last = None
    with open(path) as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            line = json.loads(raw)
            first = line if first is None else first
            last = line
            if line.get("event") == "usage":
                dollars += float(line.get("total_cost_usd") or 0)
            elif line.get("event") == "done":
                done += 1
            elif line.get("event") == "bail":
                bailed += 1
    if first is not None:
        wall += int(last["ts"]) - int(first["ts"])
print("scope %s  attempted %d  done %d  bailed %d  wall %ds  $%.2f"
      % (sys.argv[1], attempted, done, bailed, wall, dollars))
PY
}

scope=""
if [[ "${1:-}" == "--scope" ]]; then
  scope="${2:-}"
fi

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

for run in "${runs[@]}"; do
  run="${run%/}"
  branch="$(git -C "$run" symbolic-ref --short HEAD 2>/dev/null || true)"
  activity=""
  [[ -f "$run/.tdd/events.jsonl" ]] && activity="  $(run_activity "$run/.tdd/events.jsonl" "$run/.tdd/conductor.pid" "$timeout")"
  for ledger in "$run"/.tdd/issue-*.md; do
    # The heading is `# Plan for #<n> — <title>`.
    heading="$(head -n 1 "$ledger")"
    heading="${heading#\# Plan for #}"
    issue="${heading%% — *}"
    title="${heading#* — }"
    printf '#%s  %s  %s  step %s%s\n' "$issue" "$title" "$branch" "$(ledger_step "$ledger")" "$activity"
  done
done

if [[ -n "$scope" ]]; then
  events=()
  for run in "${runs[@]}"; do
    [[ -f "${run%/}/.tdd/events.jsonl" ]] && events+=("${run%/}/.tdd/events.jsonl")
  done
  scope_totals "$scope" ${events[@]+"${events[@]}"}
fi

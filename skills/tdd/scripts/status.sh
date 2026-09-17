#!/usr/bin/env bash
# status.sh — render every veri run under the repository's main working tree.
#
# Runs are discovered from `.tdd/wt/*` under the MAIN working tree, resolved the way
# solvable-issues.sh resolves it (#166): the first `worktree <path>` line of git's registry,
# never the checkout this script was called from.
#
# Usage:   status.sh
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

# The latest leaf launch in the event log, and how many launches the current step has had.
leaf_now() {  # leaf_now <events.jsonl> -> "<phase>  <actor>  <leaf> <n>s  attempt <k>"
  python3 - "$1" <<'PY'
import json, sys, time
last, attempts, step = None, 0, None
with open(sys.argv[1]) as f:
    for raw in f:
        raw = raw.strip()
        if not raw:
            continue
        line = json.loads(raw)
        if line.get("step") != step:
            step, attempts = line.get("step"), 0
        if line.get("event") == "launch":
            last = line
            attempts += 1
if last is not None:
    print("%s  %s  %s %ds  attempt %d" % (last.get("phase", ""), last.get("actor", ""),
          last.get("name", ""), int(time.time()) - int(last["ts"]), attempts))
PY
}

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
  leaf=""
  [[ -f "$run/.tdd/events.jsonl" ]] && leaf="  $(leaf_now "$run/.tdd/events.jsonl")"
  for ledger in "$run"/.tdd/issue-*.md; do
    # The heading is `# Plan for #<n> — <title>`.
    heading="$(head -n 1 "$ledger")"
    heading="${heading#\# Plan for #}"
    issue="${heading%% — *}"
    title="${heading#* — }"
    printf '#%s  %s  %s  step %s%s\n' "$issue" "$title" "$branch" "$(ledger_step "$ledger")" "$leaf"
  done
done

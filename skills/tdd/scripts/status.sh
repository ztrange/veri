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
  for ledger in "$run"/.tdd/issue-*.md; do
    # The heading is `# Plan for #<n> — <title>`.
    heading="$(head -n 1 "$ledger")"
    heading="${heading#\# Plan for #}"
    issue="${heading%% — *}"
    title="${heading#* — }"
    branch="$(git -C "$run" symbolic-ref --short HEAD 2>/dev/null || true)"
    # Step n is the first unticked step; m is every step the ledger has.
    total=0 step=0
    while IFS= read -r line; do
      case "$line" in
        "- [x] "*) total=$((total + 1)) ;;
        "- [ ] "*) total=$((total + 1)); [[ "$step" -eq 0 ]] && step="$total" ;;
      esac
    done < "$ledger"
    [[ "$step" -eq 0 ]] && step="$total"
    printf '#%s  %s  %s  step %s of %s\n' "$issue" "$title" "$branch" "$step" "$total"
  done
done

#!/usr/bin/env bash
# preserve-attempt.sh <issue> <step> <phase> <attempt> — snapshot the worktree as it stands
# to refs/veri/attempts/<issue>/<step>/<phase>-<attempt>.
#
# What a reader of a troubled step wants is the tree the leaf produced — the rejected file —
# and a rejected file is never committed to the work branch: a green commit lands only after
# verify-green PASSes. So it goes to a side ref, which git keeps, `git log` on the branch
# never shows, and a rebase-merge never carries.
#
# The snapshot is taken through a temporary index rather than the repository's own, so a
# leaf's staged-or-not state is left exactly as it was: this script reads the worktree and
# writes an object, and touches neither the index nor the branch.
#
# A fifth argument, the mark that made the step interesting (reject, bail, no-verdict,
# stuck, prediction-diverged), additionally preserves the leaf's own output — see the copy
# step at the foot of this script.
#
# Usage:   preserve-attempt.sh 409 3 develop-green 1 [<mark>]   # run from the issue's worktree
set -euo pipefail

[[ -n "${1:-}" && -n "${2:-}" && -n "${3:-}" && -n "${4:-}" ]] \
  || { echo "usage: preserve-attempt.sh <issue> <step> <phase> <attempt> [<mark>]" >&2; exit 2; }
issue="$1" step="$2" phase="$3" attempt="$4"
coords="issue $issue step $step $phase attempt $attempt"

cd "$(git rev-parse --show-toplevel)"
# hazard: git refuses an existing empty file as "index file smaller than expected", so the index is a path git creates.
scratch="$(mktemp -d)"
index="$scratch/index"
trap 'rm -rf "$scratch"' EXIT

GIT_INDEX_FILE="$index" git add -A
tree="$(GIT_INDEX_FILE="$index" git write-tree)"

ledger_step_index() {
  local ledger="$1" prose="$2"
  local box_re='^[[:space:]]*- \[[ xX]\] (.*)$'
  local line n=0
  [[ -f "$ledger" ]] || return 1
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ $box_re ]]; then
      n=$((n + 1))
      if [[ "${BASH_REMATCH[1]}" == *"$prose"* ]]; then LEDGER_STEP_INDEX="$n"; return 0; fi
    fi
  done < "$ledger"
  return 1
}

step_ref="$step"
if ledger_step_index ".tdd/issue-$issue.md" "$step"; then step_ref="$LEDGER_STEP_INDEX"; fi
step_ref="${step_ref//[^0-9A-Za-z-]/-}"

commit="$(git commit-tree "$tree" -p HEAD -m "attempt: $coords")"
ref="refs/veri/attempts/$issue/$step_ref/$phase-$attempt"
if ! git update-ref "$ref" "$commit"; then
  echo "preserve-attempt.sh: could not preserve $coords to $ref" >&2
  exit 1
fi

mark="${5:-}"
if [[ -n "$mark" ]]; then
  mkdir -p .tdd/attempts
  base=".tdd/attempts/$step_ref-$phase-$attempt-$mark"
  # hazard: `if`, not `[[ … ]] && cp`: under set -e a false test as the last command is the script's exit status.
  for ext in log out; do
    if [[ -f ".tdd/$phase.$ext" ]]; then cp ".tdd/$phase.$ext" "$base.$ext"; fi
  done
fi

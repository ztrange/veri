#!/usr/bin/env bash
# preserve-attempt.sh <issue> <step> <phase> <attempt> — snapshot the worktree as it stands
# to refs/veri/attempts/<issue>/<step>/<phase>-<attempt>.
#
# What a reader of a troubled step wants is the tree the leaf produced — the rejected file —
# and a rejected file is never committed to the work branch: a green commit lands only after
# verify-green PASSes. So it goes to a side ref, which git keeps, `git log` on the branch
# never shows, and a rebase-merge never carries (issue #409).
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
# The four coordinates as one phrase, because two readers have to agree on it: the preserved
# commit's own message and the failure line below. A reader of the run's .err pairs the one with
# the other by that text, so it is written once rather than kept in step by hand.
coords="issue $issue step $step $phase attempt $attempt"

# Every git command below runs from the top of the worktree rather than wherever the caller
# stood, so `git add -A` sees the whole tree on any git old enough to read a pathspec as
# relative to the cwd. One `cd` rather than a `-C "$top"` on each: the script runs in its own
# process, so the move is invisible to whoever called it.
cd "$(git rev-parse --show-toplevel)"
# A path git will create, not a file that already exists: an existing empty file is not an
# empty index, and git refuses it as "index file smaller than expected".
scratch="$(mktemp -d)"
index="$scratch/index"
trap 'rm -rf "$scratch"' EXIT

# An empty index plus `git add -A` is the whole worktree, tracked and untracked alike: nothing
# carries over from the repository's own index, so what the tree says is what is on disk.
GIT_INDEX_FILE="$index" git add -A
tree="$(GIT_INDEX_FILE="$index" git write-tree)"

# The ref name carries the step's INDEX in the committed ledger, never the step's own prose
# (issue #427): a plan step is a sentence with spaces, and often an apostrophe or a slash, none
# of which `git check-ref-format` accepts — so a ref built out of the title is no ref at all and
# `git update-ref` refuses it, which is why the snapshots this script promises had never been
# written. The ledger already numbers its steps by position, which is short, stable and legal.
# A substring match rather than equality, because a ticked step's line carries `⟂ refactor
# pending` after the prose the caller was handed.
#
# ledger_step_index <ledger> <prose> — when <ledger> holds a checkbox step whose text contains
# <prose>, sets LEDGER_STEP_INDEX to that step's 1-based position and returns 0; otherwise
# returns 1 and leaves LEDGER_STEP_INDEX alone, so a caller reads it only on a 0. A variable
# rather than stdout, the way lib/candidate-line.sh's `structural_candidate` answers: a value
# read back through `$(…)` is a fork per preservation for a line this shell already has.
# The reading is a function so the scan's own names — the grammar, the counter, the line —
# are `local` and never reach the rest of the script.
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

# The prose itself when the ledger cannot name the step — an absent ledger, or one no line of
# which carries what the caller was handed — which is what the callers passing an index
# already rely on. A title is a sentence, though, and `git check-ref-format` takes none of what
# a sentence is made of: a space ends the ref name, a slash starts a new path component, and an
# apostrophe is only legal by accident of what git forbids. So the fallback keeps the one class
# of character every git accepts — letters, digits and the dash — and writes every other byte
# as a dash, which is legible enough to recognise the step by and legal wherever it lands. A
# caller that passed an index, and the ledger lookup above, both come through it unchanged.
step_ref="$step"
if ledger_step_index ".tdd/issue-$issue.md" "$step"; then step_ref="$LEDGER_STEP_INDEX"; fi
step_ref="${step_ref//[^0-9A-Za-z-]/-}"

# HEAD as the parent so `git show` on the ref reads as the attempt's own diff rather than as
# every file in the repository.
commit="$(git commit-tree "$tree" -p HEAD -m "attempt: $coords")"
# A ref name derived as above is legal, but legal is not the same as writable: git also refuses
# a name whose path collides with a ref that is already there (`refs/veri/attempts/409/3` as a
# ref makes `.../409/3/develop-green-1` a file under a file). Preservation stays best-effort to
# every caller, so the one thing this script owes a reader of the run's .err is a line saying
# which attempt was lost — git's own fatal names a ref, not the attempt it belonged to, and the
# silence around it is exactly what let the prose-ref bug survive unnoticed (issue #427).
ref="refs/veri/attempts/$issue/$step_ref/$phase-$attempt"
if ! git update-ref "$ref" "$commit"; then
  echo "preserve-attempt.sh: could not preserve $coords to $ref" >&2
  exit 1
fi

# The tree is what a reader wants first, but it is not the whole record: the tree says what the
# leaf produced, and the leaf's own log is the only place what it *tried* survives. So when the
# caller names the mark that made the step interesting, the progress log and the final-output
# file are copied beside the ref under names carrying step, phase, attempt and that mark — the
# pairing a reader needs to line them up with the event in events.jsonl.
#
# A copy, not a move: run-leaf.sh's own `.tdd/<name>.log` and `.tdd/<name>.out` are what a retry
# reads back, so the leaf that wrote them must find them where it left them.
mark="${5:-}"
if [[ -n "$mark" ]]; then
  mkdir -p .tdd/attempts
  # `$step_ref`, not `$step`, for the same reason the ref above uses it (issue #427): this is a
  # path too, so a title carrying a slash names a directory nobody made, `cp` fails, and under
  # `set -e` the preservation reports a failure for a log that was sitting right there.
  base=".tdd/attempts/$step_ref-$phase-$attempt-$mark"
  # Each copy is conditional on its own source: a leaf killed before it wrote a final-output
  # file still has a log worth keeping, and a missing one is not a failure of preservation.
  # `if` rather than `[[ … ]] && cp`, because under `set -e` a false test as the script's last
  # command is the script's exit status: a missing .out would report a failed preservation.
  # The two files differ only in their extension, so the rule is written once and the list of
  # what run-leaf.sh leaves behind — the progress log and the final-output file — is the loop.
  for ext in log out; do
    if [[ -f ".tdd/$phase.$ext" ]]; then cp ".tdd/$phase.$ext" "$base.$ext"; fi
  done
fi

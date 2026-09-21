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
# Usage:   preserve-attempt.sh 409 3 develop-green 1     # run from the issue's worktree
set -euo pipefail

[[ -n "${1:-}" && -n "${2:-}" && -n "${3:-}" && -n "${4:-}" ]] \
  || { echo "usage: preserve-attempt.sh <issue> <step> <phase> <attempt>" >&2; exit 2; }
issue="$1" step="$2" phase="$3" attempt="$4"

top="$(git rev-parse --show-toplevel)"
# A path git will create, not a file that already exists: an existing empty file is not an
# empty index, and git refuses it as "index file smaller than expected".
scratch="$(mktemp -d)"
index="$scratch/index"
trap 'rm -rf "$scratch"' EXIT

# An empty index plus `git add -A` is the whole worktree, tracked and untracked alike: nothing
# carries over from the repository's own index, so what the tree says is what is on disk.
GIT_INDEX_FILE="$index" git -C "$top" add -A
tree="$(GIT_INDEX_FILE="$index" git -C "$top" write-tree)"

# HEAD as the parent so `git show` on the ref reads as the attempt's own diff rather than as
# every file in the repository.
commit="$(git -C "$top" commit-tree "$tree" -p HEAD \
  -m "attempt: issue $issue step $step $phase attempt $attempt")"
git -C "$top" update-ref "refs/veri/attempts/$issue/$step/$phase-$attempt" "$commit"

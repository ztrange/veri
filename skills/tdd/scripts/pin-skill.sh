#!/usr/bin/env bash
# pin-skill.sh — take the run's copy of the skill's `scripts/` once, at preflight, so that no
# later `$S/…` call can read a file the primary clone has changed underneath the run (#165).
#
# `~/.claude/skills/tdd` is a symlink into the primary clone, and the primary clone is not a
# fixed point: it stays on the default branch and the `merge` skill pulls it after every
# landing. A conductor that resolves `$S` into that checkout follows SKILL.md prose from
# commit A while launching leaves out of scripts from commit B — and a leaf can read a file
# git is halfway through rewriting.
#
# Usage:   pin-skill.sh          # no arguments, run from the run's worktree
# Output:  the absolute path of the snapshot's scripts directory on stdout, exit 0.
#
# A COPY, not a detached worktree of the skill commit. Both freeze the content; the copy
# takes no ref and no entry in the clone's worktree registry, so it cannot be pruned,
# collide with the worktree names issue-worktree.sh already manages, or need cleaning up
# when a run is abandoned — and it holds the skill's `prompts/` templates, which are half of
# what #165 is about, by the same one move.
set -euo pipefail

# The skill's own scripts directory — where this file is, not where the caller is. `cd … &&
# pwd -P` resolves the install symlink, so the source read below is the primary clone's real
# path rather than a link that could be re-pointed while the run is going.
src="$(cd "$(dirname "$0")" && pwd -P)"

# The run's own directory. Resolved the same way for the same reason `git worktree list`
# resolves the paths it prints: the caller compares the path we print against paths it
# derived itself, and on macOS an unresolved /var/… and a resolved /private/var/… name the
# same directory while comparing unequal.
run="$(pwd -P)"
dest="$run/.tdd/skill/scripts"
commit_file="$run/.tdd/skill-commit"

# A resume re-pins to the commit the run STARTED on, never to the clone's current HEAD — that
# is the whole point of writing the sha down. `.tdd/skill-commit` is the flag because it is
# written last, after the copy has finished: a run killed mid-copy leaves no sha, so the next
# call redoes the snapshot rather than handing back half of one.
if [[ -f "$commit_file" && -d "$dest" ]]; then
  printf '%s\n' "$dest"
  exit 0
fi

# `$src/.` rather than `$src`, so the contents land IN $dest whether or not it already exists
# — `cp -R a b` copies a to b when b is absent and to b/a when it is not, and the two shapes
# differ by exactly one abandoned half-snapshot.
mkdir -p "$dest"
cp -R "$src/." "$dest/"

# Asked of the skill's directory, not the run's: the two are different repositories here (the
# run is in a linked worktree of the target repo, the skill lives in whatever clone it was
# installed from), and the sha a reader needs is the one that says which scripts produced the
# run.
git -C "$src" rev-parse HEAD > "$commit_file"

printf '%s\n' "$dest"

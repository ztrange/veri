#!/usr/bin/env bash
# issue-worktree.sh — the linked git worktree an issue branch lives in.
#
# The conductor used to `git switch -c tdd/<n>-<slug>` in whatever checkout /solve-issue was
# invoked from, which drags that checkout off the default branch for the whole run: anything
# symlinked or served out of it (a user-level skill link, a dev server) silently starts seeing
# the issue branch. This creates a *linked worktree* instead — a second working directory that
# shares the one .git object store — and prints its absolute path, so the run can `cd` there
# and leave the caller's checkout exactly where it was.
#
# Usage:   issue-worktree.sh <n> <slug>
# Output:  the worktree's absolute path on stdout, exit 0.
set -euo pipefail

# ${1:?msg} — expand $1, but if it is unset or empty, die with msg on stderr instead of
# silently building a branch called `tdd/-`. The first argument carries the whole usage line
# and the rest just name themselves, which is how every other script here does it.
n="${1:?usage: issue-worktree.sh <n> <slug>}"
slug="${2:?missing <slug>}"

# --show-toplevel is the root of the checkout we were called from, with symlinks resolved
# (on macOS a /var/... path comes back as /private/var/...). Resolved is what we want: git
# reports worktree paths that way too, so the path we print matches what `git worktree list`
# will say about it.
root="$(git rev-parse --show-toplevel)"
branch="tdd/$n-$slug"
path="$root/.tdd/wt/$n"

# git's own registry of worktrees — asked once here, questioned twice below. `worktree list
# --porcelain` prints one block per registered worktree, blank-line separated: a
# `worktree <absolute-path>` line first, then `HEAD <sha>`, then `branch <full-ref>` (absent
# when that worktree is detached).
#
# Captured into a variable rather than piped into each reader: `set -o pipefail` above would
# let git's exit code — including the SIGPIPE it takes when a reader stops early — decide the
# answer instead of the reader's. Each question below feeds it back in with <<<, a here-string,
# which hands one string to a command as its stdin without a pipeline.
registry="$(git worktree list --porcelain)"

# Idempotent: a second call for the same issue — a resume, or a conductor re-entering step 1 —
# answers with the path it already made instead of dying on `git worktree add`'s "already
# exists". grep -x -F asks the registry for that exact `worktree <path>` line, whole and
# literal (-F: no regex, so a `.` in the path is a dot). Asking git rather than `[[ -d $path ]]`
# matters — a leftover directory git no longer knows about is not a worktree we can hand back,
# and it must fall through to the add below.
if grep -qxF "worktree $path" <<<"$registry"; then
  printf '%s\n' "$path"
  exit 0
fi

# Never steal a checkout. If the branch is already checked out somewhere else, another
# conductor owns that run, so refuse with exit 2 — "no answer could be obtained" — and name the
# path, because it is the only thing that tells a human which run to go and look at.
#
# Walk the registry line by line, remember the path of the block we are inside, and answer with
# it when a branch line names ours.
#
# `read -r key value` splits each line on whitespace into the first word and *all* the rest, so
# a path containing spaces still arrives whole in $value; -r stops backslashes being eaten.
# Feeding the loop with <<< rather than a `|` also keeps it in this shell — a pipeline would run
# it in a subshell and throw $holder away at the end.
holder=""
seen=""
while read -r key value; do
  case "$key" in
    worktree) seen="$value" ;;
    branch) if [[ "$value" == "refs/heads/$branch" ]]; then holder="$seen"; break; fi ;;
  esac
done <<<"$registry"

if [[ -n "$holder" ]]; then
  echo "issue-worktree: branch $branch is already checked out in $holder — another conductor owns it" >&2
  exit 2
fi

# The branch is cut from the DEFAULT branch, never from HEAD — cutting from HEAD would inherit
# whatever the caller's checkout happened to be sitting on, which is the collision this script
# exists to prevent.
#
# origin/HEAD is git's own record of the default branch when there is a remote; it comes back
# as `origin/main`, so ${head#origin/} strips that prefix (# removes the shortest match from
# the front). A repo with no remote — a throwaway `git init`, a clone whose origin/HEAD was
# never set — has no such record, so fall back to the two names git itself ships as defaults.
default_branch() {
  local head b
  if head="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)"; then
    printf '%s\n' "${head#origin/}"
    return 0
  fi
  for b in main master; do
    # show-ref --verify wants the full refname and answers only through its exit code (--quiet
    # suppresses the printed sha): 0 when the local branch exists, non-zero when it does not.
    if git show-ref --verify --quiet "refs/heads/$b"; then
      printf '%s\n' "$b"
      return 0
    fi
  done
  return 1
}

# Exit 2 — "no answer could be obtained" — rather than guessing: a repo whose default branch we
# cannot name is plumbing broken before any TDD cycle starts, not a step that legitimately failed.
base="$(default_branch)" || {
  echo "issue-worktree: cannot determine the default branch (no origin/HEAD, no local main or master)" >&2
  exit 2
}

# -b creates the branch at <base> and checks it out in the new worktree in one move; -q keeps
# git's "Preparing worktree" chatter out of the way, and >&2 sends anything it still prints to
# stderr, because stdout here belongs to the one line the caller parses: the path.
git worktree add -q -b "$branch" "$path" "$base" >&2

printf '%s\n' "$path"

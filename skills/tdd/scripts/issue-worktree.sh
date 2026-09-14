#!/usr/bin/env bash
# issue-worktree.sh — the linked git worktree an issue branch lives in.
#
# The conductor used to `git switch -c tdd/<n>-<slug>` in whatever checkout /tdd was
# invoked from, which drags that checkout off the default branch for the whole run: anything
# symlinked or served out of it (a user-level skill link, a dev server) silently starts seeing
# the issue branch. This creates a *linked worktree* instead — a second working directory that
# shares the one .git object store — and prints its absolute path, so the run can `cd` there
# and leave the caller's checkout exactly where it was.
#
# Usage:   issue-worktree.sh <n> <slug>
#          issue-worktree.sh --remove <n>
# Output:  the worktree's absolute path on stdout, exit 0.
set -euo pipefail

# git's own registry of worktrees — asked once here, questioned three times below. `worktree
# list --porcelain` prints one block per registered worktree, blank-line separated: a
# `worktree <absolute-path>` line first, then `HEAD <sha>`, then `branch <full-ref>` (absent
# when that worktree is detached).
#
# Captured into a variable rather than piped into each reader: `set -o pipefail` above would
# let git's exit code — including the SIGPIPE it takes when a reader stops early — decide the
# answer instead of the reader's. Each question below feeds it back in with <<<, a here-string,
# which hands one string to a command as its stdin without a pipeline.
registry="$(git worktree list --porcelain)"

# main_working_tree — the repository's main working tree, the one every other worktree is linked
# to. The **main working tree is always the first block** of the registry, so the answer is that
# block's `worktree <absolute-path>` line with the label taken off.
#
# ${registry%%$'\n'*} strips the longest match of "newline and everything after it" from the end,
# leaving that first line, and ${first_line#worktree } then takes the label off the front. The
# path git prints there is absolute and has its symlinks resolved (on macOS a /var/... path comes
# back as /private/var/...), which is the property this needs: git reports every worktree path
# that way, so the path we print matches what `git worktree list` will say about it.
#
# The two steps are a `local` and a print rather than two names in the script's own scope: what
# the first step yields is still `worktree /path/...`, label and all, and no name outside here
# should be able to hold that, because no name would be true of it. Behind the function there is
# one name for the one answer, and it says what the answer is.
main_working_tree() {
  local first_line="${registry%%$'\n'*}"
  printf '%s\n' "${first_line#worktree }"
}

# The issue worktree belongs to the repository's MAIN working tree, never to the checkout we
# happen to have been called from. `git rev-parse --show-toplevel`, which this used to ask,
# answers with the caller's own worktree — so a conductor started from a linked worktree (a
# Claude session checkout under .claude/worktrees/<name>, or any other second working directory)
# nested the run inside it: removing that session took the run's leaf logs with it, and a resume
# from the main clone computed the un-nested path, failed to find it registered, and then refused
# because the branch was checked out "somewhere else" (issue #166).
#
# Named `main_tree` and not `root`: every path below hangs off it, so the name is the one place
# a reader learns *whose* root it is. `root` is what this held back when it was --show-toplevel,
# and it reads equally true of the caller's checkout — which is exactly the reading that put the
# run inside a session worktree.
main_tree="$(main_working_tree)"

# wt_path <n> — where issue <n>'s worktree lives. The layout is stated once, here, because both
# halves of this script need it and a create that answered with a different path than the remove
# went looking for would be a silent no-op. `.tdd/` is already git-ignored, so nesting a worktree
# under it needs no new ignore rule.
wt_path() { printf '%s\n' "$main_tree/.tdd/wt/$1"; }

# --remove <n> takes the worktree back out again, once its branch is merged or a human says so.
# It is answered here, before the positional <n> <slug> parsing below, because that parsing
# would otherwise read the flag itself as the issue number.
if [[ "${1:-}" == "--remove" ]]; then
  n="${2:?usage: issue-worktree.sh --remove <n>}"
  path="$(wt_path "$n")"

  # Never destroy work. `git status --porcelain` prints one line per change — staged, unstaged
  # or untracked — and nothing at all when the tree is clean, so a non-empty answer is the
  # whole test. Asking before removing rather than letting `git worktree remove` refuse for us
  # is what makes this exit 2, "no answer could be obtained", instead of git's own 1: a
  # worktree with changes in it is not a removal that failed, it is one we must not attempt.
  if [[ -n "$(git -C "$path" status --porcelain)" ]]; then
    echo "issue-worktree: $path has uncommitted changes — refusing to remove it" >&2
    exit 2
  fi

  # No --force: with the tree clean git has nothing to object to, and leaving the safety net
  # in place means a change that lands between the check above and here still stops us.
  # >&2 keeps any chatter off stdout.
  git worktree remove "$path" >&2
  exit 0
fi

# ${1:?msg} — expand $1, but if it is unset or empty, die with msg on stderr instead of
# silently building a branch called `tdd/-`. The first argument carries the whole usage line
# and the rest just name themselves, which is how every other script here does it.
n="${1:?usage: issue-worktree.sh <n> <slug>}"
slug="${2:?missing <slug>}"

branch="tdd/$n-$slug"
path="$(wt_path "$n")"

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

# checkout_holder <branch> — the path of the worktree that has <branch> checked out, or nothing
# at all when no worktree does. Walks the registry line by line, remembering the path of the
# block it is inside, and answers with it when a branch line names the one asked about.
#
# `read -r key value` splits each line on whitespace into the first word and *all* the rest, so
# a path containing spaces still arrives whole in $value; -r stops backslashes being eaten.
# `local` keeps the walk's bookkeeping out of the rest of the script. The closing `return 0`
# pins the no-match answer to success: a while loop exits with the status of the last command
# its *body* ran (not the `read` that ended it), which here is an unmatched `if` and so happens
# to be 0 already — but it would be 1 if that line were ever reworked into a bare `[[ ]]`, and
# `set -e` would then kill the script on the ordinary "nobody holds this branch" case.
checkout_holder() {
  local key value seen=""
  while read -r key value; do
    case "$key" in
      worktree) seen="$value" ;;
      branch) if [[ "$value" == "refs/heads/$1" ]]; then printf '%s\n' "$seen"; return 0; fi ;;
    esac
  done <<<"$registry"
  return 0
}

# Never steal a checkout. If the branch is already checked out somewhere else, another
# conductor owns that run, so refuse with exit 2 — "no answer could be obtained" — and name the
# path, because it is the only thing that tells a human which run to go and look at.
holder="$(checkout_holder "$branch")"
if [[ -n "$holder" ]]; then
  echo "issue-worktree: branch $branch is already checked out in $holder — another conductor owns it" >&2
  exit 2
fi

# branch_exists <name> — does this repo already carry a local branch called <name>? Asked twice
# below, of two different things: the issue branch (a resume), and each candidate default branch.
# `show-ref --verify` wants the full refname and answers only through its exit code (--quiet
# suppresses the printed sha): 0 when the branch exists, non-zero when it does not. Naming it
# once keeps the refs/heads/ prefix — the part that makes --verify work at all — in one place.
branch_exists() { git show-ref --verify --quiet "refs/heads/$1"; }

# The branch is cut from the DEFAULT branch, never from HEAD — cutting from HEAD would inherit
# whatever the caller's checkout happened to be sitting on, which is the collision this script
# exists to prevent.
#
# origin/HEAD is git's own record of the default branch when there is a remote; it comes back
# as `origin/main`. A repo with no remote — a throwaway `git init`, a clone whose origin/HEAD was
# never set — has no such record, so fall back to the two names git itself ships as defaults.
#
# With a remote the base is the REMOTE's tip, not the local branch of the same name, and it is
# fetched first (issue #174). The local `main` here lags `origin/main` by design: pulling the
# primary clone while a conductor is live would change the scripts running under it, so the pull
# waits (#165). A branch cut from that stale local ref starts out behind and its PR then owes a
# rebase over everything that landed meanwhile — replayed one `refactor:` commit at a time,
# through whatever conflicts concurrent issues left in the same files.
#
# `git fetch origin <default>` refreshes refs/remotes/origin/<default> and nothing else: it moves
# no local branch ref and touches no working tree, so #165's reason for not pulling stays intact.
# ${head#origin/} strips the prefix (# removes the shortest match from the front) to name the
# branch on the remote side; what is printed is `$head` whole, because `origin/main` is the ref
# the new branch is cut from.
default_base() {
  local head b
  if head="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)"; then
    git fetch -q origin "${head#origin/}" >&2
    printf '%s\n' "$head"
    return 0
  fi
  for b in main master; do
    if branch_exists "$b"; then
      printf '%s\n' "$b"
      return 0
    fi
  done
  return 1
}

# One `git worktree add`, in one of two shapes, and a single print of the path afterwards —
# whichever shape ran, the caller parses the same line.
#
# A branch that already exists — a resume after the last run's worktree was removed, or one
# fetched back from the remote — gets checked out, not cut again. `git worktree add -b` refuses
# outright once the ref is there, and re-cutting it from the default branch would silently
# abandon whatever the previous run committed on it. Naming the branch as `add`'s second
# argument (no -b) is how git says "check this existing branch out here". The holder check above
# already established no other worktree has it, so taking it steals nothing.
if branch_exists "$branch"; then
  git worktree add -q "$path" "$branch" >&2
else
  # Exit 2 — "no answer could be obtained" — rather than guessing: a repo whose default branch we
  # cannot name is plumbing broken before any TDD cycle starts, not a step that legitimately failed.
  base="$(default_base)" || {
    echo "issue-worktree: cannot determine the default branch (no origin/HEAD, no local main or master)" >&2
    exit 2
  }

  # -b creates the branch at <base> and checks it out in the new worktree in one move; -q keeps
  # git's "Preparing worktree" chatter out of the way, and >&2 sends anything it still prints to
  # stderr, because stdout here belongs to the one line the caller parses: the path.
  git worktree add -q -b "$branch" "$path" "$base" >&2
fi

printf '%s\n' "$path"

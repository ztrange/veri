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

lib="$(cd "$(dirname "$0")" && pwd)/lib"
source "$lib/exit-contract.sh"
source "$lib/number-in.sh"
source "$lib/pid-file.sh"
USAGE="usage: issue-worktree.sh <n> <slug> | --remove <n>"
require_args 2 "$@"

# hazard: captured, not piped — under pipefail git's SIGPIPE status would decide the answer.
registry="$(git worktree list --porcelain)"

main_working_tree() {
  local first_line="${registry%%$'\n'*}"
  printf '%s\n' "${first_line#worktree }"
}

main_tree="$(main_working_tree)"

wt_path() { printf '%s\n' "$main_tree/.tdd/wt/$1"; }

if [[ "${1:-}" == "--remove" ]]; then
  n="$2"
  path="$(wt_path "$n")"

  if [[ -n "$(git -C "$path" status --porcelain)" ]]; then
    echo "issue-worktree: $path has uncommitted changes — refusing to remove it" >&2
    exit 2
  fi

  git worktree remove "$path" >&2
  exit 0
fi

n="$1"
slug="$2"

branch="tdd/$n-$slug"
path="$(wt_path "$n")"

if grep -qxF "worktree $path" <<<"$registry"; then
  if conductor_pid="$(live_conductor "$path")"; then
    echo "issue-worktree: $path is held by a live conductor (pid $conductor_pid) — refusing to hand back a run in flight" >&2
    exit 2
  fi
  printf '%s\n' "$path"
  exit 0
fi

# hazard: a while loop's status is its body's last command's, so `return 0` keeps set -e off the no-match case.
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

holder="$(checkout_holder "$branch")"
if [[ -n "$holder" ]]; then
  echo "issue-worktree: branch $branch is already checked out in $holder — another conductor owns it" >&2
  exit 2
fi

ref_exists() { git show-ref --verify --quiet "$1"; }

branch_exists() { ref_exists "refs/heads/$1"; }

remote_branch_ref() { printf '%s\n' "refs/remotes/origin/$1"; }

remote_branch_exists() { ref_exists "$(remote_branch_ref "$1")"; }

has_origin() { git remote get-url origin >/dev/null 2>&1; }

default_branch_name() {
  local head candidate
  if head="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)"; then
    head="${head#origin/}"
  else
    head="$(git ls-remote --symref origin HEAD 2>/dev/null)" || true
    head="$(sed -n 's|^ref: refs/heads/\([^[:space:]]*\)[[:space:]]*HEAD$|\1|p' <<<"$head")"
  fi
  if [[ -n "$head" ]]; then
    printf '%s\n' "$head"
    return 0
  fi
  if has_origin; then
    echo "issue-worktree: cannot determine origin's default branch (no refs/remotes/origin/HEAD, and the remote did not name one)" >&2
    return 2
  fi
  for candidate in main master; do
    if branch_exists "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  echo "issue-worktree: cannot determine the default branch (no origin/HEAD, no local main or master)" >&2
  return 2
}

default_base() {
  local name
  name="$(default_branch_name)" || return 2

  if ! has_origin; then
    printf '%s\n' "$name"
    return 0
  fi

  if ! git fetch -q origin "$name" >&2; then
    echo "issue-worktree: git fetch origin $name failed — refusing to cut $branch from a stale origin/$name" >&2
    return 2
  fi
  printf '%s\n' "origin/$name"
}

worktree_add() { git worktree add -q "$@" >&2; }

if [[ -f "$path/.tdd/events.jsonl" ]] &&
   [[ "$(ls -A "$path")" == .tdd ]] && [[ "$(ls -A "$path/.tdd")" == events.jsonl ]]; then
  seeded_log="$(mktemp)"
  mv "$path/.tdd/events.jsonl" "$seeded_log"
  rmdir "$path/.tdd" "$path"
  at_exit 'mkdir -p "$path/.tdd" && cat "$seeded_log" >> "$path/.tdd/events.jsonl" && rm -f "$seeded_log"'
fi

if branch_exists "$branch"; then
  worktree_add "$path" "$branch"
elif remote_branch_exists "$branch"; then
  worktree_add -b "$branch" "$path" "$(remote_branch_ref "$branch")"
else
  base="$(default_base)" || exit 2

  worktree_add --no-track -b "$branch" "$path" "$base"
fi

printf '%s\n' "$path"

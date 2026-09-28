#!/usr/bin/env bash
# ensure-run-state-ignored.sh — install veri's run-state rule into a target repo's ignore files.
#
# veri writes leaf logs, .rc markers, .prompt files and the blind spec into the target repo's
# .tdd/; only the ledger (.tdd/issue-<n>.md) belongs in history. This writes the three-line,
# order-sensitive rule that makes git agree: ignore .tdd/*, un-ignore the ledger, re-ignore
# the spec (which would otherwise be caught by the ledger's negation).
#
# The rule goes into two files and needs both: the worktree's .gitignore, which is committed and
# so keeps the merged repo safe from a later `git add -A`, and the shared info/exclude, which is
# never committed and so keeps the caller's checkout clean while the run is in progress. Why
# neither is sufficient alone is at each one's block below.
#
# Usage:   ensure-run-state-ignored.sh [repo-root]      (default: the current directory)
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/lib/appendable.sh"

root="${1:-.}"
gitignore="$root/.gitignore"

ignore_all='.tdd/*'         # sweep every run artefact under .tdd/ out of git's sight
keep_ledger='!.tdd/issue-*.md'   # except the ledger, the one file that belongs in history
drop_spec='.tdd/issue-*-spec.md' # but not the blind spec, which that negation would drag back in

common_dir="$(git -C "$root" rev-parse --git-common-dir)"
case "$common_dir" in /*) ;; *) common_dir="$root/$common_dir" ;; esac
exclude="$common_dir/info/exclude"

append_rule() {
  make_appendable "$1"
  printf '%s\n' "$ignore_all" "$keep_ledger" "$drop_spec" >> "$1"
}

# hazard: under pipefail an absent line makes grep exit 1, and set -e would kill the script; `|| true` keeps it.
where() { grep -nxF "$1" "$2" | head -1 | cut -d: -f1 || true; }

has_rule() {
  local file="$1" at_all at_ledger at_spec
  [ -f "$file" ] || return 1
  at_all="$(where "$ignore_all" "$file")"
  at_ledger="$(where "$keep_ledger" "$file")"
  at_spec="$(where "$drop_spec" "$file")"
  if [ -n "$at_all" ] && [ -n "$at_ledger" ] && [ -n "$at_spec" ] \
    && [ "$at_all" -lt "$at_ledger" ] && [ "$at_ledger" -lt "$at_spec" ]; then
    return 0
  fi
  if [ -n "$at_spec" ]; then
    echo "ensure-run-state-ignored: $file carries veri's run-state rule only in part, or with its lines out of order — fix it by hand" >&2
    exit 2
  fi
  return 1
}

if has_rule "$gitignore"; then
  verdict="already present"
else
  verdict="added"
fi

if ! has_rule "$exclude"; then
  append_rule "$exclude"
fi

if [ "$verdict" = added ]; then
  append_rule "$gitignore"
fi

echo "$verdict"

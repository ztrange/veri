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

# shellcheck source=lib/appendable.sh
source "$(cd "$(dirname "$0")" && pwd)/lib/appendable.sh"

root="${1:-.}"
gitignore="$root/.gitignore"

# The rule, one line per variable, in the order git needs to read them. Named once because the
# presence check below and `append_rule` must agree on the exact text: two spellings of
# `.tdd/issue-*-spec.md` could drift apart, and the script would then append a rule it had just
# failed to recognise.
ignore_all='.tdd/*'         # sweep every run artefact under .tdd/ out of git's sight
keep_ledger='!.tdd/issue-*.md'   # except the ledger, the one file that belongs in history
drop_spec='.tdd/issue-*-spec.md' # but not the blind spec, which that negation would drag back in

# The same rule has to reach a second file. The .gitignore above is committed on the issue branch,
# so the checkout the conductor was invoked from — still on the default branch — never sees it and
# keeps reporting the worktree under .tdd/ as untracked, which the next run's preflight refuses to
# start on. `info/exclude` under the *common* git dir is read by every worktree of the repo and is
# never committed, so it needs no branch and no PR; --git-common-dir is what resolves a linked
# worktree's own gitdir back to the primary's, and answers relative to $root when it answers
# relatively at all.
common_dir="$(git -C "$root" rev-parse --git-common-dir)"
case "$common_dir" in /*) ;; *) common_dir="$root/$common_dir" ;; esac
exclude="$common_dir/info/exclude"

# append_rule <file> — put the three lines at the end of <file>, in git's reading order, having
# first made <file> appendable at all (lib/appendable.sh says what that takes). Both destinations
# need exactly this, so it is written once.
append_rule() {
  make_appendable "$1"
  printf '%s\n' "$ignore_all" "$keep_ledger" "$drop_spec" >> "$1"
}

# where <line> <file> — the number of the first line of <file> that IS <line>, whole and on its own,
# or the empty string when absent. -F keeps the glob literal (no regex), -x forbids a partial-line
# match so `x.tdd/*` does not count as `.tdd/*`, -n prefixes each hit with `<lineno>:` — `head -1`
# takes the first hit and `cut` keeps the number, which is what the ordering check below compares.
# `|| true` is load-bearing under `pipefail`: absent the line, grep exits 1 and the whole pipeline
# inherits it, which `set -e` would turn into the script dying instead of reporting "not there".
where() { grep -nxF "$1" "$2" | head -1 | cut -d: -f1 || true; }

# has_rule <file> — true when <file> already carries the whole rule, in git's reading order; false
# when it carries none of it. Never true for a subset and never for the same three lines shuffled:
# with the negation last, `!.tdd/issue-*.md` un-ignores the spec the line above just re-ignored, so
# every line is there and the rule is not. Appending cannot repair either case — git reads a second
# `.tdd/*` after the negation that precedes it — so both are refused rather than rewritten: exit 2,
# the "no answer could be obtained" code, fails the conductor's preflight before a cycle starts
# committing its scratch. (`exit` inside a function that is not a subshell ends the script, which is
# what this wants: there is nothing to report once the file is un-appendable.)
#
# Both destinations are asked this, and it is asked before either is written: appending blind is
# what makes a resumed run — the conductor re-runs step 1.4 — double the block in info/exclude,
# which nothing commits and nothing reads back, so the duplicate would sit in the caller's ignore
# rules forever, three more lines per run.
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

# The word the conductor keys off, decided here rather than at the echo below: the .gitignore has to
# be *asked* first, so that a partial or misordered one aborts before anything is written, but it is
# *appended* last, after the exclude file. Holding the answer as the word it will print keeps those
# two moments from needing a sentinel whose spelling has to stay in step with two echo sites.
if has_rule "$gitignore"; then
  verdict="already present"
else
  verdict="added"
fi

# The exclude file is written whatever the .gitignore turned out to be: a repo that already carries
# the rule in history (veri's own, #27) still has a caller's checkout that has never been told to
# ignore .tdd/. The .gitignore's refusal comes first, so a .gitignore we will not touch leaves this
# file untouched too.
if ! has_rule "$exclude"; then
  append_rule "$exclude"
fi

if [ "$verdict" = added ]; then
  append_rule "$gitignore"
fi

echo "$verdict"

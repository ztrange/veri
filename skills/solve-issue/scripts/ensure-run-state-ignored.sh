#!/usr/bin/env bash
# ensure-run-state-ignored.sh — install veri's run-state rule into a target repo's .gitignore.
#
# veri writes leaf logs, .rc markers, .prompt files and the blind spec into the target repo's
# .tdd/; only the ledger (.tdd/issue-<n>.md) belongs in history. This writes the three-line,
# order-sensitive rule that makes git agree: ignore .tdd/*, un-ignore the ledger, re-ignore
# the spec (which would otherwise be caught by the ledger's negation).
#
# Usage:   ensure-run-state-ignored.sh [repo-root]      (default: the current directory)
set -euo pipefail

root="${1:-.}"
gitignore="$root/.gitignore"

# The rule, one line per variable, in the order git needs to read them. Named once because the
# presence check below and the append at the end must agree on the exact text: two spellings of
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

# append_rule <file> — put the three lines at the end of <file>, in git's reading order. Both
# destinations need exactly this, so it is written once: two copies of the append could drift into
# disagreeing about the newline guard, and only one of the two files would then survive it.
#
# The guard: give <file> a final newline if its last byte is not one, so the append cannot fuse its
# last rule with `.tdd/*` into a single line and destroy both. `$(...)` strips trailing newlines
# from what it captures, so a file already ending in one yields the empty string here: a non-empty
# last byte is exactly the case that needs the newline. -s keeps `tail` off a file that does not
# exist yet.
append_rule() {
  if [ -s "$1" ] && [ -n "$(tail -c 1 "$1")" ]; then
    echo "" >> "$1"
  fi
  printf '%s\n' "$ignore_all" "$keep_ledger" "$drop_spec" >> "$1"
}

# where <line> — the number of the first line of $gitignore that IS <line>, whole and on its own,
# or the empty string when absent. -F keeps the glob literal (no regex), -x forbids a partial-line
# match so `x.tdd/*` does not count as `.tdd/*`, -n prefixes each hit with `<lineno>:` — `head -1`
# takes the first hit and `cut` keeps the number, which is what the ordering check below compares.
# `|| true` is load-bearing under `pipefail`: absent the line, grep exits 1 and the whole pipeline
# inherits it, which `set -e` would turn into the script dying instead of reporting "not there".
where() { grep -nxF "$1" "$gitignore" | head -1 | cut -d: -f1 || true; }

gitignore_has_rule=no

if [ -f "$gitignore" ]; then
  # "Already present" means the whole rule, in git's reading order, never a subset and never the
  # same three lines shuffled: with the negation last, `!.tdd/issue-*.md` un-ignores the spec the
  # line above just re-ignored, so every line is there and the rule is not. Appending cannot repair
  # either case — git reads a second `.tdd/*` after the negation that precedes it — so both are
  # refused rather than rewritten: exit 2, the "no answer could be obtained" code, fails the
  # conductor's preflight before a cycle starts committing its scratch.
  at_all="$(where "$ignore_all")"
  at_ledger="$(where "$keep_ledger")"
  at_spec="$(where "$drop_spec")"
  if [ -n "$at_all" ] && [ -n "$at_ledger" ] && [ -n "$at_spec" ] \
    && [ "$at_all" -lt "$at_ledger" ] && [ "$at_ledger" -lt "$at_spec" ]; then
    gitignore_has_rule=yes
  elif [ -n "$at_spec" ]; then
    echo "ensure-run-state-ignored: $gitignore carries veri's run-state rule only in part, or with its lines out of order — fix it by hand" >&2
    exit 2
  fi
fi

# The exclude file is written whatever the .gitignore turned out to be: a repo that already carries
# the rule in history (veri's own, #27) still has a caller's checkout that has never been told to
# ignore .tdd/. The refusal above comes first, so a .gitignore we will not touch leaves this file
# untouched too.
mkdir -p "$(dirname "$exclude")"
append_rule "$exclude"

if [ "$gitignore_has_rule" = yes ]; then
  echo "already present"
  exit 0
fi

append_rule "$gitignore"

echo "added"

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

# has <line> — is <line> in $gitignore, whole and on its own line? -F keeps the glob literal
# (no regex), -x forbids a partial-line match, so `x.tdd/*` does not count as `.tdd/*`.
has() { grep -qxF "$1" "$gitignore"; }

if [ -f "$gitignore" ]; then
  # "Already present" means the whole rule, never a subset. The last line on its own would ignore
  # the ledger too, and appending a second `.tdd/*` after it cannot repair that — git reads the
  # negation that precedes it. So a .gitignore carrying part of the rule is refused rather than
  # rewritten: exit 2, the "no answer could be obtained" code, fails the conductor's preflight
  # before a cycle starts committing its scratch.
  if has '.tdd/*' && has '!.tdd/issue-*.md' && has '.tdd/issue-*-spec.md'; then
    echo "already present"
    exit 0
  fi
  if has '.tdd/issue-*-spec.md'; then
    echo "ensure-run-state-ignored: $gitignore carries part of veri's run-state rule, not all of it — fix it by hand" >&2
    exit 2
  fi
fi

# An existing .gitignore need not end in a newline; appending straight onto it would fuse its
# last rule with `.tdd/*` into one line, destroying both. Terminate that line first.
# `$(...)` strips trailing newlines from what it captures, so a file that already ends in one
# yields the empty string here: a non-empty last byte is exactly the case that needs the newline.
# -s guards the substitution — it keeps `tail` off a .gitignore that does not exist yet.
if [ -s "$gitignore" ] && [ -n "$(tail -c 1 "$gitignore")" ]; then
  echo "" >> "$gitignore"
fi

cat >> "$gitignore" <<'RULE'
.tdd/*
!.tdd/issue-*.md
.tdd/issue-*-spec.md
RULE

echo "added"

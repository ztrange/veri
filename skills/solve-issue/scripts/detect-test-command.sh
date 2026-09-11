#!/usr/bin/env bash
# detect-test-command.sh — print the one command that runs the full suite of a repo.
#
# Prints the command on stdout and exits 0; prints nothing and exits 3 when it cannot
# decide, which is the conductor's cue to ask the human.
#
# Precedence is first-match-wins, and the override below is the first rule on purpose:
# whatever a later inference would have guessed, a repo that wrote .veri/test-command
# has already answered the question, so nothing downstream gets to second-guess it.
#
# Usage:   detect-test-command.sh [repo-root]      (default: the current directory)
set -euo pipefail

root="${1:-.}"

# 1. The override file. Its first non-empty line is the command, verbatim: `IFS=` keeps
# read from stripping leading and trailing whitespace, -r keeps it from eating
# backslashes, and printf '%s\n' re-emits exactly those bytes — the whole point of the
# escape hatch is that what the repo wrote is what the leaf runs.
#
# `|| [ -n "$line" ]` is load-bearing: read exits non-zero at end of file, which is also
# what it does after handing back a final line that had no trailing newline. Without the
# second test that last line would be read and then discarded.
override="$root/.veri/test-command"
if [ -f "$override" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    if [ -n "$line" ]; then
      printf '%s\n' "$line"
      exit 0
    fi
  done < "$override"
fi

# 2. A package.json that declares a test script names the node runner. Which runner is a
# separate question, answered by the lockfile the repo committed beside it: a lockfile is
# the repo saying which package manager actually installs here, so `pnpm test` / `yarn
# test` rather than an `npm test` that would resolve a different dependency tree.
#
# `tr -d '[:space:]'` flattens the file to one line with no whitespace, so the pattern can
# be written as if package.json were minified — formatting stops mattering. `[^}]*` then
# pins the "test": key to inside the "scripts" object, so a dependency or a config section
# that happens to be called "test" cannot answer for it. Both are inside an `if`
# condition, where grep's exit 1 for "no match" is an answer rather than a failure `set
# -e` would abort on.
pkg="$root/package.json"
if [ -f "$pkg" ] && tr -d '[:space:]' < "$pkg" | grep -q '"scripts":{[^}]*"test":'; then
  if [ -f "$root/pnpm-lock.yaml" ]; then
    printf 'pnpm test\n'
  elif [ -f "$root/yarn.lock" ]; then
    printf 'yarn test\n'
  else
    printf 'npm test\n'
  fi
  exit 0
fi

# Nothing decided: say nothing, and let exit 3 — "nothing to do", not an error — send the
# question to the human.
exit 3

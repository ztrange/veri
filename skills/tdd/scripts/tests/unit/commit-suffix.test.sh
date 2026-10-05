#!/usr/bin/env bash
# Unit tests for tests/lib/commit-suffix.sh, the check over every prompts/develop-*.md that tells
# the leaf to commit: each such prompt states the `(#<issue>)` commit-subject suffix.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Contract under test:
#   Handed a directory holding a develop-*.md that asks for a commit without stating
#   `(#<issue>)`, the check prints a line naming that file and returns 1.
#
# Run: scripts/tests/unit/commit-suffix.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../lib/commit-suffix.sh"
source "$HERE/../lib/harness.sh"
scratch="$(scratch_dir)"

name="#935 the commit-suffix check fails, naming the file, over a planted develop prompt that asks for a commit without stating (#<issue>)"
plant="$scratch/prompts"
mkdir -p "$plant"
printf '%s\n' '## Phase: develop-planted' '' 'Make the change the step names, then commit that change.' > "$plant/develop-planted.md"
rc=0
out="$( source "$LIB" && commit_suffix_offenders "$plant" 2>&1 )" || rc=$?
named=""; grep -F 'develop-planted.md' <<< "$out" > /dev/null && named=named
expect_eq "$name" "1:named" "$rc:$named"

finish

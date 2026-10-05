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

name="#935 the commit-suffix check stays green over a planted develop prompt that makes no commit, and over the real prompts directory"
quiet="$scratch/quiet"
mkdir -p "$quiet"
printf '%s\n' '## Phase: develop-quiet' '' 'Make no commit.' > "$quiet/develop-quiet.md"
planted_rc=0
( source "$LIB" && commit_suffix_offenders "$quiet" > /dev/null 2>&1 ) || planted_rc=$?
real_rc=0
( source "$LIB" && commit_suffix_offenders "$HERE/../../prompts" > /dev/null 2>&1 ) || real_rc=$?
expect_eq "$name" "0:0" "$planted_rc:$real_rc"

name="#935 the commit-suffix check fails, naming the file, over a planted develop prompt whose commit instruction uses another phrasing without stating (#<issue>)"
other="$scratch/other"
mkdir -p "$other"
printf '%s\n' '## Phase: develop-other' '' 'Commit your change.' > "$other/develop-other.md"
rc=0
out="$( source "$LIB" && commit_suffix_offenders "$other" 2>&1 )" || rc=$?
named=""; grep -F 'develop-other.md' <<< "$out" > /dev/null && named=named
expect_eq "$name" "1:named" "$rc:$named"

name="#946 the commit-suffix check fails, naming the file, over a planted develop prompt saying \"Commit these changes.\" without stating (#<issue>)"
these="$scratch/these"
mkdir -p "$these"
printf '%s\n' '## Phase: develop-these' '' 'Commit these changes.' > "$these/develop-these.md"
rc=0
out="$( source "$LIB" && commit_suffix_offenders "$these" 2>&1 )" || rc=$?
named=""; grep -F 'develop-these.md' <<< "$out" > /dev/null && named=named
expect_eq "$name" "1:named" "$rc:$named"

name="#946 the commit-suffix check fails, naming the file, over a planted develop prompt saying \"Commit everything you changed.\" without stating (#<issue>)"
everything="$scratch/everything"
mkdir -p "$everything"
printf '%s\n' '## Phase: develop-everything' '' 'Commit everything you changed.' > "$everything/develop-everything.md"
rc=0
out="$( source "$LIB" && commit_suffix_offenders "$everything" 2>&1 )" || rc=$?
named=""; grep -F 'develop-everything.md' <<< "$out" > /dev/null && named=named
expect_eq "$name" "1:named" "$rc:$named"

name="#946 the commit-suffix check fails, naming the file, over a planted develop prompt saying \"commit them\" without stating (#<issue>)"
them="$scratch/them"
mkdir -p "$them"
printf '%s\n' '## Phase: develop-them' '' 'Stage the files you changed, then commit them.' > "$them/develop-them.md"
rc=0
out="$( source "$LIB" && commit_suffix_offenders "$them" 2>&1 )" || rc=$?
named=""; grep -F 'develop-them.md' <<< "$out" > /dev/null && named=named
expect_eq "$name" "1:named" "$rc:$named"

name="#946 the commit-suffix check fails, naming the file, over a planted develop prompt whose commit instruction is the bare sentence \"Commit.\" without stating (#<issue>)"
bare="$scratch/bare"
mkdir -p "$bare"
printf '%s\n' '## Phase: develop-bare' '' 'Make the change the step names.' 'Commit.' > "$bare/develop-bare.md"
rc=0
out="$( source "$LIB" && commit_suffix_offenders "$bare" 2>&1 )" || rc=$?
named=""; grep -F 'develop-bare.md' <<< "$out" > /dev/null && named=named
expect_eq "$name" "1:named" "$rc:$named"

name="#946 the commit-suffix check fails, naming the file, over a planted develop prompt saying \"make a commit\" without stating (#<issue>)"
make="$scratch/make"
mkdir -p "$make"
printf '%s\n' '## Phase: develop-make' '' 'Make the change the step names, then make a commit.' > "$make/develop-make.md"
rc=0
out="$( source "$LIB" && commit_suffix_offenders "$make" 2>&1 )" || rc=$?
named=""; grep -F 'develop-make.md' <<< "$out" > /dev/null && named=named
expect_eq "$name" "1:named" "$rc:$named"

name="#946 the commit-suffix check fails, naming the file, over a planted develop prompt saying \"Create a commit for this work.\" without stating (#<issue>)"
create="$scratch/create"
mkdir -p "$create"
printf '%s\n' '## Phase: develop-create' '' 'Create a commit for this work.' > "$create/develop-create.md"
rc=0
out="$( source "$LIB" && commit_suffix_offenders "$create" 2>&1 )" || rc=$?
named=""; grep -F 'develop-create.md' <<< "$out" > /dev/null && named=named
expect_eq "$name" "1:named" "$rc:$named"

name="#946 the commit-suffix check stays green over a planted develop prompt whose only mention of a commit is \"\`git diff <base-sha>..HEAD\`\""
diff="$scratch/diff"
mkdir -p "$diff"
printf '%s\n' '## Phase: develop-diff' '' 'Read what the step changed with `git diff <base-sha>..HEAD`.' > "$diff/develop-diff.md"
rc=0
out="$( source "$LIB" && commit_suffix_offenders "$diff" 2>&1 )" || rc=$?
expect_eq "$name" "0:" "$rc:$out"

name="#946 the commit-suffix check stays green over a planted develop prompt whose only mention of a commit is \"the step's green commit\""
green="$scratch/green"
mkdir -p "$green"
printf '%s\n' '## Phase: develop-green' '' "Compare the tree against the step's green commit." > "$green/develop-green.md"
rc=0
out="$( source "$LIB" && commit_suffix_offenders "$green" 2>&1 )" || rc=$?
expect_eq "$name" "0:" "$rc:$out"

name="#946 the commit-suffix check stays green, reporting nothing, over every shipped develop-*.md prompt"
rc=0
out="$( source "$LIB" && commit_suffix_offenders "$HERE/../../prompts" 2>&1 )" || rc=$?
expect_eq "$name" "0:" "$rc:$out"

finish

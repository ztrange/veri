#!/usr/bin/env bash
# Tests for the exit code every script under scripts/ owes a caller who left out a required
# argument: 2, with a usage line on stderr. Its subject is the argument contract all scripts
# share, not one script.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Contract under test:
#   every scripts/*.sh whose usage line names a <…> outside […],
#   called with no arguments                                      → exit 2, usage on stderr
#   every script in the second roster, called without one later
#   positional argument                                           → exit 2, usage on stderr
#   every script in the third roster, given a bad argument value  → exit 2, its own usage on stderr
#   no script's source guards a positional with `${N:?…}`, which exits 1
#
# Run: scripts/tests/missing-argument-exit.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$HERE/.."
source "$HERE/../lib/missing-argument-exit.sh"
source "$HERE/lib/harness.sh"
source "$HERE/lib/verdict.sh"
offenders=()

usage_stub() {  # usage_stub <path> <usage-line> <exit> — an executable that prints <usage-line> on stderr and exits <exit>
  printf '#!/bin/sh\necho "%s" >&2\nexit %s\n' "$2" "$3" > "$1"
  chmod +x "$1"
}

name="the missing-argument audit covers a script added to the scripts/ directory whose usage line names a required argument"
plant="$(scratch_dir)"
usage_stub "$plant/planted.sh" 'usage: planted.sh <n>' 0
expect_eq "$name" 'planted.sh: want exit 2, got 0' "$(argument_audit "$plant" 2>&1)"

name="the missing-argument audit returns 1 when a script it audits is an offender"
code=0
argument_audit "$plant" > /dev/null 2>&1 || code=$?
expect_eq "$name" 1 "$code"

name="the missing-argument audit over a directory holding no script prints nothing and returns 0"
empty="$(scratch_dir)"
code=0
out="$(argument_audit "$empty" 2>&1)" || code=$?
expect_eq "$name" '0:' "$code:$out"

name="the missing-argument audit calls only scripts whose usage line names a required argument, and wants each one's usage line to name it"
mixed="$(scratch_dir)"
usage_stub "$mixed/optional.sh" 'usage: optional.sh [<n>]' 0
usage_stub "$mixed/required.sh" 'usage: <n>' 2
expect_eq "$name" 'required.sh: usage line on stderr does not name it: usage: <n>' "$(argument_audit "$mixed" 2>&1)"

name="no script guards a required positional argument with a bare \${N:?…} expansion"
mapfile -t offenders < <(bare_expansion_offenders "$SCRIPTS")
verdict "$name" "${offenders[@]}"

finish

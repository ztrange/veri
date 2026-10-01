#!/usr/bin/env bash
# Unit tests for scripts/lib/exit-contract.sh — the usage-and-refuse move, sourced, not run.
# The suite sources the module in a subshell and calls its functions in-process.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Contract under test:
#   refuse [message] — prints message (if given), then the caller's $USAGE, on stderr; nothing
#   on stdout; exits 2.
#   require_args <n> "$@" — refuses with the caller's $USAGE unless the first n arguments are
#   present and non-empty; returns 0 otherwise.
#
# Run: scripts/tests/unit/exit-contract.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../../lib/exit-contract.sh"
source "$HERE/../lib/harness.sh"

CALLER_USAGE="usage: caller.sh <issue-number>"

refusal_of() {
  local dir out err code
  dir="$(scratch_dir)"
  (
    USAGE="$CALLER_USAGE"
    source "$LIB"
    refuse "$@"
    echo "refuse returned"
  ) > "$dir/out" 2> "$dir/err" && code=0 || code=$?
  out="$(cat "$dir/out")"
  err="$(cat "$dir/err")"
  printf 'exit=%s\nstdout=%s\nstderr=%s' "$code" "$out" "$err"
}

expect_eq "refuse prints its message then the caller's \$USAGE on stderr and exits 2" \
  "$(printf 'exit=2\nstdout=\nstderr=not a number: x\n%s' "$CALLER_USAGE")" \
  "$(refusal_of "not a number: x")"

expect_eq "refuse with no message prints only the caller's \$USAGE on stderr and exits 2" \
  "$(printf 'exit=2\nstdout=\nstderr=%s' "$CALLER_USAGE")" \
  "$(refusal_of)"

requirement_of() {
  local dir out err code
  dir="$(scratch_dir)"
  (
    USAGE="$CALLER_USAGE"
    source "$LIB"
    require_args "$@"
    echo "returned $?"
  ) > "$dir/out" 2> "$dir/err" && code=0 || code=$?
  out="$(cat "$dir/out")"
  err="$(cat "$dir/err")"
  printf 'exit=%s stdout=%s stderr=%s' "$code" "$out" "$err"
}

expect_eq "require_args refuses with the caller's \$USAGE unless the first n arguments are present and non-empty, and returns 0 otherwise" \
  "$(printf '%s\n' \
    "exit=2 stdout= stderr=$CALLER_USAGE" \
    "exit=2 stdout= stderr=$CALLER_USAGE" \
    "exit=0 stdout=returned 0 stderr=" \
    "exit=0 stdout=returned 0 stderr=")" \
  "$(printf '%s\n' \
    "$(requirement_of 2 a)" \
    "$(requirement_of 2 a '')" \
    "$(requirement_of 2 a b)" \
    "$(requirement_of 1 a '')")"

finish

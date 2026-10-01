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

outcome_of() {
  local dir out err code
  dir="$(scratch_dir)"
  (
    USAGE="$CALLER_USAGE"
    source "$LIB"
    "$@"
    echo "returned $?"
  ) > "$dir/out" 2> "$dir/err" && code=0 || code=$?
  out="$(cat "$dir/out")"
  err="$(cat "$dir/err")"
  printf 'exit=%s stdout=%s stderr=%s' "$code" "$out" "$err"
}

expect_eq "refuse prints its message then the caller's \$USAGE on stderr and exits 2" \
  "$(printf 'exit=2 stdout= stderr=not a number: x\n%s' "$CALLER_USAGE")" \
  "$(outcome_of refuse "not a number: x")"

expect_eq "refuse with no message prints only the caller's \$USAGE on stderr and exits 2" \
  "exit=2 stdout= stderr=$CALLER_USAGE" \
  "$(outcome_of refuse)"

expect_eq "require_args refuses with the caller's \$USAGE unless the first n arguments are present and non-empty, and returns 0 otherwise" \
  "$(printf '%s\n' \
    "exit=2 stdout= stderr=$CALLER_USAGE" \
    "exit=2 stdout= stderr=$CALLER_USAGE" \
    "exit=0 stdout=returned 0 stderr=" \
    "exit=0 stdout=returned 0 stderr=")" \
  "$(printf '%s\n' \
    "$(outcome_of require_args 2 a)" \
    "$(outcome_of require_args 2 a '')" \
    "$(outcome_of require_args 2 a b)" \
    "$(outcome_of require_args 1 a '')")"

expect_eq "to_contract prints 0, 1, 2 or 3 unchanged and prints 2 for any other code" \
  "$(for printed in 0 1 2 3 2 2 2 2; do
    printf 'exit=0 stdout=%s\nreturned 0 stderr=\n' "$printed"
  done)" \
  "$(for code in 0 1 2 3 4 127 141 255; do
    printf '%s\n' "$(outcome_of to_contract "$code")"
  done)"

finish

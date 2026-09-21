# lib/missing-argument-exit.sh — sourced, not run: defines `missing_argument_offender`, the
# one place a call that left out a required argument is judged against the contract
# CLAUDE.md's "Exit codes are the API" fixes — exit 2, "no answer could be obtained", with a
# usage line on stderr — never exit 1, "a clean negative", which the conductor branches on as
# a methodology failure (issue #270).
#
# The check lives here rather than inside the cross-suite guard that runs it over every
# script, so that it can itself be tested: every script in that guard's roster answers with 2
# today, so a case asserting over the real tree would pass whether the check works or not.
# tests/unit/missing-argument-guard.test.sh plants an offender in a scratch directory and
# asks this function about it instead.
#
# missing_argument_offender <scripts-dir> <script> [args …] — runs <scripts-dir>/<script>
# with <args> (stdin from /dev/null, so a script that reads stdin past its guard does not
# swallow the caller's own input, and stdout discarded). Returns 0 when the call refused as
# the contract says; otherwise prints one offender line on stdout, naming the call and what
# it came back with, and returns 1.
#
# `return`, never `exit`: this runs in the caller's shell once sourced, so an `exit` here
# would tear down the suite that is collecting offenders rather than hand it the one it just
# found — the same rule lib/leaf-role.sh's header states at greater length.
missing_argument_offender() {
  local dir="$1" script="$2"; shift 2
  local code=0 err shown="$script${*:+ $*}"
  err="$("$dir/$script" "$@" 2>&1 >/dev/null </dev/null)" || code=$?
  if [[ "$code" != 2 ]]; then
    echo "$shown: want exit 2, got $code"
    return 1
  fi
  if [[ "$err" != *usage* ]]; then
    echo "$shown: exit 2 but no usage line on stderr: ${err:-<nothing on stderr>}"
    return 1
  fi
}

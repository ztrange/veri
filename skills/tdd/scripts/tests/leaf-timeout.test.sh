#!/usr/bin/env bash
# Unit tests for scripts/leaf-timeout.sh — sizes the run's hard timeout from the wall time
# preflight already measured on the green-baseline run, so a repo whose suite takes minutes
# does not have every leaf killed as stuck while it is working (issue #121).
# Zero-dependency plain-shell asserts, same idiom as refactor-budget.test.sh.
#
# Contract under test (this step only):
#   leaf-timeout.sh <baseline-seconds>  with VERI_TIMEOUT unset
#                              → prints the larger of 900 and 6 × <baseline-seconds>,
#                                as a whole number of seconds, and exits 0.
#   a baseline that is not a whole number ≥ 0 (`abc`, `-1`, `1.5`, or no argument at all)
#                              → exit 2, a diagnostic on stderr, nothing on stdout: the
#                                fail-closed answer refactor-budget.sh gives a bad budget,
#                                so a conductor reading stdout in a command substitution
#                                cannot capture a malformed call as a real timeout.
#
# Run: scripts/tests/leaf-timeout.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LEAF_TIMEOUT="$HERE/../leaf-timeout.sh"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which probe broke rather than just that the case did.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# good_probe <baseline> <want> — a baseline the script must answer: exit 0, exactly the
# expected number on stdout and, because a valid call is not a diagnosable one, nothing on
# stderr. Separate files per stream, since the case is about which stream carries what.
# `env -u` clears VERI_TIMEOUT for the child only, so the answer is a fact about the script
# and not about whatever the surrounding run exported (hermetic-suites.test.sh's concern).
good_probe() {
  local baseline="$1" want="$2" out err code
  out="$(mktemp)" err="$(mktemp)"
  env -u VERI_TIMEOUT "$LEAF_TIMEOUT" "$baseline" >"$out" 2>"$err" && code=0 || code=$?
  [[ "$code" == 0 ]] ||
    problems+=("baseline $baseline: want exit 0, got $code")
  # One line holding exactly the number: `$(cat …)` eats the trailing newline, so this is
  # both "the right value" and "nothing else printed alongside it".
  [[ "$(cat "$out")" == "$want" ]] ||
    problems+=("baseline $baseline: want $want on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ ! -s "$err" ]] ||
    problems+=("baseline $baseline: want nothing on stderr, got: $(printf '%q' "$(cat "$err")")")
  rm -f "$out" "$err"
}

# bad_probe <label> [args...] — a call the script must refuse, run with exactly the
# arguments given. A function rather than an argv array because the "no argument" probe
# needs an argument list of length zero, and under `set -u` bash 3.2 rejects "${arr[@]}"
# on an empty array while accepting "$@" with no positionals.
bad_probe() {
  local label="$1"; shift
  local out err code
  out="$(mktemp)" err="$(mktemp)"
  env -u VERI_TIMEOUT "$LEAF_TIMEOUT" "$@" >"$out" 2>"$err" && code=0 || code=$?
  [[ "$code" == 2 ]] ||
    problems+=("$label: want exit 2, got $code")
  [[ ! -s "$out" ]] ||
    problems+=("$label: want nothing on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ -s "$err" ]] ||
    problems+=("$label: want a diagnostic on stderr, got nothing")
  rm -f "$out" "$err"
}

# 1. The whole of this step's criterion, as one case: with VERI_TIMEOUT unset the script
#    derives the timeout, and a baseline it cannot derive from is refused rather than
#    guessed at.
#
#    The four good probes are the corners of `max(900, 6 × baseline)`: 0 and 5 are repos
#    whose suite is quick, so the 900 s floor is what today's runs already get and must
#    keep; 150 is the tie (6 × 150 = 900) and 151 the first baseline where the multiple
#    takes over, which is where an off-by-one in the comparison would hide; 200 is the
#    issue's own example — a 200 s suite gets 1200 s without anyone setting anything, the
#    case that killed a Green leaf on #71 at the fixed 900 s.
#
#    The four bad probes are the ways a baseline arrives unusable. `1.5` is the quiet one:
#    the measurement is a wall time, so a decimal is exactly what a careless timing step
#    would hand over, and `[[ 1.5 -gt 150 ]]` cannot evaluate it — bash prints its own
#    arithmetic error and the comparison reads false, which would print 900 and look like
#    a real answer. Exit 2 ("no answer could be obtained") is the honest one: the timing
#    plumbing broke, and the conductor must see that rather than silently run the whole
#    issue on the floor value.
name="VERI_TIMEOUT unset: the baseline derives max(900, 6 × baseline) on stdout; a baseline that is not a whole number >= 0 exits 2 with a diagnostic on stderr and nothing on stdout"
problems=()
good_probe 0 900
good_probe 5 900
good_probe 150 900
good_probe 151 906
good_probe 200 1200
bad_probe "baseline abc" abc
bad_probe "baseline -1" -1
bad_probe "baseline 1.5" 1.5
bad_probe "no argument"
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

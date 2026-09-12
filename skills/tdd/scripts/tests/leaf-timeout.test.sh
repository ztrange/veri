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
#   VERI_TIMEOUT=<n> set        → prints <n> as given and exits 0, whatever the baseline
#                                would have derived: an explicit timeout is the answer,
#                                not an input to the derivation.
#   VERI_TIMEOUT set to anything that is not a whole number >= 1 (`0`, `abc`, `-1`, `1.5`)
#                              → exit 2 with the same fail-closed shape, rather than
#                                falling back to the derivation.
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

# assert_fail_closed <label> <code> <stdout-file> <stderr-file> — the three things every
# refusal owes, whichever way the unusable value arrived. Named once because a refusal is
# one shape: exit 2 ("no answer could be obtained", not exit 1's clean negative), nothing
# on stdout so a conductor reading it in a command substitution cannot capture a refusal
# as a timeout, and a diagnostic on stderr so a human is told which value was wrong.
# Appends to the caller's `problems`, which the case sets up as a global.
assert_fail_closed() {
  local label="$1" code="$2" out="$3" err="$4"
  [[ "$code" == 2 ]] ||
    problems+=("$label: want exit 2, got $code")
  [[ ! -s "$out" ]] ||
    problems+=("$label: want nothing on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ -s "$err" ]] ||
    problems+=("$label: want a diagnostic on stderr, got nothing")
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
  assert_fail_closed "$label" "$code" "$out" "$err"
  rm -f "$out" "$err"
}

# override_probe <veri-timeout> <baseline> — VERI_TIMEOUT set to a usable value: the script
# must print it back byte for byte and exit 0, whatever the baseline would have derived.
# The baseline passed alongside is always one whose derivation differs from the override,
# so a script that quietly re-derived would print the other number and the probe would say
# so. Nothing on stderr: an explicit knob honoured is not a diagnosable event.
override_probe() {
  local timeout="$1" baseline="$2" out err code
  out="$(mktemp)" err="$(mktemp)"
  VERI_TIMEOUT="$timeout" "$LEAF_TIMEOUT" "$baseline" >"$out" 2>"$err" && code=0 || code=$?
  [[ "$code" == 0 ]] ||
    problems+=("VERI_TIMEOUT=$timeout baseline $baseline: want exit 0, got $code")
  [[ "$(cat "$out")" == "$timeout" ]] ||
    problems+=("VERI_TIMEOUT=$timeout baseline $baseline: want $timeout on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ ! -s "$err" ]] ||
    problems+=("VERI_TIMEOUT=$timeout baseline $baseline: want nothing on stderr, got: $(printf '%q' "$(cat "$err")")")
  rm -f "$out" "$err"
}

# bad_override_probe <veri-timeout> — VERI_TIMEOUT set to something that is not a whole
# number >= 1, with a baseline the script could otherwise derive from perfectly well: the
# refusal must be about the override, so falling back to the derivation would be caught
# here as output on stdout where there should be none.
bad_override_probe() {
  local timeout="$1" out err code
  out="$(mktemp)" err="$(mktemp)"
  VERI_TIMEOUT="$timeout" "$LEAF_TIMEOUT" 200 >"$out" 2>"$err" && code=0 || code=$?
  assert_fail_closed "VERI_TIMEOUT=$timeout" "$code" "$out" "$err"
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

# 2. The other half of the same decision: an explicit VERI_TIMEOUT is the conductor's
#    answer, not an input to the derivation. It is printed as given whatever the baseline
#    measured — this is the CLAUDE.md invariant that the three budgets stay on three axes,
#    and a derivation allowed to raise or lower a hand-set timeout would merge the liveness
#    axis with the cost of measuring it. The issue's own third bullet is the 900/200 probe:
#    `VERI_TIMEOUT=900` against a baseline that derives 1200 must still be 900, which is
#    exactly the resumption the conductor did by hand on #71 (`VERI_TIMEOUT=1800`, the
#    second probe here, against a quick baseline that would derive the 900 s floor). 1 is
#    the smallest override the contract admits, and it is below the floor, so it also pins
#    that the floor does not apply to a value the operator chose.
#
#    The bad probes are the ways an override arrives unusable, and they fail closed for a
#    sharper reason than the baseline's do: this one is a value a human typed. `0` is the
#    case ">= 1" exists for and the one a ">= 0" check would wave through — a zero timeout
#    kills every leaf of the run the instant it starts, and each kill costs a stuck retry
#    and a reverted step, so a typo would burn the whole issue looking like model failure.
#    `-1` and `1.5` are the same typo one character away, and `abc` stands for the shell
#    expansion that produced a word instead of a number. Each baseline here is 200 — a
#    measurement the script derives from happily — so the refusal can only be about the
#    override, and a silent fall back to the 1200 s derivation shows up as stdout that
#    should have been empty.
name="explicit VERI_TIMEOUT is printed as given whatever the baseline measured; a VERI_TIMEOUT that is not a whole number >= 1 exits 2 with a diagnostic on stderr and nothing on stdout"
problems=()
override_probe 900 200
override_probe 1800 5
override_probe 1 200
bad_override_probe 0
bad_override_probe abc
bad_override_probe -1
bad_override_probe 1.5
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

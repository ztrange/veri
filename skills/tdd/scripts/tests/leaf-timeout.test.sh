#!/usr/bin/env bash
# Unit tests for scripts/leaf-timeout.sh — sizes the run's hard timeout from the wall time
# preflight measured on the green-baseline run.
#
# Contract under test:
#   leaf-timeout.sh <baseline-seconds>  with VERI_TIMEOUT unset
#                              → prints the larger of 900 and 6 × <baseline-seconds>,
#                                as a whole number of seconds, and exits 0.
#   a baseline that is not a whole number ≥ 0 (`abc`, `-1`, `1.5`, or no argument at all)
#                              → exit 2, a diagnostic on stderr, nothing on stdout.
#   VERI_TIMEOUT=<n> set        → prints <n> as given and exits 0, whatever the baseline.
#   VERI_TIMEOUT set to anything that is not a whole number >= 1 (`0`, `abc`, `-1`, `1.5`)
#                              → exit 2, a diagnostic on stderr, nothing on stdout.
#   leaf-timeout.sh <baseline-seconds> refactor  with VERI_TIMEOUT unset
#                              → the same derivation multiplied by
#                                max(1, VERI_REFACTOR_BUDGET) (default 5).
#   VERI_TIMEOUT=<n> set, refactor
#                              → <n> as given, unmultiplied.
#   leaf-timeout.sh <fast-seconds> --full <full-seconds>
#                              → the derivation run over <full-seconds>, not <fast-seconds>.
#   a full-tier measurement that is not a whole number >= 0 (`abc`, `-1`, `1.5`, or a
#   `--full` with nothing behind it)
#                              → exit 2, a diagnostic on stderr, nothing on stdout.
#
# Run: scripts/tests/leaf-timeout.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LEAF_TIMEOUT="$HERE/../leaf-timeout.sh"

source "$HERE/lib/harness.sh"

capture() {
  probe_out="$(mktemp)" probe_err="$(mktemp)"
  "$@" >"$probe_out" 2>"$probe_err" && probe_code=0 || probe_code=$?
}

capture_done() {
  rm -f "$probe_out" "$probe_err"
}

good_probe() {
  local baseline="$1" want="$2"
  capture env -u VERI_TIMEOUT "$LEAF_TIMEOUT" "$baseline"
  assert_answer "baseline $baseline" "$want"
  capture_done
}

assert_answer() {
  local label="$1" want="$2"
  [[ "$probe_code" == 0 ]] ||
    problems+=("$label: want exit 0, got $probe_code")
  [[ "$(cat "$probe_out")" == "$want" ]] ||
    problems+=("$label: want $want on stdout, got: $(printf '%q' "$(cat "$probe_out")")")
  [[ ! -s "$probe_err" ]] ||
    problems+=("$label: want nothing on stderr, got: $(printf '%q' "$(cat "$probe_err")")")
}

assert_fail_closed() {
  local label="$1"
  [[ "$probe_code" == 2 ]] ||
    problems+=("$label: want exit 2, got $probe_code")
  [[ ! -s "$probe_out" ]] ||
    problems+=("$label: want nothing on stdout, got: $(printf '%q' "$(cat "$probe_out")")")
  [[ -s "$probe_err" ]] ||
    problems+=("$label: want a diagnostic on stderr, got nothing")
}

bad_probe() {
  local label="$1"; shift
  capture env -u VERI_TIMEOUT "$LEAF_TIMEOUT" "$@"
  assert_fail_closed "$label"
  capture_done
}

override_probe() {
  local timeout="$1" baseline="$2"
  capture env VERI_TIMEOUT="$timeout" "$LEAF_TIMEOUT" "$baseline"
  assert_answer "VERI_TIMEOUT=$timeout baseline $baseline" "$timeout"
  capture_done
}

bad_override_probe() {
  local timeout="$1"
  capture env VERI_TIMEOUT="$timeout" "$LEAF_TIMEOUT" 200
  assert_fail_closed "VERI_TIMEOUT=$timeout"
  capture_done
}

refactor_probe() {
  local budget="$1" baseline="$2" want="$3" label
  label="VERI_REFACTOR_BUDGET=$budget baseline $baseline refactor"
  if [[ "$budget" == unset ]]; then
    capture env -u VERI_TIMEOUT -u VERI_REFACTOR_BUDGET "$LEAF_TIMEOUT" "$baseline" refactor
  else
    capture env -u VERI_TIMEOUT VERI_REFACTOR_BUDGET="$budget" "$LEAF_TIMEOUT" "$baseline" refactor
  fi
  assert_answer "$label" "$want"
  capture_done
}

refactor_override_probe() {
  local timeout="$1" budget="$2" baseline="$3" label
  label="VERI_TIMEOUT=$timeout VERI_REFACTOR_BUDGET=$budget baseline $baseline refactor"
  capture env VERI_TIMEOUT="$timeout" VERI_REFACTOR_BUDGET="$budget" "$LEAF_TIMEOUT" "$baseline" refactor
  assert_answer "$label" "$timeout"
  capture_done
}

full_tier_probe() {
  local fast="$1" full="$2" want="$3" label
  label="fast $fast full $full"
  capture env -u VERI_TIMEOUT "$LEAF_TIMEOUT" "$fast" --full "$full"
  assert_answer "$label" "$want"
  capture_done
}

full_tier_override_probe() {
  local timeout="$1" fast="$2" full="$3" label
  label="VERI_TIMEOUT=$timeout fast $fast full $full"
  capture env VERI_TIMEOUT="$timeout" "$LEAF_TIMEOUT" "$fast" --full "$full"
  assert_answer "$label" "$timeout"
  capture_done
}

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

name="leaf-timeout.sh <baseline> refactor: the run's derived timeout × max(1, VERI_REFACTOR_BUDGET), and an explicit VERI_TIMEOUT still printed as given"
problems=()
refactor_probe 5 200 6000
refactor_probe 1 200 1200
refactor_probe 0 200 1200
refactor_probe 3 5 2700
refactor_probe unset 5 4500
refactor_override_probe 900 5 200
refactor_override_probe 1800 3 5
report "$name"

name="a recorded pair of tier measurements: the timeout is derived from the full tier's measurement, not the fast one"
problems=()
full_tier_probe 5 600 3600
report "$name"

name="an explicit VERI_TIMEOUT is printed as given whatever pair of tier measurements is handed in"
problems=()
full_tier_override_probe 900 5 600
full_tier_override_probe 7200 5 20
full_tier_override_probe 1 150 151
report "$name"


name="a full-tier measurement that is not a whole number >= 0 exits 2 with a diagnostic on stderr and nothing on stdout"
problems=()
bad_probe "fast 5 full abc" 5 --full abc
bad_probe "fast 5 full -1" 5 --full -1
bad_probe "fast 5 full 1.5" 5 --full 1.5
bad_probe "fast 5 full missing" 5 --full
report "$name"


finish

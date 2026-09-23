#!/usr/bin/env bash
# Unit tests for scripts/red-divergence.sh — the pure transform that reads a develop-red
# or revise-red leaf's report on stdin and says whether its prediction diverged, so the
# conductor can stop on the surprise instead of sending the step to a blind verify-red
# (issue #356).
#
# Contract under test:
#   stdin  = the leaf's report (the PREDICTED_FAILURE:/PREDICTION:/… lines at its end)
#   stdout = on DIVERGED, a reason carrying the report's PREDICTED_FAILURE:, FAIL_OUTPUT:
#            and PREDICTION_NOTE: values, which is what the conductor writes to
#            .tdd/verify-red.reason for the revise leaf to read
#   exit   = 0 DIVERGED · 3 MATCHED (nothing to do) · 2 no readable PREDICTION:
#
# Admitted to the fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/red-divergence.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DIVERGENCE="$HERE/../../red-divergence.sh"
pass=0 fail=0

# run_on <report> — feed the report to the script on stdin and leave what it said in `out`
# (stdout and stderr together, so a case can assert that a silent exit really is silent) and
# what it exited with in `code`.
run_on() {
  out="$(printf '%s' "$1" | "$DIVERGENCE" 2>&1)" && code=0 || code=$?
}

# verdict <name> — report one case from the `problems` array the case just filled: empty is
# a pass, otherwise a FAIL line naming the case and one indented line per problem. Same
# accounting idiom as classify-bail.test.sh's check().
verdict() {
  local name="$1" p
  if (( ${#problems[@]} )); then
    fail=$((fail + 1))
    echo "FAIL - $name"
    for p in "${problems[@]}"; do echo "    $p"; done
  else
    pass=$((pass + 1))
  fi
}

# The report every case feeds the script, in its two shapes. They differ only in the values
# the reason has to carry and in the PREDICTION: line — which is the thing under test, so
# each case supplies its own, plus any line that follows it, as arguments.
predicted='slugify: command not found'
fail_output='FAIL - slugify lowercases the title (want exit 0, got 127)'
note='the suite died on a missing helper before it reached the assertion'

# report <fail-output> <predicted-failure> <trailing-line>... — a red leaf's report, printed
# with no trailing newline, the way the leaf's own report reaches the script on stdin.
report() {
  local text line
  text="TEST_PATH: skills/tdd/scripts/tests/unit/slugify.test.sh
TARGET_TEST: slugify lowercases the title
AGAINST_UNMODIFIED: FAILS
FAIL_OUTPUT: $1
PREDICTED_FAILURE: $2"
  for line in "${@:3}"; do text+="
$line"; done
  printf '%s' "$text"
}

# matched_report <trailing-line>... — the run failed on the assertion the leaf predicted, so
# nothing in it is a value the reason has to carry.
matched_report() {
  report "FAIL - slugify lowercases the title (want 'a-b', got 'A B')" \
         "the assertion on the slug, want 'a-b', got 'A B'" "$@"
}

# diverged_report <trailing-line>... — the run died on a missing helper instead, so its three
# values are the ones a DIVERGED reason is asserted to carry.
diverged_report() {
  report "$fail_output" "$predicted" "$@"
}

# 1. DIVERGED → exit 0, and the reason carries all three of the report's values, so the
#    revise leaf is told what was predicted, what actually failed, and why they differ.
name="DIVERGED report exits 0 and prints its PREDICTED_FAILURE, FAIL_OUTPUT and PREDICTION_NOTE"
run_on "$(diverged_report 'PREDICTION: DIVERGED' "PREDICTION_NOTE: $note")"
problems=()
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code")
[[ "$out" == *"$predicted"* ]] || problems+=("stdout does not carry the PREDICTED_FAILURE value '$predicted'")
[[ "$out" == *"$fail_output"* ]] || problems+=("stdout does not carry the FAIL_OUTPUT value '$fail_output'")
[[ "$out" == *"$note"* ]] || problems+=("stdout does not carry the PREDICTION_NOTE value '$note'")
if (( ${#problems[@]} )); then problems+=("it printed: $(printf '%s' "$out" | tr '\n' '|')"); fi
verdict "$name"

# 2. MATCHED → exit 3 (nothing to do) and not a byte of output, so the conductor carries
#    on to verify-red exactly as it did before there was a divergence gate.
name="MATCHED report exits 3 and prints nothing"
run_on "$(matched_report 'PREDICTION: MATCHED')"
problems=()
[[ "$code" == 3 ]] || problems+=("want exit 3, got $code")
[[ -z "$out" ]] || problems+=("want no output, got '$(printf '%s' "$out" | tr '\n' '|')'")
verdict "$name"

# 3. A prediction nobody can read — no PREDICTION: line at all, or a value that is neither
#    MATCHED nor DIVERGED — is not a matched one, so it exits 2 and the conductor handles it
#    the way it handles DIVERGED rather than sending the step on to a blind verify-red.
name="report with no PREDICTION: line, or an unrecognised value, exits 2"
problems=()
run_on "$(matched_report)"
[[ "$code" == 2 ]] || problems+=("no PREDICTION: line: want exit 2, got $code")
run_on "$(matched_report 'PREDICTION: probably')"
[[ "$code" == 2 ]] || problems+=("PREDICTION: probably: want exit 2, got $code")
verdict "$name"

# 4. The leaf prompts invite a trailing clause after the verdict word — "PREDICTION: MATCHED
#    — the run printed the assertion the step predicted" is a leaf being helpful. The
#    verdict is the first word; whatever follows it is commentary, so the line is read as
#    that verdict rather than costing the step a revise attempt (issue #428).
name="PREDICTION line with a trailing clause after the verdict word is read as that verdict"
problems=()
run_on "$(matched_report 'PREDICTION: MATCHED — the run printed the assertion the step predicted')"
[[ "$code" == 3 ]] || problems+=("MATCHED with a trailing clause: want exit 3, got $code")
[[ -z "$out" ]] || problems+=("MATCHED with a trailing clause: want no output, got '$(printf '%s' "$out" | tr '\n' '|')'")
run_on "$(diverged_report 'PREDICTION: DIVERGED — it died on a missing helper instead' "PREDICTION_NOTE: $note")"
[[ "$code" == 0 ]] || problems+=("DIVERGED with a trailing clause: want exit 0, got $code")
[[ "$out" == *"$note"* ]] || problems+=("DIVERGED with a trailing clause: stdout does not carry the PREDICTION_NOTE value '$note'")
verdict "$name"

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

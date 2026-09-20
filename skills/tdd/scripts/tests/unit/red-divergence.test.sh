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

# 1. DIVERGED → exit 0, and the reason carries all three of the report's values, so the
#    revise leaf is told what was predicted, what actually failed, and why they differ.
name="DIVERGED report exits 0 and prints its PREDICTED_FAILURE, FAIL_OUTPUT and PREDICTION_NOTE"
predicted='slugify: command not found'
fail_output='FAIL - slugify lowercases the title (want exit 0, got 127)'
note='the suite died on a missing helper before it reached the assertion'
report="TEST_PATH: skills/tdd/scripts/tests/unit/slugify.test.sh
TARGET_TEST: slugify lowercases the title
AGAINST_UNMODIFIED: FAILS
FAIL_OUTPUT: $fail_output
PREDICTED_FAILURE: $predicted
PREDICTION: DIVERGED
PREDICTION_NOTE: $note"
out="$(printf '%s' "$report" | "$DIVERGENCE" 2>&1)" && code=0 || code=$?
problems=()
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code")
[[ "$out" == *"$predicted"* ]] || problems+=("stdout does not carry the PREDICTED_FAILURE value '$predicted'")
[[ "$out" == *"$fail_output"* ]] || problems+=("stdout does not carry the FAIL_OUTPUT value '$fail_output'")
[[ "$out" == *"$note"* ]] || problems+=("stdout does not carry the PREDICTION_NOTE value '$note'")
if (( ${#problems[@]} )); then
  fail=$((fail + 1))
  echo "FAIL - $name"
  for p in "${problems[@]}"; do echo "    $p"; done
  echo "    it printed: $(printf '%s' "$out" | tr '\n' '|')"
else
  pass=$((pass + 1))
fi

# 2. MATCHED → exit 3 (nothing to do) and not a byte of output, so the conductor carries
#    on to verify-red exactly as it did before there was a divergence gate.
name="MATCHED report exits 3 and prints nothing"
report="TEST_PATH: skills/tdd/scripts/tests/unit/slugify.test.sh
TARGET_TEST: slugify lowercases the title
AGAINST_UNMODIFIED: FAILS
FAIL_OUTPUT: FAIL - slugify lowercases the title (want 'a-b', got 'A B')
PREDICTED_FAILURE: the assertion on the slug, want 'a-b', got 'A B'
PREDICTION: MATCHED"
out="$(printf '%s' "$report" | "$DIVERGENCE" 2>&1)" && code=0 || code=$?
problems=()
[[ "$code" == 3 ]] || problems+=("want exit 3, got $code")
[[ -z "$out" ]] || problems+=("want no output, got '$(printf '%s' "$out" | tr '\n' '|')'")
if (( ${#problems[@]} )); then
  fail=$((fail + 1))
  echo "FAIL - $name"
  for p in "${problems[@]}"; do echo "    $p"; done
else
  pass=$((pass + 1))
fi

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

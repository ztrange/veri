#!/usr/bin/env bash
# red-divergence.sh — say whether a red leaf's prediction diverged from what it saw.
#
# Reads a develop-red or revise-red report on stdin. A leaf that predicted one failure and
# got another reports `PREDICTION: DIVERGED`: Beck stops on that surprise, because the test
# is then the suspect. Exits 0 on DIVERGED and prints the reason the conductor writes to
# .tdd/verify-red.reason — the report's PREDICTED_FAILURE:, FAIL_OUTPUT: and
# PREDICTION_NOTE: values, so the revise leaf is told what was predicted, what actually
# failed, and why the leaf could not reconcile them.
#
# Usage:   red-divergence.sh < <the leaf's report>
set -uo pipefail

prediction="" predicted="" fail_output="" note=""
while IFS= read -r line || [[ -n "$line" ]]; do
  case "$line" in
    "PREDICTION: "*)      prediction="${line#PREDICTION: }" ;;
    "PREDICTED_FAILURE: "*) predicted="${line#PREDICTED_FAILURE: }" ;;
    "FAIL_OUTPUT: "*)     fail_output="${line#FAIL_OUTPUT: }" ;;
    "PREDICTION_NOTE: "*) note="${line#PREDICTION_NOTE: }" ;;
  esac
done

# The verdict is the line's first word, less any punctuation it ends in: the leaf prompts
# invite a trailing clause after it ("PREDICTION: MATCHED — the run printed the assertion
# the step predicted"), and a comma, semicolon, colon or full stop joins that clause as
# naturally as a space does ("PREDICTION: DIVERGED, but only in the message"). A leaf being
# helpful must not cost the step a revise attempt (issues #428, #433). The match stays
# whole-word rather than a substring, so anything that is neither verdict once stripped is
# still unreadable and the strict 1/2 distinction holds.
verdict="${prediction%% *}"
case "${verdict%[,;:.]}" in
  DIVERGED) ;;
  MATCHED)  exit 3 ;;
  *)        exit 2 ;;
esac

cat <<REASON
The red leaf's prediction diverged from the failure it saw, so the test is the suspect.

PREDICTED_FAILURE: $predicted
FAIL_OUTPUT: $fail_output
PREDICTION_NOTE: $note
REASON

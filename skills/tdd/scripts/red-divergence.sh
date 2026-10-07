#!/bin/sh
# red-divergence.sh — say whether a red leaf's prediction diverged from what it saw: a shim over veri/red_divergence.py.
#
# Reads a develop-red or revise-red report on stdin. A leaf that predicted one failure and
# got another reports `PREDICTION: DIVERGED`: Beck stops on that surprise, because the test
# is then the suspect.
#
# usage: red-divergence.sh (a develop-red or revise-red report on stdin)
#
# stdout:  on DIVERGED, the reason the conductor writes to .tdd/verify-red.reason — the
#          report's PREDICTED_FAILURE:, FAIL_OUTPUT: and PREDICTION_NOTE: values.
# exit:    0 DIVERGED · 3 MATCHED (nothing to do) · 2 no readable PREDICTION: line
exec python3 "$(dirname "$0")/veri/red_divergence.py" "$@"

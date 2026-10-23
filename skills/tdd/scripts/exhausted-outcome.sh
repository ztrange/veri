#!/bin/sh
# exhausted-outcome.sh — say which of the three outcomes an exhausted step's last leaf reported: a shim over veri/exhausted_outcome.py.
#
# When a step's revise budget runs out, the conductor sends one more leaf and asks it which of
# two things is true of the criterion nothing could satisfy: that it carries more
# than one behaviour, reported as `SPLIT:` lines the way Green already accepts them, or that it
# needs a decision the run has no authority to make, reported as `NEEDS_USER:`. Answering
# neither is the third outcome, and it is not an error: the conductor bails the step exactly as
# it does today.
#
# This pure transform reads the leaf's full raw output on stdin — free-form reasoning and all —
# and resolves it to one of those three, the way parse-verdict.sh resolves a verifier's.
#
# usage: exhausted-outcome.sh < leaf-output.txt
#
# stdout:  the split criteria, one bare text per line (what add-ledger-step.sh takes as
#          positional arguments) · or the needs-user answer verbatim (what the user reads on
#          the issue) · or nothing.
# exit:    0 split · 1 needs the user · 3 neither. Never 2: a leaf that volunteered neither
#          answer gave an answer, not a plumbing failure, so this is veri's "nothing to do".
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/exhausted_outcome.py" "$@"

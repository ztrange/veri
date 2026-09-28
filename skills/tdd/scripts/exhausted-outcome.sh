#!/usr/bin/env bash
# exhausted-outcome.sh — say which of the three outcomes an exhausted step's last leaf reported.
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
# Usage:   exhausted-outcome.sh < leaf-output.txt
#
# stdout:  the split criteria, one bare text per line (what add-ledger-step.sh takes as
#          positional arguments) · or the needs-user answer verbatim (what the user reads on
#          the issue) · or nothing.
# exit:    0 split · 1 needs the user · 3 neither. Never 2: a leaf that volunteered neither
#          answer gave an answer, not a plumbing failure, so this is veri's "nothing to do".
set -euo pipefail

# hazard: `|| [[ -n ... ]]` keeps a last line that has no trailing newline.
lines=()
while IFS= read -r line || [[ -n "$line" ]]; do
  lines+=( "$line" )
done

criteria=()
uidx=-1
utail=""
for i in "${!lines[@]}"; do
  if [[ "${lines[$i]}" =~ ^SPLIT:[[:space:]]*(.*)$ ]]; then
    criteria+=( "${BASH_REMATCH[1]}" )
  elif [[ "${lines[$i]}" =~ ^NEEDS_USER:[[:space:]]*(.*)$ ]]; then
    uidx=$i
    utail="${BASH_REMATCH[1]}"
  fi
done

if (( ${#criteria[@]} > 0 )); then
  printf '%s\n' "${criteria[@]}"
  exit 0
fi

if (( uidx >= 0 )); then
  answer=( "$utail" "${lines[@]:uidx+1}" )
  printf '%s\n' "${answer[@]}"
  exit 1
fi

exit 3

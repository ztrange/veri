#!/usr/bin/env bash
# Unit tests for scripts/pin-fast-tier.sh — the conductor check run after verify-pin PASS and
# before the `test: pin` commit.
#
# Contract under test:
#   pin-fast-tier.sh <fast-cmd>, run from the worktree
#       → exit 1 and .tdd/verify-pin.reason holding the command's own output when it fails
#       → exit 2 printing a usage line when given no argument
#
# Run: scripts/tests/pin-fast-tier.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CHECK="$HERE/../pin-fast-tier.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"
mkdir -p "$work/.tdd"
printf '#!/bin/sh\necho "FAIL - run-finished.test.sh builds its own scratch instead of the harness'"'"'s"\necho "0 passed, 1 failed"\nexit 1\n' > "$work/fast-red"
chmod +x "$work/fast-red"

red_out="$(cd "$work" && "$CHECK" "$work/fast-red" 2>&1)"; red_code=$?
reason="$(cat "$work/.tdd/verify-pin.reason" 2>/dev/null)"
if [[ "$red_code" == 1 && "$reason" == *"builds its own scratch instead of the harness's"* ]]; then ok; else
  no "pin-fast-tier #1747: a failing fast command → exit 1 and the guard's output in .tdd/verify-pin.reason (code=$red_code reason=$reason out=$red_out)"
fi

bare="$(scratch_dir)"
bare_out="$(cd "$bare" && "$CHECK" 2> "$bare/err")"; bare_code=$?
bare_err="$(cat "$bare/err")"
if [[ "$bare_code" == 2 && -z "$bare_out" && "$bare_err" == *"usage: pin-fast-tier.sh"* && ! -e "$bare/.tdd/verify-pin.reason" ]]; then ok; else
  no "pin-fast-tier #1747: no argument → usage on stderr, exit 2, no .tdd/verify-pin.reason (code=$bare_code out=$bare_out err=$bare_err)"
fi

finish

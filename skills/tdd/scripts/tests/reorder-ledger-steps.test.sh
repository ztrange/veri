#!/usr/bin/env bash
# Tests for scripts/reorder-ledger-steps.sh — the sanctioned reorder of unchecked ledger steps.
# Operates on a real temp file.
#
# Run: scripts/tests/reorder-ledger-steps.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REORDER="$HERE/../reorder-ledger-steps.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

led="$work/issue-125.md"
printf '# Plan for #125\n\n- [ ] Without dev tools compiled in, payment succeeds even when a failure choice is left in localStorage\n- [ ] The failure choice is remembered in localStorage like the other dev menus\n' > "$led"
want="$(printf '# Plan for #125\n\n- [ ] The failure choice is remembered in localStorage like the other dev menus\n- [ ] Without dev tools compiled in, payment succeeds even when a failure choice is left in localStorage\n')"
"$REORDER" "$led" "even when a failure choice is left in localStorage" after "remembered in localStorage" > "$work/out" 2> "$work/err"; code=$?
{ [[ "$code" == 0 ]] && [[ "$(cat "$led")" == "$want" ]]; } \
  && ok || no "#1550: the 'even when … left in localStorage' step placed first ends second after the remembered-choice step, every line's bytes kept (code=$code err='$(cat "$work/err")')"

led="$work/issue-126.md"
printf '# Plan for #126\n\n- [ ] alpha step\n- [ ] bravo step\n- [ ] charlie step\n' > "$led"
want="$(printf '# Plan for #126\n\n- [ ] alpha step\n- [ ] charlie step\n- [ ] bravo step\n')"
"$REORDER" "$led" "charlie" before "bravo" > "$work/out" 2> "$work/err"; code=$?
{ [[ "$code" == 0 ]] && [[ "$(cat "$led")" == "$want" ]]; } \
  && ok || no "#1550: the last step moved 'before' the middle step lands just ahead of it, every other line's order kept (code=$code err='$(cat "$work/err")')"

finish

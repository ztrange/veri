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

led="$work/issue-127.md"
printf '# Plan for #127\n\n- [x] alpha step\n- [ ] bravo step\n- [ ] charlie step\n' > "$led"
cp "$led" "$work/before"
"$REORDER" "$led" "alpha" after "charlie" > "$work/out" 2> "$work/err"; code=$?
{ [[ "$code" == 1 ]] && cmp -s "$led" "$work/before" && grep -F "alpha" "$work/err" > /dev/null; } \
  && ok || no "#1550: a ticked step to move exits 1, leaves the ledger byte-identical and names the step on stderr (code=$code err='$(cat "$work/err")')"

led="$work/issue-128.md"
printf '# Plan for #128\n\n- [x] alpha step ⟂ refactor pending\n- [ ] bravo step\n- [ ] charlie step\n' > "$led"
cp "$led" "$work/before"
"$REORDER" "$led" "charlie" after "alpha" > "$work/out" 2> "$work/err"; code=$?
{ [[ "$code" == 1 ]] && cmp -s "$led" "$work/before" && grep -F "alpha" "$work/err" > /dev/null; } \
  && ok || no "#1550: a ticked anchor carrying the refactor-pending mark exits 1, leaves the ledger byte-identical and names the anchor on stderr (code=$code err='$(cat "$work/err")')"

led="$work/issue-129.md"
printf '# Plan for #129\n\n- [ ] alpha step ⟂ refactor pending\n- [ ] bravo step\n- [ ] charlie step\n' > "$led"
cp "$led" "$work/before"
"$REORDER" "$led" "alpha" after "charlie" > "$work/out" 2> "$work/err"; code=$?
{ [[ "$code" == 1 ]] && cmp -s "$led" "$work/before" && grep -F "alpha" "$work/err" > /dev/null; } \
  && ok || no "#1550: an unchecked step to move carrying the refactor-pending mark exits 1, leaves the ledger byte-identical and names the step on stderr (code=$code err='$(cat "$work/err")')"

led="$work/issue-130.md"
printf '# Plan for #130\n\n- [ ] alpha step\n- [ ] bravo step ⟂ refactor pending\n- [ ] charlie step\n' > "$led"
cp "$led" "$work/before"
"$REORDER" "$led" "alpha" after "bravo" > "$work/out" 2> "$work/err"; code=$?
{ [[ "$code" == 1 ]] && cmp -s "$led" "$work/before" && grep -F "bravo" "$work/err" > /dev/null; } \
  && ok || no "#1550: an unchecked anchor carrying the refactor-pending mark exits 1, leaves the ledger byte-identical and names the anchor on stderr (code=$code err='$(cat "$work/err")')"

led="$work/issue-131.md"
printf '# Plan for #131\n\n- [ ] alpha step\n- [ ] bravo step\n- [ ] charlie step\n' > "$led"
cp "$led" "$work/before"
"$REORDER" "$led" "zulu" after "charlie" > "$work/out" 2> "$work/err"; code=$?
{ [[ "$code" == 1 ]] && cmp -s "$led" "$work/before" && grep -F "zulu" "$work/err" > /dev/null; } \
  && ok || no "#1550: a step substring matching no step exits 1, leaves the ledger byte-identical and names the substring on stderr (code=$code err='$(cat "$work/err")')"

led="$work/issue-132.md"
printf '# Plan for #132\n\n- [ ] alpha step\n- [ ] bravo step\n- [ ] charlie step\n' > "$led"
cp "$led" "$work/before"
"$REORDER" "$led" "alpha" after "zulu" > "$work/out" 2> "$work/err"; code=$?
{ [[ "$code" == 1 ]] && cmp -s "$led" "$work/before" && grep -F "zulu" "$work/err" > /dev/null; } \
  && ok || no "#1550: an anchor substring matching no step exits 1, leaves the ledger byte-identical and names the substring on stderr (code=$code err='$(cat "$work/err")')"

led="$work/issue-133.md"
printf '# Plan for #133\n\n- [ ] alpha step\n- [ ] bravo step\n- [ ] charlie step\n' > "$led"
cp "$led" "$work/before"
"$REORDER" "$led" "step" after "charlie" > "$work/out" 2> "$work/err"; code=$?
{ [[ "$code" == 1 ]] && cmp -s "$led" "$work/before" && grep -F "step" "$work/err" > /dev/null; } \
  && ok || no "#1550: a step substring matching more than one step exits 1, leaves the ledger byte-identical and names the substring on stderr (code=$code err='$(cat "$work/err")')"

led="$work/issue-134.md"
printf '# Plan for #134\n\n- [ ] alpha step\n- [ ] bravo shared\n- [ ] charlie shared\n' > "$led"
cp "$led" "$work/before"
"$REORDER" "$led" "alpha" after "shared" > "$work/out" 2> "$work/err"; code=$?
{ [[ "$code" == 1 ]] && cmp -s "$led" "$work/before" && grep -F "shared" "$work/err" > /dev/null; } \
  && ok || no "#1550: an anchor substring matching more than one step exits 1, leaves the ledger byte-identical and names the substring on stderr (code=$code err='$(cat "$work/err")')"

led="$work/issue-135.md"
printf '# Plan for #135\n\n- [ ] alpha step\n- [ ] bravo step\n- [ ] charlie step\n' > "$led"
cp "$led" "$work/before"
"$REORDER" "$led" "alpha" sideways "charlie" > "$work/out" 2> "$work/err"; code=$?
{ [[ "$code" == 2 ]] && cmp -s "$led" "$work/before"; } \
  && ok || no "#1550: a position other than before/after exits 2 and leaves the ledger byte-identical (code=$code err='$(cat "$work/err")')"

finish

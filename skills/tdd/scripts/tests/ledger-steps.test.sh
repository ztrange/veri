#!/usr/bin/env bash
# Tests for scripts/ledger-steps.sh — the entry point that prints lib/ledger.sh's
# `ledger_steps` records for the document on its stdin.
#
# Run: scripts/tests/ledger-steps.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STEPS="$HERE/../ledger-steps.sh"
NEXT="$HERE/../next-unchecked.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

printf '# Plan for #42\n\nprose\n\n- [x] add lowercasing ⟦criterion 1⟧ ⟂ refactor pending\n- [ ] strip edge hyphens ⟦added⟧ ⟦criterion 2⟧\n' > "$work/ledger.md"
want="$(printf '1\tdone\tstep\t1\t0\t1\tadd lowercasing ⟦criterion 1⟧\n2\topen\tstep\t0\t1\t2\tstrip edge hyphens ⟦added⟧ ⟦criterion 2⟧')"
got="$("$STEPS" < "$work/ledger.md" 2> "$work/err")"; code=$?
{ [[ "$code" == 0 ]] && [[ "$got" == "$want" ]] && [[ ! -s "$work/err" ]]; } \
  && ok || no "prints ledger_steps's records for its stdin, and nothing else (code=$code stderr='$(cat "$work/err")')
$(diff <(printf '%s\n' "$want") <(printf '%s\n' "$got") | sed 's/^/    /')"

step='replace skills/tdd/scripts/tests/status.test.sh case "status prints the plan" with a pytest case ⟦replaces-case⟧ ⟦criterion 6⟧'
printf '# Plan for #42\n\n- [x] add lowercasing ⟦criterion 5⟧\n- [ ] %s\n' "$step" > "$work/replaces.md"
want="$(printf '1\tdone\tstep\t0\t0\t5\tadd lowercasing ⟦criterion 5⟧\n2\topen\tstep\t0\t0\t6\t%s' "$step")"
got="$("$STEPS" < "$work/replaces.md" 2> "$work/err")"; code=$?
next="$("$NEXT" < "$work/replaces.md")"; next_code=$?
{ [[ "$code" == 0 ]] && [[ "$got" == "$want" ]] && [[ "$next_code" == 0 ]] && [[ "$next" == "$step" ]]; } \
  && ok || no "an open ⟦replaces-case⟧ step is kind step, added 0, criterion 6, and next-unchecked hands it out (code=$code next_code=$next_code next='$next')
$(diff <(printf '%s\n' "$want") <(printf '%s\n' "$got") | sed 's/^/    /')"

printf '# Plan for #42\n\nprose\n\n- [x] add lowercasing ⟦criterion 1⟧ ⟂ refactor pending\n- [X] trim spaces ⟦added⟧ ⟦criterion 2⟧\n- [x] tidy names ⟦added⟧ ⟦criterion 3⟧ ⟂ refactor pending\n- [ ] strip edge hyphens ⟦criterion 3⟧\n  - [ ] note without a criterion\n- [ ] a person reads the page ⟦human-owed⟧ ⟦criterion 4⟧\n- [ ] `make test` is green ⟦full-suite⟧ ⟦criterion 5⟧' > "$work/kinds.md"
want="$(printf '%s\n' \
  $'1\tdone\tstep\t1\t0\t1\tadd lowercasing ⟦criterion 1⟧' \
  $'2\tdone\tstep\t0\t1\t2\ttrim spaces ⟦added⟧ ⟦criterion 2⟧' \
  $'3\tdone\tstep\t1\t1\t3\ttidy names ⟦added⟧ ⟦criterion 3⟧' \
  $'4\topen\tstep\t0\t0\t3\tstrip edge hyphens ⟦criterion 3⟧' \
  $'5\topen\tstep\t0\t0\t\tnote without a criterion' \
  $'6\topen\thuman-owed\t0\t0\t4\ta person reads the page ⟦human-owed⟧ ⟦criterion 4⟧' \
  $'7\topen\tfull-suite\t0\t0\t5\t`make test` is green ⟦full-suite⟧ ⟦criterion 5⟧')"
got="$("$STEPS" < "$work/kinds.md" 2> "$work/err")"; code=$?
{ [[ "$code" == 0 ]] && [[ "$got" == "$want" ]] && [[ ! -s "$work/err" ]]; } \
  && ok || no "with no argument prints ledger_steps's records for every step kind and mark (code=$code stderr='$(cat "$work/err")')
$(diff <(printf '%s\n' "$want") <(printf '%s\n' "$got") | sed 's/^/    /')"

printf '# Plan for #42\n\n- [x] add lowercasing ⟦criterion 1⟧\n- [ ] a person reads the page ⟦human-owed⟧ ⟦criterion 2⟧\n- [ ] `make test` is green ⟦full-suite⟧ ⟦criterion 3⟧\n- [ ] strip edge hyphens ⟦criterion 4⟧\n' > "$work/open.md"
printf '# Plan for #42\n\n- [x] add lowercasing ⟦criterion 1⟧\n- [ ] a person reads the page ⟦human-owed⟧ ⟦criterion 2⟧\n- [ ] `make test` is green ⟦full-suite⟧ ⟦criterion 3⟧\n' > "$work/none.md"
pending="$("$STEPS" current < "$work/kinds.md" 2> "$work/err")"; pending_code=$?
open="$("$STEPS" current < "$work/open.md" 2>> "$work/err")"; open_code=$?
none="$("$STEPS" current < "$work/none.md" 2>> "$work/err")"; none_code=$?
{ [[ "$pending_code" == 0 ]] && [[ "$pending" == 'add lowercasing ⟦criterion 1⟧' ]] \
  && [[ "$open_code" == 0 ]] && [[ "$open" == 'strip edge hyphens ⟦criterion 4⟧' ]] \
  && [[ "$none_code" == 3 ]] && [[ -z "$none" ]] && [[ ! -s "$work/err" ]]; } \
  && ok || no "current prints the first refactor-pending step, else the first open step-kind step, else exits 3 with no output (pending_code=$pending_code pending='$pending' open_code=$open_code open='$open' none_code=$none_code none='$none' stderr='$(cat "$work/err")')"

printf '# Plan for #42\n\n- [ ] add lowercasing ⟦criterion 1⟧\n- [ ] `make test` is green ⟦full-suite⟧ ⟦criterion 2⟧\n' > "$work/undone.md"
: > "$work/err"
last="$("$STEPS" last-done < "$work/kinds.md" 2> "$work/err")"; last_code=$?
undone="$("$STEPS" last-done < "$work/undone.md" 2>> "$work/err")"; undone_code=$?
{ [[ "$last_code" == 0 ]] && [[ "$last" == 'tidy names ⟦added⟧ ⟦criterion 3⟧' ]] \
  && [[ "$undone_code" == 3 ]] && [[ -z "$undone" ]] && [[ ! -s "$work/err" ]]; } \
  && ok || no "last-done prints the last done step with ⟂ refactor pending cut, else exits 3 with no output (last_code=$last_code last='$last' undone_code=$undone_code undone='$undone' stderr='$(cat "$work/err")')"

printf '# Plan for #42\n\n- [x] add lowercasing ⟦criterion 1⟧\n- [x]\n- [ ] strip edge hyphens ⟦criterion 2⟧\n' > "$work/empty.md"
"$STEPS" last-done < "$work/empty.md" > "$work/out" 2> "$work/err"; code=$?
{ [[ "$code" == 0 ]] && cmp -s <(printf '\n') "$work/out" && [[ ! -s "$work/err" ]]; } \
  && ok || no "last-done counts a done step with empty text as done: prints an empty line and exits 0, not 3 (code=$code out='$(cat "$work/out")' bytes=$(wc -c < "$work/out" | tr -d ' ') stderr='$(cat "$work/err")')"

printf '## What is happening\n\n- [ ] a checkbox in the prose\n\n## Acceptance criteria\n\n- [ ] first criterion\n- [ ] second criterion carries `$S` and "quotes"\n\n## Notes\n\n- [ ] a checkbox after the section\n' > "$work/body.md"
: > "$work/err"
second="$("$STEPS" criterion 2 < "$work/body.md" 2> "$work/err")"; second_code=$?
past="$("$STEPS" criterion 3 < "$work/body.md" 2>> "$work/err")"; past_code=$?
{ [[ "$second_code" == 0 ]] && [[ "$second" == 'second criterion carries `$S` and "quotes"' ]] \
  && [[ "$past_code" == 3 ]] && [[ -z "$past" ]] && [[ ! -s "$work/err" ]]; } \
  && ok || no "criterion <k> prints the k-th checkbox under ## Acceptance criteria only, else exits 3 with no output (second_code=$second_code second='$second' past_code=$past_code past='$past' stderr='$(cat "$work/err")')"

printf '## Acceptance criteria\n\n- [ ] first criterion\n- [ ] last criterion, no final newline' > "$work/no-eol.md"
got="$("$STEPS" criterion 2 < "$work/no-eol.md" 2> "$work/err")"; code=$?
{ [[ "$code" == 0 ]] && [[ "$got" == 'last criterion, no final newline' ]] && [[ ! -s "$work/err" ]]; } \
  && ok || no "criterion <k> reads the last criterion of a body with no final newline (code=$code got='$got' stderr='$(cat "$work/err")')"

finish

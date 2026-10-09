#!/usr/bin/env bash
# Tests for scripts/ledger-steps.sh — the entry point that prints lib/ledger.sh's
# `ledger_steps` records for the document on its stdin.
#
# Run: scripts/tests/ledger-steps.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STEPS="$HERE/../ledger-steps.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

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

printf '# Plan for #42\n\n- [x] add lowercasing ⟦criterion 1⟧\n- [x] strip edge hyphens ⟦criterion 2⟧\n' > "$work/ticked.md"
printf '# Plan for #42\n\nprose\n' > "$work/empty.md"
: > "$work/err"
want_open="$("$STEPS" current < "$work/open.md" 2>> "$work/err")"
want_ticked="$("$STEPS" last-done < "$work/ticked.md" 2>> "$work/err")"
either_open="$("$STEPS" current-or-last-done < "$work/open.md" 2>> "$work/err")"; either_open_code=$?
either_ticked="$("$STEPS" current-or-last-done < "$work/ticked.md" 2>> "$work/err")"; either_ticked_code=$?
either_empty="$("$STEPS" current-or-last-done < "$work/empty.md" 2>> "$work/err")"; either_empty_code=$?
{ [[ "$either_open_code" == 0 ]] && [[ "$either_open" == "$want_open" ]] && [[ "$either_open" == 'strip edge hyphens ⟦criterion 4⟧' ]] \
  && [[ "$either_ticked_code" == 0 ]] && [[ "$either_ticked" == "$want_ticked" ]] && [[ "$either_ticked" == 'strip edge hyphens ⟦criterion 2⟧' ]] \
  && [[ "$either_empty_code" == 3 ]] && [[ -z "$either_empty" ]] && [[ ! -s "$work/err" ]]; } \
  && ok || no "current-or-last-done prints what current prints with a step open, what last-done prints with every step ticked, and exits 3 with nothing for a ledger with no step (open=$either_open_code '$either_open' ticked=$either_ticked_code '$either_ticked' empty=$either_empty_code '$either_empty' stderr='$(cat "$work/err")')"

"$STEPS" bogus < "$work/kinds.md" > "$work/out" 2> "$work/err"; code=$?
{ [[ "$code" == 2 ]] && [[ ! -s "$work/out" ]] \
  && cmp -s <(printf 'usage: ledger-steps.sh [current|last-done|current-or-last-done|criterion <k>]\n') "$work/err"; } \
  && ok || no "bogus exits 2 with nothing on stdout and stderr exactly the one usage line (code=$code out='$(cat "$work/out")' stderr='$(cat "$work/err")')"

ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
mkdir -p "$work/elsewhere"
answer() {
  local out err code
  out="$(cd "$1" && "$2" "${@:4}" < "$3" 2> "$work/answer-err")"; code=$?
  err="$(cat "$work/answer-err")"
  printf 'stdout:\n%s\nstderr:\n%s\nexit %s\n' "$out" "$err" "$code"
}
in_place="$(answer "$HERE/.." "$STEPS" "$work/kinds.md"; answer "$HERE/.." "$STEPS" "$work/none.md" current)"
linked="$(answer "$work/elsewhere" "$work/linked-skill/scripts/ledger-steps.sh" "$work/kinds.md"
  answer "$work/elsewhere" "$work/linked-skill/scripts/ledger-steps.sh" "$work/none.md" current)"
{ [[ "$linked" == "$in_place" ]] && [[ "$in_place" == "stdout:"$'\n1\tdone\t'*$'\nexit 0\nstdout:\n\nstderr:\n\nexit 3' ]]; } \
  && ok || no "ledger-steps.sh run through a symlink to the skill directory and from another working directory answers as it does when run in place
$(diff <(printf '%s\n' "$in_place") <(printf '%s\n' "$linked") | sed 's/^/    /')"

finish

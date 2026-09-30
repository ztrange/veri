#!/usr/bin/env bash
# Tests for scripts/ledger-steps.sh — the entry point that prints lib/ledger.sh's
# `ledger_steps` records for the document on its stdin.
#
# Run: scripts/tests/ledger-steps.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STEPS="$HERE/../ledger-steps.sh"
source "$HERE/lib/harness.sh"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

printf '# Plan for #42\n\nprose\n\n- [x] add lowercasing ⟦criterion 1⟧ ⟂ refactor pending\n- [ ] strip edge hyphens ⟦added⟧ ⟦criterion 2⟧\n' > "$work/ledger.md"
want="$(printf '1\tdone\tstep\t1\t0\t1\tadd lowercasing ⟦criterion 1⟧\n2\topen\tstep\t0\t1\t2\tstrip edge hyphens ⟦added⟧ ⟦criterion 2⟧')"
got="$("$STEPS" < "$work/ledger.md" 2> "$work/err")"; code=$?
{ [[ "$code" == 0 ]] && [[ "$got" == "$want" ]] && [[ ! -s "$work/err" ]]; } \
  && ok || no "prints ledger_steps's records for its stdin, and nothing else (code=$code stderr='$(cat "$work/err")')
$(diff <(printf '%s\n' "$want") <(printf '%s\n' "$got") | sed 's/^/    /')"

finish

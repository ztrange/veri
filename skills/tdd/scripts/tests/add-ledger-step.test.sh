#!/usr/bin/env bash
# Tests for scripts/add-ledger-step.sh — growing the ledger while a run is under way: it
# inserts a step, marked ⟦added⟧, next to an anchor step already in the plan (issue #360).
# Operates on a real temp file, as tick-ledger.test.sh does.
#
# Run: scripts/tests/add-ledger-step.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ADD="$HERE/../add-ledger-step.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# check <name> <code> <want> — the run exited 0 and left the ledger exactly <want>; a
# mismatch names the case and prints the diff, indented under it.
check() {
  local name="$1" code="$2" want="$3" got
  got="$(cat "$led")"
  if [[ "$code" == 0 && "$got" == "$want" ]]; then
    ok
  else
    no "$name (code=$code)"
    diff <(printf '%s\n' "$want") <(printf '%s\n' "$got") | sed 's/^/    /'
  fi
}

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

led="$work/issue-42.md"
seed() { printf '# Plan for #42\n\n- [x] lowercase the slug ⟦criterion 1⟧\n- [ ] collapse to single hyphen ⟦criterion 2⟧\n- [ ] strip edge hyphens ⟦criterion 3⟧\n' > "$led"; }

# 1. `after` inserts the text as an unchecked step on the line following the anchor,
#    marked ⟦added⟧ and carrying the anchor's own criterion, and exits 0
seed
"$ADD" "$led" after 'collapse to single hyphen' 'collapse a unicode dash too'; code=$?
want='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] collapse a unicode dash too ⟦added⟧ ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'
check "after: inserts the added step below the anchor, carrying its criterion" "$code" "$want"

# 2. `before` inserts several texts, in the order given, on the lines above the anchor
seed
"$ADD" "$led" before 'collapse to single hyphen' 'one more edge case' 'and another'; code=$?
want='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] one more edge case ⟦added⟧ ⟦criterion 2⟧
- [ ] and another ⟦added⟧ ⟦criterion 2⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'
check "before: inserts both texts, in order, on the lines above the anchor" "$code" "$want"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

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

# check_code <name> <code> <want-code> <want> — the run exited <want-code> and left the
# ledger exactly <want>; a mismatch names the case and prints the diff, indented under it.
check_code() {
  local name="$1" code="$2" want_code="$3" want="$4" got
  got="$(cat "$led")"
  if [[ "$code" == "$want_code" && "$got" == "$want" ]]; then
    ok
  else
    no "$name (code=$code)"
    diff <(printf '%s\n' "$want") <(printf '%s\n' "$got") | sed 's/^/    /'
  fi
}

# check <name> <code> <want> — check_code for a case that expects the run to have succeeded.
check() { check_code "$1" "$2" 0 "$3"; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

led="$work/issue-42.md"

# seed_lines <step-line>... — write a ledger of exactly those steps under the plan heading.
seed_lines() { { printf '# Plan for #42\n\n'; printf '%s\n' "$@"; } > "$led"; }

# seed — the three-step plan most cases start from.
seed() {
  seed_lines '- [x] lowercase the slug ⟦criterion 1⟧' \
             '- [ ] collapse to single hyphen ⟦criterion 2⟧' \
             '- [ ] strip edge hyphens ⟦criterion 3⟧'
}

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

# 3. an anchor step carrying no ⟦criterion k⟧ yields an added step carrying none
seed_lines '- [ ] collapse to single hyphen' '- [ ] strip edge hyphens ⟦criterion 3⟧'
"$ADD" "$led" after 'collapse to single hyphen' 'collapse a unicode dash too'; code=$?
want='# Plan for #42

- [ ] collapse to single hyphen
- [ ] collapse a unicode dash too ⟦added⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'
check "no criterion on the anchor: the added step carries none either" "$code" "$want"

# 4. over budget: the call is all or nothing — no checkbox is inserted, it exits 1, and every
#    text lands as a plain bullet under a trailing `## Owed steps` heading. Two texts against
#    a budget of one, so it is the texts given that overflow, not steps already added.
seed
VERI_STEP_GROWTH=1 "$ADD" "$led" before 'collapse to single hyphen' 'one more edge case' 'and another'; code=$?
want='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧

## Owed steps

- one more edge case
- and another'
check_code "over budget: inserts no checkbox, exits 1, and owes both texts as plain bullets" \
  "$code" 1 "$want"

# 5. an anchor that matches no step, and one that matches more than one, are both refusals:
#    exit 2, and the ledger is left byte-identical. Run both against the same seeded ledger —
#    a change made by either run would survive into the final comparison.
seed
"$ADD" "$led" after 'no such step' 'collapse a unicode dash too'; code1=$?
"$ADD" "$led" after 'hyphen' 'collapse a unicode dash too'; code2=$?
want='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'
check_code "ambiguous or absent anchor: exits 2 and leaves the ledger byte-identical" \
  "$code1/$code2" "2/2" "$want"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

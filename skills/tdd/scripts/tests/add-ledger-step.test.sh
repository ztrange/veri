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

# seeded — the three-step plan most cases start from, as `seed` leaves it on disk. A case
# that expects the ledger unchanged, or unchanged but for an appended block, says so against
# this string rather than a copy of it, so the two cannot drift apart.
seeded='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'

# seed — write that plan to the ledger.
seed() { printf '%s\n' "$seeded" > "$led"; }

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
want="$seeded"'

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
want="$seeded"
check_code "ambiguous or absent anchor: exits 2 and leaves the ledger byte-identical" \
  "$code1/$code2" "2/2" "$want"

# 6. The budget variable itself: unset means three, so three texts in one call fit; a value
#    that is not a non-negative integer is a refusal rather than a fallback to the default —
#    exit 2, ledger byte-identical. `three` and set-but-empty are both asked against the
#    ledger the first run left, so a change made by either would survive into the comparison.
seed
env -u VERI_STEP_GROWTH "$ADD" "$led" after 'collapse to single hyphen' \
  'first added' 'second added' 'third added'; code1=$?
VERI_STEP_GROWTH=three "$ADD" "$led" after 'collapse to single hyphen' 'a fourth'; code2=$?
VERI_STEP_GROWTH= "$ADD" "$led" after 'collapse to single hyphen' 'a fourth'; code3=$?
want='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] first added ⟦added⟧ ⟦criterion 2⟧
- [ ] second added ⟦added⟧ ⟦criterion 2⟧
- [ ] third added ⟦added⟧ ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'
check_code "unset allows three added steps; a non-integer or empty budget exits 2, ledger untouched" \
  "$code1/$code2/$code3" "0/2/2" "$want"

# 7. `instead-of` is a third placement: the texts land where the anchor step was and the
#    anchor itself is gone, under the same budget and owed-steps refusal the other two obey.
#    The second run asks for two texts against a budget of one, so it overflows and appends
#    its owed bullets to the ledger the first run left.
seed
"$ADD" "$led" instead-of 'collapse to single hyphen' \
  'collapse an ASCII hyphen run' 'collapse a unicode dash too'; code1=$?
VERI_STEP_GROWTH=1 "$ADD" "$led" instead-of 'strip edge hyphens' 'one more' 'and another'; code2=$?
want='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse an ASCII hyphen run ⟦added⟧ ⟦criterion 2⟧
- [ ] collapse a unicode dash too ⟦added⟧ ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧

## Owed steps

- one more
- and another'
check_code "instead-of: replaces the anchor step with the texts, and over budget owes them instead" \
  "$code1/$code2" "0/1" "$want"

# 8. A step marked ⟦ci-repair⟧ is inserted even when VERI_STEP_GROWTH is already spent, and
#    carries no ⟦added⟧, and next-unchecked.sh hands it over as the next step (#544).
seed_lines '- [x] lowercase the slug ⟦criterion 1⟧' '- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧'
VERI_STEP_GROWTH=1 "$ADD" "$led" after 'an extra edge case' \
  'fix the CI failure: x.test.sh ⟦ci-repair⟧'; code=$?
next="$("$HERE/../next-unchecked.sh" < "$led")"; ncode=$?
if [[ "$code/$ncode" == "0/0" && "$next" == "fix the CI failure: x.test.sh ⟦ci-repair⟧"* ]] \
  && grep -Fx -- '- [ ] fix the CI failure: x.test.sh ⟦ci-repair⟧ ⟦criterion 1⟧' "$led" > /dev/null \
  && ! grep -F '## Owed steps' "$led" > /dev/null; then
  ok
else
  no "#544: a ⟦ci-repair⟧ step, unmarked ⟦added⟧, skips the spent VERI_STEP_GROWTH and next-unchecked hands it over (code=$code, next-code=$ncode, next=$next)"
  sed 's/^/    /' "$led"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

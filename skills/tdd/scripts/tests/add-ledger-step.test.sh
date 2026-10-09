#!/usr/bin/env bash
# Tests for scripts/add-ledger-step.sh — inserts a step, marked ⟦added⟧, next to an anchor
# step already in the plan. Operates on a real temp file.
#
# Run: scripts/tests/add-ledger-step.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ADD="$HERE/../add-ledger-step.sh"
source "$HERE/lib/harness.sh"

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

check() { check_code "$1" "$2" 0 "$3"; }

work="$(scratch_dir)"

led="$work/issue-42.md"

seeded='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'

seed() { printf '%s\n' "$seeded" > "$led"; }

seed
"$ADD" "$led" after 'collapse to single hyphen' 'collapse a unicode dash too'; code=$?
want='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] collapse a unicode dash too ⟦added⟧ ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'
check "after: inserts the added step below the anchor, carrying its criterion" "$code" "$want"

seed
VERI_STEP_GROWTH=1 "$ADD" "$led" before 'collapse to single hyphen' 'one more edge case' 'and another'; code=$?
want="$seeded"'

## Owed steps

- one more edge case
- and another'
check_code "over budget: inserts no checkbox, exits 1, and owes both texts as plain bullets" \
  "$code" 1 "$want"

usage='usage: add-ledger-step.sh [--criterion <k>] <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]'
name="no argument, and three arguments, each exit 2 with nothing on stdout and stderr exactly the usage line"
"$ADD" > "$work/usage0.out" 2> "$work/usage0.err"; code0=$?
"$ADD" l.md after anchor > "$work/usage3.out" 2> "$work/usage3.err"; code3=$?
if [[ "$code0" == 2 && ! -s "$work/usage0.out" && "$(cat "$work/usage0.err")" == "$usage" \
   && "$code3" == 2 && ! -s "$work/usage3.out" && "$(cat "$work/usage3.err")" == "$usage" ]]; then
  ok
else
  no "$name (code0=$code0, code3=$code3)"
  sed 's/^/    0 args stderr: /' "$work/usage0.err"
  sed 's/^/    3 args stderr: /' "$work/usage3.err"
fi

name="run through a symlink to the skill directory and from another working directory, a relative <ledger-file> is read and rewritten in the caller's working directory exactly as when run in place"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
linked_add="$work/linked-skill/scripts/add-ledger-step.sh"
mkdir -p "$work/in-place" "$work/elsewhere"
printf '%s\n' "$seeded" > "$work/in-place/l.md"
printf '%s\n' "$seeded" > "$work/elsewhere/l.md"
(cd "$work/in-place" && "$ADD" l.md after 'collapse to single hyphen' 't' 2> "$work/in-place.after.err"); in_after=$?
(cd "$work/elsewhere" && "$linked_add" l.md after 'collapse to single hyphen' 't' 2> "$work/linked.after.err"); linked_after=$?
(cd "$work/in-place" && "$ADD" l.md after 'no such step' 't' 2> "$work/in-place.none.err"); in_none=$?
(cd "$work/elsewhere" && "$linked_add" l.md after 'no such step' 't' 2> "$work/linked.none.err"); linked_none=$?
if [[ "$in_after" == 0 && "$linked_after" == 0 && "$in_none" == 2 && "$linked_none" == 2 ]] \
   && grep -Fx -- '- [ ] t ⟦added⟧ ⟦criterion 2⟧' "$work/in-place/l.md" > /dev/null \
   && cmp -s "$work/in-place/l.md" "$work/elsewhere/l.md" \
   && cmp -s "$work/in-place.after.err" "$work/linked.after.err" \
   && [[ "$(cat "$work/in-place.none.err")" == "add-ledger-step.sh: anchor matches no single step: no such step" ]] \
   && cmp -s "$work/in-place.none.err" "$work/linked.none.err"; then
  ok
else
  no "$name (after: in place $in_after, linked $linked_after; no match: in place $in_none, linked $linked_none)"
  diff "$work/in-place/l.md" "$work/elsewhere/l.md" | sed 's/^/    ledger: /'
  diff "$work/in-place.none.err" "$work/linked.none.err" | sed 's/^/    stderr: /'
fi

finish

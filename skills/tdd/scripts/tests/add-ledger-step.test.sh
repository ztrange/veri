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

seed_lines() { { printf '# Plan for #42\n\n'; printf '%s\n' "$@"; } > "$led"; }

seeded='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'

seed() { printf '%s\n' "$seeded" > "$led"; }

stub_script() {
  mkdir -p "$stub/lib"
  cp "$ADD" "$stub/add-ledger-step.sh"
  cp "$(dirname "$ADD")/lib/exit-contract.sh" "$stub/lib/exit-contract.sh"
}

seed
"$ADD" "$led" after 'collapse to single hyphen' 'collapse a unicode dash too'; code=$?
want='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] collapse a unicode dash too ⟦added⟧ ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'
check "after: inserts the added step below the anchor, carrying its criterion" "$code" "$want"

seed
"$ADD" "$led" before 'collapse to single hyphen' 'one more edge case' 'and another'; code=$?
want='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] one more edge case ⟦added⟧ ⟦criterion 2⟧
- [ ] and another ⟦added⟧ ⟦criterion 2⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'
check "before: inserts both texts, in order, on the lines above the anchor" "$code" "$want"

seed_lines '- [ ] collapse to single hyphen' '- [ ] strip edge hyphens ⟦criterion 3⟧'
"$ADD" "$led" after 'collapse to single hyphen' 'collapse a unicode dash too'; code=$?
want='# Plan for #42

- [ ] collapse to single hyphen
- [ ] collapse a unicode dash too ⟦added⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'
check "no criterion on the anchor: the added step carries none either" "$code" "$want"

seed
VERI_STEP_GROWTH=1 "$ADD" "$led" before 'collapse to single hyphen' 'one more edge case' 'and another'; code=$?
want="$seeded"'

## Owed steps

- one more edge case
- and another'
check_code "over budget: inserts no checkbox, exits 1, and owes both texts as plain bullets" \
  "$code" 1 "$want"

seed
"$ADD" "$led" after 'no such step' 'collapse a unicode dash too'; code1=$?
"$ADD" "$led" after 'hyphen' 'collapse a unicode dash too'; code2=$?
want="$seeded"
check_code "ambiguous or absent anchor: exits 2 and leaves the ledger byte-identical" \
  "$code1/$code2" "2/2" "$want"

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

stub="$work/stub"
stub_script
cat > "$stub/lib/ledger.sh" <<'EOF'
ledger_steps() {
  local line i=0
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" == '* ['?'] '* ]] || continue
    i=$((i + 1))
    printf '%s\topen\tstep\t0\t0\t\t%s\n' "$i" "${line#'* ['?'] '}"
  done
}
ledger_add_step() { cat; printf -- '- [ ] %s ⟦added⟧ ⟦criterion %s⟧\n' "$1" "$2"; }
EOF
seed_lines '* [ ] a lamp glows'
"$stub/add-ledger-step.sh" "$led" after 'a lamp glows' 'a lamp dims'; code=$?
want='# Plan for #42

* [ ] a lamp glows
- [ ] a lamp dims ⟦added⟧'
check "finds the anchor step through lib/ledger.sh's ledger_steps, matching no checkbox of its own" \
  "$code" "$want"

stub="$work/stub-add"
stub_script
sed "s/open_step='- \[ \]'/open_step='* [ ]'/" "$HERE/../lib/ledger.sh" > "$stub/lib/ledger.sh"
seed_lines '- [ ] a lamp glows ⟦criterion 2⟧'
"$stub/add-ledger-step.sh" "$led" after 'a lamp glows' 'a lamp dims'; code=$?
want='# Plan for #42

- [ ] a lamp glows ⟦criterion 2⟧
* [ ] a lamp dims ⟦added⟧ ⟦criterion 2⟧'
check "writes each new step line through lib/ledger.sh's ledger_add_step, spelling no box of its own" \
  "$code" "$want"

finish

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
  cp "$(dirname "$ADD")"/lib/*.sh "$stub/lib/"
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
VERI_STEP_GROWTH=0 "$ADD" "$led" after 'collapse to single hyphen' 'first refused'; code1=$?
VERI_STEP_GROWTH=0 "$ADD" "$led" after 'collapse to single hyphen' 'second refused' 'third refused'; code2=$?
want="$seeded"'

## Owed steps

- first refused
- second refused
- third refused'
check_code "#580: a second refusal appends its bullets under the existing trailing Owed steps heading" \
  "$code1/$code2" "1/1" "$want"

seed_lines '- [ ] collapse to single hyphen ⟦criterion 2⟧' '' '## Notes' '' 'a remark'
VERI_STEP_GROWTH=0 "$ADD" "$led" after 'collapse to single hyphen' 'first refused'; code=$?
want='# Plan for #42

- [ ] collapse to single hyphen ⟦criterion 2⟧

## Notes

a remark

## Owed steps

- first refused'
check_code "#580: a first refusal on a ledger with no Owed steps heading still creates it, its bullet under it" \
  "$code" 1 "$want"

printf '%s\n\n## Owed steps\n\n- earlier refused\n' "$seeded" > "$led"
steps_before="$(grep -F -- '- [' "$led")"
VERI_STEP_GROWTH=0 "$ADD" "$led" after 'collapse to single hyphen' 'later refused'; code=$?
steps_after="$(grep -F -- '- [' "$led")"
if [[ "$code" == 1 && "$steps_after" == "$steps_before" ]]; then
  ok
else
  no "#580: a second refusal under the existing Owed steps heading exits 1 and leaves the checkbox steps byte-identical (code=$code)"
  diff <(printf '%s\n' "$steps_before") <(printf '%s\n' "$steps_after") | sed 's/^/    /'
fi

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

seed_lines '- [x] lowercase the slug ⟦criterion 1⟧' '- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧'
VERI_STEP_GROWTH=1 "$ADD" "$led" after 'an extra edge case' \
  'fix the full-suite failure: x.test.sh ⟦suite-repair⟧'; code1=$?
want1='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧
- [ ] fix the full-suite failure: x.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧'
got1="$(cat "$led")"
seed_lines '- [x] lowercase the slug ⟦criterion 1⟧'
VERI_STEP_GROWTH=0 "$ADD" "$led" after 'lowercase the slug' \
  'fix the full-suite failure: y.test.sh ⟦suite-repair⟧'; code0=$?
want0='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] fix the full-suite failure: y.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧'
got0="$(cat "$led")"
if [[ "$code1/$code0" == "0/0" && "$got1" == "$want1" && "$got0" == "$want0" ]]; then
  ok
else
  no "#590: a ⟦suite-repair⟧ step, unmarked ⟦added⟧ and owing nothing, skips a spent VERI_STEP_GROWTH, 0 included (code=$code1/$code0)"
  diff <(printf '%s\n' "$want1") <(printf '%s\n' "$got1") | sed 's/^/    /'
  diff <(printf '%s\n' "$want0") <(printf '%s\n' "$got0") | sed 's/^/    /'
fi

seed_lines '- [x] lowercase the slug ⟦criterion 1⟧' '- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧' \
  '- [ ] fix the full-suite failure: x.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧'
VERI_STEP_GROWTH=2 "$ADD" "$led" after 'an extra edge case' 'a unicode dash too'; code=$?
want='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧
- [ ] a unicode dash too ⟦added⟧ ⟦criterion 1⟧
- [ ] fix the full-suite failure: x.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧'
check_code "#590: a ⟦suite-repair⟧ line already in the ledger does not count toward VERI_STEP_GROWTH" \
  "$code" "0" "$want"

seed_lines '- [x] lowercase the slug ⟦criterion 1⟧' '- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧' \
  '- [x] fix the full-suite failure: x.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧'
VERI_STEP_GROWTH=1 "$ADD" "$led" after 'an extra edge case' 'a unicode dash too'; codep=$?
wantp='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧
- [x] fix the full-suite failure: x.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧

## Owed steps

- a unicode dash too'
gotp="$(cat "$led")"
seed_lines '- [x] lowercase the slug ⟦criterion 1⟧' '- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧' \
  '- [x] fix the full-suite failure: x.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧'
VERI_STEP_GROWTH=1 "$ADD" "$led" after 'an extra edge case' \
  'fix the CI failure: y.test.sh ⟦ci-repair⟧'; codec=$?
wantc='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧
- [ ] fix the CI failure: y.test.sh ⟦ci-repair⟧ ⟦criterion 1⟧
- [x] fix the full-suite failure: x.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧'
gotc="$(cat "$led")"
if [[ "$codep/$codec" == "1/0" && "$gotp" == "$wantp" && "$gotc" == "$wantc" ]]; then
  ok
else
  no "#590: at the budget an unmarked step is still owed with exit 1 and a ⟦ci-repair⟧ step still inserted unmarked (code=$codep/$codec)"
  diff <(printf '%s\n' "$wantp") <(printf '%s\n' "$gotp") | sed 's/^/    /'
  diff <(printf '%s\n' "$wantc") <(printf '%s\n' "$gotc") | sed 's/^/    /'
fi

seed_lines '- [x] say a step marked ⟦added⟧ is counted ⟦criterion 1⟧' \
  '- [ ] collapse to single hyphen ⟦criterion 2⟧'
VERI_STEP_GROWTH=1 "$ADD" "$led" after 'collapse to single hyphen' 'one more edge case'; code=$?
want='# Plan for #42

- [x] say a step marked ⟦added⟧ is counted ⟦criterion 1⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] one more edge case ⟦added⟧ ⟦criterion 2⟧'
check "#660: a step quoting ⟦added⟧ mid-text, not ending in it, is not counted toward VERI_STEP_GROWTH" \
  "$code" "$want"

seed_lines '- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧ ⟂ refactor pending' \
  '- [ ] collapse to single hyphen ⟦criterion 2⟧'
VERI_STEP_GROWTH=1 "$ADD" "$led" after 'collapse to single hyphen' 'one more edge case'; code=$?
want='# Plan for #42

- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧ ⟂ refactor pending
- [ ] collapse to single hyphen ⟦criterion 2⟧

## Owed steps

- one more edge case'
check_code "#660: a ticked ⟦added⟧ step still marked refactor pending is counted toward VERI_STEP_GROWTH" \
  "$code" 1 "$want"

seed_lines '- [ ] an extra edge case ⟦added⟧ ⟦criterion 2⟧' \
  '- [ ] collapse to single hyphen ⟦criterion 2⟧'
VERI_STEP_GROWTH=1 "$ADD" "$led" after 'collapse to single hyphen' 'one more edge case'; code=$?
want='# Plan for #42

- [ ] an extra edge case ⟦added⟧ ⟦criterion 2⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧

## Owed steps

- one more edge case'
check_code "#660: a step ending in ⟦added⟧ before its ⟦criterion k⟧ is counted toward VERI_STEP_GROWTH" \
  "$code" 1 "$want"

seed_lines '- [ ] fix the CI failure: x.test.sh ⟦ci-repair⟧ ⟦criterion 2⟧' \
  '- [x] fix the full-suite failure: y.test.sh ⟦suite-repair⟧ ⟦criterion 2⟧ ⟂ refactor pending' \
  '- [ ] collapse to single hyphen ⟦criterion 2⟧'
VERI_STEP_GROWTH=1 "$ADD" "$led" after 'collapse to single hyphen' \
  'one more edge case' 'fix the full-suite failure: z.test.sh ⟦suite-repair⟧'; code=$?
want='# Plan for #42

- [ ] fix the CI failure: x.test.sh ⟦ci-repair⟧ ⟦criterion 2⟧
- [x] fix the full-suite failure: y.test.sh ⟦suite-repair⟧ ⟦criterion 2⟧ ⟂ refactor pending
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] one more edge case ⟦added⟧ ⟦criterion 2⟧
- [ ] fix the full-suite failure: z.test.sh ⟦suite-repair⟧ ⟦criterion 2⟧'
check_code "#660: ⟦ci-repair⟧ and ⟦suite-repair⟧ steps, in the ledger or inserted, are not counted toward VERI_STEP_GROWTH" \
  "$code" 0 "$want"

seed_lines 'Steps the run grew carry ⟦added⟧' \
  '- [ ] collapse to single hyphen ⟦criterion 2⟧' \
  '' '## Owed steps' '' '- an earlier edge case ⟦added⟧'
VERI_STEP_GROWTH=1 "$ADD" "$led" after 'collapse to single hyphen' 'one more edge case'; code=$?
want='# Plan for #42

Steps the run grew carry ⟦added⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] one more edge case ⟦added⟧ ⟦criterion 2⟧

## Owed steps

- an earlier edge case ⟦added⟧'
check "#660: a prose line and an Owed steps bullet quoting ⟦added⟧ are not counted toward VERI_STEP_GROWTH" \
  "$code" "$want"

seed_lines '- [ ] port status case a ⟦replaces-case⟧ ⟦criterion 1⟧' \
  '- [ ] port status case b ⟦replaces-case⟧ ⟦criterion 1⟧' \
  '- [ ] port status case c ⟦replaces-case⟧ ⟦added⟧ ⟦criterion 1⟧'
VERI_STEP_GROWTH=2 "$ADD" "$led" after 'port status case c' 'one more'; code1=$?
VERI_STEP_GROWTH=2 "$ADD" "$led" after 'port status case c' 'and another'; code2=$?
want='# Plan for #42

- [ ] port status case a ⟦replaces-case⟧ ⟦criterion 1⟧
- [ ] port status case b ⟦replaces-case⟧ ⟦criterion 1⟧
- [ ] port status case c ⟦replaces-case⟧ ⟦added⟧ ⟦criterion 1⟧
- [ ] one more ⟦added⟧ ⟦criterion 1⟧

## Owed steps

- and another'
check_code "a ⟦replaces-case⟧ step counts against VERI_STEP_GROWTH only when it is also ⟦added⟧ (code1=$code1)" \
  "$code2" 1 "$want"

source "$HERE/../lib/ledger.sh"
disagree=()
for line in \
  '- [x] lowercase the slug ⟦criterion 1⟧' \
  '- [ ] collapse to single hyphen ⟦criterion 2⟧' \
  '- [ ] strip edge hyphens ⟦criterion 3⟧' \
  '- [ ] collapse a unicode dash too ⟦added⟧ ⟦criterion 2⟧' \
  '- [ ] one more edge case ⟦added⟧ ⟦criterion 2⟧' \
  '- [ ] collapse to single hyphen' \
  '- [ ] collapse a unicode dash too ⟦added⟧' \
  '- [ ] collapse an ASCII hyphen run ⟦added⟧ ⟦criterion 2⟧' \
  '- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧' \
  '- [ ] fix the CI failure: x.test.sh ⟦ci-repair⟧ ⟦criterion 1⟧' \
  '- [ ] fix the full-suite failure: x.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧' \
  '- [x] fix the full-suite failure: x.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧' \
  '- [x] say a step marked ⟦added⟧ is counted ⟦criterion 1⟧' \
  '- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧ ⟂ refactor pending' \
  '- [ ] an extra edge case ⟦added⟧ ⟦criterion 2⟧' \
  '- [x] fix the full-suite failure: y.test.sh ⟦suite-repair⟧ ⟦criterion 2⟧ ⟂ refactor pending' \
  '- [ ] port status case a ⟦replaces-case⟧ ⟦criterion 1⟧' \
  '- [ ] port status case c ⟦replaces-case⟧ ⟦added⟧ ⟦criterion 1⟧' \
  '- [ ] a lamp glows ⟦criterion 2⟧'; do
  seed_lines "$line" '- [ ] the probe anchor ⟦criterion 9⟧'
  VERI_STEP_GROWTH=1 "$ADD" "$led" after 'the probe anchor' 'a probe step' > /dev/null 2>&1; code=$?
  script_added=0
  [[ $code == 1 ]] && script_added=1
  IFS=$'\t' read -r _ _ _ _ lib_added _ <<< "$(ledger_steps <<< "$line")"
  [[ "$script_added" == "$lib_added" ]] || disagree+=("$line (is_added_step=$script_added ledger_steps=$lib_added)")
done
if ((${#disagree[@]} == 0)); then
  ok
else
  no "#675: is_added_step and ledger_steps' added column agree on every step line of this suite's fixtures"
  printf '    %s\n' "${disagree[@]}"
fi

stub="$work/stub"
stub_script
{ printf '. %q\n' "$(dirname "$ADD")/lib/ledger.sh"; cat <<'EOF'; } > "$stub/lib/ledger.sh"
ledger_steps() {
  local line i=0
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" == '* ['?'] '* ]] || continue
    i=$((i + 1))
    printf '%s\topen\tstep\t0\t0\t\t%s\n' "$i" "${line#'* ['?'] '}"
  done
}
EOF
seed_lines '* [ ] a lamp glows'
"$stub/add-ledger-step.sh" "$led" after 'a lamp glows' 'a lamp dims' 2> "$work/stub.err"; code=$?
want='# Plan for #42

* [ ] a lamp glows
- [ ] a lamp dims ⟦added⟧'
name="#698: finds the anchor step through lib/ledger.sh's ledger_steps, matching no checkbox of its own, printing nothing on stderr"
if [[ -s "$work/stub.err" ]]; then
  no "$name (stderr not empty)"
  sed 's/^/    /' "$work/stub.err"
else
  check "$name" "$code" "$want"
fi

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

seed
err="$("$ADD" "$led" afterr 'collapse to single hyphen' 'collapse a unicode dash too' 2>&1 > /dev/null)"; code=$?
if [[ "$code" == 2 && "$err" == *afterr* ]]; then
  ok
else
  no "#697: a position word other than after, before or instead-of exits 2 and stderr names it (code=$code, err=$err)"
fi

seed
cp "$led" "$work/before.md"
VERI_STEP_GROWTH=0 "$ADD" "$led" afterr 'collapse to single hyphen' 'collapse a unicode dash too' 2> /dev/null; code=$?
if cmp -s "$work/before.md" "$led"; then
  ok
else
  no "#697: an unknown position word leaves the ledger byte-identical, with no ## Owed steps bullet, even over VERI_STEP_GROWTH (code=$code)"
  diff "$work/before.md" "$led" | sed 's/^/    /'
fi

finish

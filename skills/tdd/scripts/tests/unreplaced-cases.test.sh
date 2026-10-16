#!/usr/bin/env bash
# Tests for scripts/unreplaced-cases.sh — name the bash cases a ⟦replaces-case⟧ step lists
# that have no pytest replacement.
#
# Run: scripts/tests/unreplaced-cases.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
UNREPLACED="$HERE/../unreplaced-cases.sh"
source "$HERE/lib/harness.sh"

name="unreplaced-cases.sh run with no arguments exits 2 with its usage line on stderr and nothing on stdout (#1521)"
out="$(mktemp)"; err="$(mktemp)"
code=0
"$UNREPLACED" > "$out" 2> "$err" < /dev/null || code=$?
expect_eq "$name" "2:usage:" "$code:$(head -c 6 "$err")"
expect_eq "$name (stdout empty)" "" "$(cat "$out")"
rm -f "$out" "$err"

name="unreplaced-cases.sh given a step naming three cases and a report replacing two exits 1 and prints the third on stdout (#1521)"
tree="$(scratch_dir)"; mkdir -p "$tree/tests/py"
printf 'def test_first():\n    pass\n\n\ndef test_second():\n    pass\n\n\ndef test_third():\n    pass\n' > "$tree/tests/py/test_x.py"
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' \
  "REPLACES: first case => tests/py/test_x.py::test_first" \
  "REPLACES: second case => tests/py/test_x.py::test_second" > "$report"
step="- [ ] x: replaces 'first case', 'second case', 'third case' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
code=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null) || code=$?
expect_eq "$name" "1:third case" "$code:$(cat "$out")"
rm -f "$report" "$out"

name="unreplaced-cases.sh given a step naming three cases and a report replacing all three exits 0 with nothing on stdout (#1521)"
tree="$(scratch_dir)"; mkdir -p "$tree/tests/py"
printf 'def test_first():\n    pass\n\n\ndef test_second():\n    pass\n\n\ndef test_third():\n    pass\n' > "$tree/tests/py/test_x.py"
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' \
  "REPLACES: first case => tests/py/test_x.py::test_first" \
  "REPLACES: second case => tests/py/test_x.py::test_second" \
  "REPLACES: third case => tests/py/test_x.py::test_third" > "$report"
step="- [ ] x: replaces 'first case', 'second case', 'third case' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
code=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null) || code=$?
expect_eq "$name" "0:" "$code:$(cat "$out")"
rm -f "$report" "$out"

name="unreplaced-cases.sh counts a REPLACES line only when its test id names a test that exists at HEAD, so a claimed replacement absent from the tree stays printed and exits 1 (#1521)"
repo="$(scratch_dir)"; report="$(mktemp)"; out="$(mktemp)"
new_repo "$repo"
mkdir -p "$repo/tests/py"
printf 'def test_first():\n    pass\n' > "$repo/tests/py/test_x.py"
git -C "$repo" add tests/py/test_x.py
git -C "$repo" commit -q -m seed
printf '%s\n' \
  "REPLACES: first case => tests/py/test_x.py::test_first" \
  "REPLACES: second case => tests/py/test_x.py::test_second" > "$report"
step="- [ ] x: replaces 'first case', 'second case' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
code=0
(cd "$repo" && "$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null) || code=$?
expect_eq "$name" "1:second case" "$code:$(cat "$out")"
rm -f "$report" "$out"

name="unreplaced-cases.sh given a step naming three cases and a report replacing the second and third exits 1 and prints the first on stdout (#1521)"
tree="$(scratch_dir)"; mkdir -p "$tree/tests/py"
printf 'def test_first():\n    pass\n\n\ndef test_second():\n    pass\n\n\ndef test_third():\n    pass\n' > "$tree/tests/py/test_x.py"
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' \
  "REPLACES: second case => tests/py/test_x.py::test_second" \
  "REPLACES: third case => tests/py/test_x.py::test_third" > "$report"
step="- [ ] x: replaces 'first case', 'second case', 'third case' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
code=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null) || code=$?
expect_eq "$name" "1:first case" "$code:$(cat "$out")"
rm -f "$report" "$out"

name="unreplaced-cases.sh counts a REPLACES claim whose test is written in the working tree but not yet committed, in a file that exists at HEAD, so it prints nothing and exits 0 (#1521)"
repo="$(scratch_dir)"; report="$(mktemp)"; out="$(mktemp)"
new_repo "$repo"
mkdir -p "$repo/tests/py"
printf 'def test_first():\n    pass\n' > "$repo/tests/py/test_x.py"
git -C "$repo" add tests/py/test_x.py
git -C "$repo" commit -q -m seed
printf 'def test_first():\n    pass\n\n\ndef test_second():\n    pass\n' > "$repo/tests/py/test_x.py"
printf '%s\n' \
  "REPLACES: first case => tests/py/test_x.py::test_first" \
  "REPLACES: second case => tests/py/test_x.py::test_second" > "$report"
step="- [ ] x: replaces 'first case', 'second case' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
code=0
(cd "$repo" && "$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null) || code=$?
expect_eq "$name" "0:" "$code:$(cat "$out")"
rm -f "$report" "$out"

name="unreplaced-cases.sh leaves a case printed and exits 1 when its REPLACES claim names a test file that does not exist in the working tree (#1521)"
repo="$(scratch_dir)"; report="$(mktemp)"; out="$(mktemp)"
new_repo "$repo"
printf '%s\n' "REPLACES: first case => tests/py/test_missing.py::test_first" > "$report"
step="- [ ] x: replaces 'first case' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
code=0
(cd "$repo" && "$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null) || code=$?
expect_eq "$name" "1:first case" "$code:$(cat "$out")"
rm -f "$report" "$out"

name="unreplaced-cases.sh given a step that names the replaces-case mark but carries no replaces clause exits 0 and prints no case name (#1603)"
report="$(mktemp)"; out="$(mktemp)"; err="$(mktemp)"
: > "$report"
step="- [ ] x: the Red prompt for replaces-case steps ⟦replaces-case⟧ ⟦criterion 1⟧"
code=0
"$UNREPLACED" "$step" "$report" > "$out" 2> "$err" < /dev/null || code=$?
expect_eq "$name" "0::" "$code:$(cat "$out"):$(cat "$err")"
rm -f "$report" "$out" "$err"

name="unreplaced-cases.sh counts a REPLACES line whose case name is wrapped in one pair of backticks, the step's delimiter, so it exits 0 and prints nothing (#1600)"
tree="$(scratch_dir)"; mkdir -p "$tree/tests/py"
printf 'def test_a():\n    pass\n' > "$tree/tests/py/test_x.py"
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' 'REPLACES: `first case` => tests/py/test_x.py::test_a' > "$report"
step='- [ ] x: replaces `first case` in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧'
code=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null) || code=$?
expect_eq "$name" "0:" "$code:$(cat "$out")"
rm -f "$report" "$out"

name="unreplaced-cases.sh counts a REPLACES line whose case name is wrapped in one pair of double quotes, the step's delimiter, so it exits 0 and prints nothing (#1600)"
tree="$(scratch_dir)"; mkdir -p "$tree/tests/py"
printf 'def test_a():\n    pass\n' > "$tree/tests/py/test_x.py"
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' 'REPLACES: "it'"'"'s a case" => tests/py/test_x.py::test_a' > "$report"
step='- [ ] x: replaces "it'"'"'s a case" in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧'
code=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null) || code=$?
expect_eq "$name" "0:" "$code:$(cat "$out")"
rm -f "$report" "$out"

name="unreplaced-cases.sh counts a REPLACES line whose case name is bare, with no delimiter around a name holding both quote characters, so it exits 0 and prints nothing (#1600)"
tree="$(scratch_dir)"; mkdir -p "$tree/tests/py"
printf 'def test_a():\n    pass\n' > "$tree/tests/py/test_x.py"
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' 'REPLACES: it'"'"'s a "quoted" case => tests/py/test_x.py::test_a' > "$report"
step='- [ ] x: replaces `it'"'"'s a "quoted" case` in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 2⟧'
code=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null) || code=$?
expect_eq "$name" "0:" "$code:$(cat "$out")"
rm -f "$report" "$out"

name="unreplaced-cases.sh prints the step's case and exits 1 when the only REPLACES line names a different case wrapped in the step's backtick delimiter (#1600)"
tree="$(scratch_dir)"; mkdir -p "$tree/tests/py"
printf 'def test_b():\n    pass\n' > "$tree/tests/py/test_x.py"
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' 'REPLACES: `other case` => tests/py/test_x.py::test_b' > "$report"
step='- [ ] x: replaces `first case` in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 3⟧'
code=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null) || code=$?
expect_eq "$name" "1:first case" "$code:$(cat "$out")"
rm -f "$report" "$out"

finish

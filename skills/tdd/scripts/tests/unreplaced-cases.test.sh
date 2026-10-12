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
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' \
  "REPLACES: first case => tests/py/test_x.py::test_first" \
  "REPLACES: second case => tests/py/test_x.py::test_second" > "$report"
step="- [ ] x: replaces 'first case', 'second case', 'third case' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
code=0
"$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null || code=$?
expect_eq "$name" "1:third case" "$code:$(cat "$out")"
rm -f "$report" "$out"

name="unreplaced-cases.sh given a step naming three cases and a report replacing all three exits 0 with nothing on stdout (#1521)"
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' \
  "REPLACES: first case => tests/py/test_x.py::test_first" \
  "REPLACES: second case => tests/py/test_x.py::test_second" \
  "REPLACES: third case => tests/py/test_x.py::test_third" > "$report"
step="- [ ] x: replaces 'first case', 'second case', 'third case' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
code=0
"$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null || code=$?
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
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' \
  "REPLACES: second case => tests/py/test_x.py::test_second" \
  "REPLACES: third case => tests/py/test_x.py::test_third" > "$report"
step="- [ ] x: replaces 'first case', 'second case', 'third case' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧"
code=0
"$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null || code=$?
expect_eq "$name" "1:first case" "$code:$(cat "$out")"
rm -f "$report" "$out"

finish

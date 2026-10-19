#!/usr/bin/env bash
# Tests for scripts/unreplaced-cases.sh — name the bash cases a ⟦replaces-case⟧ step lists
# that have no pytest replacement.
#
# Run: scripts/tests/unreplaced-cases.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
UNREPLACED="$HERE/../unreplaced-cases.sh"
source "$HERE/lib/harness.sh"

name="unreplaced-cases.sh counts a REPLACES line with a markdown bullet in front like the same line without it, so a step naming two cases prints nothing and exits 0 (#1660)"
tree="$(scratch_dir)"; mkdir -p "$tree/tests/py"
printf 'def test_a():\n    pass\n\n\ndef test_b():\n    pass\n' > "$tree/tests/py/test_x.py"
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' \
  "- REPLACES: case a => tests/py/test_x.py::test_a" \
  "* REPLACES: case b => tests/py/test_x.py::test_b" > "$report"
step="- [ ] x: replaces 'case a', 'case b' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 2⟧"
code=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null) || code=$?
expect_eq "$name" "0:" "$code:$(cat "$out")"
rm -f "$report" "$out"

name="unreplaced-cases.sh counts a REPLACES line with a star bullet in front like the same line without it, so a step naming one case prints nothing and exits 0 (#1660)"
tree="$(scratch_dir)"; mkdir -p "$tree/tests/py"
printf 'def test_a():\n    pass\n' > "$tree/tests/py/test_x.py"
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' "* REPLACES: case a => tests/py/test_x.py::test_a" > "$report"
step="- [ ] x: replaces 'case a' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 2⟧"
code=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null) || code=$?
expect_eq "$name" "0:" "$code:$(cat "$out")"
rm -f "$report" "$out"

name="unreplaced-cases.sh counts a REPLACES line whose test id is a bare test name with no :: as replaced when exactly one test function of that name exists under skills/tdd/scripts/tests/py/, so a step naming the case prints nothing and exits 0 (#1660)"
tree="$(scratch_dir)"; mkdir -p "$tree/skills/tdd/scripts/tests/py/unit"
printf 'def test_a():\n    pass\n' > "$tree/skills/tdd/scripts/tests/py/unit/test_x.py"
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' "REPLACES: case a => test_a" > "$report"
step="- [ ] x: replaces 'case a' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 3⟧"
code=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null) || code=$?
expect_eq "$name" "0:" "$code:$(cat "$out")"
rm -f "$report" "$out"

name="unreplaced-cases.sh counts a bare-name REPLACES line as unreplaced when no test function of that name exists under skills/tdd/scripts/tests/py/, so it exits 1 and the case is printed and the reason, no test of that name was found, is on stdout or stderr (criterion 5 pins which) (#1660)"
tree="$(scratch_dir)"; mkdir -p "$tree/skills/tdd/scripts/tests/py/unit"
printf 'def test_other():\n    pass\n' > "$tree/skills/tdd/scripts/tests/py/unit/test_x.py"
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' "REPLACES: case a => test_a" > "$report"
step="- [ ] x: replaces 'case a' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 3⟧"
code=0
err="$(mktemp)"
(cd "$tree" && "$UNREPLACED" "$step" "$report" > "$out" 2> "$err" < /dev/null) || code=$?
said=no
cat "$out" "$err" | grep -F 'no test of that name was found' > /dev/null && said=yes
printed=no
grep -F 'case a' "$out" > /dev/null && printed=yes
expect_eq "$name" "1:yes:yes" "$code:$printed:$said"
rm -f "$report" "$out" "$err"

name="unreplaced-cases.sh counts a bare-name REPLACES line as unreplaced when several test functions of that name exist under skills/tdd/scripts/tests/py/, so it exits 1 and the case is printed and the reason, ambiguous, is on stdout or stderr (criterion 5 pins which) (#1660)"
tree="$(scratch_dir)"; mkdir -p "$tree/skills/tdd/scripts/tests/py/unit"
printf 'def test_a():\n    pass\n' > "$tree/skills/tdd/scripts/tests/py/unit/test_x.py"
printf 'def test_a():\n    pass\n' > "$tree/skills/tdd/scripts/tests/py/unit/test_y.py"
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' "REPLACES: case a => test_a" > "$report"
step="- [ ] x: replaces 'case a' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 3⟧"
code=0
err="$(mktemp)"
(cd "$tree" && "$UNREPLACED" "$step" "$report" > "$out" 2> "$err" < /dev/null) || code=$?
said=no
cat "$out" "$err" | grep -F 'ambiguous' > /dev/null && said=yes
printed=no
grep -F 'case a' "$out" > /dev/null && printed=yes
expect_eq "$name" "1:yes:yes" "$code:$printed:$said"
rm -f "$report" "$out" "$err"

name="unreplaced-cases.sh prints an unreplaced bare-name case on stdout exactly as the step spells it and writes the reason, no test of that name was found, to stderr (#1660)"
tree="$(scratch_dir)"; mkdir -p "$tree/skills/tdd/scripts/tests/py/unit"
printf 'def test_other():\n    pass\n' > "$tree/skills/tdd/scripts/tests/py/unit/test_x.py"
report="$(mktemp)"; out="$(mktemp)"; err="$(mktemp)"
printf '%s\n' "REPLACES: case a => test_a" > "$report"
step="- [ ] x: replaces 'case a' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 5⟧"
code=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > "$out" 2> "$err" < /dev/null) || code=$?
said=no
grep -F 'no test of that name was found' "$err" > /dev/null && said=yes
expect_eq "$name" "1:case a:yes" "$code:$(cat "$out"):$said"
rm -f "$report" "$out" "$err"

name="unreplaced-cases.sh counts a bare-name REPLACES line as unreplaced when the only function of that name under skills/tdd/scripts/tests/py/ is a helper rather than a def test_ function, so it exits 1 and prints the case (#1660)"
tree="$(scratch_dir)"; mkdir -p "$tree/skills/tdd/scripts/tests/py/unit"
printf 'def make_a():\n    pass\n' > "$tree/skills/tdd/scripts/tests/py/unit/test_x.py"
report="$(mktemp)"; out="$(mktemp)"
printf '%s\n' "REPLACES: case a => make_a" > "$report"
step="- [ ] x: replaces 'case a' in scripts/tests/x.test.sh ⟦replaces-case⟧ ⟦criterion 6⟧"
code=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > "$out" 2> /dev/null < /dev/null) || code=$?
expect_eq "$name" "1:case a" "$code:$(cat "$out")"
rm -f "$report" "$out"

name="unreplaced-cases.sh and replaces-case-survivors.sh given a replaces-case step with an unquoted name after a quoted one each exit 2 with one stderr line naming the step and no traceback (#1538)"
tree="$(scratch_dir)"; report="$(mktemp)"; : > "$report"
step="- [ ] x: replaces 'a', b in t/x.test.sh ⟦replaces-case⟧ ⟦criterion 5⟧"
code_u=0; code_s=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > /dev/null 2> "$tree/err-u" < /dev/null) || code_u=$?
(cd "$tree" && "$HERE/../replaces-case-survivors.sh" "$step" > /dev/null 2> "$tree/err-s" < /dev/null) || code_s=$?
shape=""
for f in "$tree/err-u" "$tree/err-s"; do
  lines="$(wc -l < "$f" | tr -d ' ')"
  names=no; grep -F "replaces 'a', b in t/x.test.sh" "$f" > /dev/null && names=yes
  trace=no; grep -F 'Traceback' "$f" > /dev/null && trace=yes
  shape="$shape $lines:$names:$trace"
done
expect_eq "$name" "2:2: 1:yes:no 1:yes:no" "$code_u:$code_s:$shape"
rm -f "$report"

name="unreplaced-cases.sh and replaces-case-survivors.sh given a replaces-case step whose quoted name is followed by a trailing parenthetical each exit 2 with one stderr line naming the step and no traceback (#1538)"
tree="$(scratch_dir)"; report="$(mktemp)"; : > "$report"
step="- [ ] x: replaces 'a' (from #12) in t/x.test.sh ⟦replaces-case⟧ ⟦criterion 5⟧"
code_u=0; code_s=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > /dev/null 2> "$tree/err-u" < /dev/null) || code_u=$?
(cd "$tree" && "$HERE/../replaces-case-survivors.sh" "$step" > /dev/null 2> "$tree/err-s" < /dev/null) || code_s=$?
shape=""
for f in "$tree/err-u" "$tree/err-s"; do
  lines="$(wc -l < "$f" | tr -d ' ')"
  names=no; grep -F "replaces 'a' (from #12) in t/x.test.sh" "$f" > /dev/null && names=yes
  trace=no; grep -F 'Traceback' "$f" > /dev/null && trace=yes
  shape="$shape $lines:$names:$trace"
done
expect_eq "$name" "2:2: 1:yes:no 1:yes:no" "$code_u:$code_s:$shape"
rm -f "$report"

name="unreplaced-cases.sh given a replaces-case step whose named suite is not a .test.sh file exits 2 with one stderr line naming the step and the suite (#1538)"
tree="$(scratch_dir)"; report="$(mktemp)"; : > "$report"
step="- [ ] x: replaces 'a' in t/x.py ⟦replaces-case⟧ ⟦criterion 6⟧"
code=0
(cd "$tree" && "$UNREPLACED" "$step" "$report" > /dev/null 2> "$tree/err" < /dev/null) || code=$?
lines="$(wc -l < "$tree/err" | tr -d ' ')"
names=no; grep -F "replaces 'a' in t/x.py" "$tree/err" > /dev/null && grep -F 't/x.py' "$tree/err" > /dev/null && names=yes
expect_eq "$name" "2:1:yes" "$code:$lines:$names"
rm -f "$report"

finish

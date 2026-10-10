#!/usr/bin/env bash
# Tests for scripts/mutation-parity.sh — applies each pairs-table row's mutation, runs the
# row's old case and its kept case, and reports each row's result. Driven against a scratch
# repository holding one production file and one plain-shell suite.
#
# Contract under test:
#   mutation-parity.sh <pairs-table>
#   A row is tab-separated: <suite> <old case> redundant <kept case> <mutation patch>
#
# Run: scripts/tests/mutation-parity.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PARITY="$HERE/../mutation-parity.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

repo="$work/repo"
new_repo -b main "$repo" >/dev/null 2>&1
mkdir -p "$repo/tests"
cat > "$repo/calc.sh" <<'SRC'
add() { echo $(( $1 + $2 )); }
greet() { echo "hello $1"; }
SRC
cat > "$repo/tests/calc.test.sh" <<'SUITE'
#!/bin/sh
. "$(dirname "$0")/../calc.sh"
pass=0; fail=0
check() { if [ "$2" = "$3" ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL - $1"; fi; }
check "adds two numbers" 5 "$(add 2 3)"
check "adds a negative" -1 "$(add 2 -3)"
check "greets by name" "hello ann" "$(greet ann)"
echo "----"
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
SUITE
chmod +x "$repo/tests/calc.test.sh"
git -C "$repo" add -A && git -C "$repo" commit -qm init

patch="$work/add-subtracts.patch"
sed 's/\$1 + \$2/$1 - $2/' "$repo/calc.sh" > "$work/calc.mutated"
diff -u --label a/calc.sh --label b/calc.sh "$repo/calc.sh" "$work/calc.mutated" > "$patch"

table="$work/pairs.tsv"
printf 'tests/calc.test.sh\tadds two numbers\tredundant\tadds a negative\t%s\n' "$patch" > "$table"

out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/parity.err")" && code=0 || code=$?
row="$(grep -F 'adds two numbers' <<<"$out" | grep -F 'adds a negative' | grep -F "$patch" | grep -wF proven || true)"
if [[ "$code" == 0 && -n "$row" ]]; then
  ok
else
  no "a valid mutation the kept case catches is reported proven and exits 0 (exit=$code want 0)
    stdout: $out
    stderr: $(cat "$work/parity.err")"
fi

not_proven() {
  local name="$1" sed_expr="$2" patch="$work/$1.patch" table="$work/$1.tsv" out
  sed "$sed_expr" "$repo/calc.sh" > "$work/$name.mutated"
  diff -u --label a/calc.sh --label b/calc.sh "$repo/calc.sh" "$work/$name.mutated" > "$patch"
  printf 'tests/calc.test.sh\tadds two numbers\tredundant\tadds a negative\t%s\n' "$patch" > "$table"
  out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/$name.err")"
  if grep -wF proven <<<"$out" > /dev/null; then
    no "$3
    stdout: $out
    stderr: $(cat "$work/$name.err")"
  else
    ok
  fi
}

not_proven old-stays-green 's/\$1 + \$2/$1 + ${2#-}/' \
  "a mutation that leaves the old case green is not reported proven, though the kept case goes red"
not_proven none-stays-green 's/\$1 + \$2/$1 - $2/; s/hello/bye/' \
  "a mutation that leaves no other case of the suite green is not reported proven, though the old and kept cases go red"

patch="$work/kept-stays-green.patch"
sed 's/\$1 + \$2/$1 + $2 + ($2 > 0)/' "$repo/calc.sh" > "$work/kept-stays-green.mutated"
diff -u --label a/calc.sh --label b/calc.sh "$repo/calc.sh" "$work/kept-stays-green.mutated" > "$patch"
table="$work/kept-stays-green.tsv"
printf 'tests/calc.test.sh\tadds two numbers\tredundant\tadds a negative\t%s\n' "$patch" > "$table"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/kept-stays-green.err")" && code=0 || code=$?
row="$(grep -F 'adds a negative' <<<"$out" | grep -wF unproven || true)"
if [[ "$code" == 1 && -n "$row" ]]; then
  ok
else
  no "a valid mutation that leaves the kept case green is reported unproven, naming the kept case, and exits 1 (exit=$code want 1)
    stdout: $out
    stderr: $(cat "$work/kept-stays-green.err")"
fi

table="$work/old-stays-green.tsv"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/old-stays-green-owed.err")" && code=0 || code=$?
row="$(grep -F 'adds two numbers' <<<"$out" | grep -wF owed || true)"
if [[ "$code" == 1 && -n "$row" ]]; then
  ok
else
  no "a mutation that leaves the old case green is reported owed and exits 1 (exit=$code want 1)
    stdout: $out
    stderr: $(cat "$work/old-stays-green-owed.err")"
fi

table="$work/none-stays-green.tsv"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/none-stays-green-owed.err")" && code=0 || code=$?
row="$(grep -F 'adds two numbers' <<<"$out" | grep -wF owed || true)"
if [[ "$code" == 1 && -n "$row" ]]; then
  ok
else
  no "a mutation that leaves no other case of the suite green is reported owed and exits 1 (exit=$code want 1)
    stdout: $out
    stderr: $(cat "$work/none-stays-green-owed.err")"
fi

cat > "$repo/tests/test_calc.py" <<'PYTEST'
import os
import subprocess

CALC = os.path.join(os.path.dirname(__file__), "..", "calc.sh")


def test_adds_a_negative():
    run = subprocess.run(["sh", "-c", '. "$0"; add 2 -3', CALC], capture_output=True, text=True)
    assert run.stdout.strip() == "-1"
PYTEST
git -C "$repo" add -A && git -C "$repo" commit -qm 'pytest replacement'

node="tests/test_calc.py::test_adds_a_negative"
replaced() {
  local table="$work/replaced-$1.tsv"
  printf 'tests/calc.test.sh\tadds two numbers\treplaced\t%s\t%s\n' "$node" "$work/$1.patch" > "$table"
  out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/replaced-$1.err")" && code=0 || code=$?
  row="$(grep -F "$node" <<<"$out" | grep -wF "$2" || true)"
}
replaced add-subtracts proven
proven_code="$code" proven_row="$row" proven_out="$out"
replaced kept-stays-green unproven
if [[ "$proven_code" == 0 && -n "$proven_row" && "$code" == 1 && -n "$row" ]]; then
  ok
else
  no "a row replaced by a pytest node id is proven when the node goes red and unproven, naming it, when it stays green (proven exit=$proven_code want 0, unproven exit=$code want 1)
    proven stdout: $proven_out
    proven stderr: $(cat "$work/replaced-add-subtracts.err")
    unproven stdout: $out
    unproven stderr: $(cat "$work/replaced-kept-stays-green.err")"
fi

cat > "$repo/tests/test_sums.py" <<'PYTEST'
import os
import subprocess

CALC = os.path.join(os.path.dirname(__file__), "..", "calc.sh")


def run(call):
    return subprocess.run(["sh", "-c", '. "$0"; ' + call, CALC], capture_output=True,
                          text=True).stdout.strip()


def test_adds_two_numbers():
    assert run("add 2 3") == "5"


def test_greets_by_name():
    assert run("greet ann") == "hello ann"
PYTEST
git -C "$repo" add -A && git -C "$repo" commit -qm 'pytest old case'

old_node="tests/test_sums.py::test_adds_two_numbers"
old_pytest() {
  local table="$work/old-pytest-$1.tsv"
  printf 'tests/test_sums.py\t%s\treplaced\t%s\t%s\n' "$old_node" "$node" "$work/$1.patch" > "$table"
  out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/old-pytest-$1.err")" && code=0 || code=$?
  row="$(grep -F "$old_node" <<<"$out" | grep -wF "$2" || true)"
}
old_pytest add-subtracts proven
valid_code="$code" valid_row="$row" valid_out="$out"
old_pytest none-stays-green owed
if [[ "$valid_code" == 0 && -n "$valid_row" && "$code" == 1 && -n "$row" ]]; then
  ok
else
  no "a row whose old case is a pytest node id is valid when the node goes red and another case of its file stays green, and owed when none stays green (valid exit=$valid_code want 0, owed exit=$code want 1)
    valid stdout: $valid_out
    valid stderr: $(cat "$work/old-pytest-add-subtracts.err")
    owed stdout: $out
    owed stderr: $(cat "$work/old-pytest-none-stays-green.err")"
fi

finish

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

mutant() {
  local name="$1" sed_expr="$2"
  sed "$sed_expr" "$repo/calc.sh" > "$work/$name.mutated"
  diff -u --label a/calc.sh --label b/calc.sh "$repo/calc.sh" "$work/$name.mutated" > "$work/$name.patch"
}

mutant old-stays-green 's/\$1 + \$2/$1 + ${2#-}/'
mutant none-stays-green 's/\$1 + \$2/$1 - $2/; s/hello/bye/'

patch="$work/kept-stays-green.patch"
sed 's/\$1 + \$2/$1 + $2 + ($2 > 0)/' "$repo/calc.sh" > "$work/kept-stays-green.mutated"
diff -u --label a/calc.sh --label b/calc.sh "$repo/calc.sh" "$work/kept-stays-green.mutated" > "$patch"
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

sed 's/hello/bye/' "$repo/calc.sh" > "$work/greet-byes.mutated"
diff -u --label a/calc.sh --label b/calc.sh "$repo/calc.sh" "$work/greet-byes.mutated" > "$work/greet-byes.patch"
several() {
  local table="$work/several-$1.tsv" err="$work/several-$1.err"
  shift
  printf '%s\n' "$@" > "$table"
  out="$(cd "$repo" && "$PARITY" "$table" 2>"$err")" && code=0 || code=$?
  out="$out
    stderr: $(cat "$err")"
}
several proven \
  "tests/calc.test.sh"$'\t'"adds two numbers"$'\t'"redundant"$'\t'"adds a negative"$'\t'"$work/add-subtracts.patch" \
  "tests/calc.test.sh"$'\t'"greets by name"$'\t'"replaced"$'\t'"tests/test_sums.py::test_greets_by_name"$'\t'"$work/greet-byes.patch"
all_code="$code" all_out="$out"
all_rows="$(grep -wF proven <<<"$all_out" | grep -cF -e 'adds two numbers' -e 'greets by name' || true)"
several mixed \
  "tests/calc.test.sh"$'\t'"greets by name"$'\t'"replaced"$'\t'"tests/test_sums.py::test_greets_by_name"$'\t'"$work/greet-byes.patch" \
  "tests/calc.test.sh"$'\t'"adds two numbers"$'\t'"redundant"$'\t'"adds a negative"$'\t'"$work/old-stays-green.patch" \
  "tests/calc.test.sh"$'\t'"adds two numbers"$'\t'"redundant"$'\t'"adds a negative"$'\t'"$work/kept-stays-green.patch"
mixed_rows="$(grep -cE $'\t(proven|owed|unproven)$' <<<"$out" || true)"
if [[ "$all_code" == 0 && "$all_rows" == 2 && "$code" == 1 && "$mixed_rows" == 3 ]] \
  && grep -F 'greets by name' <<<"$out" | grep -wF proven > /dev/null \
  && grep -F "$work/old-stays-green.patch" <<<"$out" | grep -wF owed > /dev/null \
  && grep -F "$work/kept-stays-green.patch" <<<"$out" | grep -wF unproven > /dev/null; then
  ok
else
  no "a table of several rows reports every row, each row's case run with only its own mutation in place, and exits 0 only when every row is proven, 1 when any is unproven or owed (all-proven exit=$all_code want 0, rows=$all_rows want 2; mixed exit=$code want 1, rows=$mixed_rows want 3)
    all-proven stdout: $all_out
    mixed stdout: $out"
fi

cat > "$repo/tests/single.test.sh" <<'SUITE'
#!/bin/sh
. "$(dirname "$0")/../calc.sh"
pass=0; fail=0
check() { if [ "$2" = "$3" ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL - $1"; fi; }
check "adds two numbers" 5 "$(add 2 3)"
echo "----"
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
SUITE
chmod +x "$repo/tests/single.test.sh"
git -C "$repo" add -A && git -C "$repo" commit -qm 'single-case suite'
table="$work/single.tsv"
printf 'tests/single.test.sh\tadds two numbers\treplaced\t%s\t%s\n' "$node" "$work/add-subtracts.patch" > "$table"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/single.err")" && code=0 || code=$?
row="$(grep -F 'adds two numbers' <<<"$out" | grep -wF proven || true)"
if [[ "$code" == 0 && -n "$row" ]]; then
  ok
else
  no "#1594: a row whose old suite holds exactly one case reads proven when that suite runs to its count line with the named case failed and the replacement is caught (exit=$code want 0)
    stdout: $out
    stderr: $(cat "$work/single.err")"
fi

sed 's/single.test.sh/x/' "$repo/tests/single.test.sh" > "$repo/tests/single-dies.test.sh"
chmod +x "$repo/tests/single-dies.test.sh"
git -C "$repo" add -A && git -C "$repo" commit -qm 'second single-case suite'
{ cat "$repo/calc.sh"; echo 'exit 9'; } > "$work/dies.mutated"
diff -u --label a/calc.sh --label b/calc.sh "$repo/calc.sh" "$work/dies.mutated" > "$work/dies.patch" || true
table="$work/single-dies.tsv"
printf 'tests/single-dies.test.sh\tadds two numbers\treplaced\t%s\t%s\n' "$node" "$work/dies.patch" > "$table"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/single-dies.err")" && code=0 || code=$?
row="$(grep -F 'adds two numbers' <<<"$out" | grep -wF owed || true)"
if [[ "$code" == 1 && -n "$row" ]]; then
  ok
else
  no "#1594: a row whose old suite holds exactly one case reads owed when, under the mutation, that suite dies before its count line (exit=$code want 1)
    stdout: $out
    stderr: $(cat "$work/single-dies.err")"
fi

table="$work/single-kept-green.tsv"
printf 'tests/single.test.sh\tadds two numbers\treplaced\t%s\t%s\n' "$node" "$work/kept-stays-green.patch" > "$table"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/single-kept-green.err")" && code=0 || code=$?
row="$(grep -F 'adds two numbers' <<<"$out" | grep -wF unproven || true)"
if [[ "$code" == 1 && -n "$row" ]]; then
  ok
else
  no "#1594: a row whose old suite holds exactly one case reads unproven when that suite runs to its count line with the named case failed but the replacement is not caught (exit=$code want 1)
    stdout: $out
    stderr: $(cat "$work/single-kept-green.err")"
fi

sed 's/5 "\$(add 2 3)"/6 "$(add 2 3)"/' "$repo/tests/single.test.sh" > "$repo/tests/single-red.test.sh"
chmod +x "$repo/tests/single-red.test.sh"
git -C "$repo" add -A && git -C "$repo" commit -qm 'single-case suite already red'
table="$work/single-red.tsv"
printf 'tests/single-red.test.sh\tadds two numbers\treplaced\t%s\t%s\n' "$node" "$work/add-subtracts.patch" > "$table"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/single-red.err")" && code=0 || code=$?
row="$(grep -F 'adds two numbers' <<<"$out" | grep -wF unproven || true)"
if [[ "$code" == 1 && -n "$row" ]] && grep -F 'old case adds two numbers' "$work/single-red.err" > /dev/null; then
  ok
else
  no "#1596: a row whose old suite holds exactly one case reads unproven and names the old case when that case already fails with the mutation not applied, though the replacement is caught (exit=$code want 1)
    stdout: $out
    stderr: $(cat "$work/single-red.err")"
fi

sed 's/5 "\$(add 2 3)"/6 "$(add 2 3)"/' "$repo/tests/calc.test.sh" > "$repo/tests/calc-red.test.sh"
chmod +x "$repo/tests/calc-red.test.sh"
git -C "$repo" add -A && git -C "$repo" commit -qm 'multi-case suite whose old case already red'
table="$work/multi-red.tsv"
printf 'tests/calc-red.test.sh\tadds two numbers\tredundant\tadds a negative\t%s\n' "$work/add-subtracts.patch" > "$table"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/multi-red.err")" && code=0 || code=$?
row="$(grep -F 'adds two numbers' <<<"$out" | grep -wF unproven || true)"
if [[ "$code" == 1 && -n "$row" ]] && grep -F 'old case adds two numbers' "$work/multi-red.err" > /dev/null; then
  ok
else
  no "#1596: a row whose old suite holds several cases reads unproven and names the old case when that case already fails with the mutation not applied (exit=$code want 1)
    stdout: $out
    stderr: $(cat "$work/multi-red.err")"
fi

cat > "$repo/tests/test_calc_red.py" <<'PYTEST'
import os
import subprocess

CALC = os.path.join(os.path.dirname(__file__), "..", "calc.sh")


def test_adds_a_negative():
    run = subprocess.run(["sh", "-c", '. "$0"; add 2 -3', CALC], capture_output=True, text=True)
    assert run.stdout.strip() == "-2"
PYTEST
git -C "$repo" add -A && git -C "$repo" commit -qm 'pytest replacement already red'
red_node="tests/test_calc_red.py::test_adds_a_negative"
table="$work/replaced-red.tsv"
printf 'tests/calc.test.sh\tadds two numbers\treplaced\t%s\t%s\n' "$red_node" "$work/add-subtracts.patch" > "$table"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/replaced-red.err")" && code=0 || code=$?
row="$(grep -F "$red_node" <<<"$out" | grep -wF unproven || true)"
if [[ "$code" == 1 && -n "$row" ]] && grep -F "replacement $red_node" "$work/replaced-red.err" > /dev/null &&
   ! grep -F 'old case' "$work/replaced-red.err" > /dev/null; then
  ok
else
  no "#1596: a row whose pytest replacement already fails with the mutation not applied reads unproven and names the replacement, not the old case (exit=$code want 1)
    stdout: $out
    stderr: $(cat "$work/replaced-red.err")"
fi

sed 's/-1 "\$(add 2 -3)"/-2 "$(add 2 -3)"/' "$repo/tests/calc.test.sh" > "$repo/tests/calc-neg-red.test.sh"
chmod +x "$repo/tests/calc-neg-red.test.sh"
git -C "$repo" add -A && git -C "$repo" commit -qm 'multi-case suite whose kept case already red'
table="$work/redundant-red.tsv"
printf 'tests/calc-neg-red.test.sh\tadds two numbers\tredundant\tadds a negative\t%s\n' "$work/add-subtracts.patch" > "$table"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/redundant-red.err")" && code=0 || code=$?
row="$(grep -F 'adds two numbers' <<<"$out" | grep -wF unproven || true)"
if [[ "$code" == 1 && -n "$row" ]] && grep -F 'replacement adds a negative' "$work/redundant-red.err" > /dev/null &&
   ! grep -F 'old case' "$work/redundant-red.err" > /dev/null; then
  ok
else
  no "#1596: a row whose kept bash case already fails with the mutation not applied reads unproven and names the replacement, not the old case (exit=$code want 1)
    stdout: $out
    stderr: $(cat "$work/redundant-red.err")"
fi

table="$work/multi-dies.tsv"
printf 'tests/calc.test.sh\tadds two numbers\tredundant\tadds a negative\t%s\n' "$work/dies.patch" > "$table"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/multi-dies.err")" && code=0 || code=$?
if [[ "$code" == 2 ]] && ! grep -w owed <<<"$out" > /dev/null; then
  ok
else
  no "#1596: a row whose old suite holds several cases ends in an error, not owed, when under the mutation that suite dies before its count line (exit=$code want 2)
    stdout: $out
    stderr: $(cat "$work/multi-dies.err")"
fi

table="$work/multi-all-fail.tsv"
printf 'tests/calc.test.sh\tadds two numbers\treplaced\t%s\t%s\n' "$node" "$work/none-stays-green.patch" > "$table"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/multi-all-fail.err")" && code=0 || code=$?
row="$(grep -F 'adds two numbers' <<<"$out" | grep -wF owed || true)"
if [[ "$code" == 1 && -n "$row" ]]; then
  ok
else
  no "#1594: a row whose old suite holds more than one case reads owed when the mutation fails every case of that suite, though the replacement is caught (exit=$code want 1)
    stdout: $out
    stderr: $(cat "$work/multi-all-fail.err")"
fi

printf 'mul() { echo $(( $1 * $2 )); }\n' > "$work/mul.sh"
sed 's/\*/\//' "$work/mul.sh" > "$work/mul.mutated"
diff -u --label a/calc.sh --label b/calc.sh "$work/mul.sh" "$work/mul.mutated" > "$work/does-not-apply.patch"
table="$work/does-not-apply.tsv"
printf 'tests/calc.test.sh\tadds two numbers\tredundant\tadds a negative\t%s\n' "$work/does-not-apply.patch" > "$table"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/does-not-apply.err")" && code=0 || code=$?
if [[ "$code" == 2 ]]; then
  ok
else
  no "a row whose mutation does not apply to the tree exits 2 (exit=$code want 2)
    stdout: $out
    stderr: $(cat "$work/does-not-apply.err")"
fi

sed '/^echo "\$pass passed/d' "$repo/tests/calc.test.sh" > "$repo/tests/no-count.test.sh"
chmod +x "$repo/tests/no-count.test.sh"
git -C "$repo" add -A && git -C "$repo" commit -qm 'suite without a count line'
unrunnable() {
  local table="$work/unrunnable-$1.tsv"
  printf '%s\n' "$2" > "$table"
  out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/unrunnable-$1.err")" && code=0 || code=$?
  unrunnable_out+="
    $1 (exit=$code) stdout: $out
    $1 stderr: $(cat "$work/unrunnable-$1.err")"
}
unrunnable_out=""
unrunnable missing-suite \
  "tests/absent.test.sh"$'\t'"adds two numbers"$'\t'"redundant"$'\t'"adds a negative"$'\t'"$work/add-subtracts.patch"
missing_code="$code"
unrunnable uncollected \
  "tests/calc.test.sh"$'\t'"adds two numbers"$'\t'"replaced"$'\t'"tests/test_calc.py::test_not_there"$'\t'"$work/add-subtracts.patch"
uncollected_code="$code"
if [[ "$missing_code" == 2 && "$uncollected_code" == 2 ]]; then
  ok
else
  no "a row whose case cannot be run — a suite path that does not exist, a pytest node id that is not collected — exits 2 (missing suite exit=$missing_code, uncollected node exit=$uncollected_code, want 2 each)$unrunnable_out"
fi

snapshot() {
  local files
  files="$(cd "$repo" && find . -path ./.git -prune -o -type f -print | LC_ALL=C sort)"
  (cd "$repo" && git ls-files -s && paste <(printf '%s\n' "$files") \
    <(printf '%s\n' "$files" | git hash-object --stdin-paths))
}
printf 'staged\n' > "$repo/staged.txt"
git -C "$repo" add staged.txt
printf 'sub() { echo $(( $1 - $2 )); }\n' >> "$repo/calc.sh"
printf 'untracked\n' > "$repo/untracked.txt"
sed 's/\$1 + \$2/$1 - $2/' "$repo/calc.sh" > "$work/dirty.mutated"
diff -u --label a/calc.sh --label b/calc.sh "$repo/calc.sh" "$work/dirty.mutated" > "$work/dirty.patch"
{ cat "$repo/calc.sh"; echo 'exit 9'; } > "$work/dirty-dies.mutated"
diff -u --label a/calc.sh --label b/calc.sh "$repo/calc.sh" "$work/dirty-dies.mutated" > "$work/dirty-dies.patch" || true
table="$work/dirty.tsv"
printf 'tests/calc.test.sh\tadds two numbers\tredundant\tadds a negative\t%s\n' "$work/dirty.patch" > "$table"
before="$(snapshot)"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/dirty.err")" && code=0 || code=$?
after="$(snapshot)"
if [[ ( "$code" == 0 || "$code" == 1 ) && "$before" == "$after" ]]; then
  ok
else
  no "after the pairs check exits 0 or 1 the working tree and the index are byte-identical to before it, a staged change, an unstaged change to a file the mutation patches and an untracked file included (exit=$code want 0 or 1)
$(diff <(printf '%s\n' "$before") <(printf '%s\n' "$after"))
    stdout: $out
    stderr: $(cat "$work/dirty.err")"
fi


table="$work/unmutated-dies.tsv"
printf 'tests/no-count.test.sh\tadds two numbers\tredundant\tadds a negative\t%s\n' "$work/add-subtracts.patch" > "$table"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/unmutated-dies.err")" && code=0 || code=$?
row="$(grep -F 'adds two numbers' <<<"$out" | grep -wF unproven || true)"
if [[ "$code" == 1 && -n "$row" ]] \
  && grep -F 'tests/no-count.test.sh' "$work/unmutated-dies.err" | grep -F 'did not run to completion' > /dev/null; then
  ok
else
  no "#1612: a row whose old suite dies before its count line run unmutated reads unproven and exits 1, with stderr naming the suite and saying it did not run to completion (exit=$code want 1)
    stdout: $out
    stderr: $(cat "$work/unmutated-dies.err")"
fi

{ cat "$repo/tests/test_calc.py"; echo 'def (:'; } > "$work/breaks-collection.mutated"
diff -u --label a/tests/test_calc.py --label b/tests/test_calc.py "$repo/tests/test_calc.py" "$work/breaks-collection.mutated" > "$work/breaks-collection.patch" || true
table="$work/raises-mutated.tsv"
printf 'tests/calc.test.sh\tadds two numbers\treplaced\t%s\t%s\n' "$node" "$work/breaks-collection.patch" > "$table"
before="$(snapshot)"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/raises-mutated.err")" && code=0 || code=$?
after="$(snapshot)"
if [[ "$code" == 2 && "$before" == "$after" ]]; then
  ok
else
  no "#1612: an exception raised while a row's mutation is applied — a pytest replacement the mutation stops collecting — is raised after the mutation is reverted, so the tree is byte-identical to before the row (exit=$code want 2)
$(diff <(printf '%s\n' "$before") <(printf '%s\n' "$after"))
    stdout: $out
    stderr: $(cat "$work/raises-mutated.err")"
fi

rm -rf "$repo/.pytest_cache"
before="$(snapshot)"
out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/raises-mutated.err")" && code=0 || code=$?
after="$(snapshot)"
if [[ "$code" == 2 && "$before" == "$after" ]]; then
  ok
else
  no "#1612: a row that raises with its mutation applied leaves every file of the tree byte-identical to before it, .pytest_cache included (exit=$code want 2)
$(diff <(printf '%s\n' "$before") <(printf '%s\n' "$after"))
    stdout: $out
    stderr: $(cat "$work/raises-mutated.err")"
fi

exit_two_out=""
exit_two_codes=""
for scenario in does-not-apply:does-not-apply dies:dirty-dies uncollected:dirty; do
  name="${scenario%%:*}" patch="$work/${scenario#*:}.patch"
  case "$name" in
    does-not-apply) row="tests/calc.test.sh"$'\t'"adds two numbers"$'\t'"redundant"$'\t'"adds a negative" ;;
    dies) row="tests/calc.test.sh"$'\t'"adds two numbers"$'\t'"redundant"$'\t'"adds a negative" ;;
    uncollected) row="tests/calc.test.sh"$'\t'"adds two numbers"$'\t'"replaced"$'\t'"tests/test_calc.py::test_not_there" ;;
  esac
  table="$work/exit-two-$name.tsv"
  printf '%s\t%s\n' "$row" "$patch" > "$table"
  before="$(snapshot)"
  out="$(cd "$repo" && "$PARITY" "$table" 2>"$work/exit-two-$name.err")" && code=0 || code=$?
  after="$(snapshot)"
  exit_two_codes+=" $name=$code"
  if [[ "$code" != 2 || "$before" != "$after" ]]; then
    exit_two_out+="
    $name (exit=$code want 2):
$(diff <(printf '%s\n' "$before") <(printf '%s\n' "$after"))
    $name stdout: $out
    $name stderr: $(cat "$work/exit-two-$name.err")"
  fi
done
if [[ -z "$exit_two_out" ]]; then
  ok
else
  no "after the pairs check exits 2 — a mutation that does not apply, a bash suite that never reaches its count line under the mutation or a pytest node id that is not collected while the mutation is in place — the working tree and the index are byte-identical to before it, a staged change, an unstaged change and an untracked file included (exits:$exit_two_codes)$exit_two_out"
fi

finish

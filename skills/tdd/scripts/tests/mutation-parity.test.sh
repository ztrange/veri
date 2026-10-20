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

mutant none-stays-green 's/\$1 + \$2/$1 - $2/; s/hello/bye/'

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

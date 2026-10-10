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

finish

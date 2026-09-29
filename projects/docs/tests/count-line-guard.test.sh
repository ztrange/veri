#!/usr/bin/env bash
# Unit test for projects/docs/Makefile's test target: a suite that never reaches its count line
# fails the target, named. Plain-shell asserts, same idiom as the other suites under docs/tests/.
#
# Contract under test:
#   `make -C <docs> test` over a tests/ holding one suite that exits 0 without printing a
#   `<n> passed, <m> failed` last line exits non-zero and prints
#   `<suite>: never reached its count line`.
#
# Run: projects/docs/tests/count-line-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DOCS="$HERE/.."
pass=0 fail=0

name="make test fails, naming the suite, for a suite that exits 0 without a count line"

scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
mkdir "$scratch/tests"
cp "$DOCS/Makefile" "$scratch/Makefile"
printf '#!/bin/sh\necho "half way there"\nexit 0\n' > "$scratch/tests/dies-quietly.test.sh"
chmod +x "$scratch/tests/dies-quietly.test.sh"

out="$(env -u VERI_TEST_CMD make -C "$scratch" test 2>&1 < /dev/null)"
rc=$?

problems=()
[[ "$rc" -ne 0 ]] || problems+=("want a non-zero exit, got 0")
[[ "$out" == *"dies-quietly.test.sh: never reached its count line"* ]] ||
  problems+=("output does not name the suite as never reaching its count line: $(printf '%s\n' "$out" | tail -n 2 | tr '\n' '|')")

if [[ "${#problems[@]}" -eq 0 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name"
  printf '    %s\n' "${problems[@]}"
fi

name="make test fails, naming the suite, for a suite that runs one case then dies on an unbound variable and exits 0"

mkdir "$scratch/unbound"
mkdir "$scratch/unbound/tests"
cp "$DOCS/Makefile" "$scratch/unbound/Makefile"
cat > "$scratch/unbound/tests/unbound.test.sh" <<'SUITE'
#!/usr/bin/env bash
set -uo pipefail
trap 'exit 0' EXIT
echo "ok - first case"
[[ cases_run -le 1 ]]
echo "1 passed, 0 failed"
SUITE
chmod +x "$scratch/unbound/tests/unbound.test.sh"

suite_rc=0
( cd "$scratch/unbound" && env -u VERI_TEST_CMD ./tests/unbound.test.sh > /dev/null 2>&1 < /dev/null ) || suite_rc=$?
out="$(env -u VERI_TEST_CMD make -C "$scratch/unbound" test 2>&1 < /dev/null)"
rc=$?

problems=()
[[ "$suite_rc" -eq 0 ]] || problems+=("fixture premise broken: the suite exits $suite_rc, want 0")
[[ "$rc" -ne 0 ]] || problems+=("want a non-zero exit, got 0")
[[ "$out" == *"unbound.test.sh: never reached its count line"* ]] ||
  problems+=("output does not name the suite as never reaching its count line: $(printf '%s\n' "$out" | tail -n 2 | tr '\n' '|')")

if [[ "${#problems[@]}" -eq 0 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name"
  printf '    %s\n' "${problems[@]}"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

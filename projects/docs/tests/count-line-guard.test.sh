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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

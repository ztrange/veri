#!/usr/bin/env bash
# Unit test for projects/docs/Makefile: make run from projects/docs/ resolves the docs target.
# Plain-shell asserts, same idiom as the other suites under docs/tests/.
#
# Contract under test:
#   `make -C projects/docs -n docs` exits 0 and its plan runs projects/docs/build-walkthrough.py.
#   `make -C projects/docs -n fresh` and `-n check` exit 0 and their plans run
#   projects/docs/check-walkthrough.py.
#
# Run: projects/docs/tests/makefile.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DOCS="$HERE/.."
pass=0 fail=0

name="make -C projects/docs -n docs plans a run of build-walkthrough.py"

out="$(env -u VERI_TEST_CMD make -C "$DOCS" -n docs 2>&1)"
rc=$?

problems=()
[[ "$rc" -eq 0 ]] || problems+=("want exit 0, got $rc: $(printf '%s\n' "$out" | tail -n 1)")
[[ "$out" == *build-walkthrough.py* ]] || problems+=("plan does not name build-walkthrough.py: $(printf '%s\n' "$out" | tail -n 1)")

if [[ "${#problems[@]}" -eq 0 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name"
  printf '    %s\n' "${problems[@]}"
fi

name="make -C projects/docs -n fresh and -n check plan a run of check-walkthrough.py"

problems=()
for target in fresh check; do
  out="$(env -u VERI_TEST_CMD make -C "$DOCS" -n "$target" 2>&1)"
  rc=$?
  [[ "$rc" -eq 0 ]] || problems+=("$target: want exit 0, got $rc: $(printf '%s\n' "$out" | tail -n 1)")
  [[ "$out" == *check-walkthrough.py* ]] || problems+=("$target: plan does not name check-walkthrough.py: $(printf '%s\n' "$out" | tail -n 1)")
done

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

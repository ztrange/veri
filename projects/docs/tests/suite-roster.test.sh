#!/usr/bin/env bash
# Unit test for the roster of projects/docs/tests/: the seven pipeline suites are copied there and
# the ADR suites and suite-lanes stay behind. Plain-shell asserts, same idiom as the other suites
# under docs/tests/.
#
# Contract under test:
#   projects/docs/tests/ holds build-guards, commentary-figures, docs-guard-filter, docs-owed,
#   generator-inputs, lane-insulation and merge-gates, each naming projects/docs/ paths, and holds
#   none of docs-gap-adr, no-verdict-relaunch-adr, preamble-cost-adr or suite-lanes.
#
# Run: projects/docs/tests/suite-roster.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
pass=0 fail=0

name="projects/docs/tests/ holds the seven pipeline suites naming projects/docs/ paths, and not the ADR suites or suite-lanes"

problems=()
for s in build-guards commentary-figures docs-guard-filter docs-owed generator-inputs lane-insulation merge-gates; do
  if [[ ! -f "$HERE/$s.test.sh" ]]; then
    problems+=("$s.test.sh: missing")
  elif ! grep -F 'projects/docs/' "$HERE/$s.test.sh" > /dev/null; then
    problems+=("$s.test.sh: names no projects/docs/ path")
  fi
done
for s in docs-gap-adr no-verdict-relaunch-adr preamble-cost-adr suite-lanes; do
  [[ ! -e "$HERE/$s.test.sh" ]] || problems+=("$s.test.sh: present, but it stays with veri")
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

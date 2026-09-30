#!/usr/bin/env bash
# Audits that no suite carries its own copy of the `report` helper: every file under tests/ and
# tests/unit/ that defines a function named `report` — the suites and tests/record-helpers.sh
# alike — is named, bar lib/harness.sh, the one definition they source.
#
# Admitted to the fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/no-report-copies.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TESTS="$(cd "$HERE/.." && pwd)"
pass=0 fail=0
export LC_ALL=C

name="no suite defines its own report, and lib/harness.sh defines it"
problems=""
copies="$(cd "$TESTS" && grep -nE '^[[:space:]]*(function[[:space:]]+)?report[[:space:]]*\(\)' \
  ./*.sh ./unit/*.sh)"
while IFS= read -r hit; do
  [[ -n "$hit" ]] || continue
  file="${hit%%:*}"
  rest="${hit#*:}"
  problems+="    ${file#./}:${rest%%:*} defines report()"$'\n'
done <<< "$copies"
if ! grep -E '^report[[:space:]]*\(\)' "$TESTS/lib/harness.sh" > /dev/null; then
  problems+="    lib/harness.sh does not define report()"$'\n'
fi
if [[ -z "$problems" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1)); echo "FAIL - $name"
  printf '%s' "$problems"
fi

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

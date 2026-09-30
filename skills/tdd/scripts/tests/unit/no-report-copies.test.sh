#!/usr/bin/env bash
# Audits that no suite carries its own copy of what lib/harness.sh defines. Every file under
# tests/ and tests/unit/ that defines a function named `report` — the suites and
# tests/record-helpers.sh alike — is named, bar lib/harness.sh, the one definition they source;
# so is every one that defines `ok` or `no`, initialises `pass=0 fail=0` or prints its own
# count line, bar harness.test.sh, whose subject is the harness itself.
#
# Admitted to the fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/no-report-copies.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TESTS="$(cd "$HERE/.." && pwd)"
export LC_ALL=C
# shellcheck disable=SC1091
source "$TESTS/lib/harness.sh"

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
  ok
else
  no "$name"
  printf '%s' "$problems"
fi

name="no suite defines its own ok/no, initialises its own counters or prints its own count line"
problems=""
copies="$(cd "$TESTS" && grep -nE \
  -e '^[[:space:]]*(function[[:space:]]+)?(ok|no)[[:space:]]*\(\)' \
  -e '^[[:space:]]*pass=0[[:space:]]+fail=0' \
  -e '^[[:space:]]*(echo|printf)[[:space:]].*\$(\{pass\}|pass)[^"]* passed, .*failed' \
  ./*.sh ./unit/*.sh | grep -v '^\./unit/harness\.test\.sh:')"
while IFS= read -r hit; do
  [[ -n "$hit" ]] || continue
  file="${hit%%:*}"
  rest="${hit#*:}"
  problems+="    ${file#./}:${rest%%:*} carries its own harness scaffolding"$'\n'
done <<< "$copies"
if [[ -z "$problems" ]]; then
  ok
else
  no "$name"
  printf '%s' "$problems"
fi

finish

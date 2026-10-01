#!/usr/bin/env bash
# Guard suite — no suite under skills/tdd/scripts/tests/ asks the `test` recipe to run a
# named suite without emptying UNIT_TESTS. Its subject is the tree it is run in.
#
# Contract under test:
#   A suite that calls `make … test TESTS=…` and leaves UNIT_TESTS out is reported as
#   `<suite>:<line>`, because the recipe then runs every suite under tests/unit/ as well.
#
# Run: skills/tdd/scripts/tests/no-recipe-unit-tier.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SELF="$(basename "$0")"

MAKE_WORD='(^|[[:space:](])make[[:space:]]'
RECIPE_CALL="$MAKE_WORD.*[[:space:]]test[[:space:]]+(.*[[:space:]])?TESTS="
UNIT_EMPTIED='UNIT_TESTS=([[:space:]]|$|["])'

source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

offenders() {
  local suite hit line text
  for suite in "$HERE"/*.test.sh; do
    [[ "$(basename "$suite")" == "$SELF" ]] && continue
    while IFS= read -r hit; do
      line="${hit%%:*}"
      text="${hit#*:}"
      [[ "$text" =~ ^[[:space:]]*# ]] && continue
      [[ "$text" =~ $UNIT_EMPTIED ]] && continue
      printf '%s:%s:%s\n' "$(basename "$suite")" "$line" "$text"
    done < <(grep -nE -- "$RECIPE_CALL" "$suite")
  done
  return 0
}

name="no suite under tests/ calls the test recipe with TESTS= and leaves UNIT_TESTS unemptied"
problems=()

while IFS= read -r site; do
  [[ -n "$site" ]] || continue
  problems+=("${site%%:*}:$(cut -d: -f2 <<< "$site") runs the recipe's whole fast tier beside the suite it names; add UNIT_TESTS= to the call: $(flat "${site#*:*:}")")
done < <(offenders)

report "$name"

finish

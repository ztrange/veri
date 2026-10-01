#!/usr/bin/env bash
# Unit tests for the guard suite that keeps a suite from asking the `test` recipe to run a
# named suite while leaving the fast tier on — no-recipe-unit-tier.test.sh. Like
# job-spec-guard.test.sh this suite has no script as its subject: its subject is what the guard
# reports about the directory it is run in. Zero-dependency plain-shell asserts.
#
# Contract under test:
#   Over a directory holding one planted suite whose nested recipe call names a fixture and
#   leaves UNIT_TESTS unemptied, the guard fails and names that suite as `<suite>:<line>`;
#   once the plant is removed it passes.
#
# Run: skills/tdd/scripts/tests/recipe-unit-tier-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

GUARD_BASE='no-recipe-unit-tier'
GUARD_PATH="$HERE/$GUARD_BASE.test.sh"
PLANT_NAME='planted-offender.test.sh'

# hazard: assembled from parts — spelled whole here, this suite's own line would trip the guard.
MAKE_CMD='make'
RECIPE_ARGS='-C "$ROOT" test TESTS=fixture.test.sh'
MARK='recipe-unit-tier-probe'

source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

plant() {
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch directory to plant the offender in, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/lib"
  cp "$GUARD_PATH" "$tree/$GUARD_BASE.test.sh"
  cp "$HERE/lib/harness.sh" "$tree/lib/"
  chmod 755 "$tree/$GUARD_BASE.test.sh"
  plant_path="$tree/$PLANT_NAME"
  {
    echo '#!/usr/bin/env bash'
    echo 'set -uo pipefail'
    printf 'out="$(%s %s)"  # %s\n' "$MAKE_CMD" "$RECIPE_ARGS" "$MARK"
  } > "$plant_path"
  chmod 755 "$plant_path"
  plant_line="$(grep -n "$MARK" "$plant_path" | cut -d: -f1)"
}

run_guard() {
  guard_out="$("$tree/$GUARD_BASE.test.sh" 2>&1)" && guard_code=0 || guard_code=$?
}

name="$GUARD_BASE.test.sh goes red naming the planted suite as <suite>:<line> and green again once it is removed"
problems=()

if [[ -f "$GUARD_PATH" ]] && plant; then
  run_guard
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over a planted suite whose recipe call leaves UNIT_TESTS unemptied; it exited 0 and said: $(flat "$guard_out")")
  grep -F -- "$PLANT_NAME:$plant_line" <<< "$guard_out" > /dev/null ||
    problems+=("the guard never named the planted site as $PLANT_NAME:$plant_line; it said: $(flat "$guard_out")")

  rm -f "$plant_path"
  run_guard
  [[ "$guard_code" == 0 ]] ||
    problems+=("want the guard to pass once the planted suite is removed; it exited $guard_code and said: $(flat "$guard_out")")
else
  problems+=("there is no guard suite at $GUARD_PATH, or the plant could not be made")
fi

report "$name"

finish

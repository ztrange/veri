#!/usr/bin/env bash
# Unit tests for what the `test` recipe says over a tree whose code has moved past the
# SYSTEM prose that states it. Its subject is the verdict the development lane's own runner
# reaches over a tree, not a script.
#
# Contract under test:
#   Over a copy of this tree with refactor-budget.sh's VERI_REFACTOR_BUDGET default bumped by
#   one and both prose statements of it untouched, `make test` runs the suite that owns that
#   script, comes back non-zero with its own `SUITES FAILED` verdict, and the output names
#   both sentences the change left behind.
#
# Run: skills/tdd/scripts/tests/prose-drift-red.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
ROOT="$(cd "$HERE/../../../.." && pwd)"

WORK="$(scratch_dir)"

TUNABLE='VERI_REFACTOR_BUDGET'
SCRIPT='skills/tdd/scripts/refactor-budget.sh'
SUITE='skills/tdd/scripts/tests/refactor-budget.test.sh'
SUITE_NAME="${SUITE##*/}"

SKILL_MARKER='SKILL.md'
HEADER_MARKER='header'

FAILED_LINE='SUITES FAILED'

flat() { printf '%s' "$1" | tr '\n' '/'; }

why() { flat "$( { grep -E '^FAIL - ' <<< "$1"; tail -5 <<< "$1"; } )"; }

figure() {
  local hit
  hit="$(head -1 < <(grep -oE "$2" "$1"))"
  [[ -n "$hit" ]] || { echo '<none>'; return; }
  printf '%s' "$hit" | grep -oE '[0-9]+' | tail -1
}

ENCODED_RE="$TUNABLE:-[0-9]+"
HEADER_RE="$TUNABLE \(default [0-9]+"
SKILL_RE="$TUNABLE.{0,3} \(default [0-9]+"

tree_whose_default_moved() {
  local planted="$WORK/tree" here_default
  mkdir -p "$planted"
  cp -R "$ROOT/skills" "$planted/skills"
  cp "$ROOT/Makefile" "$planted/"
  here_default="$(figure "$ROOT/$SCRIPT" "$ENCODED_RE")"
  sed -E "s/$TUNABLE:-[0-9]+/$TUNABLE:-$((here_default + 1))/" \
    "$ROOT/$SCRIPT" > "$planted/$SCRIPT.planted"
  mv "$planted/$SCRIPT.planted" "$planted/$SCRIPT"
  chmod 755 "$planted/$SCRIPT"
  printf '%s' "$planted"
}

probe_plant_is_real() {
  local moved here site
  moved="$(figure "$1/$SCRIPT" "$ENCODED_RE")"
  here="$(figure "$ROOT/$SCRIPT" "$ENCODED_RE")"
  [[ "$moved" =~ ^[0-9]+$ && "$here" =~ ^[0-9]+$ && "$moved" != "$here" ]] ||
    problems+=("the case is vacuous: $SCRIPT encodes $moved in the copy against $here here, so the constant the prose describes has not moved")
  while IFS='|' read -r site file regex; do
    [[ -n "$site" ]] || continue
    [[ "$(figure "$1/$file" "$regex")" == "$here" ]] ||
      problems+=("the case is vacuous: $site in the copy says $(figure "$1/$file" "$regex"), not the $here it said before the plant, so no sentence was left behind")
  done <<SITES
$SCRIPT-header|$SCRIPT|$HEADER_RE
SKILL.md-refactor|skills/tdd/SKILL.md|$SKILL_RE
SITES
}

name="\`make test\` is red over a tree whose $TUNABLE default has moved and whose two prose statements of it have not, naming both"
problems=()

planted="$(tree_whose_default_moved)"
probe_plant_is_real "$planted"

out="$(make -C "$planted" test TESTS="$SUITE" 2>&1)" && code=0 || code=$?

[[ "$code" != 0 ]] ||
  problems+=("want a non-zero exit from the runner over a tree whose $TUNABLE default has drifted from the prose stating it; got 0: $(flat "$out")")
grep -Fqx "$FAILED_LINE" <<< "$out" ||
  problems+=("want the runner's own '$FAILED_LINE' over that tree; got: $(why "$out")")
grep -Fqx "== $SUITE_NAME" <<< "$out" ||
  problems+=("want the runner to have announced '== $SUITE_NAME' — an empty roster says nothing about the guard; got: $(flat "$out")")
grep -Fq "$SKILL_MARKER" <<< "$out" ||
  problems+=("want the red to name '$SKILL_MARKER', the statement the plant left behind — a red that never mentions it is the figure's own cases failing, not the drift guard; got: $(why "$out")")
grep -Fq "$HEADER_MARKER" <<< "$out" ||
  problems+=("want the red to name the script's own '$HEADER_MARKER', the other statement the plant left behind; got: $(why "$out")")

report "$name"

finish

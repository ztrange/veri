#!/usr/bin/env bash
# Unit tests for what the `test` recipe says over a tree whose scripts have grown past the
# prose that lists them. Its subject is the verdict the development lane's own runner reaches
# over a tree, not a script.
#
# Contract under test:
#   Over a tree with one script one line longer than the suite that owns it expects, `make
#   test` runs that suite, that suite passes, and the runner says `all suites green`.
#
# Run: skills/tdd/scripts/tests/prose-lag-green.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
ROOT="$(cd "$HERE/../../../.." && pwd)"

WORK="$(scratch_dir)"

SCRIPT='skills/tdd/scripts/fixture-prose-lag.sh'
SCRIPT_NAME="${SCRIPT##*/}"
SUITE='skills/tdd/scripts/tests/fixture-prose-lag.test.sh'
SUITE_NAME="${SUITE##*/}"

GREEN_LINE='all suites green'

flat() { printf '%s' "$1" | tr '\n' '/'; }

why() { flat "$( { grep -E '^FAIL - ' <<< "$1"; tail -5 <<< "$1"; } )"; }

lines_of() { awk 'END {print NR}' "$1"; }

tree_grown_past_its_prose() {
  local planted="$WORK/tree"
  mkdir -p "$planted/$(dirname "$SCRIPT")" "$planted/$(dirname "$SUITE")"
  cp "$ROOT/Makefile" "$planted/"
  mkdir -p "$planted/skills/tdd/scripts/lib"
  cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$planted/skills/tdd/scripts/lib/"
  cp "$ROOT/skills/tdd/scripts/run-suite.sh" "$planted/skills/tdd/scripts/"
  cp -R "$ROOT/skills/tdd/scripts/veri" "$planted/skills/tdd/scripts/"

  {
    printf '#!/usr/bin/env bash\n'
    printf '# A fixture script prose-lag-green.test.sh grows to observe make test'"'"'s verdict\n'
    printf '# over a tree whose prose has fallen behind its code (#143). Not shipped.\n'
    printf 'echo ok\n'
  } > "$WORK/pristine"
  cp "$WORK/pristine" "$planted/$SCRIPT"
  chmod 755 "$planted/$SCRIPT"

  {
    printf '#!/usr/bin/env bash\n'
    printf '# Fixture suite for prose-lag-green.test.sh: %s still prints "ok".\n' "$SCRIPT_NAME"
    printf 'set -uo pipefail\n'
    printf 'here="$(cd "$(dirname "$0")" && pwd)"\n'
    printf 'pass=0 fail=0\n'
    printf 'out="$("$here/../%s" 2>/dev/null)"\n' "$SCRIPT_NAME"
    printf '[[ "$out" == ok ]] && pass=$((pass + 1)) || { fail=$((fail + 1)); echo "FAIL - %s still prints ok"; }\n' "$SCRIPT_NAME"
    printf 'echo "----"\n'
    printf 'echo "${pass:-0} passed, $fail failed"\n'
    printf '[[ "$fail" -eq 0 ]]\n'
  } > "$planted/$SUITE"
  chmod 755 "$planted/$SUITE"

  printf '\n# a line this script grew after the prose that lists it was written\n' >> "$planted/$SCRIPT"
  printf '%s' "$planted"
}

probe_plant_is_real() {
  local grown here
  grown="$(lines_of "$1/$SCRIPT")"
  here="$(lines_of "$WORK/pristine")"
  [[ "$grown" -gt "$here" ]] ||
    problems+=("the case is vacuous: $SCRIPT is $grown lines in the planted tree against $here in the pristine fixture, so nothing in the fixture was left describing a file that has moved on")
}

name="\`make test\` is green over a tree whose $SCRIPT_NAME has grown past the prose listing it, with nothing rebuilt in between"
problems=()

planted="$(tree_grown_past_its_prose)"
probe_plant_is_real "$planted"

out="$(make -C "$planted" test TESTS="$SUITE" UNIT_TESTS= 2>&1)" && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from the runner over a tree whose $SCRIPT has grown without a rebuild — a development commit must not owe one to keep the baseline green; got $code: $(why "$out")")
grep -Fqx "$GREEN_LINE" <<< "$out" ||
  problems+=("want the runner's own '$GREEN_LINE' over that tree; got: $(why "$out")")
grep -Fqx "== $SUITE_NAME" <<< "$out" ||
  problems+=("want the runner to have announced '== $SUITE_NAME' — an empty roster prints a green verdict over nothing run; got: $(flat "$out")")

report "$name"

finish

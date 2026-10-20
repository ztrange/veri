#!/usr/bin/env bash
# Unit tests for the refusal veri gives on a bash older than 5, at the three places a run or a
# test run begins: `make test`, run-conductor.sh (what starts a run) and leaf-launchable.sh (the
# preflight check SKILL.md runs before any leaf is paid for). Zero-dependency plain-shell asserts.
#
# Contract under test:
#   1. `make test` refuses, exit non-zero, naming the requirement, before any suite runs, when
#      the bash on PATH is older than 5 — and runs its suites when it is not.
#   2. run-conductor.sh refuses with exit 2, naming the requirement, before it launches anything.
#   3. leaf-launchable.sh refuses with exit 2, naming the requirement — and still answers 0 for
#      a launchable binary on bash 5.
#   4. On a real bash older than 5, the refusal comes from the bash itself, not the stand-in.
#   5. run-conductor.sh refuses with exit 2, naming the Python 3.12 floor and the version found,
#      before it launches anything, when python3 is older than 3.12.
#   6. leaf-launchable.sh refuses with exit 2, naming the Python 3.12 floor and the version
#      found, when python3 is older than 3.12.
#   7. leaf-launchable.sh does not refuse on the Python floor when the python3 version cannot be read.
#   8. run-conductor.sh's Python-floor refusal names $VERI_VENV/bin to put first on PATH when the
#      venv there meets the floor.
#   9. leaf-launchable.sh's Python-floor refusal names $VERI_VENV/bin to put first on PATH when the
#      venv there meets the floor.
#  10. run-conductor.sh's Python-floor refusal, with no venv at $VERI_VENV, is today's one line and
#      names no venv path.
#  11. leaf-launchable.sh's Python-floor refusal, with no venv at $VERI_VENV, is today's one line and
#      names no venv path.
#  12. run-conductor.sh's and leaf-launchable.sh's Python-floor refusals, with a venv at $VERI_VENV
#      whose own interpreter is also below the floor, are today's one line and name no venv path.
#  13. On a real python3 below the floor first on PATH, leaf-launchable.sh refuses with exit 2,
#      naming the floor and that interpreter's version.
#
# Run: skills/tdd/scripts/tests/bash-version-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
SCRIPTS="$HERE/.."

REQUIREMENT='needs bash 5 or newer'

GREEN_FIXTURE='skills/tdd/scripts/tests/fixtures/live-suites/ends-green.test.sh'


source "$HERE/lib/harness.sh"

flat() { printf '%s' "$1" | tr '\n' '/'; }

work="$(scratch_dir)"

claude_stub "$work" "$(cat <<'C'
: > "$LAUNCHED"
echo "2.1.0 (Claude Code)"
C
)"

old_out="$(env VERI_BASH_MAJOR=3 make -C "$ROOT" test TESTS="$GREEN_FIXTURE" UNIT_TESTS= 2>&1)"
new_out="$(env VERI_BASH_MAJOR=5 make -C "$ROOT" test TESTS="$GREEN_FIXTURE" UNIT_TESTS= 2>&1)"

name="the nested make test calls run only their fixture: the recipe output lists no suite from tests/unit/"
problems=()
for unit_suite in "$HERE"/unit/*.test.sh; do
  unit_name="$(basename "$unit_suite")"
  [[ "$old_out" != *"== $unit_name"* ]] || problems+=("bash 3 call ran unit suite $unit_name")
  [[ "$new_out" != *"== $unit_name"* ]] || problems+=("bash 5 call ran unit suite $unit_name")
done
report "$name"

finish

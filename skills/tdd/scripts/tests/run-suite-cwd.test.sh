#!/usr/bin/env bash
# Unit tests for run-suite.sh run with its working directory outside veri.
#
# Contract under test:
#   run-suite.sh, run from inside a git repository that is not veri and has no Makefile, exits
#   with a red suite's own code and exits 1 naming a suite that exits 0 without its count line.
#
# Run: skills/tdd/scripts/tests/run-suite-cwd.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
source "$HERE/lib/harness.sh"

FIXTURE='skills/tdd/scripts/tests/fixtures/silent-death/dies-silently.test.sh'
FIXTURE_PATH="$ROOT/$FIXTURE"
FIXTURE_NAME="$(basename "$FIXTURE")"

RED_FIXTURE_PATH="$ROOT/skills/tdd/scripts/tests/fixtures/live-suites/ends-red.test.sh"

RUNNER="$ROOT/skills/tdd/scripts/run-suite.sh"

GUARD_MESSAGE=': never reached its count line'

COUNT_LINE='^[0-9]+ passed, [0-9]+ failed$'

flat() { printf '%s' "$1" | tr '\n' '/'; }

direct() {
  direct_out="$("$@" 2>&1)" && direct_code=0 || direct_code=$?
}

probe_fixture_dies_quietly() {
  direct "$FIXTURE_PATH"
  [[ "$direct_code" == 0 ]] ||
    problems+=("the fixture no longer exits 0 when it dies; got $direct_code, so nothing here pins a runner that trusts the exit code")
  grep -q 'unbound variable' <<< "$direct_out" ||
    problems+=("the fixture no longer dies from an unbound variable; its output was: $(flat "$direct_out")")
  ! grep -Eq "$COUNT_LINE" <<< "$direct_out" ||
    problems+=("the fixture reached its count line, so it did not die: $(flat "$direct_out")")
}

runner_passes_red_code_through() {
  local runner="$1" where="$2" own_code
  direct "$RED_FIXTURE_PATH"
  own_code="$direct_code"
  direct "$runner" "$RED_FIXTURE_PATH"
  [[ "$direct_code" == "$own_code" ]] ||
    problems+=("want exit $own_code, the red suite's own, from the runner $where; it exited $direct_code and said: $(flat "$direct_out")")
  grep -Fx '0 passed, 1 failed' <<< "$direct_out" > /dev/null ||
    problems+=("want the red suite's own output from the runner $where, ending '0 passed, 1 failed'; it said: $(flat "$direct_out")")
  ! grep -F "$GUARD_MESSAGE" <<< "$direct_out" > /dev/null ||
    problems+=("want no count-line refusal from the runner $where over a red suite that reached its count line; it said: $(flat "$direct_out")")
}

runner_refuses_countless() {
  local runner="$1" where="$2"
  direct "$runner" "$FIXTURE_PATH"
  [[ "$direct_code" == 1 ]] ||
    problems+=("want exit 1 from the runner $where over a suite that exited 0 without its count line; it exited $direct_code and said: $(flat "$direct_out")")
  grep -Fx "$FIXTURE_NAME$GUARD_MESSAGE" <<< "$direct_out" > /dev/null ||
    problems+=("want the line '$FIXTURE_NAME$GUARD_MESSAGE' from the runner $where; it said: $(flat "$direct_out")")
}

name="run-suite.sh, run with the working directory inside a git repository that is not veri and has no Makefile, exits with a red suite's own code and exits 1 naming a suite that exits 0 without its count line (#617)"
problems=()

probe_runner_red_and_countless_from_foreign_repo() {
  local tree
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch directory for the foreign repository, so the question went unasked")
    return 1
  }
  new_repo "$tree/repo" || {
    problems+=("could not make a git repository to run from, so the question went unasked")
    return 1
  }
  cd "$tree/repo" || return 1
  runner_passes_red_code_through "$RUNNER" "run from inside a git repository that is not veri and has no Makefile"
  runner_refuses_countless "$RUNNER" "run from inside a git repository that is not veri and has no Makefile"
  cd "$HERE" || return 1
}

probe_fixture_dies_quietly
probe_runner_red_and_countless_from_foreign_repo

report "$name"

finish

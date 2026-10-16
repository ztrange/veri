#!/usr/bin/env bash
# Unit tests for the guard suite that keeps the fast tier's suites from running real scripts —
# skills/tdd/scripts/tests/no-unit-subprocess.test.sh. Its subject is what that suite reports
# about a planted tree it is run in.
#
# Contract under test:
#   Over a tests directory whose unit/ tier holds a suite that runs a script under
#   skills/tdd/scripts/ as a subprocess, no-unit-subprocess.test.sh fails and names that
#   suite as `<suite>:<line>` at the offending line.
#
# Run: skills/tdd/scripts/tests/unit-subprocess-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

GUARD='skills/tdd/scripts/tests/no-unit-subprocess.test.sh'
GUARD_PATH="$ROOT/$GUARD"
GUARD_NAME="$(basename "$GUARD")"

TESTS_DIR='skills/tdd/scripts/tests'
SCRIPTS_DIR='skills/tdd/scripts'

OFFENDER='runs-a-script.test.sh'
MARK='the-probe'

source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

problems=()
tree="$(scratch_dir)"
mkdir -p "$tree/$TESTS_DIR/unit/lib" "$tree/$SCRIPTS_DIR"
offender_path="$tree/$TESTS_DIR/unit/$OFFENDER"
guard_copy="$tree/$TESTS_DIR/$GUARD_NAME"

{
  echo '#!/usr/bin/env bash'
  echo '# Unit tests for a script — the line below runs it instead of sourcing it.'
  echo 'set -uo pipefail'
  echo 'HERE="$(cd "$(dirname "$0")" && pwd)"'
  echo 'pass=0 fail=0'
  echo 'out="$("$HERE/../../status.sh" 2>&1)"  # '"$MARK"
  echo 'echo "----"'
  echo 'echo "${pass:-0} passed, $fail failed"'
} > "$offender_path"
chmod 755 "$offender_path"
printf '#!/bin/sh\nexit 0\n' > "$tree/$SCRIPTS_DIR/status.sh"
chmod 755 "$tree/$SCRIPTS_DIR/status.sh"
offender_line="$(grep -n "$MARK" "$offender_path" | cut -d: -f1)"

name="no-unit-subprocess.test.sh names a unit-tier suite that runs a script under skills/tdd/scripts/ as a subprocess as <suite>:<line>"

if [[ ! -f "$GUARD_PATH" ]]; then
  problems+=("there is no guard suite at $GUARD, so nothing checks that a suite under $TESTS_DIR/unit/ sources its script instead of running it")
else
  cp "$GUARD_PATH" "$guard_copy"
  cp "$HERE/lib/"*.sh "$tree/$TESTS_DIR/unit/lib/" 2>/dev/null
  mkdir -p "$tree/$TESTS_DIR/lib" && cp "$HERE/lib/"*.sh "$tree/$TESTS_DIR/lib/"
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over a unit suite that runs status.sh at line $offender_line; it exited 0 and said: $(flat "$guard_out")")
  grep -qF -- "$OFFENDER:$offender_line" <<< "$guard_out" ||
    problems+=("no line of the guard's output names $OFFENDER:$offender_line; it said: $(flat "$guard_out")")
fi

report "$name"

finish

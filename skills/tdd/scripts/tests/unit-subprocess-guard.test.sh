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
mkdir -p "$tree/$TESTS_DIR/unit" "$tree/$SCRIPTS_DIR"
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
  mkdir -p "$tree/$TESTS_DIR/lib" && cp "$HERE/lib/"*.sh "$tree/$TESTS_DIR/lib/"
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over a unit suite that runs status.sh at line $offender_line; it exited 0 and said: $(flat "$guard_out")")
  grep -qF -- "$OFFENDER:$offender_line" <<< "$guard_out" ||
    problems+=("no line of the guard's output names $OFFENDER:$offender_line; it said: $(flat "$guard_out")")
fi

report "$name"

problems=()
name="no-unit-subprocess.test.sh lets a planted subprocess-running suite through only when its exemption entry carries a reason, and names the entry when the reason is empty"

plant_exemption() {
  local reason="$1" out="$tree/$TESTS_DIR/exempt-$2.test.sh"
  awk -v entry="  [$OFFENDER]=\"$reason\"" '{ print } /^declare -A EXEMPT=\(/ { print entry }' "$guard_copy" > "$out"
  chmod 755 "$out"
  guard_out="$("$out" 2>&1)" && guard_code=0 || guard_code=$?
}

if [[ -f "$GUARD_PATH" ]]; then
  plant_exemption 'a reason the entry carries' reasoned
  [[ "$guard_code" == 0 ]] ||
    problems+=("want the guard to pass over a subprocess-running suite whose exemption entry carries a reason; it exited $guard_code and said: $(flat "$guard_out")")
  plant_exemption '' blank
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over an exemption entry with an empty reason; it exited 0 and said: $(flat "$guard_out")")
  grep -qF -- "[$OFFENDER]" <<< "$guard_out" ||
    problems+=("no line of the guard's output names the entry [$OFFENDER] whose reason is empty; it said: $(flat "$guard_out")")
fi

report "$name"

problems=()
name="no-unit-subprocess.test.sh passes over the real unit/ tier, naming no offender"

if [[ -f "$GUARD_PATH" ]]; then
  guard_out="$("$GUARD_PATH" 2>&1)" && guard_code=0 || guard_code=$?
  [[ "$guard_code" == 0 ]] ||
    problems+=("want the guard to pass over the real unit/ tier; it exited $guard_code and said: $(flat "$guard_out")")
  ! grep -qE -- '[A-Za-z0-9_.-]+\.test\.sh:[0-9]+' <<< "$guard_out" ||
    problems+=("want no <suite>:<line> offender named over the real unit/ tier; it said: $(flat "$guard_out")")
fi

report "$name"

problems=()
name="no-unit-subprocess.test.sh names a unit-tier suite that assigns a variable a path to a script under skills/tdd/scripts/ and later runs \"\$VAR\" as <suite>:<line>"

VAR_OFFENDER='runs-a-variable.test.sh'
var_tree="$(scratch_dir)"
mkdir -p "$var_tree/$TESTS_DIR/unit" "$var_tree/$SCRIPTS_DIR" "$var_tree/$TESTS_DIR/lib"
var_offender_path="$var_tree/$TESTS_DIR/unit/$VAR_OFFENDER"
{
  echo '#!/usr/bin/env bash'
  echo '# Unit tests for a script — the line below runs it instead of sourcing it.'
  echo 'set -uo pipefail'
  echo 'HERE="$(cd "$(dirname "$0")" && pwd)"'
  echo 'STATUS="$HERE/../../status.sh"'
  echo 'pass=0 fail=0'
  echo 'out="$("$STATUS" 2>&1)"  # '"$MARK"
  echo 'echo "${pass:-0} passed, $fail failed"'
} > "$var_offender_path"
chmod 755 "$var_offender_path"
printf '#!/bin/sh\nexit 0\n' > "$var_tree/$SCRIPTS_DIR/status.sh"
chmod 755 "$var_tree/$SCRIPTS_DIR/status.sh"
var_offender_line="$(grep -n "$MARK" "$var_offender_path" | cut -d: -f1)"

if [[ -f "$GUARD_PATH" ]]; then
  cp "$GUARD_PATH" "$var_tree/$TESTS_DIR/$GUARD_NAME"
  cp "$HERE/lib/"*.sh "$var_tree/$TESTS_DIR/lib/"
  guard_out="$("$var_tree/$TESTS_DIR/$GUARD_NAME" 2>&1)" && guard_code=0 || guard_code=$?
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over a unit suite that runs \"\$STATUS\" at line $var_offender_line; it exited 0 and said: $(flat "$guard_out")")
  grep -qF -- "$VAR_OFFENDER:$var_offender_line" <<< "$guard_out" ||
    problems+=("no line of the guard's output names $VAR_OFFENDER:$var_offender_line; it said: $(flat "$guard_out")")
fi

report "$name"

problems=()
name="no-unit-subprocess.test.sh names a unit-tier suite that runs a script variable inside a command substitution, out=\"\$(\"\$VAR\" ...)\", as <suite>:<line>"

CS_OFFENDER='runs-a-substitution.test.sh'
cs_tree="$(scratch_dir)"
mkdir -p "$cs_tree/$TESTS_DIR/unit" "$cs_tree/$SCRIPTS_DIR" "$cs_tree/$TESTS_DIR/lib"
cs_offender_path="$cs_tree/$TESTS_DIR/unit/$CS_OFFENDER"
{
  echo '#!/usr/bin/env bash'
  echo '# Unit tests for a script — the line below runs it instead of sourcing it.'
  echo 'set -uo pipefail'
  echo 'HERE="$(cd "$(dirname "$0")" && pwd)"'
  echo 'RUN_AFFORDABLE="$HERE/../run-affordable.sh"'
  echo 'run_affordable() {'
  echo '  local out code'
  echo '  out="$("$RUN_AFFORDABLE" "$@" 2>"$HERE/stderr")" && code=0 || code=$?  # '"$MARK"
  echo '}'
  echo 'echo "${pass:-0} passed, ${fail:-0} failed"'
} > "$cs_offender_path"
chmod 755 "$cs_offender_path"
printf '#!/bin/sh\nexit 0\n' > "$cs_tree/$SCRIPTS_DIR/run-affordable.sh"
chmod 755 "$cs_tree/$SCRIPTS_DIR/run-affordable.sh"
cs_offender_line="$(grep -n "$MARK" "$cs_offender_path" | cut -d: -f1)"

if [[ -f "$GUARD_PATH" ]]; then
  cp "$GUARD_PATH" "$cs_tree/$TESTS_DIR/$GUARD_NAME"
  cp "$HERE/lib/"*.sh "$cs_tree/$TESTS_DIR/lib/"
  guard_out="$("$cs_tree/$TESTS_DIR/$GUARD_NAME" 2>&1)" && guard_code=0 || guard_code=$?
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over a unit suite that runs \"\$RUN_AFFORDABLE\" in a command substitution at line $cs_offender_line; it exited 0 and said: $(flat "$guard_out")")
  grep -qF -- "$CS_OFFENDER:$cs_offender_line" <<< "$guard_out" ||
    problems+=("no line of the guard's output names $CS_OFFENDER:$cs_offender_line; it said: $(flat "$guard_out")")
fi

report "$name"

problems=()
name="no-unit-subprocess.test.sh names a unit-tier suite that runs a script variable behind a NAME=value prefix, NAME=value \"\$VAR\" ..., as <suite>:<line>"

PFX_OFFENDER='runs-a-prefixed-variable.test.sh'
pfx_tree="$(scratch_dir)"
mkdir -p "$pfx_tree/$TESTS_DIR/unit" "$pfx_tree/$SCRIPTS_DIR" "$pfx_tree/$TESTS_DIR/lib"
pfx_offender_path="$pfx_tree/$TESTS_DIR/unit/$PFX_OFFENDER"
{
  echo '#!/usr/bin/env bash'
  echo '# Unit tests for a script — the line below runs it instead of sourcing it.'
  echo 'set -uo pipefail'
  echo 'HERE="$(cd "$(dirname "$0")" && pwd)"'
  echo 'RUN_AFFORDABLE="$HERE/../run-affordable.sh"'
  echo 'run_affordable() {'
  echo '  VERI_BUDGET=3 "$RUN_AFFORDABLE" "$@" > "$HERE/stdout" 2>&1  # '"$MARK"
  echo '}'
  echo 'echo "${pass:-0} passed, ${fail:-0} failed"'
} > "$pfx_offender_path"
chmod 755 "$pfx_offender_path"
printf '#!/bin/sh\nexit 0\n' > "$pfx_tree/$SCRIPTS_DIR/run-affordable.sh"
chmod 755 "$pfx_tree/$SCRIPTS_DIR/run-affordable.sh"
pfx_offender_line="$(grep -n "$MARK" "$pfx_offender_path" | cut -d: -f1)"

if [[ -f "$GUARD_PATH" ]]; then
  cp "$GUARD_PATH" "$pfx_tree/$TESTS_DIR/$GUARD_NAME"
  cp "$HERE/lib/"*.sh "$pfx_tree/$TESTS_DIR/lib/"
  guard_out="$("$pfx_tree/$TESTS_DIR/$GUARD_NAME" 2>&1)" && guard_code=0 || guard_code=$?
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over a unit suite that runs \"\$RUN_AFFORDABLE\" behind a NAME=value prefix at line $pfx_offender_line; it exited 0 and said: $(flat "$guard_out")")
  grep -qF -- "$PFX_OFFENDER:$pfx_offender_line" <<< "$guard_out" ||
    problems+=("no line of the guard's output names $PFX_OFFENDER:$pfx_offender_line; it said: $(flat "$guard_out")")
fi

report "$name"

finish

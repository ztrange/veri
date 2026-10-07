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

name="make test refuses before any suite runs when the bash on PATH is older than 5, and runs them when it is not"
problems=()
old_out="$(env VERI_BASH_MAJOR=3 make -C "$ROOT" test TESTS="$GREEN_FIXTURE" UNIT_TESTS= 2>&1)" && old_code=0 || old_code=$?
[[ "$old_code" != 0 ]] || problems+=("want a non-zero exit with VERI_BASH_MAJOR=3, got 0: $(flat "$old_out")")
[[ "$old_out" == *"$REQUIREMENT"* ]] || problems+=("want the output to say it $REQUIREMENT: $(flat "$old_out")")
[[ "$old_out" != *"== $(basename "$GREEN_FIXTURE")"* ]] || problems+=("a suite ran before the refusal: $(flat "$old_out")")
new_out="$(env VERI_BASH_MAJOR=5 make -C "$ROOT" test TESTS="$GREEN_FIXTURE" UNIT_TESTS= 2>&1)" && new_code=0 || new_code=$?
[[ "$new_code" == 0 && "$new_out" == *"all suites green"* ]] ||
  problems+=("want the suite run and green with VERI_BASH_MAJOR=5, got exit $new_code: $(flat "$new_out")")
report "$name"

name="the nested make test calls run only their fixture: the recipe output lists no suite from tests/unit/"
problems=()
for unit_suite in "$HERE"/unit/*.test.sh; do
  unit_name="$(basename "$unit_suite")"
  [[ "$old_out" != *"== $unit_name"* ]] || problems+=("bash 3 call ran unit suite $unit_name")
  [[ "$new_out" != *"== $unit_name"* ]] || problems+=("bash 5 call ran unit suite $unit_name")
done
report "$name"

name="run-conductor.sh refuses with exit 2 before launching anything when bash is older than 5"
problems=()
mkdir -p "$work/conductor"
rc_err="$( cd "$work/conductor" && env VERI_BASH_MAJOR=3 CLAUDE_BIN="$work/claude" LAUNCHED="$work/conductor/launched" \
    "$SCRIPTS/run-conductor.sh" 4242 2>&1 >/dev/null )" && rc_code=0 || rc_code=$?
[[ "$rc_code" == 2 ]] || problems+=("want exit 2, got $rc_code: $(flat "$rc_err")")
[[ "$rc_err" == *"$REQUIREMENT"* ]] || problems+=("want stderr to say it $REQUIREMENT: $(flat "$rc_err")")
[[ ! -e "$work/conductor/launched" ]] || problems+=("the conductor's binary was launched before the refusal")
report "$name"

name="run-conductor.sh refuses with exit 2 before launching anything, naming the Python 3.12 floor and the version found, when python3 is older than 3.12"
problems=()
mkdir -p "$work/py-conductor"
py_err="$( cd "$work/py-conductor" && env VERI_BASH_MAJOR=5 VERI_PYTHON_VERSION=3.11.9 CLAUDE_BIN="$work/claude" \
    LAUNCHED="$work/py-conductor/launched" "$SCRIPTS/run-conductor.sh" 4242 2>&1 >/dev/null )" && py_code=0 || py_code=$?
[[ "$py_code" == 2 ]] || problems+=("want exit 2, got $py_code: $(flat "$py_err")")
[[ "$py_err" == *"Python 3.12"* ]] || problems+=("want stderr to name the Python 3.12 floor: $(flat "$py_err")")
[[ "$py_err" == *"3.11.9"* ]] || problems+=("want stderr to name the version found, 3.11.9: $(flat "$py_err")")
[[ ! -e "$work/py-conductor/launched" ]] || problems+=("the conductor's binary was launched before the refusal")
report "$name"

name="run-conductor.sh's Python-floor refusal names \$VERI_VENV/bin to put first on PATH when the venv there meets the floor (#936)"
problems=()
mkdir -p "$work/venv-ok/bin" "$work/py-venv-conductor"
cat > "$work/venv-ok/bin/python3" <<'P'
#!/bin/sh
case "$*" in *platform*) echo 3.13.1 ;; esac
exit 0
P
chmod +x "$work/venv-ok/bin/python3"
pv_err="$( cd "$work/py-venv-conductor" && env VERI_BASH_MAJOR=5 VERI_PYTHON_VERSION=3.11.9 VERI_VENV="$work/venv-ok" \
    CLAUDE_BIN="$work/claude" LAUNCHED="$work/py-venv-conductor/launched" "$SCRIPTS/run-conductor.sh" 4242 2>&1 >/dev/null )" &&
  pv_code=0 || pv_code=$?
[[ "$pv_code" == 2 ]] || problems+=("want exit 2, got $pv_code: $(flat "$pv_err")")
[[ "$pv_err" == *"$work/venv-ok/bin"* && "$pv_err" == *PATH* ]] ||
  problems+=("want stderr to name $work/venv-ok/bin to put first on PATH: $(flat "$pv_err")")
report "$name"

name="run-conductor.sh's Python-floor refusal, with no venv at \$VERI_VENV, exits 2 with today's message and names no venv path (#936)"
problems=()
mkdir -p "$work/py-novenv-conductor"
pn_err="$( cd "$work/py-novenv-conductor" && env VERI_BASH_MAJOR=5 VERI_PYTHON_VERSION=3.11.9 VERI_VENV="$work/no-venv" \
    CLAUDE_BIN="$work/claude" LAUNCHED="$work/py-novenv-conductor/launched" "$SCRIPTS/run-conductor.sh" 4242 2>&1 >/dev/null )" &&
  pn_code=0 || pn_code=$?
[[ "$pn_code" == 2 ]] || problems+=("want exit 2, got $pn_code: $(flat "$pn_err")")
[[ "$pn_err" == "run-conductor: veri needs Python 3.12 or newer; the python3 on PATH is version 3.11.9." ]] ||
  problems+=("want stderr to be exactly today's one-line refusal: $(flat "$pn_err")")
[[ "$pn_err" != *"$work/no-venv"* ]] || problems+=("want stderr to name no venv path: $(flat "$pn_err")")
report "$name"

name="leaf-launchable.sh refuses with exit 2 when bash is older than 5, and still answers 0 for a launchable binary on bash 5"
problems=()
ll_err="$(env VERI_BASH_MAJOR=3 CLAUDE_BIN="$work/claude" LAUNCHED="$work/ll-launched" \
    "$SCRIPTS/leaf-launchable.sh" 2>&1 >/dev/null)" && ll_code=0 || ll_code=$?
[[ "$ll_code" == 2 ]] || problems+=("want exit 2 with VERI_BASH_MAJOR=3, got $ll_code: $(flat "$ll_err")")
[[ "$ll_err" == *"$REQUIREMENT"* ]] || problems+=("want stderr to say it $REQUIREMENT: $(flat "$ll_err")")
env VERI_BASH_MAJOR=5 CLAUDE_BIN="$work/claude" LAUNCHED="$work/ll-launched" \
  "$SCRIPTS/leaf-launchable.sh" >/dev/null 2>&1 && ll5=0 || ll5=$?
[[ "$ll5" == 0 ]] || problems+=("want exit 0 for a launchable binary with VERI_BASH_MAJOR=5, got $ll5")
report "$name"

name="leaf-launchable.sh refuses with exit 2, naming the Python 3.12 floor and the version found, when python3 is older than 3.12"
problems=()
llpy_err="$(env VERI_BASH_MAJOR=5 VERI_PYTHON_VERSION=3.11.9 CLAUDE_BIN="$work/claude" LAUNCHED="$work/llpy-launched" \
    "$SCRIPTS/leaf-launchable.sh" 2>&1 >/dev/null)" && llpy_code=0 || llpy_code=$?
[[ "$llpy_code" == 2 ]] || problems+=("want exit 2, got $llpy_code: $(flat "$llpy_err")")
[[ "$llpy_err" == *"Python 3.12"* ]] || problems+=("want stderr to name the Python 3.12 floor: $(flat "$llpy_err")")
[[ "$llpy_err" == *"3.11.9"* ]] || problems+=("want stderr to name the version found, 3.11.9: $(flat "$llpy_err")")
report "$name"

name="leaf-launchable.sh does not refuse on the Python floor when the python3 version cannot be read, and answers 0 for a launchable binary"
problems=()
llnv_err="$(env VERI_BASH_MAJOR=5 VERI_PYTHON_VERSION=unknown CLAUDE_BIN="$work/claude" LAUNCHED="$work/llnv-launched" \
    "$SCRIPTS/leaf-launchable.sh" 2>&1 >/dev/null)" && llnv_code=0 || llnv_code=$?
[[ "$llnv_code" == 0 ]] || problems+=("want exit 0 for an unreadable python3 version, got $llnv_code: $(flat "$llnv_err")")
[[ "$llnv_err" != *"Python 3.12"* ]] || problems+=("want no Python-floor refusal for an unreadable version: $(flat "$llnv_err")")
report "$name"

name="leaf-launchable.sh's Python-floor refusal names \$VERI_VENV/bin to put first on PATH when the venv there meets the floor (#936)"
problems=()
llv_err="$(env VERI_BASH_MAJOR=5 VERI_PYTHON_VERSION=3.11.9 VERI_VENV="$work/venv-ok" CLAUDE_BIN="$work/claude" \
    LAUNCHED="$work/llv-launched" "$SCRIPTS/leaf-launchable.sh" 2>&1 >/dev/null)" && llv_code=0 || llv_code=$?
[[ "$llv_code" == 2 ]] || problems+=("want exit 2, got $llv_code: $(flat "$llv_err")")
[[ "$llv_err" == *"$work/venv-ok/bin"* && "$llv_err" == *PATH* ]] ||
  problems+=("want stderr to name $work/venv-ok/bin to put first on PATH: $(flat "$llv_err")")
report "$name"

name="leaf-launchable.sh's Python-floor refusal, with no venv at \$VERI_VENV, exits 2 with today's message and names no venv path (#936)"
problems=()
lln_err="$(env VERI_BASH_MAJOR=5 VERI_PYTHON_VERSION=3.11.9 VERI_VENV="$work/no-venv" CLAUDE_BIN="$work/claude" \
    LAUNCHED="$work/lln-launched" "$SCRIPTS/leaf-launchable.sh" 2>&1 >/dev/null)" && lln_code=0 || lln_code=$?
[[ "$lln_code" == 2 ]] || problems+=("want exit 2, got $lln_code: $(flat "$lln_err")")
[[ "$lln_err" == "leaf-launchable: veri needs Python 3.12 or newer; the python3 on PATH is version 3.11.9." ]] ||
  problems+=("want stderr to be exactly today's one-line refusal: $(flat "$lln_err")")
[[ "$lln_err" != *"$work/no-venv"* ]] || problems+=("want stderr to name no venv path: $(flat "$lln_err")")
report "$name"

name="run-conductor.sh's and leaf-launchable.sh's Python-floor refusals, with a venv at \$VERI_VENV below the floor too, exit 2 with today's message and name no venv path (#936)"
problems=()
mkdir -p "$work/venv-old/bin" "$work/py-oldvenv-conductor"
cat > "$work/venv-old/bin/python3" <<'P'
#!/bin/sh
case "$*" in *version_info*) exit 1 ;; *platform*) echo 3.11.2 ;; esac
exit 0
P
chmod +x "$work/venv-old/bin/python3"
po_err="$( cd "$work/py-oldvenv-conductor" && env VERI_BASH_MAJOR=5 VERI_PYTHON_VERSION=3.11.9 VERI_VENV="$work/venv-old" \
    CLAUDE_BIN="$work/claude" LAUNCHED="$work/py-oldvenv-conductor/launched" "$SCRIPTS/run-conductor.sh" 4242 2>&1 >/dev/null )" &&
  po_code=0 || po_code=$?
[[ "$po_code" == 2 ]] || problems+=("run-conductor: want exit 2, got $po_code: $(flat "$po_err")")
[[ "$po_err" == "run-conductor: veri needs Python 3.12 or newer; the python3 on PATH is version 3.11.9." ]] ||
  problems+=("run-conductor: want stderr to be exactly today's one-line refusal: $(flat "$po_err")")
[[ "$po_err" != *"$work/venv-old"* ]] || problems+=("run-conductor: want stderr to name no venv path: $(flat "$po_err")")
llo_err="$(env VERI_BASH_MAJOR=5 VERI_PYTHON_VERSION=3.11.9 VERI_VENV="$work/venv-old" CLAUDE_BIN="$work/claude" \
    LAUNCHED="$work/llo-launched" "$SCRIPTS/leaf-launchable.sh" 2>&1 >/dev/null)" && llo_code=0 || llo_code=$?
[[ "$llo_code" == 2 ]] || problems+=("leaf-launchable: want exit 2, got $llo_code: $(flat "$llo_err")")
[[ "$llo_err" == "leaf-launchable: veri needs Python 3.12 or newer; the python3 on PATH is version 3.11.9." ]] ||
  problems+=("leaf-launchable: want stderr to be exactly today's one-line refusal: $(flat "$llo_err")")
[[ "$llo_err" != *"$work/venv-old"* ]] || problems+=("leaf-launchable: want stderr to name no venv path: $(flat "$llo_err")")
report "$name"

if [[ -x /bin/bash ]] && [[ "$(/bin/bash -c 'echo "${BASH_VERSINFO[0]}"')" -lt 5 ]]; then
  name="on a real bash older than 5 (/bin/bash), leaf-launchable.sh refuses with exit 2"
  problems=()
  mkdir -p "$work/old-bash"
  ln -sf /bin/bash "$work/old-bash/bash"
  real_err="$(env -u VERI_BASH_MAJOR PATH="$work/old-bash:$PATH" CLAUDE_BIN="$work/claude" LAUNCHED="$work/real-launched" \
      "$SCRIPTS/leaf-launchable.sh" 2>&1 >/dev/null)" && real_code=0 || real_code=$?
  [[ "$real_code" == 2 && "$real_err" == *"$REQUIREMENT"* ]] ||
    problems+=("want exit 2 and '$REQUIREMENT' from /bin/bash $(/bin/bash -c 'echo $BASH_VERSION'), got exit $real_code: $(flat "$real_err")")
  report "$name"
fi

finish

#!/usr/bin/env bash
# Unit tests for which python3 run-suite.sh runs a tests/py/test_*.py file with when VERI_VENV
# is unset.
#
# Contract under test:
#   With VERI_VENV unset, run-suite.sh runs the file with ~/.veri-tools/venv/bin/python3 when it
#   is present, and with the python3 on PATH when it is absent.
#
# Run: skills/tdd/scripts/tests/run-suite-venv.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
source "$HERE/lib/harness.sh"

RUNNER="$ROOT/skills/tdd/scripts/run-suite.sh"

flat() { printf '%s' "$1" | tr '\n' '/'; }

direct() {
  direct_out="$("$@" 2>&1)" && direct_code=0 || direct_code=$?
}

python3_stub() {
  printf '#!/bin/sh\ncase "$1" in */veri/*.py) exec "%s" "$@" ;; esac\n%s\n' "$(command -v python3)" "$2" > "$1/python3"
  chmod +x "$1/python3"
}

py_tree="$(scratch_dir)"
mkdir -p "$py_tree/tests/py"
printf 'def test_breaks():\n    assert 1 + 1 == 3\n' > "$py_tree/tests/py/test_red.py"

path_bin="$(scratch_dir)"
python3_stub "$path_bin" 'echo "path python3 $*"
exit 0'

name="run-suite.sh with VERI_VENV unset runs a pytest file with ~/.veri-tools/venv's python3, and with the python3 on PATH when that venv has none"
problems=()

home="$(scratch_dir)"
mkdir -p "$home/.veri-tools/venv/bin"
python3_stub "$home/.veri-tools/venv/bin" 'echo "home venv python3 $*"
exit 0'
direct env -u VERI_VENV HOME="$home" PATH="$path_bin:$PATH" "$RUNNER" "$py_tree/tests/py/test_red.py"
[[ "$direct_code" == 0 && "$direct_out" == "home venv python3 -m pytest $py_tree/tests/py/test_red.py" ]] ||
  problems+=("want ~/.veri-tools/venv/bin/python3 to run the file when VERI_VENV is unset (exit 0, 'home venv python3 -m pytest …'); got $direct_code, and it said: $(flat "$direct_out")")

direct env -u VERI_VENV HOME="$(scratch_dir)" PATH="$path_bin:$PATH" "$RUNNER" "$py_tree/tests/py/test_red.py"
[[ "$direct_code" == 0 && "$direct_out" == "path python3 -m pytest $py_tree/tests/py/test_red.py" ]] ||
  problems+=("want the python3 on PATH when VERI_VENV is unset and ~/.veri-tools/venv has no bin/python3 (exit 0, 'path python3 -m pytest …'); got $direct_code, and it said: $(flat "$direct_out")")

report "$name"

finish

#!/bin/sh
# lib/shim-python.sh — sourced by a /bin/sh shim, not run: sets `py` to the interpreter its module runs on.
#
# py — $VERI_VENV/bin/python3 (default ~/.veri-tools/venv/bin/python3) when it is executable and Python 3.12
#      or newer, else the python3 on PATH when that is 3.12 or newer, else the shim exits 2 naming each
#      interpreter it tried, its source and its version.
shim_meets_floor() {
  shim_version="$("$1" --version 2>&1)"
  shim_version="${shim_version#Python }"
  shim_minor="${shim_version#*.}"
  shim_minor="${shim_minor%%.*}"
  [ "${shim_version%%.*}" -gt 3 ] 2>/dev/null || { [ "${shim_version%%.*}" -eq 3 ] 2>/dev/null && [ "$shim_minor" -ge 12 ] 2>/dev/null; }
}
shim_venv_py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
shim_venv_version=
py=
if [ -x "$shim_venv_py" ]; then
  if shim_meets_floor "$shim_venv_py"; then
    py="$shim_venv_py"
  else
    shim_venv_version="$shim_version"
  fi
fi
if [ -z "$py" ] && command -v python3 >/dev/null 2>&1; then
  if shim_meets_floor python3; then
    py=python3
  else
    shim_path_version="$shim_version"
  fi
fi
if [ -z "$py" ]; then
  [ -z "$shim_venv_version" ] || echo "$0: venv python3 $shim_venv_py is Python $shim_venv_version, below 3.12" >&2
  [ -z "$shim_path_version" ] || echo "$0: PATH python3 is Python $shim_path_version, below 3.12" >&2
  exit 2
fi
unset shim_version shim_minor shim_venv_py shim_venv_version shim_path_version
unset -f shim_meets_floor

#!/bin/sh
# lib/shim-python.sh — sourced by a /bin/sh shim, not run: sets `py` to the interpreter its module runs on.
#
# py — $VERI_VENV/bin/python3 (default ~/.veri-tools/venv/bin/python3) when it is executable and Python
#      $VENV_FLOOR (read from lib/venv-python.sh) or newer, else the python3 on PATH when that meets the floor,
#      else the shim exits 2 with one stderr line per interpreter: its source and its version, "unknown" when it
#      reports none, or that none was found. An unreadable floor exits 2 naming lib/venv-python.sh.
case "$0" in
  */*) shim_lib="${0%/*}/lib" ;;
  *) shim_lib=./lib ;;
esac
shim_floor=
while IFS= read -r shim_line; do
  case "$shim_line" in VENV_FLOOR=*) shim_floor="${shim_line#VENV_FLOOR=}" ;; esac
done < "$shim_lib/venv-python.sh"
case "$shim_floor" in
  *[!0-9.]*) shim_floor= ;;
  [0-9]*.[0-9]*) ;;
  *) shim_floor= ;;
esac
[ -n "$shim_floor" ] || { echo "$0: cannot read VENV_FLOOR from $shim_lib/venv-python.sh." >&2; exit 2; }
shim_meets_floor() {
  shim_version="$("$1" -c 'import platform; print(platform.python_version())' 2>/dev/null || "$1" --version 2>&1)"
  shim_version="${shim_version#Python }"
  shim_minor="${shim_version#*.}"
  shim_minor="${shim_minor%%.*}"
  [ "${shim_version%%.*}" -gt "${shim_floor%%.*}" ] 2>/dev/null ||
    { [ "${shim_version%%.*}" -eq "${shim_floor%%.*}" ] 2>/dev/null && [ "$shim_minor" -ge "${shim_floor#*.}" ] 2>/dev/null; }
}
shim_venv_py=${VERI_VENV:-~/.veri-tools/venv}/bin/python3
shim_venv_said="no venv python3 at $shim_venv_py"
shim_path_said="no python3 on PATH"
py=
if [ -x "$shim_venv_py" ]; then
  if shim_meets_floor "$shim_venv_py"; then
    py="$shim_venv_py"
  else
    shim_venv_said="the venv python3 at $shim_venv_py is version ${shim_version:-unknown}"
  fi
fi
if [ -z "$py" ] && command -v python3 >/dev/null 2>&1; then
  if shim_meets_floor python3; then
    py=python3
  else
    shim_path_said="the python3 on PATH is version ${shim_version:-unknown}"
  fi
fi
if [ -z "$py" ]; then
  echo "$0: veri needs Python $shim_floor or newer; $shim_venv_said." >&2
  echo "$0: veri needs Python $shim_floor or newer; $shim_path_said." >&2
  exit 2
fi
unset shim_lib shim_line shim_floor shim_version shim_minor shim_venv_py shim_venv_said shim_path_said
unset -f shim_meets_floor
unset PYTHONPYCACHEPREFIX
export PYTHONDONTWRITEBYTECODE=1

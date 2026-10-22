# lib/shim-python.sh — sourced by a /bin/sh shim, not run: sets `py` to the interpreter its module runs on.
#
# py — $VERI_VENV/bin/python3 (default ~/.veri-tools/venv/bin/python3) when it is executable and Python 3.12
#      or newer, else the python3 on PATH.
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
if [ -x "$py" ]; then
  shim_version="$("$py" --version 2>&1)"
  shim_version="${shim_version#Python }"
  shim_minor="${shim_version#*.}"
  shim_minor="${shim_minor%%.*}"
  if [ "${shim_version%%.*}" -lt 3 ] || { [ "${shim_version%%.*}" -eq 3 ] && [ "$shim_minor" -lt 12 ]; }; then
    py=python3
  fi
else
  py=python3
fi
unset shim_version shim_minor

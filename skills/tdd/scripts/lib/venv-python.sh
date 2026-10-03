#!/usr/bin/env bash
# lib/venv-python.sh — sourced, not run: defines `venv_dir` and `venv_python`.
#
# venv_dir    — echo the environment the pytest leg runs in: $VERI_VENV, else ~/.veri-tools/venv.
# venv_python — echo that environment's bin/python3 when it is executable, else the python3 on PATH.
venv_dir() {
  printf '%s\n' "${VERI_VENV:-$HOME/.veri-tools/venv}"
}

venv_python() {
  local py
  py="$(venv_dir)/bin/python3"
  [[ -x "$py" ]] || py="$(command -v python3)"
  printf '%s\n' "$py"
}

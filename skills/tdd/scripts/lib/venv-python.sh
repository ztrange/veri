#!/usr/bin/env bash
# lib/venv-python.sh — sourced, not run: defines `venv_dir` and `venv_python`.
#
# venv_dir    — echo the environment the pytest leg runs in: $VERI_VENV, else ~/.veri-tools/venv.
# venv_python — echo that environment's bin/python3 when it is executable, else the python3 on PATH.
# venv_meets_floor — return 0 when the interpreter $1 runs Python 3.12 or newer.
# venv_builder — echo the first of python3, python3.13, python3.12 on PATH that is Python 3.12 or newer;
#                with none, name the floor on stderr and return 2.
# venv_usable  — return 0 when the environment at $1 runs Python 3.12 or newer; else name its path,
#                its version and the floor on stderr and return 2.
venv_dir() {
  printf '%s\n' "${VERI_VENV:-$HOME/.veri-tools/venv}"
}

venv_python() {
  local py
  py="$(venv_dir)/bin/python3"
  [[ -x "$py" ]] || py="$(command -v python3)"
  printf '%s\n' "$py"
}

venv_meets_floor() {
  "$1" -c 'import sys; sys.exit(sys.version_info < (3, 12))' 2> /dev/null
}

venv_builder() {
  local candidates=(python3 python3.13 python3.12) candidate names
  for candidate in "${candidates[@]}"; do
    if venv_meets_floor "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  names="$(printf '%s, ' "${candidates[@]}")"
  printf 'veri needs Python 3.12 or newer to build its environment; none of %s on PATH is.\n' "${names%, }" >&2
  return 2
}

venv_usable() {
  local py="$1/bin/python3" version
  venv_meets_floor "$py" && return 0
  version="$("$py" -c 'import platform; print(platform.python_version())' 2> /dev/null)"
  printf 'veri needs Python 3.12 or newer; the environment at %s runs Python %s. Remove it and run make install-dev again.\n' "$1" "${version:-unknown}" >&2
  return 2
}

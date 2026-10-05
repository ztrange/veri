#!/usr/bin/env bash
# lib/venv-python.sh — sourced, not run: defines `venv_dir` and `venv_python`.
#
# VENV_FLOOR  — the oldest Python veri runs on, as major.minor.
# venv_dir    — echo the environment the pytest leg runs in: $VERI_VENV, else ~/.veri-tools/venv.
# venv_python — echo that environment's bin/python3 when it is executable, else the python3 on PATH.
# venv_meets_floor — return 0 when the interpreter $1 runs Python $VENV_FLOOR or newer.
# venv_builder — echo the first of python3, then python3.13 down to python$VENV_FLOOR, on PATH that is
#                Python $VENV_FLOOR or newer; with none, name the floor on stderr and return 2.
# venv_usable  — return 0 when the environment at $1 runs Python $VENV_FLOOR or newer; else name its path,
#                its version and the floor on stderr and return 2.
VENV_FLOOR=3.12

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
  "$1" -c 'import sys; sys.exit(sys.version_info < ('"${VENV_FLOOR%%.*}, ${VENV_FLOOR#*.}"'))' 2> /dev/null
}

venv_builder() {
  local candidates=(python3) candidate names minor
  for ((minor = 13; minor >= ${VENV_FLOOR#*.}; minor--)); do
    candidates+=("python3.$minor")
  done
  for candidate in "${candidates[@]}"; do
    if venv_meets_floor "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  names="$(printf '%s, ' "${candidates[@]}")"
  printf 'veri needs Python %s or newer to build its environment; none of %s on PATH is.\n' "$VENV_FLOOR" "${names%, }" >&2
  return 2
}

venv_usable() {
  local py="$1/bin/python3" version
  venv_meets_floor "$py" && return 0
  version="$("$py" -c 'import platform; print(platform.python_version())' 2> /dev/null)"
  printf 'veri needs Python %s or newer; the environment at %s runs Python %s. Remove it and run make install-dev again.\n' "$VENV_FLOOR" "$1" "${version:-unknown}" >&2
  return 2
}

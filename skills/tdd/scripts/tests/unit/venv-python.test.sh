#!/usr/bin/env bash
# Tests for scripts/lib/venv-python.sh — sourced, defines `venv_dir` (the environment the
# pytest leg runs in: $VERI_VENV, else ~/.veri-tools/venv) and `venv_python` (that
# directory's bin/python3 when it is executable, else the python3 on PATH).
# Fast tier: no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/venv-python.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/../lib/harness.sh"
source "$HERE/../../lib/venv-python.sh"

work="$(scratch_dir)"
mkdir -p "$work/home" "$work/path" "$work/venv/bin" "$work/home/.veri-tools/venv/bin"
printf '#!/bin/sh\n' > "$work/path/python3"
printf '#!/bin/sh\n' > "$work/venv/bin/python3"
printf '#!/bin/sh\n' > "$work/home/.veri-tools/venv/bin/python3"
chmod +x "$work/path/python3" "$work/venv/bin/python3" "$work/home/.veri-tools/venv/bin/python3"

probe() {
  local label="$1" want_dir="$2" want_py="$3" got_dir got_py
  got_dir="$(venv_dir)"
  got_py="$(venv_python)"
  [[ "$got_dir" == "$want_dir" ]] || problems+=("$label: venv_dir want '$want_dir', got '$got_dir'")
  [[ "$got_py" == "$want_py" ]] || problems+=("$label: venv_python want '$want_py', got '$got_py'")
}

(
  export HOME="$work/home" PATH="$work/path"
  VERI_VENV="$work/venv" probe "VERI_VENV set, its python3 executable" \
    "$work/venv" "$work/venv/bin/python3"
  VERI_VENV="$work/absent" probe "VERI_VENV set, no python3 under it" \
    "$work/absent" "$work/path/python3"
  /bin/chmod -x "$work/venv/bin/python3"
  VERI_VENV="$work/venv" probe "VERI_VENV set, its python3 not executable" \
    "$work/venv" "$work/path/python3"
  unset VERI_VENV
  probe "VERI_VENV unset" \
    "$work/home/.veri-tools/venv" "$work/home/.veri-tools/venv/bin/python3"
  printf '%s\n' ${problems+"${problems[@]}"}
) > "$work/problems"
while IFS= read -r line; do
  [[ -n "$line" ]] && problems+=("$line")
done < "$work/problems"
report "venv_dir is \$VERI_VENV or ~/.veri-tools/venv; venv_python is its executable bin/python3, else PATH's python3"

finish

#!/usr/bin/env bash
# Audits that no suite copies a script into a scratch tree without the lib it cannot start
# without. A `cp` line under tests/ or tests/unit/ that names a script under scripts/ which
# sources lib/exit-contract.sh — by a literal path or through the suite's own variable
# assignments — is named, unless the suite also puts lib/exit-contract.sh in the tree: by
# naming it, or by copying a directory whole with `cp -R`.
# Admitted to the fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/scratch-copy-libs.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TESTS="$(cd "$HERE/.." && pwd)"
SCRIPTS="$(cd "$TESTS/.." && pwd)"
export LC_ALL=C
source "$TESTS/lib/harness.sh"

needs_contract() {
  [[ -f "$SCRIPTS/$1" ]] && grep -E '^(source|\.)[[:space:]].*lib/exit-contract\.sh' "$SCRIPTS/$1" > /dev/null
}

expand() {
  local text="$1" pass var
  for pass in 1 2 3; do
    for var in "${!vars[@]}"; do
      text="${text//\$\{$var\}/${vars[$var]}}"
      text="${text//\$$var/${vars[$var]}}"
    done
  done
  printf '%s' "$text"
}

name="a suite that copies a script sourcing lib/exit-contract.sh into a scratch tree puts that lib there too"
problems=""
for suite in "$TESTS"/*.test.sh "$TESTS"/unit/*.test.sh; do
  grep -F 'exit-contract.sh' "$suite" > /dev/null && continue
  grep -E '(^|[[:space:]])cp[[:space:]]+-[A-Za-z]*R' "$suite" > /dev/null && continue
  declare -A vars=()
  while IFS= read -r line; do
    [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)=[\'\"]?([^\'\"]*)[\'\"]?[[:space:]]*$ ]] \
      && vars["${BASH_REMATCH[1]}"]="${BASH_REMATCH[2]}"
  done < "$suite"
  n=0
  while IFS= read -r line; do
    n=$((n + 1))
    [[ "$line" =~ (^|[[:space:]])cp[[:space:]] ]] || continue
    rest="$(expand "$line")"
    while [[ "$rest" =~ (^|[/\"\' ])([A-Za-z0-9_.-]+\.sh)(.*)$ ]]; do
      rest="${BASH_REMATCH[3]}"
      hit="    ${suite#"$TESTS"/}:$n copies ${BASH_REMATCH[2]} without lib/exit-contract.sh"$'\n'
      [[ "$problems" == *"$hit"* ]] && continue
      needs_contract "${BASH_REMATCH[2]}" && problems+="$hit"
    done
  done < "$suite"
  unset vars
done
if [[ -z "$problems" ]]; then
  ok
else
  no "$name"
  printf '%s' "$problems"
fi

finish

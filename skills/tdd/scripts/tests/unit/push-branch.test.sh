#!/usr/bin/env bash
# Unit tests for scripts/push-branch.sh — the script sourced, never executed, with every
# command it shells out to mocked as a same-named shell function.
#
# Admitted to the fast tier (#336) by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/push-branch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PUSH="$HERE/../../push-branch.sh"
pass=0 fail=0
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

# 1. sourcing the script runs nothing: no git call, no exit out of the sourcing shell, and a
#    `main` function left defined for a caller to run
name="sourcing push-branch.sh runs nothing and defines main"
calls="$scratch/calls"
: > "$calls"
got="$(
  git() { echo "git $*" >> "$calls"; return 0; }
  sleep() { echo "sleep $*" >> "$calls"; return 0; }
  source "$PUSH"
  echo "source returned"
  declare -F main >/dev/null && echo "main defined"
)"
want="source returned
main defined"
if [[ -s "$calls" ]]; then
  fail=$((fail + 1)); echo "FAIL - $name (sourcing ran commands, want none):"; cat "$calls"
elif [[ "$got" != "$want" ]]; then
  fail=$((fail + 1)); echo "FAIL - $name"; diff <(echo "$want") <(echo "$got")
else
  pass=$((pass + 1))
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

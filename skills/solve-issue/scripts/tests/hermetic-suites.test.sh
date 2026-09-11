#!/usr/bin/env bash
# Unit tests for the suites themselves — a suite that asserts a script's DEFAULT must not
# inherit an override for that default from the shell that ran it.
# Zero-dependency plain-shell asserts, same idiom as refactor-budget.test.sh.
#
# Why this exists (issue #87): an unattended run exports VERI_STUCK_RETRIES for its outer
# supervisor, the inner `make test` inherits it, and veri's own preflight then reads a red
# baseline on veri's own repo and refuses to start. A suite's answer must be a fact about
# the script, not about the caller's environment.
#
# Contract under test:
#   VERI_STUCK_RETRIES=0 supervise-retry.test.sh → exit 0, "1 passed, 0 failed",
#   exactly as with the variable unset.
#
# Run: scripts/tests/hermetic-suites.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# 1. The contract above, probed by running the whole suite as a child process: the leak is
#    in how supervise-retry.test.sh spawns the supervisor, so only a real run of it walks
#    that path — there is nothing to assert in-process.
name="supervise-retry.test.sh: ambient VERI_STUCK_RETRIES=0 still gives 1 passed, 0 failed"
problems=()
out="$(VERI_STUCK_RETRIES=0 "$HERE/supervise-retry.test.sh" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0, got $code")
[[ "$out" == *'1 passed, 0 failed'* ]] ||
  problems+=("want '1 passed, 0 failed' on stdout, got: $(printf '%q' "$out")")
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

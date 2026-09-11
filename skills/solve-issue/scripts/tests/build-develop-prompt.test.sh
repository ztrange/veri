#!/usr/bin/env bash
# Tests for scripts/build-develop-prompt.sh — see that script's header for why the
# developer's prompt is a versioned template rather than prose improvised each cycle.
# These tests hold it to the half of that bargain a test can observe: what the assembled
# prompt must carry.
#
# Contract under test, red phase:
#   build-develop-prompt.sh red <spec-file> <step-text> <test-cmd>
#   exits 0 and prints a prompt carrying the spec, the step criterion and the test command
#   verbatim, plus the `AGAINST_UNMODIFIED` report line — the protocol token the conductor
#   greps for to route a passing red test to verify-pin (SKILL.md, Red step).
#
# Run: scripts/tests/build-develop-prompt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUILD="$HERE/../build-develop-prompt.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# Distinctive strings throughout, so no assertion below can match on boilerplate prose
# that the template happens to contain. The spec also carries &, \, / and {} — the
# characters a naive sed substitution would mangle.
cat > "$work/spec.md" <<'SPEC'
zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux" — see {ref}\n done.
SPEC
step_text='QWIXTLE: a seed ending in a newline gains the block and reports added'
test_cmd='make test ZORBLAT=1 -- --only "frob & nitz/quux"'

# 1. the red prompt carries its three inputs verbatim and the AGAINST_UNMODIFIED line
red="$("$BUILD" red "$work/spec.md" "$step_text" "$test_cmd" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$red" == *'zorblat("Frob & Nitz/Quux")'* ]] \
  && [[ "$red" == *"$step_text"* ]] \
  && [[ "$red" == *"$test_cmd"* ]] \
  && [[ "$red" == *'AGAINST_UNMODIFIED'* ]] \
  && ok || no "develop-red carries spec + step + test command verbatim and the AGAINST_UNMODIFIED report line (exit $code)"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

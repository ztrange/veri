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
# Contract under test, green phase:
#   build-develop-prompt.sh green <spec-file> <step-text> <test-cmd> <test-path> <target>
#   exits 0 and prints a prompt naming the test the implementation must satisfy — its path
#   and its case name — and forbidding any edit to it, the rule that keeps "make it green"
#   from degenerating into "weaken the test".
#
# Contract under test, refactor phase:
#   build-develop-prompt.sh refactor <spec-file> <step-text> <test-cmd> <touched-files>
#   exits 0 and prints a prompt naming the files this cycle touched — the bounds of the
#   tidy-up — carrying the rule that bounds it further (no generality no test demands), and
#   requiring the `RESULT:` / `FLAGS:` footer the conductor branches on.
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

# 2. the green prompt names the test it must satisfy — path and case name — and forbids
#    editing it
test_path='tests/zorblat/test_frob & nitz.sh'
target='qwixtle seeds a newline-terminated block'
green="$("$BUILD" green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$green" == *"$test_path"* ]] \
  && [[ "$green" == *"$target"* ]] \
  && grep -qiE "(do not|don't|never) (modify|change|edit|touch|weaken).{0,40}test|test.{0,40}(must not|may not) be (modified|changed|edited|touched)" <<<"$green" \
  && ok || no "develop-green names the test path + target test and forbids modifying the test (exit $code)"

# 3. the refactor prompt names the files the cycle touched, carries the rule that bounds
#    the tidy-up (no generality no test demands) and requires the RESULT:/FLAGS: footer
touched='scripts/zorblat.sh, tests/zorblat/test_frob & nitz.sh'
refactor="$("$BUILD" refactor "$work/spec.md" "$step_text" "$test_cmd" "$touched" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$refactor" == *"$touched"* ]] \
  && grep -qiE '(no|not|never|without)[^.]{0,80}(generality|generali[sz]ation|abstraction)' <<<"$refactor" \
  && grep -q 'RESULT:' <<<"$refactor" \
  && grep -q 'FLAGS:' <<<"$refactor" \
  && ok || no "develop-refactor carries the touched-files list + the no-untested-generality rule and the RESULT:/FLAGS: footer (exit $code)"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

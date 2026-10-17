#!/usr/bin/env bash
# Tests for scripts/build-develop-prompt.sh — what the assembled developer prompt carries.
#
# Contract under test, red phase:
#   build-develop-prompt.sh red <spec-file> <step-text> <test-cmd>
#   exits 0 and prints a prompt carrying the spec, the step criterion and the test command
#   verbatim, the `AGAINST_UNMODIFIED` report line, the `UNTESTABLE` outcome and the rules a
#   valid test holds to — behaviour over mechanism, lightweight, self-contained.
#
# Contract under test, green phase:
#   build-develop-prompt.sh green <spec-file> <step-text> <test-cmd> <test-path> <target> <fast-cmd>
#   exits 0 and prints a prompt naming the test's path and case name, and forbidding any edit
#   to it.
#
# Contract under test, refactor phase:
#   build-develop-prompt.sh refactor <spec-file> <step-text> <test-cmd> <touched-files>
#   exits 0 and prints a prompt naming the files this cycle touched, the rule against
#   generality no test demands, and the `RESULT:` / `CANDIDATES:` / `NEW_STEP:` footer.
#
# Contract under test, the reader of that footer:
#   SKILL.md's `#### Refactor loop` section tells the two stop conditions apart and, when the
#   budget ended the loop, says how many candidates were left and lists them.
#
# Contract under test, revise phase:
#   build-develop-prompt.sh revise <phase> <spec-file> <step-text> <test-cmd> <reason-file>
#   exits 0 and prints a prompt carrying the verifier's rejection reason verbatim, and
#   offering `IMPOSSIBLE`.
#
# Contract under test, refusals:
#   an unknown phase, a missing positional, or a missing template, spec or reason file, exits
#   2 with a diagnostic and prints no prompt.
#
# Run: scripts/tests/build-develop-prompt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUILD="$HERE/../build-develop-prompt.sh"
source "$HERE/lib/harness.sh"
source "$HERE/lib/probe-order.sh"

work="$(scratch_dir)"

cat > "$work/spec.md" <<'SPEC'
zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux" — see {ref}\n done.
SPEC
step_text='QWIXTLE: a seed ending in a newline gains the block and reports added'
test_cmd='make test ZORBLAT=1 -- --only "frob & nitz/quux"'

test_path='tests/zorblat/test_frob & nitz.sh'
target='qwixtle seeds a newline-terminated block'

touched='scripts/zorblat.sh, tests/zorblat/test_frob & nitz.sh'

name="#974 the diff prompt tells the leaf to run the given fast command through timed-test-run.sh fast and then the affected suites, and to finish only with both green"
dd_fast='make unit ZORBLAT=fast -- --only "frob & nitz/quux"'

finish

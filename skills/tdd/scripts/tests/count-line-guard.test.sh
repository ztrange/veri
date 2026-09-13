#!/usr/bin/env bash
# Unit tests for the `test` recipe in this repository's Makefile — the runner whose green
# is what preflight's baseline, every Green leaf, both blind verifiers and CI's gates job
# all read. Like hermetic-suites.test.sh and workflow-timeouts.test.sh this suite has no
# script as its subject: its subject is what the runner does with a suite that stops
# asserting. Zero-dependency plain-shell asserts, same idiom as refactor-budget.test.sh.
#
# Why this exists (issue #157): under `set -uo pipefail`, which every suite here declares,
# an operand of `[[ … -le … ]]` that is a word rather than a number is read as a variable
# name; an unset name kills the script, and a script killed that way exits with the status
# of the command before it — routinely 0. The recipe runs each suite as `"$t" || fail=1`
# and trusts that code alone, so it prints `all suites green` over a suite that asserted
# nothing after the point it died. build-guards.test.sh ran 37 of its 54 cases that way
# until commit c4a6bdb, and no output said so.
#
# Contract under test:
#   `make test` over a suite that dies from an unbound variable inside a numeric
#   comparison after its first case and exits 0 comes back non-zero, and says which suite
#   never reached its count line.
#
# The suite it is handed is fixtures/silent-death/dies-silently.test.sh, which is under
# the fixtures directory rather than beside the real suites so that `make test`'s own glob
# never picks it up: only this file runs it, and only through the runner. Nothing on that
# path says "count line" on purpose — the last probe below asks whether a line of output
# names the suite AND says it never reached its count line, and a fixture path carrying
# those words would answer that probe with its own name.
#
# Run: skills/tdd/scripts/tests/count-line-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The fixture twice, and neither name substitutes for the other: repo-relative is what the
# recipe is handed and what it prints, absolute is what running the fixture directly needs,
# and the basename is what a failure line naming the suite would carry.
FIXTURE='skills/tdd/scripts/tests/fixtures/silent-death/dies-silently.test.sh'
FIXTURE_PATH="$ROOT/$FIXTURE"
FIXTURE_NAME="$(basename "$FIXTURE")"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the contract broke rather than just that the case did.
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

# flat <text> — one line of it, for a failure message: newlines become slashes so a run's
# output quoted inside an indented problem line stays one line.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# probe_fixture_dies_quietly — the premise the case rests on, asserted rather than assumed:
# the fixture really does die after its first case and really does come back 0. A fixture
# that had stopped doing either would leave the probes below passing against a runner that
# reads nothing but the exit code, and the case would report green over the hole it exists
# to pin.
probe_fixture_dies_quietly() {
  local out code
  out="$("$FIXTURE_PATH" 2>&1)" && code=0 || code=$?
  [[ "$code" == 0 ]] ||
    problems+=("the fixture no longer exits 0 when it dies; got $code, so nothing here pins a runner that trusts the exit code")
  grep -q 'unbound variable' <<< "$out" ||
    problems+=("the fixture no longer dies from an unbound variable; its output was: $(flat "$out")")
  ! grep -Eq '[0-9]+ passed, [0-9]+ failed' <<< "$out" ||
    problems+=("the fixture reached its count line, so it did not die: $(flat "$out")")
}

# probe_make_fails — the criterion itself. `make test TESTS=<fixture>` points the recipe at
# that one suite, so this runs the real runner over the real shape rather than a copy of
# either, and asks for the answer the runner gives a human and a merge: a non-zero exit.
probe_make_fails() {
  make_out="$(make -C "$ROOT" test TESTS="$FIXTURE" 2>&1)" && make_code=0 || make_code=$?
  [[ "$make_code" != 0 ]] ||
    problems+=("want 'make test' to fail over a suite that died; it exited 0 and said: $(flat "$make_out")")
}

# probe_make_names_the_suite — the other half of the criterion, and the reason it is not
# asked as "the output mentions the fixture": the recipe already prints `== <suite>` before
# running each one, and bash's own death message carries the fixture's path too, so both
# are there whatever the runner concludes. What has to name the suite is the report of the
# failure — a line that both names it and says what was wrong with it.
probe_make_names_the_suite() {
  local named
  named="$(grep -F "$FIXTURE_NAME" <<< "$make_out")"
  grep -Eqi 'count[ -]line' <<< "$named" ||
    problems+=("no line of 'make test' output both names $FIXTURE_NAME and says it never reached its count line; the lines naming it were: $(flat "$named")")
}

# 1. One criterion, one case: a suite that dies silently is refused, and the refusal says
#    which suite. Three probes — the premise, the exit code, the report — each arguing for
#    itself above. probe_make_fails runs the recipe and leaves its output in `make_out` for
#    probe_make_names_the_suite, so the two read one run rather than paying for two.
name="make test over a suite that dies from an unbound variable after its first case and exits 0 fails and names it"
problems=()
make_out="" make_code=0

probe_fixture_dies_quietly
probe_make_fails
probe_make_names_the_suite

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

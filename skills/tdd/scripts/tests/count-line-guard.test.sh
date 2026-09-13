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

# The two suites that run to the end, one with each answer: fixtures/live-suites holds the
# shapes the runner must go on treating exactly as it did before #157, and case 2 below
# says why each of them is a shape a wrong runner could get wrong. Repo-relative for the
# same reason as above — it is what the recipe is handed — with the absolute path beside it
# for running the fixture on its own.
GREEN_FIXTURE='skills/tdd/scripts/tests/fixtures/live-suites/ends-green.test.sh'
GREEN_FIXTURE_PATH="$ROOT/$GREEN_FIXTURE"
RED_FIXTURE='skills/tdd/scripts/tests/fixtures/live-suites/ends-red.test.sh'
RED_FIXTURE_PATH="$ROOT/$RED_FIXTURE"

# The runner itself, and the directory its glob looks in. Case 3 needs both by name because
# it stands the runner up somewhere else: the only way to watch what the recipe does with a
# suite that was not there before is to add one, and adding one here would hand `make test` a
# suite whose first act is to run `make test`.
MAKEFILE="$ROOT/Makefile"
TESTS_DIR='skills/tdd/scripts/tests'
ADDED_NAME='newly-added.test.sh'

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
  local make_code
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
#    probe_make_names_the_suite, so the two read one run rather than paying for two. That
#    one variable is the whole of what they share: the run's exit status is local to the
#    probe that asks about it.
name="make test over a suite that dies from an unbound variable after its first case and exits 0 fails and names it"
problems=()
make_out=""

probe_fixture_dies_quietly
probe_make_fails
probe_make_names_the_suite

report "$name"

# probe_live_fixtures_are_what_they_claim — the premises of case 2, asserted rather than
# assumed exactly as probe_fixture_dies_quietly asserts case 1's: the green fixture really
# does end in a count line reporting nothing failed and really does exit 0, and the red one
# really does reach its count line and really does exit non-zero. A fixture that had drifted
# off either shape would leave the two probes after it agreeing with a runner that had
# stopped telling the shapes apart.
probe_live_fixtures_are_what_they_claim() {
  local out code
  out="$("$GREEN_FIXTURE_PATH" 2>&1)" && code=0 || code=$?
  [[ "$code" == 0 ]] ||
    problems+=("the green fixture no longer exits 0; got $code, so nothing below pins the passing half")
  [[ "$(tail -n 1 <<< "$out")" =~ ^[0-9]+' passed, 0 failed'$ ]] ||
    problems+=("the green fixture no longer ends in a count line reporting nothing failed: $(flat "$out")")

  out="$("$RED_FIXTURE_PATH" 2>&1)" && code=0 || code=$?
  [[ "$code" != 0 ]] ||
    problems+=("the red fixture no longer exits non-zero, so nothing below pins a runner that reads the count line instead of the exit code")
  [[ "$(tail -n 1 <<< "$out")" =~ ^[0-9]+' passed, '[0-9]+' failed'$ ]] ||
    problems+=("the red fixture no longer reaches its count line, so it fails the way case 1's fixture does: $(flat "$out")")
}

# probe_make_passes_the_green_suite — the half that keeps the check from being satisfied by
# a runner that refuses everything. `make test TESTS=<fixture>` points the recipe at that
# one suite, as case 1 does, and asks for the answer a green suite has always got.
probe_make_passes_the_green_suite() {
  local out code
  out="$(make -C "$ROOT" test TESTS="$GREEN_FIXTURE" 2>&1)" && code=0 || code=$?
  [[ "$code" == 0 ]] ||
    problems+=("want 'make test' to pass a suite that ends in its count line with nothing failed; it exited $code and said: $(flat "$out")")
}

# probe_make_fails_the_red_suite — the half that keeps the count line from displacing the
# exit code rather than joining it. This fixture has the line the check asks for, so a
# runner that had come to read only that line calls it green, and an ordinary test failure
# — the most common red there is — stops being reported at all.
probe_make_fails_the_red_suite() {
  local out code
  out="$(make -C "$ROOT" test TESTS="$RED_FIXTURE" 2>&1)" && code=0 || code=$?
  [[ "$code" != 0 ]] ||
    problems+=("want 'make test' to fail a suite that exits non-zero even though it reached its count line; it exited 0 and said: $(flat "$out")")
}

# 2. The two answers the runner gave before #157 and must go on giving: a suite that ends in
#    its count line with nothing failed and exits 0 still passes, and a suite that prints its
#    count line but exits non-zero still fails. One criterion — what the new check did NOT
#    change — so one case, with a probe for each direction it could have been broken in and
#    one for the fixtures both rest on.
name="make test still passes a suite ending in its count line with nothing failed, and still fails one that prints its count line and exits non-zero"
problems=()

probe_live_fixtures_are_what_they_claim
probe_make_passes_the_green_suite
probe_make_fails_the_red_suite

report "$name"

# probe_added_suite_gets_the_check — the criterion, watched rather than argued. A throwaway
# tree gets the two things the recipe needs and nothing else: this repository's Makefile,
# copied byte for byte, and one suite sitting at the path the glob looks in. No TESTS is
# passed and no name is written anywhere, so the recipe reaching that suite at all means it
# found it by existing — and the failure line naming it is the count-line check, the one
# thing in the recipe that has anything to say about a suite that died. `cmp` is the other
# half of the criterion: it asserts the runner under test really is the committed one, so
# the case cannot be satisfied by a Makefile this suite quietly adjusted on its way past.
#
# The suite added is case 1's fixture under a new name — the shape the check exists to
# catch — because a suite that runs to its count line would be let through by a runner that
# checks it and by one that checks nothing, and say nothing about which this is.
probe_added_suite_gets_the_check() {
  local tree out code named
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch tree to add a suite to, so the criterion went unasked")
    return
  }
  mkdir -p "$tree/$TESTS_DIR"
  cp "$MAKEFILE" "$tree/Makefile"
  cp "$FIXTURE_PATH" "$tree/$TESTS_DIR/$ADDED_NAME"
  cmp -s "$MAKEFILE" "$tree/Makefile" ||
    problems+=("the runner under test is not this repository's Makefile, so nothing here says the check costs no edit to it")

  out="$(make -C "$tree" test 2>&1)" && code=0 || code=$?
  [[ "$code" != 0 ]] ||
    problems+=("want the recipe to refuse a suite added under $TESTS_DIR with no TESTS override and no edit to it; it exited 0 and said: $(flat "$out")")
  named="$(grep -F "$ADDED_NAME" <<< "$out")"
  grep -Eqi 'count[ -]line' <<< "$named" ||
    problems+=("no line of the run names $ADDED_NAME and says it never reached its count line, so the added suite did not get the check; the lines naming it were: $(flat "$named")")

  rm -rf "$tree"
}

# 3. A suite added under skills/tdd/scripts/tests/ is checked without the runner being
#    touched. Cases 1 and 2 both hand the recipe a TESTS value, which is how a fixture is
#    run at all but also how a runner that only checked suites it was told about would pass
#    them; this case names no suite and edits nothing, and the check still fires.
name="a suite added under skills/tdd/scripts/tests/ gets the count-line check with no edit to the runner"
problems=()

probe_added_suite_gets_the_check

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

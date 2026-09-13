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

# A suite that says something and then goes on working, for case 4: it prints one FAIL line,
# waits, and only then reaches its count line. Repo-relative and nothing else — this fixture
# is never run on its own, only through the recipe, because when its lines appear is a fact
# about the runner rather than about the fixture.
PAUSE_FIXTURE='skills/tdd/scripts/tests/fixtures/streaming/pauses-midway.test.sh'
PAUSE_LINE='FAIL - a suite says something before it is finished'

# The runner itself, and the directory its glob looks in. Case 3 needs both by name because
# it stands the runner up somewhere else: the only way to watch what the recipe does with a
# suite that was not there before is to add one, and adding one here would hand `make test` a
# suite whose first act is to run `make test`.
MAKEFILE="$ROOT/Makefile"
TESTS_DIR='skills/tdd/scripts/tests'
ADDED_NAME='newly-added.test.sh'

# The line every suite under skills/tdd/scripts/tests/ prints last, and so the thing the
# runner now looks for — the Makefile names it once as `COUNT_LINE` for the same reason.
# Anchored, because "the suite reached its count line" is a claim about a whole line: an
# unanchored copy would also be answered by a suite that quoted the words mid-sentence on
# its way down. Four probes below ask for it, and a pattern that drifted between them would
# leave half the cases agreeing with a runner the other half refused. Case 2's green fixture
# spells `0 failed` out instead, since what it asserts is not that the line is there but
# that it reports nothing failed.
COUNT_LINE='^[0-9]+ passed, [0-9]+ failed$'

# The document case 5 reads. Absolute only: nothing prints this path — a failure there names
# the section rather than the file, since there is one CLAUDE.md and its location is not the
# thing in doubt.
CLAUDE_MD="$ROOT/CLAUDE.md"

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

# blames <run output> <suite> <consequence> — the half of the criterion cases 1 and 3 both end
# in, asked once because both ask it of the same runner: a line of the run's output has to
# both name <suite> and say it never reached its count line. It is not asked as "the output
# mentions the suite" because the recipe already prints `== <suite>` before running each one,
# and bash's own death message carries the suite's path too, so both are there whatever the
# runner concluded. What has to name the suite is the report of the failure. One problem is
# appended if no line does, carrying <consequence> — what the silence costs that case — and
# the lines that did name the suite, which is what tells a missing report from a misworded one.
blames() {
  local named
  named="$(grep -F "$2" <<< "$1")"
  grep -Eqi 'count[ -]line' <<< "$named" ||
    problems+=("no line of the run both names $2 and says it never reached its count line$3; the lines naming it were: $(flat "$named")")
}

# recipe <fixture> — run this repository's `test` recipe over that one suite and nothing else,
# leaving the run's combined output in `recipe_out` and its exit status in `recipe_code`. Three
# probes below ask the same thing of the same runner and differ only in which answer they want,
# and `make test TESTS=<fixture>` is the whole of how a fixture is put in front of the real
# recipe rather than a copy of it — so the invocation is written once here. Both halves are left
# where the caller can see them because case 1 asks two questions of one run: the exit status
# first, then whether the output named the suite.
recipe() {
  recipe_out="$(make -C "$ROOT" test TESTS="$1" 2>&1)" && recipe_code=0 || recipe_code=$?
}

# direct <fixture path> — the other run this suite makes, and the reason the fixtures are held
# by absolute path as well: one fixture on its own, outside the recipe, its combined output left
# in `direct_out` and its exit status in `direct_code`. Every premise probe below needs it where
# the cases need `recipe` above, because what a premise asserts is the shape of the fixture
# itself — it dies, it exits 0, it ends in a count line — and a run through the recipe would be
# answering for the runner in the same breath. Written once because the way a status is caught
# here is not the obvious one: this suite does not run under `set -e`, so the exit code has to be
# taken on the spot, and `&& … || …` is the only form that survives a fixture that fails.
direct() {
  direct_out="$("$1" 2>&1)" && direct_code=0 || direct_code=$?
}

# probe_fixture_dies_quietly — the premise the case rests on, asserted rather than assumed:
# the fixture really does die after its first case and really does come back 0. A fixture
# that had stopped doing either would leave the probes below passing against a runner that
# reads nothing but the exit code, and the case would report green over the hole it exists
# to pin.
probe_fixture_dies_quietly() {
  direct "$FIXTURE_PATH"
  [[ "$direct_code" == 0 ]] ||
    problems+=("the fixture no longer exits 0 when it dies; got $direct_code, so nothing here pins a runner that trusts the exit code")
  grep -q 'unbound variable' <<< "$direct_out" ||
    problems+=("the fixture no longer dies from an unbound variable; its output was: $(flat "$direct_out")")
  ! grep -Eq "$COUNT_LINE" <<< "$direct_out" ||
    problems+=("the fixture reached its count line, so it did not die: $(flat "$direct_out")")
}

# probe_make_fails — the criterion itself. The run goes through `recipe` above, so it is the
# real runner over the real shape rather than a copy of either, and this asks for the answer
# the runner gives a human and a merge: a non-zero exit.
probe_make_fails() {
  recipe "$FIXTURE"
  [[ "$recipe_code" != 0 ]] ||
    problems+=("want 'make test' to fail over a suite that died; it exited 0 and said: $(flat "$recipe_out")")
}

# 1. One criterion, one case: a suite that dies silently is refused, and the refusal says
#    which suite. Three probes — the premise, the exit code, the report — each arguing for
#    itself above. probe_make_fails runs the recipe through the helper above and leaves the
#    run in `recipe_out` for the `blames` check after it, so the two read one run rather than
#    paying for two.
name="make test over a suite that dies from an unbound variable after its first case and exits 0 fails and names it"
problems=()
recipe_out=""
recipe_code=0

probe_fixture_dies_quietly
probe_make_fails
blames "$recipe_out" "$FIXTURE_NAME" ", so its refusal does not say which suite died"

report "$name"

# probe_live_fixtures_are_what_they_claim — the premises of case 2, asserted rather than
# assumed exactly as probe_fixture_dies_quietly asserts case 1's: the green fixture really
# does end in a count line reporting nothing failed and really does exit 0, and the red one
# really does reach its count line and really does exit non-zero. A fixture that had drifted
# off either shape would leave the two probes after it agreeing with a runner that had
# stopped telling the shapes apart.
probe_live_fixtures_are_what_they_claim() {
  direct "$GREEN_FIXTURE_PATH"
  [[ "$direct_code" == 0 ]] ||
    problems+=("the green fixture no longer exits 0; got $direct_code, so nothing below pins the passing half")
  [[ "$(tail -n 1 <<< "$direct_out")" =~ ^[0-9]+' passed, 0 failed'$ ]] ||
    problems+=("the green fixture no longer ends in a count line reporting nothing failed: $(flat "$direct_out")")

  direct "$RED_FIXTURE_PATH"
  [[ "$direct_code" != 0 ]] ||
    problems+=("the red fixture no longer exits non-zero, so nothing below pins a runner that reads the count line instead of the exit code")
  [[ "$(tail -n 1 <<< "$direct_out")" =~ $COUNT_LINE ]] ||
    problems+=("the red fixture no longer reaches its count line, so it fails the way case 1's fixture does: $(flat "$direct_out")")
}

# probe_make_passes_the_green_suite — the half that keeps the check from being satisfied by
# a runner that refuses everything. Through `recipe` as case 1 is, pointed at the one fixture,
# and asking for the answer a green suite has always got.
probe_make_passes_the_green_suite() {
  recipe "$GREEN_FIXTURE"
  [[ "$recipe_code" == 0 ]] ||
    problems+=("want 'make test' to pass a suite that ends in its count line with nothing failed; it exited $recipe_code and said: $(flat "$recipe_out")")
}

# probe_make_fails_the_red_suite — the half that keeps the count line from displacing the
# exit code rather than joining it. This fixture has the line the check asks for, so a
# runner that had come to read only that line calls it green, and an ordinary test failure
# — the most common red there is — stops being reported at all.
probe_make_fails_the_red_suite() {
  recipe "$RED_FIXTURE"
  [[ "$recipe_code" != 0 ]] ||
    problems+=("want 'make test' to fail a suite that exits non-zero even though it reached its count line; it exited 0 and said: $(flat "$recipe_out")")
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
  local tree out code
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
  blames "$out" "$ADDED_NAME" ", so the added suite did not get the check"

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

# probe_run_showed_the_line_while_the_suite_ran — the criterion, and the only way to ask it
# is to watch a run rather than read one: a runner that collects a suite's output and prints
# it when the suite is over leaves exactly the same text behind as one that streams it. So
# the run goes into the background writing to a file, and the file is read ten times a
# second while it fills.
#
# What counts as an answer is the pair, not the FAIL line alone: the fixture's own count line
# is the last thing it prints, so output holding the FAIL line and NOT the count line can
# only have been written before the suite finished. A runner that buffered would put both
# there in the same instant, and no look finds one without the other.
#
# The loop ends when the count line lands, which is the suite finishing; the 30 s cap is
# there so a runner that hangs is reported rather than hanging this suite with it.
probe_run_showed_the_line_while_the_suite_ran() {
  local looks=0 mk
  stream_log="$(mktemp)" || {
    problems+=("could not make a file to collect a run's output into, so the criterion went unasked")
    return
  }

  local started=$SECONDS
  make -C "$ROOT" test TESTS="$PAUSE_FIXTURE" > "$stream_log" 2>&1 &
  mk=$!
  while :; do
    # A look that finds the FAIL line is the last one, whichever way it answers: no count
    # line beside it is the streamed run this case wants, and a count line beside it is the
    # suite already over. So both leave the loop here, and the two questions are asked in
    # this order — the FAIL line first, the count line second — because the log only grows:
    # the count line missing *after* the FAIL line was seen is what says the two coexisted.
    if grep -qF "$PAUSE_LINE" "$stream_log"; then
      grep -Eq "$COUNT_LINE" "$stream_log" || streamed=yes
      break
    fi
    # The FAIL line is not there, so a count line means the suite ended without it — a
    # broken fixture, reported by the probe below rather than waited out here.
    grep -Eq "$COUNT_LINE" "$stream_log" && break
    looks=$((looks + 1))
    if [[ "$looks" -gt 300 ]]; then
      problems+=("the run had still not printed the fixture's count line after 30s; gave up on it")
      kill "$mk" 2>/dev/null
      break
    fi
    sleep 0.1
  done
  wait "$mk" 2>/dev/null
  stream_elapsed=$((SECONDS - started))

  [[ "$streamed" == yes ]] || {
    if grep -qF "$PAUSE_LINE" "$stream_log"; then
      problems+=("the suite's FAIL line was never there without its count line beside it, so the run had shown nothing until the suite was over; it said: $(flat "$(cat "$stream_log")")")
    else
      problems+=("the run never showed the suite's FAIL line at all; it said: $(flat "$(cat "$stream_log")")")
    fi
  }
}

# probe_that_run_could_have_told_the_difference — the premises of the probe above, asked of
# the run it already made rather than of a second one, which is why it comes after it: the
# fixture is slow on purpose and a second run of it would be paid by every `make test`.
# Both premises are load-bearing in the same direction — a fixture that stopped pausing
# leaves the two lines microseconds apart, and one whose count line stopped matching the
# pattern above leaves "without its count line" true forever — and either would let a
# buffering runner through.
probe_that_run_could_have_told_the_difference() {
  [[ "$stream_elapsed" -ge 1 ]] ||
    problems+=("the whole run took under a second, so the fixture no longer pauses and there was no window in which a streamed line and a buffered one differ")
  grep -Eq "$COUNT_LINE" "$stream_log" ||
    problems+=("the fixture's count line never matched the pattern the probe above waits for, so 'the FAIL line without the count line' was true of every look and says nothing: $(flat "$(cat "$stream_log")")")
  rm -f "$stream_log"
}

# 4. The recipe still shows each suite's lines as they are printed. Cases 1 to 3 are all
#    satisfied by a runner that collects a suite's output and reads it once the suite is
#    over — that is the obvious way to ask a suite for its last line — and such a runner
#    turns `make test` into 70 s of silence followed by everything at once. This case is
#    what stops that trade.
name="make test shows a suite's line while that suite is still running"
problems=()
stream_log=""
stream_elapsed=0
streamed=no

probe_run_showed_the_line_while_the_suite_ran
probe_that_run_could_have_told_the_difference

report "$name"

# plain — stdin with emphasis marks and backticks dropped and the case folded, so a regex
# below is written one way and still matches prose that marked the same words up as
# `make test` or **count line**. The normalisation skill-suite-runs.test.sh uses on the same
# document, for the same reason.
plain() { tr -d '*`' | tr '[:upper:]' '[:lower:]'; }

# says <fact> <regex>... — one fact the text in `$idiom` has to carry, written as the regexes
# any wording carrying it would match: all of them have to match, and one problem naming the
# fact is appended if any does not. Regexes rather than fixed strings because what the
# section records is the claim and how it is phrased is the author's — the protocol the other
# prose suites in this tree use.
says() {
  local fact="$1" re
  shift
  for re in "$@"; do
    [[ "$idiom" =~ $re ]] || {
      problems+=("CLAUDE.md's Testing idiom section does not say $fact")
      return
    }
  done
}

# probe_idiom_records_the_check — the criterion. The section is read by its heading, from
# `## Testing idiom` to the next `## `, and not by matching the whole document: that section
# is where an author writing a suite is sent, so a sentence about the count line two sections
# up in the command table would answer for prose that section does not have. Lines are joined
# onto one because CLAUDE.md wraps mid-sentence, and a claim split over a line break has to
# still read as one sentence.
#
# Fails closed on a section that is not there: an empty string matches no regex, so both
# facts would be reported missing — true, but it names two edits when the repair is that the
# heading moved.
probe_idiom_records_the_check() {
  idiom="$(awk '/^## Testing idiom/ { f = 1; next } f && /^## / { exit } f' "$CLAUDE_MD" | plain | tr '\n' ' ')"
  [[ -n "${idiom// /}" ]] || {
    problems+=("CLAUDE.md has no '## Testing idiom' section to read, so neither half of the rule is recorded where an author writing a suite is sent")
    return
  }

  says "the runner itself fails a suite that never reached its count line" \
    'count[ -]line' 'fail|refus|reject|red'
  says "why a suite's exit code alone is not trusted — one that stops asserting partway can still come back 0" \
    'exit (code|status)|exits? 0|exit-code' \
    'alone|by itself|only|not enough|trust' \
    'die|dies|died|dying|stops? asserting|silen|unbound|set -u'
}

# 5. What the document says, which is the half of this issue that outlives the runner. Cases
#    1 to 4 pin what `make test` does; this one pins that the next author to write a suite is
#    told the runner asks for the count line, and told why an exit code is not taken for an
#    answer. Without the second half the rule reads as a formatting convention, and the first
#    person whose suite is refused deletes the check rather than the bug — the mechanism is
#    exactly the thing that is not obvious from reading a green run.
name="CLAUDE.md's Testing idiom section says the runner enforces the count line, and why an exit code alone is not trusted"
problems=()
idiom=""

probe_idiom_records_the_check

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

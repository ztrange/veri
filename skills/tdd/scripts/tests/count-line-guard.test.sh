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

# The other way a suite is run in this tree, and case 9's subject: the runner a leaf is told to
# use when it runs ONE suite rather than the whole tier. `make test TESTS=<suite>` is the only
# single-suite invocation cases 1 to 8 ask anything of, and it leaks TESTS into every nested
# make, which is why a human — and, until #418, a leaf — ran the file itself instead and got no
# count-line check at all. Absolute, because the case runs it from wherever this suite started.
RUNNER="$ROOT/skills/tdd/scripts/run-suite.sh"

# The name case 10 writes its own one-line suite under, inside a scratch directory of its own.
# That case asks what the runner puts in a suite's ENVIRONMENT, which no fixture on disk can
# answer without reporting it, and the fixtures here judge the runner's verdict rather than
# its environment — so the suite that reports it is written by the case, the way case 3 writes
# the tree it adds a suite to. The name is not one this directory holds, so nothing globs it.
ENV_SUITE_NAME='reports-tests-var.test.sh'

# Case 12's scratch tree, named here beside the other fixtures it stands in for. The runner
# reads the guard out of the Makefile at its own grandparent's parent, so the only way to put a
# root in front of it that cannot answer for the guard is to stand a copy of the runner up in
# one — the same move case 3 makes when it needs a tree with a suite this one does not have.
# The suite written in there reaches its count line and reports nothing failed, so a runner
# that shrugged off the unanswerable root would come back 0 over it.
GUARDLESS_SUITE_NAME='answers-green.test.sh'

# The two texts case 11 counts, and the reason it counts them at all: a guard written twice is
# two guards, and the one a leaf meets depends on how it invoked the suite. The first is what a
# countless suite's refusal says — the `%s: …` message cases 1 and 9 both read — and the second
# is the substring every spelling of the count-line pattern contains, whether it is written as
# make's `COUNT_LINE := ^[0-9]+ passed, [0-9]+ failed$$` or a shell script's single-quoted copy.
# Substrings rather than whole lines, because what must not exist twice is the decision, not a
# particular way of writing it down.
GUARD_MESSAGE=': never reached its count line'
GUARD_PATTERN='passed, [0-9]+ failed'

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

# direct <command> [argument]... — every run this suite makes that does not go through `make`,
# and the reason the fixtures are held by absolute path as well: a fixture on its own, or the
# single-suite runner over one, its combined output left in `direct_out` and its exit status in
# `direct_code`. Every premise probe below needs it where the cases need `recipe` above, because
# what a premise asserts is the shape of the fixture itself — it dies, it exits 0, it ends in a
# count line — and a run through the recipe would be answering for the runner in the same breath;
# case 9 needs it for the runner, which is the same run with a command in front of the fixture.
# Written once because the way a status is caught here is not the obvious one: this suite does not
# run under `set -e`, so the exit code has to be taken on the spot, and `&& … || …` is the only
# form that survives a fixture that fails.
direct() {
  direct_out="$("$@" 2>&1)" && direct_code=0 || direct_code=$?
}

# have_runner <consequence> — the premise the three probes below the recipe's own share: the
# single-suite runner is there to be run. Written once and asked rather than assumed, because a
# runner that is not there exits non-zero too — the shell's 127 for a name it cannot find — so a
# probe that only read the exit status would be answered by the runner's own absence. Each caller
# passes what its own case loses when the runner is missing; the problem line carries the path,
# which is the same whoever asks. Returns 1 so a caller ends with `|| return`.
have_runner() {
  [[ -x "$RUNNER" ]] && return 0
  problems+=("there is no executable single-suite runner at $RUNNER, $1")
  return 1
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
# the run goes into the background writing to a file, and the file is read fifty times a
# second while it fills — fast enough to keep pace with PAUSE_FIXTURE's own 0.2s pause
# (pauses-midway.test.sh) without costing more than a couple of forks per look.
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

  # Bash's own $SECONDS only counts whole seconds, which fit a 2s PAUSE but not a 0.2s one —
  # every look inside the same second would read the same value. EPOCHREALTIME (bash 5,
  # which veri now requires — CLAUDE.md, "Versions are tags") is microsecond-precision and
  # needs no external `date`, so it costs no extra fork either.
  local started="$EPOCHREALTIME"
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
    if [[ "$looks" -gt 1500 ]]; then
      problems+=("the run had still not printed the fixture's count line after 30s; gave up on it")
      kill "$mk" 2>/dev/null
      break
    fi
    sleep 0.02
  done
  wait "$mk" 2>/dev/null
  stream_elapsed="$(awk -v a="$started" -v b="$EPOCHREALTIME" 'BEGIN { printf "%.3f", b - a }')"

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
#
# The floor is 0.15s, not PAUSE_FIXTURE's full 0.2s: `sleep "$PAUSE"` there guarantees AT
# LEAST 0.2s of real time (only ever more, under load — a busy runner cannot make the
# fixture's own pause shorter), and this run's elapsed time also carries `make`'s and
# bash's own startup on top of it, so 0.15 (75% of the guaranteed minimum) is comfortable
# margin below a floor that CI contention can only push up, never down.
probe_that_run_could_have_told_the_difference() {
  awk -v e="$stream_elapsed" 'BEGIN { exit !(e >= 0.15) }' ||
    problems+=("the whole run took under 0.15s (got ${stream_elapsed}s), so the fixture no longer pauses long enough and there was no window in which a streamed line and a buffered one differ")
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

# probe_reaching_suite_is_refused_and_named — the criterion for the two shims that remain
# bash scripts. gh and curl are not the hot path (a run makes ~1,900 git calls against a
# handful of gh/curl calls total), so they still go through tests/offline/{gh,curl}, which
# still log every attempt to the reach log the recipe reads. The suite handed to the recipe
# tries both at an `.invalid` host (RFC 2606), so a recipe that does not cut them off pays a
# failed DNS lookup and nothing more. Each attempt carries a token no other line would, and
# the refusal has to put that token on one line with the suite's name.
probe_reaching_suite_is_refused_and_named() {
  local tree suite reach tried
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch tree to hold a suite that reaches the network, so the criterion went unasked")
    return
  }
  suite="$tree/reaches-network.test.sh"
  cat > "$suite" <<'SUITE'
#!/usr/bin/env bash
set -uo pipefail
gh api --hostname example.invalid veri-gh-probe >/dev/null 2>&1
curl -s --max-time 2 https://example.invalid/veri-curl-probe >/dev/null 2>&1
echo "1 passed, 0 failed"
exit 0
SUITE
  chmod +x "$suite"

  recipe "$suite"
  [[ "$recipe_code" != 0 ]] ||
    problems+=("want 'make test' to fail a suite that tried the network; it exited 0 and said: $(flat "$recipe_out")")
  for reach in veri-gh-probe veri-curl-probe; do
    tried="$(grep -F 'reaches-network.test.sh' <<< "$recipe_out" | grep -F "$reach")"
    [[ -n "$tried" ]] ||
      problems+=("no line of the run names reaches-network.test.sh together with the attempt carrying $reach, so the refusal does not say which suite tried what")
  done

  rm -rf "$tree"
}

# 6. gh and curl keep the bash-script shim and its reach log: a suite that calls either still
#    fails `make test`, and the failure names the suite and what it tried. git is no longer part
#    of this contract (case 7 below) — it dropped out of `probe_reaching_suite_is_refused_and_named`
#    when the git shim did.
name="make test fails a suite that runs gh or curl, naming the suite and what it tried"
problems=()
recipe_out=""
recipe_code=0

probe_reaching_suite_is_refused_and_named

report "$name"

# probe_git_transport_allowlist — the criterion for git. Measured 2026-09-18: the bash shim that
# used to stand in front of every git call cost ~26 ms/call against ~8 ms for the real binary, and
# a `make test` run makes ~1,900 of them — 1,820 of the run's 4,834 bash starts were that one
# script. It is gone; `git` on the recipe's PATH is now a symlink straight to the real binary (no
# wrapper, no bash start at all — case 8 pins that), and what used to be the shim's job — refusing
# a remote reach — is now git's own transport allowlist: `protocol.allow=never` with
# `protocol.file.allow=always`, set the same way the recipe already sets `http.proxy`, via
# GIT_CONFIG_COUNT/KEY/VALUE.
#
# The accepted trade-off is the reach log's "tried the network: …" line, which named the suite and
# the URL on one line of `make test`'s own output. Nothing forwards a git reach into that log any
# more, so a suite whose fetch fails silently (its own exit code unchecked, its own output
# discarded) is refused but not specially reported — the failure is git's, on stderr, wherever the
# suite sends stderr. What is still true, and what this probe and case 8 below pin instead:
#   - every non-file transport is refused, for every URL shape (https, ssh://, git://, and the
#     scp-style `user@host:path` git treats as ssh) — verified against a real local remote for
#     each, not by pattern-matching git's own error text;
#   - a local remote (a bare path, or `file://`) is unaffected, since many suites here clone,
#     fetch and push between scratch repos on disk;
#   - this checkout's own origin, fetched with no scheme (as run-conductor.sh does since #251), is
#     refused by the same general rule rather than by a rule of its own; and
#   - a suite that DOES check the exit code — the well-behaved shape, not the fire-and-forget one
#     the old shim's reach log existed to catch — still fails `make test`, visibly: git's own
#     "not allowed" text reaches the run's output rather than a manufactured line.
probe_git_transport_allowlist() {
  local tree suite own_origin
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch tree to hold the git-allowlist probe, so the criterion went unasked")
    return
  }
  git init -q -b main "$tree/src" >/dev/null 2>&1
  ( cd "$tree/src" && : > f && git add f && git -c user.email=a@b.c -c user.name=a commit -q -m init ) \
    >/dev/null 2>&1
  git init -q -b main "$tree/dest" >/dev/null 2>&1
  own_origin="$(git -C "$ROOT" remote get-url origin 2>/dev/null)"

  suite="$tree/checks-transport-allowlist.test.sh"
  {
    printf '#!/usr/bin/env bash\nset -uo pipefail\n'
    printf 'dest=%q\n' "$tree/dest"
    printf 'own_origin=%q\n' "$own_origin"
    cat <<'SUITE'
problems=()
blocked() {
  local label="$1" url="$2" err rc
  err="$(GIT_TERMINAL_PROMPT=0 git -C "$dest" fetch "$url" 2>&1 >/dev/null)"; rc=$?
  [[ "$rc" -ne 0 ]] || problems+=("$label was not refused (exit 0)")
  grep -qi 'not allowed' <<< "$err" ||
    problems+=("$label's refusal carried no 'not allowed' message: $err")
}
for pair in \
  "https:https://example.invalid/veri-https-probe.git" \
  "ssh-scheme:ssh://example.invalid/veri-ssh-probe.git" \
  "git-scheme:git://example.invalid/veri-git-scheme-probe.git" \
  "scp-style:git@example.invalid:veri-scp-probe.git"; do
  blocked "${pair%%:*}" "${pair#*:}"
done
if [[ -n "$own_origin" ]]; then
  blocked "own-origin" "$own_origin"
fi
err="$(GIT_TERMINAL_PROMPT=0 git -C "$dest" fetch --quiet ../src 2>&1 >/dev/null)"; rc=$?
[[ "$rc" -eq 0 ]] || problems+=("a local relative fetch was refused: $err")
if [[ "${#problems[@]}" -eq 0 ]]; then
  echo "1 passed, 0 failed"
  exit 0
else
  printf 'PROBLEM: %s\n' "${problems[@]}"
  echo "0 passed, 1 failed"
  exit 1
fi
SUITE
  } > "$suite"
  chmod +x "$suite"

  recipe "$suite"
  [[ "$recipe_code" == 0 ]] ||
    problems+=("want 'make test' to pass a suite whose every remote git form was refused and whose local fetch still worked; got exit $recipe_code: $(flat "$recipe_out")")
  [[ -n "$own_origin" ]] ||
    problems+=("this checkout has no origin, so the own-origin form of the probe checked nothing")

  rm -rf "$tree"
}

# 7. git's own transport allowlist, not a bash shim, is what keeps a suite off the network: every
#    non-file remote form is refused (https, ssh://, git://, scp-style, and this checkout's own
#    origin), and a local fetch (a bare path) still works, since suites here rely on that between
#    scratch repos.
name="make test's git allows only local remotes: https, ssh, git and scp-style forms are refused, a local path still fetches"
problems=()
recipe_out=""
recipe_code=0

probe_git_transport_allowlist

report "$name"

# probe_unswallowed_git_reach_fails_visibly — the other half of the accepted trade-off: a suite
# that does not discard git's exit code still fails `make test`, and git's own refusal reaches the
# run's output — there is just no manufactured "tried the network: …" line for it any more, since
# nothing forwards a git reach into the reach log now that gh and curl are the only shims left.
probe_unswallowed_git_reach_fails_visibly() {
  local tree suite
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch tree to hold the unswallowed-reach probe, so the criterion went unasked")
    return
  }
  git init -q -b main "$tree/dest" >/dev/null 2>&1
  suite="$tree/reach-not-swallowed.test.sh"
  {
    printf '#!/usr/bin/env bash\nset -uo pipefail\n'
    printf 'dest=%q\n' "$tree/dest"
    cat <<'SUITE'
GIT_TERMINAL_PROMPT=0 git -C "$dest" fetch https://example.invalid/veri-visible-probe.git
rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "1 passed, 0 failed"
  exit 0
else
  echo "0 passed, 1 failed"
  exit 1
fi
SUITE
  } > "$suite"
  chmod +x "$suite"

  recipe "$suite"
  [[ "$recipe_code" != 0 ]] ||
    problems+=("want 'make test' to fail a suite whose git fetch of a remote URL it did not swallow; it exited 0 and said: $(flat "$recipe_out")")
  grep -qi 'not allowed' <<< "$recipe_out" ||
    problems+=("want git's own refusal text ('transport … not allowed') visible in the run's output; got: $(flat "$recipe_out")")
  ! grep -qF 'tried the network' <<< "$recipe_out" ||
    problems+=("a git reach is no longer caught by the reach log (that mechanism now covers only gh and curl); want no manufactured 'tried the network' line, got: $(flat "$recipe_out")")

  rm -rf "$tree"
}

# 8. The accepted trade-off, named: a suite that surfaces a git remote reach as its own failure
#    still fails `make test`, and git's refusal is visible in the run's output — but the run no
#    longer manufactures a "tried the network: …" line for git the way it does for gh and curl.
name="make test fails a suite whose unswallowed git fetch of a remote URL is refused, visibly, with no manufactured reach-log line"
problems=()
recipe_out=""
recipe_code=0

probe_unswallowed_git_reach_fails_visibly

report "$name"

# probe_runner_refuses_the_countless_suite — the criterion, asked of the single-suite runner
# rather than of the recipe. The recipe's guard reaches only the suites its glob or a TESTS=
# override hands it, so a leaf running one suite on its own had nothing checking it: not the
# exit code, which this fixture shows lying, and not the count line, which nothing read. The
# probes run in the order a reader needs them — the runner exists, it refuses, the refusal
# names the suite — and the first is not an assumption this case may skip: a runner that is
# not there exits non-zero too (the shell's 127 for a name it cannot find), so the exit-code
# probe alone would be answered by the runner's own absence.
#
# The fixture goes in by absolute path, since this suite's own working directory is whoever
# ran it, and it is the same fixture case 1 hands the recipe: the criterion is that the two
# invocations agree about it, which a second fixture of its own would not ask.
probe_runner_refuses_the_countless_suite() {
  have_runner "so a leaf that runs one suite has nothing to run it through and its count line goes unread" || return
  direct "$RUNNER" "$FIXTURE_PATH"
  [[ "$direct_code" != 0 ]] ||
    problems+=("want the runner to fail over a suite that died without reaching its count line; it exited 0 and said: $(flat "$direct_out")")
  blames "$direct_out" "$FIXTURE_NAME" ", so its refusal does not say which suite died"
}

# 9. The same fixture, the same verdict, through the other invocation: one suite run directly
#    through this repository's suite runner is refused and named, exactly as case 1's `make
#    test` refuses and names it. Cases 1 to 8 all go through the recipe, which is the whole of
#    where the guard lived — so a leaf that ran a suite by itself read a partially-dead suite
#    as green, and on #415 the leaf that did so was the blind verifier whose PASS lets a green
#    commit land (#418).
name="the suite runner over a suite that exits 0 without reaching its count line fails and names it"
problems=()

probe_fixture_dies_quietly
probe_runner_refuses_the_countless_suite

report "$name"

# probe_runner_runs_the_named_suite_with_no_TESTS — the criterion, asked of the environment the
# runner hands the suite it was told to run. `make test TESTS=<suite>` is the invocation this
# repository had for running one suite, and a command-line variable is exported to the recipe
# and to every make nested under it, so a suite that shells out to `make` gets its own TESTS
# silently narrowed — which is why CLAUDE.md sends a human to the suite file itself instead.
# A runner that reached for that same override would carry the leak into the leaves along with
# the guard.
#
# The suite it runs is written here rather than taken from fixtures/: what is being asked is
# what reaches a suite's environment, so the suite has to report it, and it reaches its count
# line so the guard case 9 pins is not what answers this case. TESTS is removed from the
# runner's own environment first (`env -u`), because a value inherited from whoever ran this
# file would otherwise read as one the runner set.
probe_runner_runs_the_named_suite_with_no_TESTS() {
  local tree probe seen
  have_runner "so there is no invocation to ask this of" || return
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch directory to write a suite into, so the criterion went unasked")
    return
  }
  probe="$tree/$ENV_SUITE_NAME"
  cat > "$probe" <<'SUITE'
#!/usr/bin/env bash
# Written by count-line-guard.test.sh. It judges nothing: it writes down whether TESTS was in
# the environment it was run in, then reaches its count line so the runner has nothing else to
# say about it.
set -uo pipefail
printf 'TESTS=%s\n' "${TESTS-<unset>}"
echo "1 passed, 0 failed"
SUITE
  chmod +x "$probe"

  direct env -u TESTS "$RUNNER" "$probe"
  seen="$(grep -E '^TESTS=' <<< "$direct_out" | tail -n 1)"
  [[ -n "$seen" ]] ||
    problems+=("the runner never ran the suite it was named, so nothing here says what its environment held; it exited $direct_code and said: $(flat "$direct_out")")
  [[ "$direct_code" == 0 ]] ||
    problems+=("want the runner to pass a suite that reaches its count line with nothing failed; it exited $direct_code and said: $(flat "$direct_out")")
  [[ -z "$seen" || "$seen" == 'TESTS=<unset>' ]] ||
    problems+=("the runner put TESTS in the named suite's environment ($seen), so a make nested inside that suite inherits it and runs that one suite instead of its own")

  rm -rf "$tree"
}

# 10. The runner names the suite it runs without going through TESTS=. Case 9 is satisfied by a
#     runner that shells out to `make test TESTS=<suite>` — that is the single-suite invocation
#     this repository already had, and it would inherit the guard for free — but a command-line
#     variable is exported into every nested make, so a suite that itself calls `make` would
#     have its own TESTS overwritten by the name of the suite being run. That leak is the whole
#     reason a leaf ran the suite file directly in the first place, so the runner that replaces
#     the direct run must not reintroduce it (#418).
name="the suite runner runs the suite it is named with no TESTS in that suite's environment"
problems=()

probe_runner_runs_the_named_suite_with_no_TESTS

report "$name"

# guard_sites <text> — the files of this tree that make a decision containing <text>, one per
# line, by basename. "Make a decision" is why comment lines are dropped first: both the Makefile
# and run-suite.sh explain the count-line contract in prose at length, and a guard that moved
# out of one of them would rightly leave the sentence saying where it went behind. What must
# not appear twice is the code. The scope is this repository's own runnable sources — the
# Makefile and the scripts under skills/tdd/scripts — with tests/ left out, since the suites and
# the fixtures quote both texts on purpose and are not what either invocation reads at run time.
guard_sites() {
  local text="$1" site sites=()
  while IFS= read -r site; do
    local body
    body="$(grep -v '^[[:space:]]*#' "$site")"
    grep -qF "$text" <<< "$body" && sites+=("$(basename "$site")")
  done < <(printf '%s\n' "$MAKEFILE"; find "$ROOT/skills/tdd/scripts" -name '*.sh' -not -path '*/tests/*' | sort)
  # Nothing at all when nothing matched, rather than one empty line: the caller counts lines,
  # and a blank one would read as a place the decision is written.
  ((${#sites[@]})) && printf '%s\n' "${sites[@]}"
}

# probe_one_guard_behind_both_invocations — the criterion. Each of the two decisions a guard
# makes — what a count line looks like, and what a suite that never printed one is told — has to
# be written in exactly one runnable place, because two places is two guards: `make test` reads
# one of them and the single-suite runner reads the other, and nothing makes a change to either
# reach the other. Not one place is as wrong in the other direction: zero would mean the guard
# went away entirely, which cases 1 and 9 would then be reading off nothing.
probe_one_guard_behind_both_invocations() {
  local pair text label sites n
  for pair in "$GUARD_MESSAGE|what a countless suite is told" "$GUARD_PATTERN|what a count line looks like"; do
    text="${pair%%|*}"
    label="${pair#*|}"
    mapfile -t sites < <(guard_sites "$text")
    n="${#sites[@]}"
    [[ "$n" -eq 1 ]] ||
      problems+=("$label is decided in $n place(s) — ${sites[*]:-nowhere} — so 'make test' and the suite runner do not share one guard and can drift apart about it")
  done
}

# probe_both_invocations_word_it_the_same — the visible half of the same criterion, and the thing
# a leaf actually meets: the one fixture, run both ways, has to come back refused in the very
# same words. Two guards that agree today pass this and fail the probe above; one guard cannot
# fail either. The line compared is the refusal itself rather than the whole run, since the
# recipe also prints its own `== <suite>` header and its closing verdict, which the runner over
# a single suite has no reason to.
probe_both_invocations_word_it_the_same() {
  local made ran
  have_runner "so there is no second invocation to compare the recipe against" || return
  recipe "$FIXTURE"
  made="$(grep -F "$GUARD_MESSAGE" <<< "$recipe_out" | awk 'NR==1')"
  direct "$RUNNER" "$FIXTURE_PATH"
  ran="$(grep -F "$GUARD_MESSAGE" <<< "$direct_out" | awk 'NR==1')"
  [[ -n "$made" && -n "$ran" ]] || {
    problems+=("one of the two invocations did not report the countless suite at all; 'make test' said: $(flat "$recipe_out") and the runner said: $(flat "$direct_out")")
    return
  }
  [[ "$made" == "$ran" ]] ||
    problems+=("the two invocations word the refusal differently: 'make test' said '$made' and the runner said '$ran'")
}

# 11. The two invocations are one guard, not two that agree for now. Cases 1 and 9 pin each
#     invocation's verdict on the same countless fixture separately, and both would go on
#     passing with the pattern and the message written out twice — which is how they stood when
#     this case was added, the recipe holding its own copy and run-suite.sh a second one. A
#     second copy is a guard that only looks like the first: tighten the pattern in one place,
#     or reword the refusal, and the invocation that did not get the change reports a different
#     suite as green (#418).
name="the make target and the suite runner refuse a countless suite from one guard, in the same words"
problems=()
recipe_out=""
recipe_code=0

probe_one_guard_behind_both_invocations
probe_both_invocations_word_it_the_same

report "$name"

# ran_in_root <makefile body> — stand this repository's runner up in a fresh tree of its own
# whose Makefile is the one given, run it there over a suite that reaches its count line with
# nothing failed, and take the tree away again; the run is left in `direct_out`/`direct_code`
# like every other. The runner's copy sits at the path the real one sits at relative to the
# root, since that relative position is how it finds the Makefile it asks. All of it is written
# once because case 12's two probes differ in exactly one thing — what `make count-line-guard`
# answers in each — and in nothing about standing the tree up, running it or clearing it away.
# Returns 1, having said so, when the tree could not be made: the probe then has no run to read
# and ends with `|| return`, rather than asking its question of an empty `direct_out`.
ran_in_root() {
  local tree body="$1" probe
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch directory to stand a runner up in, so the question went unasked")
    return 1
  }
  probe="$tree/$GUARDLESS_SUITE_NAME"
  mkdir -p "$tree/skills/tdd/scripts"
  cp "$RUNNER" "$tree/skills/tdd/scripts/run-suite.sh"
  # A newline of its own, so a body written as a `count-line-guard:` rule and its recipe line is
  # a Makefile whatever the caller's heredoc left behind.
  printf '%s\n' "$body" > "$tree/Makefile"
  cat > "$probe" <<'SUITE'
#!/usr/bin/env bash
# Written by count-line-guard.test.sh. It asserts nothing about this tree: it reaches its count
# line and reports nothing failed, so the only thing a runner can have to say about it comes
# from the runner's own state rather than from the suite.
set -uo pipefail
echo "1 passed, 0 failed"
SUITE
  chmod +x "$probe"

  direct "$tree/skills/tdd/scripts/run-suite.sh" "$probe"
  rm -rf "$tree"
}

# probe_root_that_answers_the_guard_runs_the_suite — the premise case 12 rests on, and not one
# it may assume: a copy of the runner standing in a tree that is not this repository could fail
# to run a suite for any number of reasons that have nothing to do with the guard, and the case
# below would then read that failure as the refusal it is looking for. So the same copy, in the
# same shape of tree, over the same suite, with a Makefile that DOES answer for the guard has to
# come back 0 first.
probe_root_that_answers_the_guard_runs_the_suite() {
  local body
  # A Makefile that answers for the guard the way this repository's own does, written out here
  # rather than borrowed from $ROOT: what this premise needs is a root that answers at all, and
  # a copy of the real Makefile would drag its every other target into the scratch tree with it.
  # The heredoc is quoted, so make gets `$$` (its own escape for a literal `$`) and printf gets
  # the `\n` that COUNTLESS carries, neither of them touched by this suite's shell.
  body="$(cat <<'MK'
count-line-guard:
	@printf "COUNT_LINE='%s'\nCOUNTLESS='%s'\n" '^[0-9]+ passed, [0-9]+ failed$$' '%s: never reached its count line\n'
MK
)"
  ran_in_root "$body" || return
  [[ "$direct_code" == 0 ]] ||
    problems+=("the runner does not pass a green suite even in a scratch root whose make answers for the guard; it exited $direct_code and said: $(flat "$direct_out") — so nothing below distinguishes a refused guard from a copy that cannot run at all")
}

# probe_root_that_cannot_answer_the_guard_is_refused — the criterion's other edge. The runner
# does not carry the guard, it asks the Makefile for it, so there is a state in which it holds
# no guard at all: a root whose `count-line-guard` answers nothing. A runner that went on from
# there would check a suite against an empty pattern, which every line matches, and hand back
# the suite's own exit code — the very 0 that #157 established lies, and for every suite rather
# than only a partially-dead one. So no suite may be reported out of that state: it is exit 2,
# "no answer could be obtained" (CLAUDE.md, "Exit codes are the API"), said in words that name
# what could not be read, since a bare 2 is also what a missing argument earns.
probe_root_that_cannot_answer_the_guard_is_refused() {
  # The target exists and answers nothing — the state the runner's own eval lands in whenever
  # the guard cannot be read, reached here in the one line that names it rather than by hiding
  # the Makefile, so what is under test is the empty answer and not a missing file.
  ran_in_root "count-line-guard:
	@:" || return
  [[ "$direct_code" == 2 ]] ||
    problems+=("want exit 2 from a runner whose root cannot answer for the guard — no answer could be obtained — got $direct_code, and it said: $(flat "$direct_out")")
  ! grep -Fq "$GUARD_MESSAGE" <<< "$direct_out" ||
    problems+=("the runner reported a verdict on the suite while holding no guard to judge it by: $(flat "$direct_out")")
  grep -Eqi 'could not read.*guard' <<< "$direct_out" ||
    problems+=("the runner did not say that it could not read the guard, so a caller cannot tell this 2 from any other; it said: $(flat "$direct_out")")
}

# 12. The runner holds no guard of its own, and says so rather than guessing. Cases 9 and 11
#     make the guard one text in one place, which case 10's runner then has to go and fetch —
#     and fetching can come back empty. Left unchecked that is worse than the hole #418 opened:
#     an empty pattern is matched by every line, so every suite run through the runner would
#     pass its count-line check and be reported on its exit code alone, which is the one thing
#     #157 established cannot be trusted. The state is a root whose `make count-line-guard`
#     answers nothing; the answer owed is exit 2 with no verdict on the suite.
name="the suite runner whose root cannot answer for the guard reports no suite and exits 2"
problems=()

probe_root_that_answers_the_guard_runs_the_suite
probe_root_that_cannot_answer_the_guard_is_refused

report "$name"

# probe_runner_refuses_the_countless_suite_as_a_clean_negative — the criterion itself, asked of
# the code the refusal comes back as. Case 9 asks the partially-dead fixture of the direct
# invocation and wants a non-zero, which was the whole of what #418 opened: a leaf running one
# suite by itself read it as 0. But non-zero is two answers in this repository, and the two mean
# opposite things to a conductor — 1 is a clean negative, the suite ran and what came back about
# the tree under it is that it is not green; 2 is "no answer could be obtained", the plumbing
# broke and nothing was established either way (CLAUDE.md, "Exit codes are the API"). Case 12
# spends that 2 on the runner's own unreadable guard, so a runner that answered 2 here as well
# would pass case 9 while telling every caller that the partially-dead suite had not been judged
# — and a partially-dead suite unjudged is exactly the state #415's blind verifier was in.
probe_runner_refuses_the_countless_suite_as_a_clean_negative() {
  have_runner "so the one invocation a leaf is told to use for a single suite cannot be asked what a countless suite earns" || return
  direct "$RUNNER" "$FIXTURE_PATH"
  [[ "$direct_code" == 1 ]] ||
    problems+=("want exit 1 from the runner over a suite that died without its count line — the suite ran and the tree under it is not green — got $direct_code, and it said: $(flat "$direct_out")")
  blames "$direct_out" "$FIXTURE_NAME" ", so its refusal does not say which suite died"
}

# 13. The direct invocation's verdict on the deliberately partially-dead fixture is a clean
#     negative, named — the guard pinned against that fixture run directly, and not only through
#     the `make test` target cases 1 to 8 ask of (criterion 5 of #418). The fixture is the one
#     case 1 hands the recipe, since what is being pinned is that the shape #157 found — asserts
#     a while, dies, still exits 0 — cannot come back green however a leaf reached it.
name="the partially-dead fixture run directly through the suite runner is refused as a clean negative, named"
problems=()

probe_fixture_dies_quietly
probe_runner_refuses_the_countless_suite_as_a_clean_negative

# 14. The pipeline-fed matches above answer from the text they read, not from the writer
#    feeding them (#422). A probe that folds a document through a pipeline and asserts on
#    that pipeline's status asks two questions at once: what the text says, and whether the
#    writer survived to EOF. On a glibc pipe a reader that leaves early closes it under a
#    writer with bytes still to push, the writer dies of SIGPIPE, `pipefail` hands that 141
#    up as the pipeline's status, and the assertion is inverted — green on this Mac, where
#    BSD buffering makes the writer need one write, and red on CI. That is how #418 was lost
#    in this very suite. So the preemption is injected rather than raced for: `plain`, the
#    fold case 5's probe reads its document through, is replaced by one that writes the same
#    bytes and then returns 141, the status a writer killed by SIGPIPE leaves, and the probe
#    must reach the same verdict as it does with the fold intact — on a document that carries
#    both facts and on one that carries neither.
name="the pipeline-fed matches give the same verdict on a matching and a non-matching input when the writer is preempted"
problems=()

# verdict <CLAUDE.md path> — what the pipeline-fed probe collects for one document: the count
# first, then one line per problem, so two runs compare as text. Both `problems` and `idiom`
# are declared local here, so the probe fills this function's copies rather than the case's.
verdict() {
  local CLAUDE_MD="$1" idiom="" problems=()
  probe_idiom_records_the_check
  printf '%s\n' "${#problems[@]}" "${problems[@]}"
}

unpreempted="$(declare -f plain)"
barren="$(mktemp)" || {
  problems+=("could not write a document carrying neither fact, so half the criterion went unasked")
  barren=/dev/null
}
printf '## Testing idiom\nSuites live beside the scripts they cover and match the house style.\n\n## Next\n' > "$barren"

honest_match="$(verdict "$CLAUDE_MD")"
honest_miss="$(verdict "$barren")"
plain() { tr -d '*`' | tr '[:upper:]' '[:lower:]'; return 141; }
preempted_match="$(verdict "$CLAUDE_MD")"
preempted_miss="$(verdict "$barren")"
eval "$unpreempted"
rm -f "$barren"

if [[ "$honest_match" != 0 ]]; then
  problems+=("with the fold intact the probe already objects to CLAUDE.md (${honest_match%%$'\n'*} problems), so a verdict that survives preemption would only be two wrong answers agreeing")
fi
if [[ "${honest_miss%%$'\n'*}" == 0 ]]; then
  problems+=("with the fold intact the probe accepts a document carrying neither fact, so a verdict that survives preemption would prove nothing")
fi
if [[ "$preempted_match" != "$honest_match" ]]; then
  problems+=("a preempted writer changes the pipeline-fed verdict on a matching input: ${honest_match%%$'\n'*} problems become ${preempted_match%%$'\n'*}")
fi
if [[ "$preempted_miss" != "$honest_miss" ]]; then
  problems+=("a preempted writer changes the pipeline-fed verdict on a non-matching input: ${honest_miss%%$'\n'*} problems become ${preempted_miss%%$'\n'*}")
fi

report "$name"

# 15. The repair of #524 left the refusal where it was (#524). Its count-line check now reads
#     the suite's last line to EOF rather than leaving at the first match, and the one thing
#     such a rewrite can quietly change is WHICH line it reads: a check that came to search the
#     whole output would pass a suite that printed its count line and then kept going, since
#     the line it asks for is in there somewhere. So the suite handed to the recipe here does
#     exactly that — reaches a count line reporting nothing failed, prints one more line, exits
#     0 — and the answer owed is the one the recipe gave before the repair: a non-zero exit and
#     the refusal line, word for word, naming it. Written into a scratch tree beside a copy of
#     the committed Makefile, the way case 3 adds a suite, so nothing here globs it.
name="make test still fails a suite whose last line is not its count line, naming it exactly as before the repair (#524)"
problems=()

trailing_tree="$(mktemp -d)" || {
  problems+=("could not make a scratch tree to hold the suite, so the criterion went unasked")
  trailing_tree=""
}
if [[ -n "$trailing_tree" ]]; then
  trailing_name='count-then-chatter.test.sh'
  mkdir -p "$trailing_tree/$TESTS_DIR"
  cp "$MAKEFILE" "$trailing_tree/Makefile"
  printf '#!/bin/sh\necho "3 passed, 0 failed"\necho "one more line after the count"\nexit 0\n' \
    > "$trailing_tree/$TESTS_DIR/$trailing_name"
  chmod +x "$trailing_tree/$TESTS_DIR/$trailing_name"

  trailing_out="$(make -C "$trailing_tree" test 2>&1)" && trailing_code=0 || trailing_code=$?
  [[ "$trailing_code" != 0 ]] ||
    problems+=("want 'make test' to fail a suite whose last line is not its count line; it exited 0 and said: $(flat "$trailing_out")")
  grep -Fx "$trailing_name$GUARD_MESSAGE" <<< "$trailing_out" > /dev/null ||
    problems+=("want the line '$trailing_name$GUARD_MESSAGE' in the run's output; it said: $(flat "$trailing_out")")
  rm -rf "$trailing_tree"
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

#!/usr/bin/env bash
# Unit tests for the docs guard suite's own case filter — like hermetic-suites.test.sh and
# workflow-timeouts.test.sh this suite has no single script as its subject: its subject is
# another suite, projects/docs/tests/build-guards.test.sh, and the only way to ask what that suite
# does with an environment variable is to run it as a child process.
# Zero-dependency plain-shell asserts, same idiom as workflow-timeouts.test.sh.
#
# Why this exists (issue #119): every developer and verifier leaf on a docs issue ran
# `make docs-test` one to three times, at ~140 s a run, because the target test and the
# full suite resolve to the same command — build-guards.test.sh builds a sandbox and a
# page per case, twenty-eight of them, and had no way to run one. The 140 s of silence is
# also what supervise.sh's heartbeat sees.
#
# Contract under test:
#   ONLY=<substring> projects/docs/tests/build-guards.test.sh runs the cases whose name contains
#   <substring> and no others — so it exits 0, reports exactly those cases in its count
#   line, and comes back in seconds rather than in the minutes the whole suite takes.
#
# The pin lives beside the suite it is about, under `make docs-test`, and not under `make
# test`. It was under `make test` for a day, where it cost every veri leaf ~17 s on every
# run of the suite to defend a docs tool; the docs are not functional and are brought up
# to date on their own cadence (ADR 0016), so nothing about them rides in veri's own
# development cycle. `make merge-gates` runs it for any change under projects/docs/tests/, and so
# for any change to the suite it pins. It costs ~18 s: three sandboxed page builds for the
# filter and ok-line cases (~4 s), and one whole run of merge-gates.test.sh (~14 s) for the
# case that asks whether `make docs-test` still fails the way it did before the filter
# existed. That suite has no filter of its own, so the last case pays for all eleven of its
# cases; the alternative is not observing the claim at all.
#
# Case 5 widens the subject from that suite to the target that runs it: not what `make
# docs-test` does with one suite's cases, but which suites it runs at all. It belongs here
# rather than in a suite of its own for the reason it is about — a new file under
# projects/docs/tests/ is run by nothing until the Makefile says so, so a suite added to pin that
# could not be the thing that pins it.
#
# `make docs-test` runs this suite, and cases 4 and 5 run `make docs-test` over copies of
# the tree. Neither recurses. Case 4's copy is sabotaged so that its first recipe line,
# build-guards.test.sh, fails, and make stops at the first recipe line that fails, so the
# copy never reaches this suite — it would recurse one level only if build-guards stopped
# failing over the sabotage, which is exactly what case 4 then reports. Case 5's copy
# carries no suite but its own one-line fixture, so there is nothing there to recurse into.
#
# Run: projects/docs/tests/docs-guard-filter.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
SUITE="$ROOT/projects/docs/tests/build-guards.test.sh"
pass=0 fail=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# The case this asks for by name, and what the suite must then report. A fixture, not a
# claim about that case: it is the cheapest one — one sandbox and one build, no git history
# — and case 4 below reuses it, so it also has to be a case that expects the build to
# SUCCEED, which is what lets a broken build turn it red. Named once here so a rename over
# in build-guards.test.sh has one place to be followed.
# 'baseline builds' and not 'builds': the last case of that suite is "the committed page is
# the one this tree builds", so the shorter substring would match two cases and this would
# be asserting something else.
ONLY_CASE='baseline builds'
ONLY_COUNT='1 passed, 0 failed'

# The ceiling a filtered run has to come back inside. One sandboxed build is ~4 s and the
# unfiltered suite is ~140 s, so anything in between separates them; 30 s is far enough
# above the one build to survive a loaded machine and far enough below the whole suite that
# a run which quietly builds the other twenty-seven sandboxes cannot slip under it.
LIMIT=30

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

# kill_tree <pid> — end that process and everything it started, the way supervise.sh:66
# does: TERM to the whole process group first, so the suite's own EXIT trap runs and takes
# its sandboxes with it, then KILL after a grace for a child that ignored it. Each signal
# goes to the group and falls back to the bare process, for a launch that never became a
# group leader.
kill_tree() {
  local pid="$1"
  kill -TERM -"$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null
  for _ in 1 2 3 4 5; do kill -0 "$pid" 2>/dev/null || return 0; sleep 0.4; done
  kill -KILL -"$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
}

# run_filtered <only> — run the guard suite with ONLY=<only> under a deadline, and set the
# three things a case then asks about: `code`, its exit status; `elapsed`, the seconds it
# took; and `report_text`, everything it printed. Publishing them as variables is the same
# protocol `report` already uses for `problems` — the caller reads them where it stands.
#
# It owns its scratch file rather than being handed one: where the output is parked is
# nobody's business but this function's, and a caller that passes a path and then has to
# remember to read that same path back is two halves that can get out of step. One path
# reused across calls is enough — the redirect truncates it, and each caller reads it before
# the next run overwrites it.
#
# The deadline is the whole point of running the suite as a background job rather than
# inline: the failure this case exists to catch is a suite that ignores ONLY and builds
# everything, and unbounded that failure costs 140 s every time `make test` runs while the
# filter is still missing. Killed at the ceiling it costs 30 s and reports a non-zero exit,
# which is a truthful red either way.
#
# Launched in its own process group (job-control monitor mode, as supervise.sh does) so the
# deadline reaches the python build the suite is inside and not just the shell wrapping it.
run_filtered() {
  local only="$1" pid start out="$WORK/run.txt"
  set -m
  ONLY="$only" "$SUITE" >"$out" 2>&1 &
  pid=$!
  set +m
  start=$SECONDS
  while kill -0 "$pid" 2>/dev/null; do
    if (( SECONDS - start >= LIMIT )); then
      kill_tree "$pid"
      break
    fi
    sleep 1
  done
  wait "$pid" && code=0 || code=$?
  elapsed=$((SECONDS - start))
  report_text="$(cat "$out" 2>/dev/null)"
}

# in_time <what kind of run> — the deadline probe both cases end on, appended to `problems`
# when the run hit the ceiling rather than coming back inside it.
#
# Both cases make that claim for the same reason, so the reason is written here once: a
# suite that ignored ONLY goes on to build the sandboxes it was not asked for, and is still
# building them when kill_tree reaches it. Spelled out per case it read as two probes with
# the consequence reworded, which invites the next case to reword it again.
#
# It reads `elapsed` where run_filtered left it, the way the probes around it read `code`
# and `report_text`, and appends to the caller's `problems` — both are the protocol this
# suite already runs on rather than anything this function introduces.
in_time() {
  (( elapsed < LIMIT )) ||
    problems+=("want a $1 run back inside ${LIMIT}s, got ${elapsed}s — it built cases nothing asked for")
}

# exits_clean <the filter that was asked for> — the exit-status probe the two matching-run
# cases open on, appended to `problems` when the suite came back non-zero.
#
# Written once for the same reason in_time is: both cases name a filter whose every matching
# case passes in this tree, so for both a non-zero exit is the guard suite failing and not
# the claim under test. Spelled out per case it read as two probes with that consequence
# reworded, which invites the next case to reword it again.
#
# Case 2 is not a caller. It wants exit 3, and that code is the whole of what it claims
# rather than a condition it shares — a filter matching nothing is the one run where coming
# back 0 is the failure.
exits_clean() {
  [[ "$code" == 0 ]] ||
    problems+=("want exit 0 from ONLY='$1' $SUITE — the cases it names pass in this tree; got $code after ${elapsed}s")
}

# 1. The contract above, and all three of its halves in one case, because no two of them
#    are worth anything apart. A suite that ignores ONLY and runs everything is green on
#    "exited 0"; one that runs the matching case and then the rest of them is green on
#    "reported 1 passed"; and a run that came back in two seconds having done nothing at
#    all is green on the clock. Only the three together say the filter ran that case, ran
#    no other, and skipped the twenty-seven builds it did not need.
name="ONLY='$ONLY_CASE' runs that one case of build-guards.test.sh and nothing else, in seconds"
problems=()
run_filtered "$ONLY_CASE"
exits_clean "$ONLY_CASE"
[[ "$report_text" == *"$ONLY_COUNT"* ]] ||
  problems+=("want '$ONLY_COUNT' in its output — the matching case and no other; got: $(printf '%s' "$report_text" | tail -3 | tr '\n' '/')")
in_time filtered
report "$name"

# 2. A filter that matches nothing is the typo path, and it is the one case where a silent
#    green is actively dangerous: every case skips, nothing is asserted, and a suite that
#    ends `[[ $fail -eq 0 ]]` exits 0 — so a leaf that mistyped its ONLY reads "the guards
#    pass" off a run that guarded nothing. Exit 3 is the code every veri script uses for
#    "nothing to do" (CLAUDE.md: exit codes are the API), which the conductor already tells
#    apart from a real negative.
#
#    Three probes, for the three halves of the step: the code, the message that says which
#    filter found nothing, and the claim that it ran no case. The last is pinned twice over
#    because either half alone is cheap to fake — a run back inside the ceiling could still
#    have built one sandbox, and a "0 passed" line could still be printed by a run that
#    built all twenty-eight and skipped the counting. The message is matched
#    case-insensitively on "no case" plus the filter itself: the wording is the
#    implementer's, but it has to name what was asked for, or it cannot be acted on.
NO_MATCH='no-such-case-zzz'
name="ONLY='$NO_MATCH' matches no case: exit 3, says so, and runs nothing"
problems=()
run_filtered "$NO_MATCH"
lowered="$(printf '%s' "$report_text" | tr 'A-Z' 'a-z')"
[[ "$code" == 3 ]] ||
  problems+=("want exit 3 — nothing to do — from ONLY='$NO_MATCH' $SUITE, got $code after ${elapsed}s")
[[ "$lowered" == *"no case"* && "$report_text" == *"$NO_MATCH"* ]] ||
  problems+=("want it to say no case matched '$NO_MATCH'; got: $(printf '%s' "$report_text" | tail -3 | tr '\n' '/')")
printf '%s\n' "$report_text" | grep -Eq '[1-9][0-9]* passed' &&
  problems+=("want no case run at all; got a count claiming passes: $(printf '%s' "$report_text" | tail -1)")
in_time no-match
report "$name"

# 3. The other half of #119: the suite printed only failures and a final count, so reading
#    what one case did meant running the whole thing again through grep — and 140 s of
#    silence is also all supervise.sh's heartbeat sees. Every passing case has to announce
#    itself as it passes, `ok - <name> (<n>s)`, beside the FAIL lines that were already
#    there.
#
#    Two cases and not one, because "one line per case, in order" is not a claim a single
#    case can carry: a suite that prints one ok line for the whole run, or prints them in
#    whatever order it finishes, is green on any one-case run. 'expands intact' is the
#    cheapest pair that shares a substring — two `accepts` cases, a bare sandbox and a page
#    each, no git history — and their names are listed here in the order build-guards.test.sh
#    invokes them: the two cases of its case 6, the expansion-guard regression, brace-heavy
#    first and nested-brace second. That is the order the output has to be in. Named rather
#    than cited by line, because a line number in build-guards.test.sh is stale the next time
#    anything is inserted above it.
#
#    The probe reads the ok lines back through a sed that only matches the full shape,
#    `ok - ` then the name then a parenthesised whole-number seconds, and compares the names
#    it extracted against the two wanted — as one string, so it pins all three halves at
#    once: the format (a line in any other shape yields no name and drops out), the order,
#    and that there is exactly one line per passing case and no other.
OK_FILTER='expands intact'
OK_CASES=('brace-heavy display expands intact' 'nested-brace display expands intact')
name="every passing case prints one 'ok - <name> (<n>s)' line, in order"
problems=()
run_filtered "$OK_FILTER"
exits_clean "$OK_FILTER"
got_oks="$(printf '%s\n' "$report_text" | sed -n 's/^ok - \(.*\) ([0-9][0-9]*s)$/\1/p')"
want_oks="$(printf '%s\n' "${OK_CASES[@]}")"
[[ "$got_oks" == "$want_oks" ]] ||
  problems+=("want one 'ok - <name> (<n>s)' line per passing case, in order: $(printf '%s' "$want_oks" | tr '\n' '/'); got: $(printf '%s' "$got_oks" | tr '\n' '/')")
in_time ok-line
report "$name"

# 4. and none of #119 is allowed to have cost `make docs-test` its exit code, which is the
#    whole of what a human, a merge gate and CI read off that target. Both halves of the
#    work above sit on the path to it: `selected` returns 0 for a skipped case, so a suite
#    that let a case through and never ran it counts nothing; `passed` moves the pass
#    counter; and the `ran`/exit-3 tail now returns before `[[ $fail -eq 0 ]]` is ever
#    reached. Any of those going wrong ends in the same place — a suite that prints its
#    FAIL lines and exits 0 — and from the Makefile that is indistinguishable from green.
#
#    So this runs the real target, through make, over a tree where a case genuinely fails.
#    The sabotage is build-guards' own unknown-reference mutator — one {{p-id|…}} in
#    projects/docs/wt/commentary.py misspelt into an id no entry has — applied to the ROOT that
#    suite copies its sandboxes from, so the reference guard refuses the build that
#    ONLY_CASE expects to succeed. A copy and not this tree: the failure has to be real,
#    and this tree has to stay green. Filtered to the one case, so the whole probe costs
#    one refused build.
#
#    It used to append an uncovered line to a script instead, which stopped being a
#    failure at all in issue #125: a line no commentary chunk claims is now debt the page
#    carries and reports. The typo is the guard that reversal deliberately left fatal —
#    debt is prose somebody has not written yet, a dead reference is a mistake — so it is
#    the sabotage least likely to stop being one under this suite's feet.
#
#    A non-zero make is not on its own the claim, and this is worth spelling out because
#    the loose version of this case passes over a suite whose exit status has been broken
#    outright: make stops at the first recipe line that fails, so when build-guards exits 0
#    over a FAIL it simply runs on to merge-gates.test.sh, which is failing too in a tree
#    whose page will not build — and make comes back non-zero having been told nothing by
#    the case that was supposed to report. So the exit status the Makefile actually consumes
#    is pinned where it is produced: the guard suite itself, run directly over the same
#    sabotaged tree, has to come back 1 — a clean negative, the leaf ran and failed — and
#    not 2 or 3, which in this repo mean no answer was obtained and nothing was there to do
#    (CLAUDE.md: exit codes are the API). The `FAIL - <name>` line beside it says the
#    failure reported is that case's and not a filter that matched nothing, and the make
#    run then says the target still passes that status on.
#
#    The step's other half is merge-gates.test.sh, the second suite `make docs-test` runs.
#    It is downstream of every edit to the guard suite without looking like it — `repo()`
#    copies projects/docs/tests wholesale into each sandbox repository it builds, and one of its
#    its cases asserts on what a change to the guard suite owes a merge. Its exit code is
#    the claim, and the count line beside it: eleven cases that all passed and zero cases
#    run both end `[[ $fail -eq 0 ]]` and exit 0, so a green count with a non-zero pass
#    figure is what separates them. Run with ONLY cleared, because that suite has no filter
#    today and an ambient ONLY must not be what decides whether it ran anything.
name="a failing case still makes 'make docs-test' exit non-zero, and merge-gates.test.sh still passes"
problems=()
sab="$WORK/sabotaged"
mkdir -p "$sab/projects/docs" "$sab/skills/tdd"
cp "$ROOT/projects/docs/Makefile" "$sab/projects/docs/"
cp "$ROOT/projects/docs/build-walkthrough.py" "$sab/projects/docs/"
cp -R "$ROOT/projects/docs/wt" "$sab/projects/docs/wt"
rm -rf "$sab/projects/docs/wt/__pycache__"
cp -R "$ROOT/projects/docs/tests" "$sab/projects/docs/tests"
rm -f "$sab"/projects/docs/tests/{docs-guard-filter,lane-insulation,merge-gates}.test.sh
cp -R "$ROOT/skills/tdd/scripts" "$sab/skills/tdd/scripts"
sed -i.bak 's/{{p-strict|set -euo pipefail}}/{{p-stirct|set -euo pipefail}}/' \
  "$sab/projects/docs/wt/commentary.py" && rm -f "$sab/projects/docs/wt/commentary.py.bak"
grep -q 'p-stirct' "$sab/projects/docs/wt/commentary.py" ||
  problems+=("the sabotage did not land: no {{p-strict|set -euo pipefail}} in projects/docs/wt/commentary.py to misspell")
sab_out="$(ONLY="$ONLY_CASE" "$sab/projects/docs/tests/build-guards.test.sh" 2>&1)" && sab_code=0 || sab_code=$?
[[ "$sab_code" == 1 ]] ||
  problems+=("want exit 1 — a clean negative — from ONLY='$ONLY_CASE' build-guards.test.sh over a tree where that case fails; got $sab_code: $(printf '%s' "$sab_out" | tail -2 | tr '\n' '/')")
[[ "$sab_out" == *"FAIL - $ONLY_CASE"* ]] ||
  problems+=("want a 'FAIL - $ONLY_CASE' line — the failure reported has to be that case's; got: $(printf '%s' "$sab_out" | tail -3 | tr '\n' '/')")
make_out="$(ONLY="$ONLY_CASE" make -C "$sab/projects/docs" test 2>&1)" && make_code=0 || make_code=$?
[[ "$make_code" != 0 ]] ||
  problems+=("want a non-zero exit from ONLY='$ONLY_CASE' make docs-test over a tree where that case fails; got 0: $(printf '%s' "$make_out" | tail -2 | tr '\n' '/')")
mg_out="$(ONLY= "$ROOT/projects/docs/tests/merge-gates.test.sh" 2>&1)" && mg_code=0 || mg_code=$?
{ [[ "$mg_code" == 0 ]] && printf '%s\n' "$mg_out" | grep -Eq '[1-9][0-9]* passed, 0 failed'; } ||
  problems+=("want exit 0 and a green count over cases that ran from $ROOT/projects/docs/tests/merge-gates.test.sh; got $mg_code: $(printf '%s' "$mg_out" | tail -3 | tr '\n' '/')")
report "$name"

# 5. The other thing a human, a merge gate and CI read off that target: which suites it
#    runs. It used to name them one recipe line each, and a new suite under projects/docs/tests/ was
#    then run by nothing until someone also edited the Makefile — and the edit nobody makes
#    is the one they did not know was owed. `make test` has never had that failure mode; it
#    globs, so a suite runs by existing. That is the claim here, for docs-test, and stated
#    as behaviour rather than as the shape of the recipe: over a tree holding a docs suite
#    this Makefile has never heard of, the target runs it.
#
#    The fixture tree is the Makefile and that one suite — no build-walkthrough.py, no git
#    history, none of the suites projects/docs/tests/ really holds. Partly cost: the real ones are
#    minutes together and this case asks nothing of any of them. Partly recursion, per the
#    note at the top of this file: a copy carrying this suite would run this case again one
#    level down. And partly the claim itself — over a tree where the suites the old recipe
#    named are absent, a recipe that still names them stops on the first missing file and
#    the new suite never runs, while one that globs finds exactly what is there and nothing
#    else.
#
#    Two probes. The marker the fixture writes is the whole claim: a target that exited 0
#    without ever running it is precisely the failure, and an exit status alone cannot tell
#    those apart. Make's own status is the second, for the same reason case 4 pins it
#    passing a 1 through — a discovered suite whose 0 the target swallowed, or whose 0 it
#    turned into something else, is not a suite the target runs.
name="a docs suite the Makefile has never heard of runs under 'make docs-test' by existing"
problems=()
disc="$WORK/discovery"
# The fixture suite's path, named once because three statements have to agree on it: the
# mkdir creates the directory it sits in, the heredoc writes the file and chmod makes it
# runnable. A suite written at one path and made executable at another — or written into a
# directory the glob does not cover — is a fixture the target cannot run, which reads as
# the failure this case is looking for. Same reason ONLY_CASE is named above.
new_suite="$disc/projects/docs/tests/brand-new.test.sh"
marker="$disc/brand-new.ran"
mkdir -p "$(dirname "$new_suite")"
cp "$ROOT/projects/docs/Makefile" "$disc/projects/docs/"
cat > "$new_suite" <<EOF
#!/usr/bin/env bash
# Fixture: a docs suite added to the tree without touching the Makefile. It records that it
# was run and passes; what a real one would assert is beside the point here.
: > "$marker"
echo "1 passed, 0 failed"
EOF
chmod 755 "$new_suite"
disc_out="$(make -C "$disc/projects/docs" test 2>&1)" && disc_code=0 || disc_code=$?
# Both probes end on the same excerpt of the same run, so it is cut once rather than twice:
# whichever of them fails, what the reader needs is what that one make run printed.
disc_tail="$(printf '%s' "$disc_out" | tail -3 | tr '\n' '/')"
[[ -e "$marker" ]] ||
  problems+=("want projects/docs/tests/brand-new.test.sh run by 'make docs-test' with no Makefile edit; it left no marker, so nothing ran it: $disc_tail")
[[ "$disc_code" == 0 ]] ||
  problems+=("want exit 0 from 'make docs-test' over a tree whose one docs suite passes; got $disc_code: $disc_tail")
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

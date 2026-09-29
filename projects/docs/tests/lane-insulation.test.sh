#!/usr/bin/env bash
# Unit tests for which tree the docs lane's own suites are allowed to judge — like
# suite-lanes.test.sh this suite has no script as its subject: its subject is whether a
# suite under projects/docs/tests/ answers for a tree it built or for the tree it happens to be
# running in. Zero-dependency plain-shell asserts, same idiom as the other suites here.
#
# Why this exists (issue #137): `make docs-test` is the test command a /tdd run on a docs
# issue uses, so the conductor reads its baseline off it and refuses to start on a red one.
# A suite that judges THIS tree goes red on events belonging to the other lane — a script
# commit leaving lines no commentary chunk covers, a tag cut with no commit behind it — and
# the docs pool then cannot be drained until somebody rebuilds the page by hand. Observed
# 2026-09-13: #131 added lines inside detect-test-command.sh and docs-owed.test.sh was red
# on main until a prose PR (#142) caught up. A page behind the code is already a
# docs-owed.sh reading and docs-fresh's job at merge time; it is not the generator's
# suite's to fail on.
#
# Contract under test:
#   projects/docs/tests/docs-owed.test.sh passes over a tree whose scripts carry lines no commentary
#   chunk covers. Its zero-debt case is a claim about a tree that suite builds, so how far
#   this repository's own prose has fallen behind its own scripts cannot decide it.
#
#   projects/docs/tests/build-guards.test.sh has no case that judges the committed page at all: asked
#   for one over a tree whose projects/docs/walkthrough.html is not what that tree builds, it reports
#   that nothing matched. The generator's suite answers for the generator.
#
#   projects/docs/tests/build-guards.test.sh run whole over such a tree reaches its count line, and
#   exits non-zero if that line says anything failed. Surviving the run is a separate claim
#   from declining to judge the page: a suite that dies where it stands reports green.
#
# The tree is copied and planted rather than asserted about where it stands, because the
# claim is about some other repository and this one owes no commentary today: a probe run
# here would pass on both sides of the fix and pin nothing. What that copy is, and what it
# deliberately leaves out, is `tree_owing_prose` below.
#
# It costs one copy of those paths and one page build over it, shared by all three cases —
# that build's two streams are what says the plant is really a plant, see `build_over`; then
# one run of docs-owed.test.sh, two filtered runs of build-guards.test.sh with one sandboxed
# build apiece, and one unfiltered run of it. ~215 s measured, some 200 of them that last run
# — the suite's own cost over one tree, and the only thing that can observe it completing.
#
# Run: projects/docs/tests/lane-insulation.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
pass=0 fail=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# The two suites under test — one case on docs-owed.test.sh, two on build-guards.test.sh — and
# the script every case plants a coverage gap in. Named once each because the failure messages
# quote them and the probes act on them, and a case that planted the gap in one script while
# naming another in its complaint would send the reader to the wrong file. Both here rather
# than one at the top and one beside the case that runs it, and neither called just `SUITE`,
# because this file's subject is the pair: the question it asks — which tree may a docs-lane
# suite judge — is asked of docs-owed.test.sh and of build-guards.test.sh in the same words,
# and a reader comparing the two answers should meet both names at once. The bare script name
# too: the build reports debt by basename.
OWED_SUITE='projects/docs/tests/docs-owed.test.sh'
GUARDS_SUITE='projects/docs/tests/build-guards.test.sh'
SCRIPT='skills/tdd/scripts/classify-bail.sh'
SCRIPT_NAME="${SCRIPT##*/}"

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

# flat <text> — one line of it, for a failure message. Newlines become slashes so something
# multi-line — a build's stderr, a suite's tail — is still readable inside an indented
# problem line.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# tail_of <output> — how a run under test ended, flattened onto one problem line: its last
# few lines, which is where a suite's own count line and whatever stopped it are. Every
# probe below that reports an unexpected exit code quotes this, so it is one helper rather
# than six copies of `flat "$(tail -N <<< "$out")"` — nested twice, that is most of a dense
# problem line, and its N had drifted to 3 in four of them and 5 in the other two while
# meaning the same thing in all six. Five lines, the wider of the two the copies used.
tail_of() { flat "$(tail -5 <<< "$1")"; }

# tree_owing_prose — a disposable copy of this tree with $SCRIPT grown past the last line
# any commentary chunk claims, printed as a path. Named, and out of the case body, so the
# case reads as the three steps it is: build the tree, prove the plant is really a plant,
# run the suite over it — the same shape `repo` gives the suite under test.
#
# projects/docs/, skills/ and the Makefile are what that suite reads; the whole tree is not copied
# because in the primary clone .tdd/wt/ holds this repository's worktrees and cp -R would
# descend into them. The gap is planted at the END of the script: a chunk claims a line
# range, so a line inside the file's existing length may already be claimed, while the
# lines past its end can be claimed by nothing.
#
# Built once and handed to every case that asks: all three cases below want the same tree, and
# a second copy on top of the first would land projects/docs/ inside projects/docs/ and append the plant twice.
#
# Each case holds the path it returns as `planted`, for the reason run_in_copy names its
# three inputs: the probes are dense single lines several lines below the call, and a reader
# meeting `build_over "$planted"` or `cmp -s "$BUILT" "$planted/projects/docs/walkthrough.html"` there
# is told what tree is being asked, rather than a letter to go and resolve.
tree_owing_prose() {
  local planted="$WORK/tree"
  [[ -d "$planted" ]] && { printf '%s' "$planted"; return 0; }
  mkdir -p "$planted/projects"
  cp -R "$ROOT/projects/docs" "$planted/projects/docs"
  cp -R "$ROOT/skills" "$planted/skills"
  cp "$ROOT/projects/docs/Makefile" "$planted/projects/docs/"
  rm -rf "$planted/projects/docs/wt/__pycache__"
  printf '\n# a line this tree grew after its prose was written\n# and a second one\n' >> "$planted/$SCRIPT"
  printf '%s' "$planted"
}

# build_over <dir> — one page build over <dir>, its stdout left in $BUILT and its stderr in
# $BUILD_ERR. Memoized on $BUILT for the same reason tree_owing_prose is memoized on its
# directory: all three cases probe the plant by asking the generator about that one tree, and
# the two things they want are the two streams of a single build — the coverage debt it reports
# on stderr (cases 1 and 3), and the page it emits on stdout (case 2). Asked once per case it
# would cost two more builds to learn the same two facts about the same bytes.
#
# --stdout, so no probe ever writes the projects/docs/walkthrough.html a case then compares against.
# The exit code is nobody's claim here: a build that died leaves an empty page and an empty
# debt report, and both probes read that as the plant not being a plant, which is what a
# broken fixture should say.
BUILT="$WORK/built.html"
BUILD_ERR="$WORK/built.err"
build_over() {
  [[ -f "$BUILT" ]] && return 0
  ( cd "$1" && python3 projects/docs/build-walkthrough.py --stdout >"$BUILT" 2>"$BUILD_ERR" )
}

# probe_plant_is_debt <dir> — the plant is only a plant if the build reads it as debt, and the
# build is where docs-owed.sh reads coverage from too, so this asks the same question the
# subjects ask, of the copy, rather than re-deriving the coverage rule here. Named once
# because two cases make exactly this probe and each would be vacuous without it in a
# different way: a renamed script or a commentary chunk that grew to the end of the file
# leaves case 1 passing over a tree that owes nothing — the tree it already passes over today
# — and leaves case 3 watching the suite reach its count line for want of any stderr to
# misread. One wording for one claim, so a reader who has met it once need not check the
# second copy still says the same thing.
#
# Off the memoized build, so both cases pay for one. Appends to `$problems` the way report()
# reads it.
probe_plant_is_debt() {
  build_over "$1"
  grep -Fq "owed: $SCRIPT_NAME" "$BUILD_ERR" ||
    problems+=("the case is vacuous: appending to $SCRIPT left no coverage gap for the build to report; it said: $(flat "$(cat "$BUILD_ERR")")")
}

# run_in_copy <dir> <suite> [<filter>] — run <suite> out of the planted copy at <dir>,
# leaving its output, both streams, in $out and its exit code in $code. Every observation
# this file makes is one of these: the whole question is what a docs-lane suite says when
# it is run somewhere other than where it lives, so the runs are the probes.
#
# Named because every one of those runs asserts on the exit code, and the incantation that
# records it is the one piece of bash here a reader can get wrong without the suite noticing:
# `$?` is gone the moment the next command runs, so the `&& code=0 || code=$?` tail is the
# whole of the capture. A copy of it that dropped the tail would leave `$code` holding the
# PREVIOUS run's answer — the case below asserting exit 3 would pass over a suite that
# exited 0, because the liveness probe before it left a 3 behind on a bad day. One door,
# so there is one place to get it right.
#
# It also retires the second pair of variables: case 2 runs the same suite twice and had
# to call the first pair `live`/`live_code` to keep the second from clobbering it, which
# read as two different kinds of result when they are two runs of one kind. Each probe
# now reads $out and $code immediately after its own call, so the reuse is the point.
#
# The three inputs are named on their own line, as `report` names its one, because the run
# itself is a single dense line and `"$1/$2"` there reads as two anonymous words rather than
# a path into the copy. ONLY is the filter build-guards.test.sh reads (see `selected`
# there); `${3-}` is empty when the caller passed nothing, and a suite that has no filter
# never looks at the variable.
run_in_copy() {
  local dir="$1" suite="$2" filter="${3-}"
  out="$(ONLY="$filter" "$dir/$suite" 2>&1)" && code=0 || code=$?
}

# 1. A script gains lines nobody has written prose for, which is what a merged development
#    PR leaves behind every time (#125: the build carries an uncovered line as debt instead
#    of refusing to emit the page, and a change under skills/ owes no rebuild). The docs
#    lane's suite for the tool that REPORTS that debt must still pass, because the debt is
#    the tool's subject and not its verdict on the repository it lives in.
#
#    Exit code and the count line together are the claim, for the reason case 4 of
#    docs-guard-filter.test.sh spells out: a suite with zero cases run and a suite with
#    every case passing both exit 0, and only one of them is evidence.
name="$OWED_SUITE passes over a tree whose scripts carry lines no commentary chunk covers"
problems=()
planted="$(tree_owing_prose)"

probe_plant_is_debt "$planted"

run_in_copy "$planted" "$OWED_SUITE"
{ [[ "$code" == 0 ]] && grep -Eq '[1-9][0-9]* passed, 0 failed' <<< "$out"; } ||
  problems+=("want $OWED_SUITE green over a tree owing prose for $SCRIPT_NAME — a script commit is a development-lane event and must not turn the docs lane red; got $code: $(tail_of "$out")")

report "$name"

# 2. The same lane, the other suite under projects/docs/tests/ that judged the tree it was running in
#    rather than one it built: the generator's own. `page_is_current` asked whether
#    projects/docs/walkthrough.html is the fixpoint of a build over this tree, and `page_checks_out`
#    ran check-walkthrough.py over the same committed bytes — so a tag cut in another
#    worktree, or a script commit nobody has written the prose for yet, turned `make
#    docs-test` red with nothing whatever wrong with the generator. That the page is behind
#    is already docs-owed.sh's reading and `make docs-fresh`'s refusal at merge; it is not a
#    verdict the suite for the tool that BUILDS the page gets to reach.
#
#    So: asked over such a tree for its cases about the committed page, the suite has none to
#    run, and says so — exit 3, the code every veri script uses for nothing to do (CLAUDE.md:
#    exit codes are the API) and the one its own no-match path already returns, pinned by
#    case 2 of docs-guard-filter.test.sh.
#
#    Filtered rather than run whole, and the filtered run is the whole of the observation and
#    not a corner of it: every other case in that suite builds its own sandbox and judges what
#    came out of it, so none of them can see this tree's page at all. Watching the other
#    fifty-four pass costs ~240 s of the ~250 s that suite takes, and says nothing this does
#    not. The filter is the fixture, like docs-guard-filter's ONLY_CASE: it names the cases
#    the fix removes, so a rename rather than a removal would read here as a removal.
PAGE_FILTER='committed page'
LIVE_CASE='baseline builds'
name="$GUARDS_SUITE has no case that judges the committed page, over a tree whose page is behind its scripts"
problems=()
planted="$(tree_owing_prose)"

# The tree has to be one a case judging the committed page would FAIL over, or exit 3 and a
# green run are the same observation and this pins nothing. The same build case 1 probed the
# plant with, read off its other stream: ask the copy the question the removed case asked —
# is the committed page what this tree builds — rather than re-deriving an answer here.
build_over "$planted"
cmp -s "$BUILT" "$planted/projects/docs/walkthrough.html" &&
  problems+=("the case is vacuous: the committed page in the copy is already what that tree builds, so a case judging it would pass there anyway")

# And the suite has to be able to run in the copy at all, or exit 3 could be a suite that
# dies before it reaches any case. The cheapest case it has — one sandbox, one build, no git
# history — is the same fixture docs-guard-filter.test.sh uses for that.
run_in_copy "$planted" "$GUARDS_SUITE" "$LIVE_CASE"
{ [[ "$code" == 0 ]] && grep -Fq '1 passed, 0 failed' <<< "$out"; } ||
  problems+=("want ONLY='$LIVE_CASE' $GUARDS_SUITE green in the copy — without it exit 3 below says nothing; got $code: $(tail_of "$out")")

# The claim. The message beside the code, because exit 3 alone could come from anywhere in
# the suite: it has to be the no-match path, which names the filter that found nothing. The
# wording is the implementer's, so only "no case" and the filter itself are matched, the way
# case 2 of docs-guard-filter.test.sh matches them.
run_in_copy "$planted" "$GUARDS_SUITE" "$PAGE_FILTER"
lowered="$(tr 'A-Z' 'a-z' <<< "$out")"
[[ "$code" == 3 ]] ||
  problems+=("want exit 3 — no case to run — from ONLY='$PAGE_FILTER' $GUARDS_SUITE over a tree whose committed page is stale; got $code: $(tail_of "$out")")
[[ "$lowered" == *"no case"* && "$out" == *"$PAGE_FILTER"* ]] ||
  problems+=("want it to say no case matched '$PAGE_FILTER' — the generator's suite must judge no committed page; got: $(tail_of "$out")")

report "$name"

# 3. The same suite over the same tree, asked the other question: not which cases it declines
#    to run, but whether it survives the run at all. A tree owing prose makes the build talk
#    on stderr — a `COMMENTARY OWED:` header and one `owed:` line per gap — and the case that
#    counts the build's git processes captures it with 2>&1 and reads the first line as its
#    two numbers, so it gets the word `COMMENTARY` where it wanted a count. Arithmetic on an
#    unset name under `set -u` kills the file where it stands: no count line, and exit 0. So
#    `make docs-test` and the merge gate behind it both report success over a suite whose
#    later cases never ran — this issue's third criterion (a script commit leaving lines
#    uncovered leaves the docs lane green) failing in the one direction nobody watches.
#
#    Unfiltered, and that is the observation rather than an oversight: the tail that prints
#    the count sits after every case, so reaching it IS every case having been reached, and a
#    filtered run would skip past whichever case dies. ~200 s, the suite's own cost over one
#    tree; nothing cheaper can see a suite finish.
#
#    Green is deliberately not the claim. A case may legitimately fail over a tree owing
#    prose, and either answer belongs to the docs lane; what must never happen is the suite
#    claiming success without having reached a verdict. So: the count line is there, and the
#    exit code agrees with what it says.
name="$GUARDS_SUITE runs every case to its count line over a tree whose scripts carry lines no commentary chunk covers"
problems=()
planted="$(tree_owing_prose)"

probe_plant_is_debt "$planted"

# The last count line rather than the first: every `ok - <name>` line above it carries a
# per-case figure, and the suite's own tail is the one that counts cases.
run_in_copy "$planted" "$GUARDS_SUITE"
count="$(grep -Eo '[0-9]+ passed, [0-9]+ failed' <<< "$out" | tail -1)"
if [[ -z "$count" ]]; then
  problems+=("want $GUARDS_SUITE to reach its count line over a tree owing prose for $SCRIPT_NAME — it stopped before its tail, so every case after the one that stopped it never ran; got $code: $(tail_of "$out")")
else
  # Two ways the tail and the exit code can disagree, each spelled as the state it
  # complains about rather than as the state it demands: a branch on what the count says
  # with the assertion inverted inside it has the reader work out which disagreement is
  # being reported, and the report is the whole value of a failing case.
  failed="${count#* passed, }"; failed="${failed% failed}"
  if [[ "$failed" == 0 && "$code" != 0 ]]; then
    problems+=("want exit 0 from $GUARDS_SUITE to agree with its own '$count'; got $code: $(tail_of "$out")")
  elif [[ "$failed" != 0 && "$code" == 0 ]]; then
    problems+=("want a non-zero exit from $GUARDS_SUITE to agree with its own '$count' — a green exit over failing cases is what makes make docs-test and the merge gate behind it report success anyway")
  fi
fi

report "$name"

# 4. The same survival claim, asked of the one case that reads the build's stderr as numbers.
#    ONLY names it, so the run costs one sandboxed build instead of the suite's whole roster,
#    and the count line is still there for a run that died on the way to it.
GIT_BUDGET_FILTER='a build asks git once per script'
name="ONLY='$GIT_BUDGET_FILTER' $GUARDS_SUITE reaches its count line over a tree owing prose"
problems=()
planted="$(tree_owing_prose)"

probe_plant_is_debt "$planted"

run_in_copy "$planted" "$GUARDS_SUITE" "$GIT_BUDGET_FILTER"
{ [[ "$code" == 0 ]] && grep -Fq '1 passed, 0 failed' <<< "$out"; } ||
  problems+=("want ONLY='$GIT_BUDGET_FILTER' $GUARDS_SUITE to reach '1 passed, 0 failed' over a tree owing prose for $SCRIPT_NAME; got $code: $(tail_of "$out")")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

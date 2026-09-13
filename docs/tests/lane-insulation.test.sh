#!/usr/bin/env bash
# Unit tests for which tree the docs lane's own suites are allowed to judge — like
# suite-lanes.test.sh this suite has no script as its subject: its subject is whether a
# suite under docs/tests/ answers for a tree it built or for the tree it happens to be
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
#   docs/tests/docs-owed.test.sh passes over a tree whose scripts carry lines no commentary
#   chunk covers. Its zero-debt case is a claim about a tree that suite builds, so how far
#   this repository's own prose has fallen behind its own scripts cannot decide it.
#
#   docs/tests/build-guards.test.sh has no case that judges the committed page at all: asked
#   for one over a tree whose docs/walkthrough.html is not what that tree builds, it reports
#   that nothing matched. The generator's suite answers for the generator.
#
# The tree is copied and planted rather than asserted about where it stands, because the
# claim is about some other repository and this one owes no commentary today: a probe run
# here would pass on both sides of the fix and pin nothing. What that copy is, and what it
# deliberately leaves out, is `tree_owing_prose` below.
#
# It costs one copy of those paths and one page build over it, both shared by the two cases —
# that build's two streams are what says the plant is really a plant, see `build_over`; then
# one run of docs-owed.test.sh and two filtered runs of build-guards.test.sh, one sandboxed
# build apiece. ~15 s measured, nearly all of it those runs — which are the observation itself.
#
# Run: docs/tests/lane-insulation.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
pass=0 fail=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# The two suites under test — one case each — and the script both cases plant a coverage gap
# in. Named once each because the failure messages quote them and the probes act on them, and
# a case that planted the gap in one script while naming another in its complaint would send
# the reader to the wrong file. Both here rather than one at the top and one beside the case
# that runs it, and neither called just `SUITE`, because this file's subject is the pair: the
# question it asks — which tree may a docs-lane suite judge — is asked of docs-owed.test.sh
# and of build-guards.test.sh in the same words, and a reader comparing the two answers
# should meet both names at once. The bare script name too: the build reports debt by basename.
OWED_SUITE='docs/tests/docs-owed.test.sh'
GUARDS_SUITE='docs/tests/build-guards.test.sh'
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

# flat <text> — one line of it, for a failure message. Newlines become slashes so a suite's
# tail that came back red is still readable inside an indented problem line.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# tree_owing_prose — a disposable copy of this tree with $SCRIPT grown past the last line
# any commentary chunk claims, printed as a path. Named, and out of the case body, so the
# case reads as the three steps it is: build the tree, prove the plant is really a plant,
# run the suite over it — the same shape `repo` gives the suite under test.
#
# docs/, skills/ and the Makefile are what that suite reads; the whole tree is not copied
# because in the primary clone .tdd/wt/ holds this repository's worktrees and cp -R would
# descend into them. The gap is planted at the END of the script: a chunk claims a line
# range, so a line inside the file's existing length may already be claimed, while the
# lines past its end can be claimed by nothing.
#
# Built once and handed to every case that asks: both cases below want the same tree, and a
# second copy on top of the first would land docs/ inside docs/ and append the plant twice.
tree_owing_prose() {
  local d="$WORK/tree"
  [[ -d "$d" ]] && { printf '%s' "$d"; return 0; }
  mkdir -p "$d"
  cp -R "$ROOT/docs" "$d/docs"
  cp -R "$ROOT/skills" "$d/skills"
  cp "$ROOT/Makefile" "$d/"
  rm -rf "$d/docs/wt/__pycache__"
  printf '\n# a line this tree grew after its prose was written\n# and a second one\n' >> "$d/$SCRIPT"
  printf '%s' "$d"
}

# build_over <dir> — one page build over <dir>, its stdout left in $BUILT and its stderr in
# $BUILD_ERR. Memoized on $BUILT for the same reason tree_owing_prose is memoized on its
# directory: both cases probe the plant by asking the generator about that one tree, and the
# two things they want are the two streams of a single build — the coverage debt it reports
# on stderr, and the page it emits on stdout. Asked twice it would cost a second build to
# learn the same two facts about the same bytes.
#
# --stdout, so no probe ever writes the docs/walkthrough.html a case then compares against.
# The exit code is nobody's claim here: a build that died leaves an empty page and an empty
# debt report, and both probes read that as the plant not being a plant, which is what a
# broken fixture should say.
BUILT="$WORK/built.html"
BUILD_ERR="$WORK/built.err"
build_over() {
  [[ -f "$BUILT" ]] && return 0
  ( cd "$1" && python3 docs/build-walkthrough.py --stdout >"$BUILT" 2>"$BUILD_ERR" )
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
d="$(tree_owing_prose)"

# The plant is only a plant if the build reads it as debt, and the build is where
# docs-owed.sh reads coverage from too — so this asks the same question the subject asks,
# of the copy, rather than re-deriving the coverage rule here. Without it a renamed script
# or a commentary chunk that grew to the end of the file would leave the case passing over
# a tree that owes nothing, which is the tree it already passes over today.
build_over "$d"
grep -Fq "owed: $SCRIPT_NAME" "$BUILD_ERR" ||
  problems+=("the case is vacuous: appending to $SCRIPT left no coverage gap for the build to report; it said: $(flat "$(cat "$BUILD_ERR")")")

out="$("$d/$OWED_SUITE" 2>&1)" && code=0 || code=$?
{ [[ "$code" == 0 ]] && grep -Eq '[1-9][0-9]* passed, 0 failed' <<< "$out"; } ||
  problems+=("want $OWED_SUITE green over a tree owing prose for $SCRIPT_NAME — a script commit is a development-lane event and must not turn the docs lane red; got $code: $(flat "$(tail -5 <<< "$out")")")

report "$name"

# 2. The same lane, the other suite under docs/tests/ that judged the tree it was running in
#    rather than one it built: the generator's own. `page_is_current` asked whether
#    docs/walkthrough.html is the fixpoint of a build over this tree, and `page_checks_out`
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
d="$(tree_owing_prose)"

# The tree has to be one a case judging the committed page would FAIL over, or exit 3 and a
# green run are the same observation and this pins nothing. The same build case 1 probed the
# plant with, read off its other stream: ask the copy the question the removed case asked —
# is the committed page what this tree builds — rather than re-deriving an answer here.
build_over "$d"
cmp -s "$BUILT" "$d/docs/walkthrough.html" &&
  problems+=("the case is vacuous: the committed page in the copy is already what that tree builds, so a case judging it would pass there anyway")

# And the suite has to be able to run in the copy at all, or exit 3 could be a suite that
# dies before it reaches any case. The cheapest case it has — one sandbox, one build, no git
# history — is the same fixture docs-guard-filter.test.sh uses for that.
live="$(ONLY="$LIVE_CASE" "$d/$GUARDS_SUITE" 2>&1)" && live_code=0 || live_code=$?
{ [[ "$live_code" == 0 ]] && grep -Fq '1 passed, 0 failed' <<< "$live"; } ||
  problems+=("want ONLY='$LIVE_CASE' $GUARDS_SUITE green in the copy — without it exit 3 below says nothing; got $live_code: $(flat "$(tail -3 <<< "$live")")")

# The claim. The message beside the code, because exit 3 alone could come from anywhere in
# the suite: it has to be the no-match path, which names the filter that found nothing. The
# wording is the implementer's, so only "no case" and the filter itself are matched, the way
# case 2 of docs-guard-filter.test.sh matches them.
out="$(ONLY="$PAGE_FILTER" "$d/$GUARDS_SUITE" 2>&1)" && code=0 || code=$?
lowered="$(tr 'A-Z' 'a-z' <<< "$out")"
[[ "$code" == 3 ]] ||
  problems+=("want exit 3 — no case to run — from ONLY='$PAGE_FILTER' $GUARDS_SUITE over a tree whose committed page is stale; got $code: $(flat "$(tail -5 <<< "$out")")")
[[ "$lowered" == *"no case"* && "$out" == *"$PAGE_FILTER"* ]] ||
  problems+=("want it to say no case matched '$PAGE_FILTER' — the generator's suite must judge no committed page; got: $(flat "$(tail -3 <<< "$out")")")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

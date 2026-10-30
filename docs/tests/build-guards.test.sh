#!/usr/bin/env bash
# Unit tests for docs/build-walkthrough.py — the guards that keep the generated
# walkthrough honest. Zero-dependency plain-shell asserts, same idiom as the
# scripts/tests/*.test.sh suites.
#
# The walkthrough is generated: its code half is read from the real scripts, and its
# prose half lives in docs/wt/commentary.py keyed by line range. Three guards stop that
# arrangement failing silently, and each one exists because the failure actually
# happened during authoring:
#
#   1. coverage    — a script's chunks must claim lines 1..N in order, each line once.
#                    A chunk claiming lines the file does not have, or lines another
#                    chunk already claimed, is a wrong range and still fails the build.
#                    A line NO chunk claims is the half issue #125 reversed: it is debt
#                    the page carries and the build reports, not a failure.
#   2. unknown ref — {{p-id|…}} must name a real reference entry, or the page ships a
#                    dead tooltip.
#   3. expansion   — no {{ref}} may survive into the output. The original matcher used
#                    [^}]* for display text, which silently failed on bash display like
#                    {{p-pipe|"${PIPESTATUS[0]}"}} and truncated {{p-default|${VAR:-default}}}
#                    to "${VAR:-default" — four dead refs and five corrupted ones.
#
# A guard that has never been seen to fire is decoration, so every case below breaks the
# thing on purpose and asserts the build refuses.
#
# Cases 11 and 12 guard something else: not how the build behaves, but the prose it
# carries — a sentence in docs/wt/commentary.py that was wrong once and must not come back,
# and one that has to be there. There is no build behaviour to break on purpose in either,
# so neither has a mutator; they just assert on the page the tree produces as it stands.
#
# Every case runs against a disposable copy of the tree, so the real repo is never
# mutated even if a case aborts — and, since issue #137, never judged either. The subject
# here is the generator, so every claim is about a tree this suite built. Whether the
# committed docs/walkthrough.html is still what this tree builds is not one of them: a
# script commit that leaves lines no commentary chunk claims, or a tag cut in another
# worktree, puts the page behind with nothing whatever wrong with the generator, and
# `make docs-test` is the command a /tdd run on a docs issue reads its baseline off. That
# lag is already a docs-owed.sh reading ("page behind", "tag") and `make docs-fresh`'s
# refusal inside `make merge-gates`, which is what still stops a stale page landing.
#
# Two cases reach past python3 for node: since-mode is a decision the page's own JS makes,
# and nothing in the markup records it. See ask_page, which both go through. node is a
# dependency of reading the page back, never of building or shipping it, and those cases
# fail rather than skip when it is absent.
#
# One bash trap, and it has bitten: a heredoc nested inside a $( ) is scanned for quotes
# THROUGH its body by bash 3.2, so a lone apostrophe in one opens a quote the parser never
# closes and the whole suite dies with "unexpected EOF" before a single case runs. The
# python readers below are all written that way, so an apostrophe there has to be paired,
# or sit inside a double-quoted run where bash reads it as literal — which is the only
# thing keeping the "entry's" in a docstring below from killing the file. The JS questions
# are out of reach of it entirely: ask_page has them written to a file first.
#
# Run: docs/tests/build-guards.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
pass=0 fail=0 ran=0 case_start=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# selected <case name> — true when this run was asked for this case.
#
# Every case below builds its own disposable tree and its own page, twenty-eight of them,
# which is why the whole suite costs ~140 s and why a leaf developing a docs issue paid
# that for the one case it was actually working on: the target test and the full suite
# were the same command (issue #119). `ONLY=<substring>` names the cases to run — the
# match is a substring of the case name, not the whole of it, so a run can ask for a case
# by the fragment that is quick to type.
#
# The guard sits at the top of every assertion, before it reaches for a sandbox, because
# the sandbox and the build ARE the cost: a case that is skipped copies no tree, starts no
# python and asks git nothing. It returns 0 — a skipped case is neither a pass nor a
# failure, and must not move either counter.
#
# The filter is read into a local first so that no filter is one named thing — and so the
# `set -u` safety is in the read, not in `[[ ]]` short-circuiting past an unset `$ONLY`
# before it can be expanded. It stays quoted in the pattern: a filter is a substring to
# find, never a glob to match, so `*` in it means an asterisk.
#
# It also counts what it let through, because this is the one place that knows: a filter
# that matches nothing otherwise ends the suite green over a run that asserted nothing, so
# `ran` is what the tail below turns into exit 3.
#
# And it starts that case's clock, for the same reason: this is the one line every case
# passes through on its way in, before it copies a tree or starts a python. `passed` below
# reads the clock back.
selected() {
  local filter="${ONLY:-}"
  [[ -z "$filter" || "$1" == *"$filter"* ]] || return 1
  ran=$((ran + 1))
  case_start=$SECONDS
}

# passed <case name> — close a case that passed: count it, and say so on one line,
# `ok - <name> (<n>s)`.
#
# The other half of issue #119. The suite used to print only its failures and a final
# count, so a leaf that wanted to know what one case did had to run the whole suite again
# through grep — and the ~140 s of silence in between is also all supervise.sh's heartbeat
# ever sees, which is what a stuck-detection bail on a healthy run is made of. One line as
# each case passes fixes both: the output is a readable per-case record, and it arrives
# while the suite is still working.
#
# The seconds come from `case_start`, stamped by `selected` when this case was let in, so
# the figure is that case's own sandbox-and-build cost and not the elapsed suite. Whole
# seconds: SECONDS is the only clock bash 3.2 has without a subprocess, and per-case
# resolution finer than that buys nothing here.
passed() {
  pass=$((pass + 1))
  echo "ok - $1 ($((SECONDS - case_start))s)"
}

# Which sandbox the assertion helpers below build in. Most cases want the default —
# a bare tree with no .git — so the version layer stays out of the way; the cases that
# exercise it flip this to sandbox_git for the length of one call.
SANDBOX=sandbox

# sandbox — a fresh copy of everything the build reads, printed on stdout
sandbox() {
  local d; d="$(mktemp -d "$WORK/case.XXXXXX")"
  mkdir -p "$d/docs" "$d/skills/tdd"
  cp "$ROOT/docs/build-walkthrough.py" "$d/docs/"
  cp -R "$ROOT/docs/wt" "$d/docs/wt"
  cp -R "$ROOT/skills/tdd/scripts" "$d/skills/tdd/scripts"
  rm -rf "$d/docs/wt/__pycache__"
  printf '%s' "$d"
}

# sandbox_git — the same copy, but a real repository, so `git blame`, `git tag` and the
# rest of the version layer have something to answer with.
#
# The whole tree lands as ONE feat: commit tagged v0.1, which is deliberately the
# poorest history that still turns the version layer on: every script was added by a
# behaviour commit, and every script shipped in the first and only version. A mutator
# can commit more on top before the build runs.
#
# Identity and signing are set on the repo rather than inherited, so the case does not
# depend on — or write to — whatever ~/.gitconfig this machine has.
sandbox_git() {
  local d; d="$(sandbox)"
  git -C "$d" -c init.defaultBranch=main init -q
  git -C "$d" config user.email veri@example.invalid
  git -C "$d" config user.name  veri
  git -C "$d" config commit.gpgsign false
  git -C "$d" config tag.gpgsign false
  git -C "$d" add -A
  git -C "$d" commit -qm 'feat: the walkthrough and the scripts it quotes (#1)'
  git -C "$d" tag -a v0.1 -m 'the first version'
  printf '%s' "$d"
}

# sandbox_check — sandbox_git plus the two files only the CHECKER reads: itself, and the
# SKILL.md whose revise budget its TDD-figure phase is checked against. The build needs
# neither, which is why sandbox() does not copy them.
#
# They land untracked, after the commit: `git blame` is only ever asked about the scripts,
# so committing them would buy nothing but a second commit in every history.
sandbox_check() {
  local d; d="$(sandbox_git)"
  cp "$ROOT/docs/check-walkthrough.py" "$d/docs/"
  cp "$ROOT/skills/tdd/SKILL.md" "$d/skills/tdd/"
  printf '%s' "$d"
}

build() {  # build <dir> -> stdout=page, stderr=problems; returns the build's exit code
  ( cd "$1" && python3 docs/build-walkthrough.py --stdout 2>"$1/err.txt" )
}

# hunk_spans <page> -> how many hunk marks that built page carries
# Two assertions count them for different reasons — tags_git, to claim the page tagged
# exactly the runs it should and no others; hunk_map_git, to claim the inverted map holds
# an entry for every one of them — so the count is one named thing rather than the same
# pipeline written twice.
# Occurrences, not matching lines: grep -o then wc -l, since nothing guarantees two tags
# could not share one output line.
hunk_spans() {
  printf '%s' "$1" | grep -o 'class="l hunk"' | wc -l | tr -d ' '
}

# refuses <name> <expected-substring-in-stderr> <mutator...>
# The mutator runs inside the sandbox dir; the build must then FAIL and say why.
refuses() {
  selected "$1" || return 0
  local name="$1" want="$2"; shift 2
  local d code err; d="$("$SANDBOX")"
  ( cd "$d" && "$@" )
  build "$d" >/dev/null && code=0 || code=$?
  err="$(cat "$d/err.txt" 2>/dev/null)"
  if [[ "$code" != 0 && "$err" == *"$want"* ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    echo "    want: non-zero exit and stderr containing: $want"
    echo "    got:  exit $code"
    printf '%s\n' "$err" | sed 's/^/    | /' | head -6
  fi
}

# accepts <name> <expected-substring-in-page> [mutator...]
accepts() {
  selected "$1" || return 0
  local name="$1" want="$2"; shift 2
  local d code page; d="$("$SANDBOX")"
  [[ $# -gt 0 ]] && ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  if [[ "$code" == 0 && "$page" == *"$want"* ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want the page to contain: $want"
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# omits <name> <substring-that-must-NOT-appear> [mutator...]
# The negative form of accepts: the build must succeed AND not contain this.
omits() {
  selected "$1" || return 0
  local name="$1" unwanted="$2"; shift 2
  local d code page; d="$("$SANDBOX")"
  [[ $# -gt 0 ]] && ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  if [[ "$code" == 0 && "$page" != *"$unwanted"* ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want a successful build with NO: $unwanted"
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# accepts_without <name> <expected-substring> <substring-that-must-NOT-appear> [mutator...]
# accepts() and omits() in one breath, for a claim whose two halves are only worth
# anything together. A figure computed from git has to degrade to prose with no number in
# it, and either half alone is satisfied by the wrong page: a build that dropped the
# sentence entirely passes the "no number" half, and one that carried a hand-typed number
# in the prose passes the "sentence is there" half.
accepts_without() {
  selected "$1" || return 0
  local name="$1" want="$2" unwanted="$3"; shift 3
  local d code page; d="$("$SANDBOX")"
  [[ $# -gt 0 ]] && ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  if [[ "$code" == 0 && "$page" == *"$want"* && "$page" != *"$unwanted"* ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want a successful build containing:  $want"
    echo "    and NOT containing:                  $unwanted"
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# region_between <text> <start> <end>
# The slice of <text> that lies strictly between the first <start> and the first <end>
# after it, printed on stdout. Missing either landmark prints nothing: a caller asking
# "is it in this region" of a text that has no such region must get no, never a fallback
# to matching against the whole thing.
region_between() {
  local text="$1" start="$2" end="$3" region
  [[ "$text" == *"$start"*"$end"* ]] || return 0
  region="${text#*"$start"}"        # drop everything up to and including the start landmark
  printf '%s' "${region%%"$end"*}"  # and everything from the end landmark on
}

# missing_from <text> <wants>
# Of the substrings in <wants> — one per line — the ones <text> does not contain, printed
# one per line. Nothing printed means every one of them is there.
# All of them, not the first: a report that named one missing string at a time would send
# you round the build again for the next.
missing_from() {
  local text="$1" want
  while IFS= read -r want; do
    [[ "$text" == *"$want"* ]] || printf '%s\n' "$want"
  done <<< "$2"
}

# owes <name> <wants> <expected-substring-in-stderr> <mutator...>
# The mutator leaves the tree in DEBT — a script line no commentary chunk claims — and the
# build must carry it rather than refuse it: exit 0, a page that shows the line and says a
# reader is owed prose for it, and a stderr summary that names the debt.
#
# This is refuses() turned inside out, and it needs all three halves at once because each
# one alone is satisfied by a wrong build. Exit 0 on its own is a build that swallowed the
# gap in silence, which is how prose rots unnoticed. The page strings on their own would
# pass a build that marked the listing and told nobody running it. And the stderr line on
# its own would pass a build that reported the debt and then dropped the uncovered lines
# out of the listing — the page promises the source verbatim, so the lines a chunk does
# not cover are exactly the lines that must still be there.
#
# <wants> is ONE argument holding one required page substring per line, the same shape
# opens_with and rail_lists take, for the same reason: the claim is that all of them are
# in the page, and a report naming one at a time sends you round the build again.
owes() {
  selected "$1" || return 0
  local name="$1" wants="$2" want_err="$3"; shift 3
  local d code page err missing; d="$("$SANDBOX")"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  err="$(cat "$d/err.txt" 2>/dev/null)"
  missing="$(missing_from "$page" "$wants")"
  if [[ "$code" == 0 && -z "$missing" && "$err" == *"$want_err"* ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want exit 0, a page containing all of: $wants"
    echo "    and stderr containing:                 $want_err"
    if [[ -n "$missing" ]]; then
      echo "    missing from the page:"
      printf '%s\n' "$missing" | sed 's/^/      /'
    fi
    echo "    stderr was:"
    printf '%s\n' "$err" | sed 's/^/    | /' | head -6
  fi
}

# opens_with <name> <wants> [mutator...]
# Every assertion above asks its question of the whole page, which is no use for a claim
# about where something sits. This one cuts the page down to the slice the build puts
# between the masthead and "What veri actually is" — `</header>` to `<h2 id="what"`, with
# the capability index empty in a bare sandbox — and asks only of that.
# The slice is what makes the case mean anything: every string it looks for also occurs
# elsewhere on the page. The rail links to #s2 and #supervise, and the "built with itself"
# sentence already lives inside the intro, below. Asked of the whole page, this case would
# be green today.
# <wants> is ONE argument holding one required substring per line, for the same reason
# tags_git takes its spans that way: the claim is that all of them are in that one slice.
opens_with() {
  selected "$1" || return 0
  local name="$1" wants="$2"; shift 2
  local d code page region missing
  d="$("$SANDBOX")"
  [[ $# -gt 0 ]] && ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  # after the rail, the crumb and the masthead; before the old opening section
  region="$(region_between "$page" '</header>' '<h2 id="what"')"
  missing="$(missing_from "$region" "$wants")"
  if [[ "$code" == 0 && -z "$missing" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want, between the masthead and <h2 id=\"what\">, all of: $wants"
    echo "    missing:"
    [[ -n "$missing" ]] && printf '%s\n' "$missing" | sed 's/^/      /'
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# rail_lists <name> <wants> [mutator...]
# opens_with for the other half of a section's existence: a heading the rail does not
# link to is a section nobody navigating the page can reach. Same cut, different region —
# `<aside class="rail">` to `</aside>`, which is the whole of the navigation and nothing
# else. The slice matters here for the same reason it does above: every anchor in the rail
# also appears as an `id=` on the heading it points at, so asked of the whole page this
# would pass on a section that was never added to the nav at all.
rail_lists() {
  selected "$1" || return 0
  local name="$1" wants="$2"; shift 2
  local d code page region missing
  d="$("$SANDBOX")"
  [[ $# -gt 0 ]] && ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  region="$(region_between "$page" '<aside class="rail">' '</aside>')"
  missing="$(missing_from "$region" "$wants")"
  if [[ "$code" == 0 && -z "$missing" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want, inside the rail, all of: $wants"
    echo "    missing:"
    [[ -n "$missing" ]] && printf '%s\n' "$missing" | sed 's/^/      /'
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# rail_group_lists <name> <group-heading> <wants> [mutator...]
# rail_lists narrowed one level further: not "somewhere in the rail" but "inside this one
# rail group, with its peers". The rail is flat markup — an <h4> opens a group and the
# next <h4> ends it — so a group is the region between its heading and the following
# <h4>, which is the cut region_between already makes.
# What the narrower region buys is the half of the claim rail_lists cannot see: a link
# that was given a group of its own, or filed under the reference entries, is still
# somewhere in the rail. Only the group says it is a top-level section like the others.
rail_group_lists() {
  selected "$1" || return 0
  local name="$1" head="$2" wants="$3"; shift 3
  local d code page region missing
  d="$("$SANDBOX")"
  [[ $# -gt 0 ]] && ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  region="$(region_between "$page" "$head" '<h4>')"
  missing="$(missing_from "$region" "$wants")"
  if [[ "$code" == 0 && -z "$missing" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want, inside the rail group $head, all of: $wants"
    echo "    missing:"
    [[ -n "$missing" ]] && printf '%s\n' "$missing" | sed 's/^/      /'
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# blocks_of <text> <open-marker> <close-marker>
# Every <open>…<close> block in <text>, one per line, with the newlines inside each block
# squashed to spaces so one block is one line. Callers that need to ask something of a
# single figure — rather than of every figure at once — read this line by line.
blocks_of() {
  local rest="$1" open="$2" close="$3" block
  while [[ "$rest" == *"$open"* ]]; do
    rest="${rest#*"$open"}"             # drop everything up to and including this opener
    [[ "$rest" == *"$close"* ]] || break   # an unclosed opener has no block to report
    block="${rest%%"$close"*}"
    printf '%s\n' "${block//$'\n'/ }"
    rest="${rest#*"$close"}"            # continue after this block, not inside it
  done
}

# figures_in <text>
# Every figure in <text>, one per line, in blocks_of's one-block-per-line form. A figure is
# one <pre class="src"> sketch or one inline <svg>: those are the two ways this page draws a
# diagram (stages 2 and 4 use the first, the orientation figures the second), and this is
# the one place that says so.
figures_in() {
  blocks_of "$1" '<pre class="src"' '</pre>'
  blocks_of "$1" '<svg' '</svg>'
}

# figure_holding <text> <wants>
# The first figure in <text> that contains every substring in <wants> — one per line —
# printed on stdout. Nothing printed means no single figure holds all of them.
# The ONE-figure part is the whole claim, which is why it is a query of its own rather
# than a loop inside the assertion. A stage section also contains the full source of every
# script in it, so the names of those scripts are all over the region already — asked of
# the region as a whole, this would be answered by four names sitting in four unrelated
# listings, which is not a diagram. Only a single block holding all of them is.
figure_holding() {
  local text="$1" wants="$2" block
  while IFS= read -r block; do
    [[ -n "$block" ]] || continue
    if [[ -z "$(missing_from "$block" "$wants")" ]]; then printf '%s' "$block"; return 0; fi
  done < <( figures_in "$text" )
}

# figure_between <name> <start> <end> <wants>
# One figure inside a region must carry every one of <wants>. The region is the
# region_between cut; the figure is figure_holding's.
# No [mutator...] tail, unlike omits() and friends: a figure case asks what the page the
# repository actually builds contains, so there is nothing to mutate. Add the tail when a
# case needs one, rather than carrying an argument no caller can reach.
figure_between() {
  selected "$1" || return 0
  local name="$1" start="$2" end="$3" wants="$4"
  local d code page region found
  d="$("$SANDBOX")"
  page="$(build "$d")" && code=0 || code=$?
  region="$(region_between "$page" "$start" "$end")"
  found="$(figure_holding "$region" "$wants")"
  if [[ "$code" == 0 && -n "$found" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want, between $start and $end, ONE <pre class=\"src\"> or <svg> block"
    echo "    holding all of: $wants"
    echo "    got: no single figure with all of them"
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# stage3_figure <name> <wants>
# figure_between, bounded to stage 3's section. A stage is flat markup — the section opens
# at its own anchor and the next stage's anchor ends it — so "inside stage 3" is the region
# between id="s3" and id="s4", and this says that once instead of at every case that needs
# it. Spelled out at the call sites the pair reads as two arbitrary strings; named here it
# reads as the claim it encodes, and the two ids stay in one place if the anchors ever move.
stage3_figure() { figure_between "$1" 'id="s3"' 'id="s4"' "$2"; }

# omits_git — omits(), but against a sandbox that is a real repository.
# `local` inside a function is visible to everything it then calls — bash scopes locals
# to the call chain, not to the function body — so omits() sees this SANDBOX, and the
# global is back in place the moment omits_git returns.
omits_git() { local SANDBOX=sandbox_git; omits "$@"; }
accepts_without_git() { local SANDBOX=sandbox_git; accepts_without "$@"; }

# index_says <name> <wants>
# opens_with's question, asked of the capability index: the slice the build puts between
# `<div class="stage-head" id="capabilities">` and the pitch's first heading, which is the
# whole of that section and nothing else. That section is where the reader chooses a
# version, so it is the only place a sentence about what the choice answers is next to the
# control rather than two thousand lines away from it — and a claim about WHERE a sentence
# sits cannot be asked of the whole page.
# Built in sandbox_git, because the index is the one section that exists only when git does
# (case 10). In a bare sandbox the region is the empty string, which would make this a
# question about nothing.
# No mutator tail, unlike its three siblings above: what it asks about is prose the build
# emits from `commentary.py` whatever the repository looks like, so there is nothing to
# change in the sandbox first. The parameter goes back the day a case needs one.
index_says() {
  selected "$1" || return 0
  local name="$1" wants="$2"
  local d code page region missing
  d="$(sandbox_git)"
  page="$(build "$d")" && code=0 || code=$?
  region="$(region_between "$page" '<div class="stage-head" id="capabilities">' '<h2 id="why"')"
  missing="$(missing_from "$region" "$wants")"
  if [[ "$code" == 0 && -z "$missing" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want, inside the capability index, all of: $wants"
    echo "    missing:"
    [[ -n "$missing" ]] && printf '%s\n' "$missing" | sed 's/^/      /'
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# tags_git <name> <n-hunk-tags> <expected-spans> <mutator...>
# accepts() and omits() each ask one yes/no question of the whole page, and a hunk tag
# needs two asked together: "this line carries v0.2" is only half the claim, because an
# implementation that tagged every line would satisfy it and defeat the point — the tag
# is worth reading only if it says where to look. So tags_git asserts the page contains
# every one of <expected-spans> AND carries exactly <n> hunk tags in total.
# <expected-spans> is ONE argument holding one expected span per line, because a case
# with two tags has to claim both at once: found separately they could still be the same
# line tagged twice, or one span overwritten by the other.
tags_git() {
  selected "$1" || return 0
  local name="$1" n="$2" wants="$3"; shift 3
  local d code page got want missing=""; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  got="$(hunk_spans "$page")"
  while IFS= read -r want; do
    [[ "$page" == *"$want"* ]] || missing="$want"
  done <<< "$wants"
  if [[ "$code" == 0 && -z "$missing" && "$got" == "$n" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want $n hunk-tagged line(s), including: $wants"
    echo "    got  $got hunk-tagged line(s), missing: ${missing:-none}"
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# hunks_git <name> <expected-report> <mutator...>
# Every other version-layer assertion here reads the built page, which can only ever show
# a hunk's FIRST line: the wrapper <span> sits on that one line and nothing in the markup
# says where the run ends. An extent is a fact about the PAIR of lines a hunk runs
# between, so this one asks gitmeta itself, in the same sandbox_git repository the
# page-level cases build in.
# The report is one line per hunk — `<first>-<last> <tag>`, lowest line first — and the
# whole of it is compared, not searched: a hunk the implementation invented, or one it
# dropped, is as wrong as an extent that ends on the wrong line.
# Read back through gitmeta.read() rather than by calling hunks() with a hand-written tag
# list and `since`, because those two arguments are exactly what the build works out for
# itself; supplying them would let the case pass against a tree the real build reads
# differently.
hunks_git() {
  selected "$1" || return 0
  local name="$1" want="$2"; shift 2
  local d code got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  got="$( cd "$d" && python3 - 2>&1 <<'PY'
import sys
sys.path.insert(0, "docs/wt")
import gitmeta
meta = gitmeta.read(".", {"classify-bail.sh": "skills/tdd/scripts/classify-bail.sh"})
for first, (tag, description, last) in sorted(meta["marks"]["classify-bail.sh"]["hunks"].items()):
    print("%d-%d %s" % (first, last, tag))
PY
  )" && code=0 || code=$?
  if [[ "$code" == 0 && "$got" == "$want" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want the hunks of classify-bail.sh to report: $want"
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -6
  fi
}

# hunk_map_git <name> <expected-report> <mutator...>
# The page's markup can say "this line starts a v0.2 hunk" and nothing more: the wrapper
# <span> carries the tag and the description, but it is keyed by line and it stops where
# it started. A reader asking "what did v0.2 touch?" needs the other direction — tag to
# the hunks it owns, each with the script it is in and both ends of its run — which is why
# the build emits an inverted map as `window.__VERI_HUNKS__`.
#
# Two claims, and neither is worth anything alone. The map has to CONTAIN the right
# entries, so the whole report is compared rather than searched, exactly as hunks_git
# does: an entry the build invented, or one it dropped, is as wrong as a bad extent. And
# the map has to be COMPLETE — one entry per `.hunk` span on the page — so the entry count
# is checked against the span count the page itself carries. Without that second half a
# map holding one correct entry out of five passes, and since-mode silently loses the
# other four; without the first, a map of five entries full of nonsense passes.
#
# The report is one line per entry — `<tag> <script> <first>-<last> <description>`, tags
# in order and lowest line first within a tag, which is plain tuple order because no two
# entries can share a (tag, script, first line) — and it is read out of the BUILT PAGE, not
# out of gitmeta: the claim is about what ships to the browser, which is the only place
# app.js can read it from.
# An entry is accepted either as a 4-element array in the order the map is specified in
# (script, first line, last line, description) or as an object keyed by those same words,
# because which of the two a build emits is a spelling choice and not a behaviour.
hunk_map_git() {
  selected "$1" || return 0
  local name="$1" want="$2"; shift 2
  local d code read_code page spans got entries; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  spans="$(hunk_spans "$page")"
  printf '%s' "$page" > "$d/page.html"
  got="$( cd "$d" && python3 - page.html 2>&1 <<'PY'
import json, re, sys
page = open(sys.argv[1]).read()
m = re.search(r"window\.__VERI_HUNKS__\s*=\s*(.+?);?\s*</script>", page, re.S)
if not m:
    sys.exit("the page carries no window.__VERI_HUNKS__")
inverted = json.loads(m.group(1))
KEYS = ("script", "first", "last", "description")

def fields(entry):
    """One entry's (script, first, last, description), in either spelling the map may use."""
    return [entry.get(k) for k in KEYS] if isinstance(entry, dict) else list(entry)[:4]

rows = sorted((tag, *fields(e)) for tag, entries in inverted.items() for e in entries)
for tag, script, first, last, description in rows:
    print("%s %s %s-%s %s" % (tag, script, first, last, description))
PY
  )" && read_code=0 || read_code=$?
  entries="$(printf '%s' "$got" | grep -c . | tr -d ' ')"
  if [[ "$code" == 0 && "$read_code" == 0 && "$got" == "$want" && "$entries" == "$spans" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, map read exit $read_code)"
    echo "    want window.__VERI_HUNKS__ to report, one entry per hunk span ($spans):"
    printf '%s\n' "$want" | sed 's/^/      /'
    echo "    got $entries entr(y|ies):"
    printf '%s\n' "$got" | sed 's/^/      /' | head -6
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# since_reader — how a built page is asked for each script's own `since`, printed on
# stdout as a python program. Two spellings are read, because which one a build emits is
# a spelling choice and not a behaviour, exactly as hunk_map_git has it for the entries of
# the hunk map: a `window.__VERI_SINCE_OF__` map from script to tag, or a `data-since`
# attribute on the script header the listing already opens with.
# It prints how many scripts the page LISTS on its first line and then one line per script
# that carries a since — `<script> <tag>`, sorted — so a caller can ask whether the answer
# covers every script without writing eighteen names down.
# Shipped as a file rather than a heredoc inside a $( ), for the reason at the top of this
# file: bash 3.2 scans a nested heredoc for quotes through its body.
since_reader() {
  cat <<'PY'
import json, re, sys

page = open(sys.argv[1]).read()

def emitted(name):
    """One of the page globals, decoded, or None when the page carries no such block."""
    m = re.search(r"window\.__VERI_%s__\s*=\s*(.+?);?\s*</script>" % name, page, re.S)
    return json.loads(m.group(1)) if m else None

listed = emitted("SCRIPTS") or []
since = dict(emitted("SINCE_OF") or {})

# The other spelling: the attribute on the header each listing opens with. The markup is
# read with the scripts and the stylesheet cut out, so a mention inside them cannot answer
# for it, and a header already reporting through the map above is not counted twice.
markup = re.sub(r"<(style|script)\b.*?</\1>", "", page, flags=re.S)
for attrs, fname in re.findall(r"<h3\b([^>]*)>\s*<code>([^<]+)</code>", markup):
    m = re.search(r'data-since="([^"]+)"', attrs)
    if m:
        since.setdefault(fname, m.group(1))

print(len(listed))
for name in sorted(since):
    if since[name]:
        print("%s %s" % (name, since[name]))
PY
}

# since_of_git <name> <wants> <mutator...>
# The hunk map says which LINES a version touched. It cannot say which SCRIPTS a reader has
# never seen at all: a script that arrived whole in v0.18 has no hunk in it — hunks() drops
# every run at or below the file's own `since`, because the header badge already says it —
# so a client holding only the map cannot tell a script the reader read long ago from one
# that did not exist when they read. That fact is on the page already, as the badge, and a
# badge is prose; this is the same fact in a form the client can rank a script by.
#
# Two halves, and neither is worth anything alone. The answer has to be COMPLETE — one
# since per script the page lists — which is checked against the page's own script list
# rather than against a list typed here, for the reason the git budget is computed rather
# than typed: adding a script to the walkthrough must not silently move the line. And it
# has to be each script's own `since` rather than any other version on hand, which is what
# <wants> pins by naming a script whose `since` and whose `changed` are different tags: a
# build emitting the file's latest change, or the repo's latest tag, answers v0.2 where the
# script arrived in v0.1.
#
# The third half is the tree that has no version layer at all — no git, no tags, which is
# what a tarball or a shallow checkout looks like — and it is in this case rather than
# beside it because a map that ships is only safe if it is absent there: the client reads
# an empty answer instead of checking whether there is one, and the build still succeeds.
since_of_git() {
  selected "$1" || return 0
  local name="$1" wants="$2"; shift 2
  local d code read_code page got listed body entries missing
  local bare bare_code bare_read bare_page bare_got bare_entries

  d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  since_reader > "$d/read-since.py"
  got="$( cd "$d" && python3 read-since.py page.html 2>&1 )" && read_code=0 || read_code=$?
  listed="$(printf '%s\n' "$got" | sed -n 1p)"
  body="$(printf '%s\n' "$got" | tail -n +2)"
  entries="$(printf '%s' "$body" | grep -c . | tr -d ' ')"
  missing="$(missing_from "$body" "$wants")"

  bare="$(sandbox)"
  bare_page="$(build "$bare")" && bare_code=0 || bare_code=$?
  printf '%s' "$bare_page" > "$bare/page.html"
  since_reader > "$bare/read-since.py"
  bare_got="$( cd "$bare" && python3 read-since.py page.html 2>&1 )" \
    && bare_read=0 || bare_read=$?
  bare_entries="$(printf '%s\n' "$bare_got" | tail -n +2 | grep -c . | tr -d ' ')"

  if [[ "$code" == 0 && "$read_code" == 0 && -z "$missing" && "$entries" == "$listed" \
        && "$bare_code" == 0 && "$bare_read" == 0 && "$bare_entries" == 0 ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, since read exit $read_code)"
    echo "    want a since for each of the $listed script(s) the page lists, including:"
    printf '%s\n' "$wants" | sed 's/^/      /'
    echo "    got $entries:"
    printf '%s\n' "$body" | sed 's/^/      /' | head -6
    [[ -n "$missing" ]] && { echo "    missing:"; printf '%s\n' "$missing" | sed 's/^/      /'; }
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
    echo "    and, with no git: a build (exit $bare_code, since read exit $bare_read)"
    echo "    carrying no since at all, got $bare_entries:"
    printf '%s\n' "$bare_got" | tail -n +2 | sed 's/^/      /' | head -4
    [[ "$bare_code" != 0 ]] && sed 's/^/    | /' "$bare/err.txt" | head -6
  fi
}

# hunk_css <name> <wants>
# Every other assertion here reads the page's markup. This one reads the stylesheet the
# build inlines into that same page, because a mark nothing styles is not a mark: the
# `<span class="l hunk" data-tag="vX.Y">` wrapper shipped with nothing matching it, so the
# only trace a reader got was the browser's native tooltip on hover.
#
# The stylesheet is reduced to one line per declaration that belongs to a selector naming
# `hunk` — `<selector> | <property> | <value>`, whitespace collapsed — and <wants> holds
# one extended regex per line, each of which must match at least one of those lines.
# Regexes rather than substrings because none of what this pins is a spelling: which
# pseudo-element carries the chip, the rule's width and colour, and how the declarations
# are laid out are all free, and pinning any of them would pin the implementation instead
# of what a reader sees.
# Dropping the declarations of rules that do NOT name hunk is what stops the case passing
# on the `pre.src .l::before` line-number rule that is already there, and on the word
# "chunks" in a comment.
hunk_css() {
  selected "$1" || return 0
  local name="$1" wants="$2"; shift 2
  local d code read_code page got want missing=""; d="$("$SANDBOX")"
  [[ $# -gt 0 ]] && ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  got="$( cd "$d" && python3 - page.html 2>&1 <<'PY'
import re, sys
page = open(sys.argv[1]).read()
m = re.search(r"<style>(.*?)</style>", page, re.S)
if not m:
    sys.exit("the page carries no inlined stylesheet")
css = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)
# Innermost blocks only: a selector cannot contain a brace, so an @media prelude never
# matches and the rules nested inside it are read with their own selectors.
for selector, block in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
    selector = " ".join(selector.split())
    if "hunk" not in selector:
        continue
    for declaration in block.split(";"):
        prop, sep, value = declaration.partition(":")
        if sep:
            print("%s | %s | %s" % (selector, " ".join(prop.split()), " ".join(value.split())))
PY
  )" && read_code=0 || read_code=$?
  while IFS= read -r want; do
    printf '%s\n' "$got" | grep -Eq "$want" || missing+="$want"$'\n'
  done <<< "$wants"
  if [[ "$code" == 0 && "$read_code" == 0 && -z "$missing" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, stylesheet read exit $read_code)"
    echo "    want a .hunk declaration matching each of: $wants"
    echo "    matched by nothing:"
    [[ -n "$missing" ]] && printf '%s' "$missing" | sed 's/^/      /'
    echo "    the .hunk declarations the page carries:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -8
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# undimmed_git <name> <mutator...>
# The page has a resting state — no version chosen, nothing in storage — and this is the
# assertion that it stays plain in it: today's page with the marks on it, every hunk at
# full strength. Dimming is what since-mode turns ON for the hunks a reader has already
# seen; a stylesheet that fades hunks by default and un-fades the chosen ones renders the
# resting page wrong for every reader who never picks a version.
#
# Read from the built page, both halves of it, because "dimmed at rest" is a claim about
# the stylesheet AND the markup together: a rule only fades a hunk if its selector matches
# the page as it ships. So the markup — stylesheet and scripts cut out, so their text
# cannot answer for it — yields the class tokens and attribute names the page actually
# carries, and a rule is LIVE when every class and attribute it names is among them. That
# is one test for two failures: a rule keyed on nothing (`.l.hunk{opacity:.45}`) is live
# because the page carries `.hunk`, and a rule properly keyed on a since-mode state is live
# too if the build ever shipped the page already in that state. `:not(...)` is dropped
# before the tokens are read, since a class named there is one the selector matches for the
# ABSENCE of — `.l.hunk:not(.lit)` matches everything at rest, and counting `lit` as
# required would read it as gated.
# Dimming is opacity below 1 or any filter, which are the two properties that fade an
# element without changing what it says; an unparseable opacity counts as dimming rather
# than being waved through. Hunk-naming selectors only, and not the whole stylesheet,
# because the page has honest reasons to rest something at zero opacity — `.tip` is a
# tooltip that is not showing.
undimmed_git() {
  selected "$1" || return 0
  local name="$1"; shift
  local d code read_code page got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  got="$( cd "$d" && python3 - page.html 2>&1 <<'PY'
import re, sys
page = open(sys.argv[1]).read()
m = re.search(r"<style>(.*?)</style>", page, re.S)
if not m:
    sys.exit("the page carries no inlined stylesheet")
css = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)

markup = re.sub(r"<(style|script)\b.*?</\1>", "", page, flags=re.S)
carried = set(re.findall(r"([A-Za-z_][\w-]*)=", markup))
for value in re.findall(r'class="([^"]*)"', markup):
    carried.update(value.split())

def dims(prop, value):
    if prop == "opacity":
        try:
            return float(value) < 1
        except ValueError:
            return True
    return prop == "filter" and value != "none"

def live(selector):
    """Does this selector match the page as it ships — every class and attribute carried?"""
    selector = re.sub(r":not\([^()]*\)", "", selector)
    return all(t in carried for t in re.findall(r"[.\[]([A-Za-z_][\w-]*)", selector))

# Innermost blocks only, as in hunk_css: a selector cannot contain a brace, so an @media
# prelude never matches and the rules nested inside it are read with their own selectors.
for selector, block in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
    selector = " ".join(selector.split())
    if "hunk" not in selector or not live(selector):
        continue
    for declaration in block.split(";"):
        prop, sep, value = declaration.partition(":")
        prop, value = " ".join(prop.split()), " ".join(value.split())
        if sep and dims(prop, value):
            print("%s | %s | %s" % (selector, prop, value))
PY
  )" && read_code=0 || read_code=$?
  if [[ "$code" == 0 && "$read_code" == 0 && -z "$got" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, stylesheet read exit $read_code)"
    echo "    want no rule that fades a hunk on the page as it ships"
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -8
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# paint_css <name> <expected-report> <mutator...>
# The paint the layer above puts ON the marks, read from the stylesheet that renders it.
# `lit` and `dim` are class tokens until some rule answers for them: a page that sorts
# every mark correctly and styles neither class looks, to the reader who just chose a
# version, exactly like the page that has no since-mode in it.
#
# Three lines, because a choice has three renderings to keep apart — the marks that are
# news, the marks that are not, and the marks on a page where nobody chose anything:
#
#   dim <verdict>       what a rule requiring .dim does to a mark
#   lit <verdict>       what a rule requiring .lit does to one
#   unmarked untouched  or one line per rule that fades a mark requiring neither
#
# A verdict is read from the declarations of every rule whose selector NAMES the class,
# outside `:not(...)` — a class named there is one the rule matches for the absence of, so
# `.l.hunk:not(.lit)` is not a rule about lit marks. `unstyled` is no such rule at all;
# `faded` is opacity below 1 or any filter, the two properties that fade an element
# without changing what it says, and an unparseable opacity counts as fading rather than
# being waved through; `plain` is declarations that only put back the resting look
# (`opacity:1`, `filter:none`), which is what "fade everything and un-fade the lit ones"
# leaves behind and is not a highlight; `highlighted` is anything else. Which property
# does the highlighting — a colour, a weight, a background, an outline — is free, for the
# reason case 19 leaves faintness free: no assertion this suite can make would tell a
# tasteful highlight from a garish one, and pinning the property would pin the design.
#
# The third line is the resting reader, and it is the claim that the paint is GATED: a
# stylesheet that fades `.hunk` outright and restores `.lit` renders the two chosen states
# correctly and greys out the page for everyone who chose nothing. Read as case 20 reads
# it — a rule counts only if it is LIVE, every class and attribute it names carried by the
# markup the build ships — and narrowed to selectors that name a mark (`hunk`, `data-tag`,
# `data-since`), because the page has honest reasons to rest something at zero opacity:
# `.tip` is a tooltip that is not showing. Fading only, on the same footing as case 20:
# an ungated highlight is not something this reader can tell from the page-as-designed.
#
# Built over a real history with a hunk in it so the page genuinely carries both kinds of
# mark — `data-tag` on a run of changed lines, `data-since` on every script header — since
# a rule keyed on an attribute the page does not carry is never live, and the third line
# would be green on a page with nothing on it to fade.
paint_css() {
  selected "$1" || return 0
  local name="$1" want="$2"; shift 2
  local d code read_code page got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  got="$( cd "$d" && python3 - page.html 2>&1 <<'PY'
import re, sys
page = open(sys.argv[1]).read()
m = re.search(r"<style>(.*?)</style>", page, re.S)
if not m:
    sys.exit("the page carries no inlined stylesheet")
css = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)

markup = re.sub(r"<(style|script)\b.*?</\1>", "", page, flags=re.S)
carried = set(re.findall(r"([A-Za-z_][\w-]*)=", markup))
for value in re.findall(r'class="([^"]*)"', markup):
    carried.update(value.split())

def bare(selector):
    """The selector minus its :not() arguments, which name classes it matches WITHOUT."""
    return re.sub(r":not\([^()]*\)", "", selector)

def requires(selector, token):
    return re.search(r"\.%s(?![\w-])" % token, bare(selector)) is not None

def fades(prop, value):
    if prop == "opacity":
        try:
            return float(value) < 1
        except ValueError:
            return True
    return prop == "filter" and value != "none"

def restores(prop, value):
    return (prop, value) in (("opacity", "1"), ("filter", "none"))

def live(selector):
    """Does this selector match the page as it ships — every class and attribute carried?"""
    return all(t in carried for t in re.findall(r"[.\[]([A-Za-z_][\w-]*)", bare(selector)))

MARKS = ("hunk", "data-tag", "data-since")

def reaches_a_resting_mark(selector):
    """Does this rule reach a mark on the page a reader who chose NOTHING is looking at?

    Three ways it does not. It names `.lit` or `.dim`: those classes exist only once a
    choice has been made, so the rule is gated and cannot touch the resting page. It
    names no mark: the page rests other things at zero opacity for honest reasons, and
    `.tip` is a tooltip that is not showing. It is not live: a rule whose classes and
    attributes the markup does not carry styles nothing, as in case 20."""
    if requires(selector, "lit") or requires(selector, "dim"):
        return False
    return any(token in selector for token in MARKS) and live(selector)

# Innermost blocks only, as in hunk_css: a selector cannot contain a brace, so an @media
# prelude never matches and the rules nested inside it are read with their own selectors.
rules = []
for selector, block in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
    selector = " ".join(selector.split())
    declarations = []
    for declaration in block.split(";"):
        prop, sep, value = declaration.partition(":")
        if sep:
            declarations.append((" ".join(prop.split()), " ".join(value.split())))
    rules.append((selector, declarations))

def verdict(token):
    declared = [d for selector, block in rules if requires(selector, token) for d in block]
    if not declared:
        return "unstyled"
    if any(fades(prop, value) for prop, value in declared):
        return "faded"
    if any(not restores(prop, value) for prop, value in declared):
        return "highlighted"
    return "plain"

print("dim %s" % verdict("dim"))
print("lit %s" % verdict("lit"))

ungated = []
for selector, block in rules:
    if not reaches_a_resting_mark(selector):
        continue
    for prop, value in block:
        if fades(prop, value):
            ungated.append("unmarked %s | %s | %s" % (selector, prop, value))
print("\n".join(ungated) if ungated else "unmarked untouched")
PY
  )" && read_code=0 || read_code=$?
  if [[ "$code" == 0 && "$read_code" == 0 && "$got" == "$want" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, stylesheet read exit $read_code)"
    echo "    want, of the stylesheet the page inlines:"
    printf '%s\n' "$want" | sed 's/^/      /'
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -8
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# dom_stub — the browser the page gets when there is no browser, printed on stdout: a DOM
# that answers every query with nothing, so the tooltip and scrollspy layers bail at load
# exactly as they do on a page whose markup they cannot find, and the layer a question is
# about is what is left. It ends by evaluating the page's own <script> blocks in document
# order, so whatever they hang on `window` is there for the question appended underneath.
dom_stub() {
  cat <<'JS'
var fs = require("fs");
var page = fs.readFileSync(process.argv[2], "utf8");

/* A stand-in for one element: every method a page script might reach for, answering
   with nothing of its own. Written out rather than proxied so a call the stub does not
   cover fails as a named TypeError. */
function element() {
  return {
    className: "", style: {}, dataset: {}, children: [], firstChild: null, value: "",
    scrollTop: 0, offsetWidth: 0, offsetHeight: 0,
    classList: { add: function () {}, remove: function () {}, toggle: function () {},
                 contains: function () { return false; } },
    getAttribute: function () { return null; }, setAttribute: function () {},
    removeAttribute: function () {}, hasAttribute: function () { return false; },
    appendChild: function () {}, removeChild: function () {}, insertBefore: function () {},
    addEventListener: function () {}, removeEventListener: function () {},
    querySelector: function () { return element(); },
    querySelectorAll: function () { return []; },
    closest: function () { return null; }, matches: function () { return false; },
    contains: function () { return false; },
    scrollIntoView: function () {}, focus: function () {},
    getBoundingClientRect: function () {
      return { top: 0, bottom: 0, left: 0, right: 0, width: 0, height: 0 };
    }
  };
}

globalThis.window = globalThis;             // so `window.__VERI_X__ = …` is a global
globalThis.addEventListener = function () {};
globalThis.removeEventListener = function () {};
globalThis.requestAnimationFrame = function () { return 0; };
globalThis.cancelAnimationFrame = function () {};
globalThis.scrollX = 0; globalThis.scrollY = 0;
globalThis.innerWidth = 1200; globalThis.innerHeight = 800;
/* The URL the page is opened at. VERI_ASK_HASH is how a case says "reloaded at this
   address": the page scripts are evaluated at the bottom of this stub, so whatever a case
   puts here is what they read at load, which is the whole of what a reload is. Unset — the
   resting page, no hash — is what every other question asks about.
   history is the other way a page can write the URL, and it writes the same place: a page
   that replaces the address rather than assigning location.hash has still put the choice
   where the next load will find it, and which of the two it uses is not behaviour.

   Assigning the hash is also how the page hears about it. A browser fires `hashchange` at
   the window on that assignment, so a page that repaints there repaints for the reader who
   pressed Back and the one who edited the address bar too — and a control that calls
   choose() and leaves the repainting to that event is not broken, it is idiomatic. So the
   setter fires it, and history.replaceState, which changes the same address and fires
   nothing in a browser, does not: a page that replaces the address and waits for an event
   waits forever there, and must not be told otherwise here. Nothing is fired when the
   address does not actually change, which is the other half of what a browser does.
   The event only reaches anyone under VERI_ASK_WIRED — the unwired stub drops every
   listener at the door, as it did before this existed. */
var hashNow = process.env.VERI_ASK_HASH || "";
function setHash(next, fire) {
  if (String(next) === hashNow) return;
  hashNow = String(next);
  if (fire && typeof globalThis.__fire === "function") {
    globalThis.__fire("hashchange", { type: "hashchange" });
  }
}
globalThis.location = { href: "", search: "" };
Object.defineProperty(globalThis.location, "hash", {
  get: function () { return hashNow; },
  set: function (v) { setHash(v, true); }
});
globalThis.history = {
  replaceState: function (state, title, url) {
    setHash(String(url).replace(/^[^#]*/, ""), false);
  },
  pushState: function (state, title, url) { history.replaceState(state, title, url); }
};
globalThis.navigator = { userAgent: "node" };
/* The browser's durable store. VERI_ASK_STORE names a JSON file that survives the node
   process, which is how one case asks what a SECOND load of the same page finds: the run
   that writes and the run that reads are separate processes for the same reason a reload
   is — nothing of the first is left in the second except what was stored.
   VERI_ASK_STORE_BLOCKED is the browser that refuses, and it refuses the way one does:
   every read and every write throws, rather than the store quietly answering nothing.
   Unset — no file, nothing stored, nothing refused — is what every other question asks
   about, and answers exactly as the inert stub this replaced did. */
globalThis.localStorage = (function () {
  var file = process.env.VERI_ASK_STORE || "";
  var blocked = !!process.env.VERI_ASK_STORE_BLOCKED;
  var data = file && fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, "utf8")) : {};
  function refuse() { throw new Error("this browser blocks storage"); }
  function save() { if (file) fs.writeFileSync(file, JSON.stringify(data)); }
  return {
    getItem: function (k) {
      if (blocked) refuse();
      return Object.prototype.hasOwnProperty.call(data, k) ? data[k] : null;
    },
    setItem: function (k, v) { if (blocked) refuse(); data[k] = String(v); save(); },
    removeItem: function (k) { if (blocked) refuse(); delete data[k]; save(); }
  };
})();
globalThis.getComputedStyle = function () { return {}; };
globalThis.matchMedia = function () {
  return { matches: false, addEventListener: function () {}, addListener: function () {} };
};
globalThis.document = element();
document.readyState = "complete";
document.documentElement = element();
document.body = element();
document.createElement = function () { return element(); };
document.getElementById = function () { return null; };
document.querySelector = function () { return element(); };

/* VERI_ASK_WIRED — the browser with a DOM in it, for the one question that has to press
   a key and click a button rather than call a function.
   Everything above answers every query with nothing, which is exactly what the other
   questions want: the layers bail at load and the one under test is what is left. A
   question about the WIRING has nothing left to ask that way — a keydown listener
   registered against a no-op addEventListener is dropped, and a button appended to an
   element that forgets its children is gone the moment it is made. So for this question,
   and only for it, three things are real:

     listeners  are remembered, so the question can fire the event the reader would
     elements   remember their children, their attributes and their handlers
     the marks  are parsed back out of the page's OWN markup, every attribute carried

   That last one is what keeps the stub from lying: a mark answers what the page shipped
   and nothing this harness invented, so an implementation that reads an attribute the
   build does not emit finds nothing here either.

   Scrolling is observed as scrollIntoView on the mark, which is the one route that says
   WHICH stop the reader was taken to: a window.scrollTo of a measured offset says only
   "somewhere" to a stub whose every rectangle is zero. */
if (process.env.VERI_ASK_WIRED) {
  var listeners = {};
  var on = function (type, fn) { (listeners[type] = listeners[type] || []).push(fn); };
  globalThis.addEventListener = on;
  /* Both ways a page can be listening: the listeners it added, and the `onhashchange`-style
     property it may have assigned instead. A browser calls both, and which of the two a
     page uses is a spelling choice — the event is the same event. */
  globalThis.__fire = function (type, event) {
    (listeners[type] || []).slice().forEach(function (fn) { fn(event); });
    if (typeof globalThis["on" + type] === "function") globalThis["on" + type](event);
  };

  /* One element's class list, as a list the page can actually change. element() above
     answers every membership with false and drops every add, which is what the questions
     asked of the unwired stub want — a layer that paints a page it cannot find has painted
     nothing. A question about the PAINT has nothing left to read that way, so here the
     tokens are kept, and kept in `className` and in the `class` attribute at once, the way
     a browser keeps them: a page that adds through one and is read back through the other
     must see its own edit either way.
     A thing of its own beside node() rather than thirty lines inside it: this is the one
     part of an element that has state and rules about it, and the rest of node() is a list
     of methods that each keep what they are handed. */
  var classListFor = function (el) {
    function tokens() { return el.className ? el.className.split(/\s+/) : []; }
    function write(list) {
      var seen = {};
      el.className = list.filter(function (c) {
        if (!c || seen[c]) return false;
        seen[c] = true;
        return true;
      }).join(" ");
      el.attrs["class"] = el.className;
    }
    var classes = {
      contains: function (c) { return tokens().indexOf(c) >= 0; },
      add: function () { write(tokens().concat([].slice.call(arguments))); },
      remove: function () {
        var drop = [].slice.call(arguments);
        write(tokens().filter(function (c) { return drop.indexOf(c) < 0; }));
      },
      toggle: function (c, on) {
        var want = on === undefined ? !classes.contains(c) : !!on;
        if (want) classes.add(c); else classes.remove(c);
        return want;
      }
    };
    return classes;
  };

  /* One element that remembers: element() above with the methods that drop what they are
     given replaced by ones that keep it. Still written out rather than proxied, for the
     reason element() is — a call neither covers fails as a named TypeError. */
  var node = function (tag) {
    var el = element();
    el.tagName = String(tag).toUpperCase();
    el.attrs = {};
    el.handlers = {};
    el.children = [];
    el.classList = classListFor(el);

    el.setAttribute = function (k, v) {
      el.attrs[k] = String(v);
      if (k === "class") el.className = String(v);
    };
    el.getAttribute = function (k) {
      return Object.prototype.hasOwnProperty.call(el.attrs, k) ? el.attrs[k] : null;
    };
    el.hasAttribute = function (k) { return el.getAttribute(k) !== null; };
    el.removeAttribute = function (k) { delete el.attrs[k]; };
    el.appendChild = function (c) { el.children.push(c); return c; };
    el.insertBefore = function (c) { el.children.unshift(c); return c; };
    el.removeChild = function (c) {
      var at = el.children.indexOf(c);
      if (at >= 0) el.children.splice(at, 1);
      return c;
    };
    el.addEventListener = function (type, fn) {
      (el.handlers[type] = el.handlers[type] || []).push(fn);
    };
    el.scrollIntoView = function () { globalThis.__scrolled = el; };
    return el;
  };

  /* Does this element answer that selector? The stub holds a flat list and no tree, so
     only the LAST compound of a selector is read — `pre.src .l.hunk[data-tag]` asks for
     the `.l.hunk` carrying a `data-tag`, and the ancestors it names are context this
     harness cannot check. A selector LIST is any one of its parts, which is how a single
     query can ask for the hunk marks and the script headers at once. Only the exact
     `[attr]` and `[attr="value"]` forms are modelled; a page reaching for `~=` or `^=`
     here would find nothing rather than everything. */
  var selects = function (el, sel) {
    return String(sel).split(",").some(function (part) {
      var compound = part.trim().split(/[\s>+~]+/).pop();
      if (!compound) return false;
      var tag = /^[A-Za-z][\w-]*/.exec(compound);
      if (tag && el.tagName !== tag[0].toUpperCase()) return false;
      var ok = true;
      (compound.match(/\.[\w-]+/g) || []).forEach(function (c) {
        if (!el.classList.contains(c.slice(1))) ok = false;
      });
      (compound.match(/#[\w-]+/g) || []).forEach(function (i) {
        if (el.getAttribute("id") !== i.slice(1)) ok = false;
      });
      (compound.match(/\[[^\]]+\]/g) || []).forEach(function (a) {
        var want = /^\[([\w-]+)(?:=["']?([^"'\]]*)["']?)?\]$/.exec(a);
        var got = want && el.getAttribute(want[1]);
        if (!want || got === null || got === undefined) { ok = false; return; }
        if (want[2] !== undefined && got !== want[2]) ok = false;
      });
      return ok;
    });
  };

  /* One element parsed back out of the page's own markup: its tag, every attribute the
     open tag carries, and the offset it sits at, which is what puts it in document order
     beside the rest. Nothing is invented here — an implementation that reads an attribute
     the build does not emit finds nothing, which is the whole reason the marks are parsed
     rather than handed over. */
  var parsed = function (tag, attrs, at, inner) {
    var el = node(tag);
    el.at = at;
    var attr = /([\w-]+)="([^"]*)"/g, pair;
    while ((pair = attr.exec(attrs)) !== null) {
      el.setAttribute(pair[1], pair[2]);
      if (pair[1].indexOf("data-") === 0) el.dataset[pair[1].slice(5)] = pair[2];
    }
    /* What the element says, for the elements a reader reads rather than scrolls to. The
       markup between the tags, as markup and as the words left when the tags are taken out
       of it, because a caller asking what a control is called does not know which of the
       two it was written in. `value` comes back the way a browser hands it back, as the
       property and not only as the attribute. */
    if (inner !== undefined) {
      el.innerHTML = inner;
      el.textContent = inner.replace(/<[^>]*>/g, "").replace(/\s+/g, " ").trim();
    }
    if (el.getAttribute("value") !== null) el.value = el.getAttribute("value");
    el.matches = function (sel) { return selects(el, sel); };
    return el;
  };

  /* The hunk marks the page ships, in document order, each carrying the attributes its
     own <span> carries. `class="l hunk"` matches the first line of a run only: a
     continuation line is `class="l hunk cont"`, and the closing quote is what tells them
     apart — the same distinction hunk_spans counts by. */
  var marks = [];
  var head = /<span class="l hunk"([^>]*)>/g, hit;
  while ((hit = head.exec(page)) !== null) {
    var mark = parsed("span", 'class="l hunk"' + hit[1], hit.index);
    mark.kind = "hunk";
    mark.position = marks.length + 1;    // where it sits among the marks, top of page first
    marks.push(mark);
  }

  /* The script headers, and every element inside one. A stop that is a whole script has to
     be a place in the page the same way a hunk is, and the header is that place — but
     WHICH element of it carries the mark is a spelling choice the page makes: the <h3>
     itself, the version badge inside it, a span of its own. So all of them are parsed and
     the query decides, exactly as it does among the listings.
     A script's header is an <h3> naming the file in a <code>: the six prose headings and
     the reference groups are <h3> too, and no listing belongs to any of them. That name is
     remembered by every element of the header, and by every hunk mark below it down to the
     next header, so a question can say WHICH script a press landed in without reading the
     markup a second time. */
  var heads = [];
  var headings = /<h3([^>]*)>([\s\S]*?)<\/h3>/g, heading;
  while ((heading = headings.exec(page)) !== null) {
    var names = /<code>([\w.-]+\.sh)<\/code>/.exec(heading[2]);
    if (!names) continue;
    var opens = /<([A-Za-z][\w-]*)((?:\s[^>]*)?)>/g, open;
    while ((open = opens.exec(heading[0])) !== null) {
      var part = parsed(open[1], open[2], heading.index + open.index);
      part.kind = "header";
      part.script = names[1];
      heads.push(part);
    }
  }

  /* The capability index's rows — one <li class="ver"> per version, the element a choice
     either leaves showing or takes away. Parsed like the marks and for the same reason:
     what a row IS comes out of the page's own markup, so a question about the rows cannot
     be answered by anything this harness invented.
     The version a row is for is the one it prints in its `vtag`, which is the only thing
     on the row that names it; `class="ver unreleased"` is the row for work past the last
     tag and names no version, so it carries "" and answers for itself. */
  var rows = [];
  var items = /<li class="ver([^"]*)"([^>]*)>([\s\S]*?)<\/li>/g, item;
  while ((item = items.exec(page)) !== null) {
    var row = parsed("li", 'class="ver' + item[1] + '"' + item[2], item.index);
    row.kind = "row";
    var vtag = /<span class="vtag">([^<]*)<\/span>/.exec(item[3]);
    row.version = vtag ? vtag[1] : "";
    rows.push(row);
  }

  /* The controls the page's markup carries — every <select> and every <button>, each with
     its options and with what it says. A control is the one element here a reader USES
     rather than reads, and the two routes a page can put one on the page are both real: the
     build can write it into the markup, which is what this parses, or the page can make one
     at load and append it, which is what the index elements below are for. Which of the two
     an implementation picks is a spelling choice, and the reader finds the same control
     either way — so a harness that modelled only one of them would fail a page that works.
     A <select> keeps its own <option>s as its children, because what a select offers is
     the whole of the first half of the claim, and they are parsed out of its own markup
     rather than as elements in their own right for the same reason. */
  var controls = [];
  var openers = /<(select|button)((?:\s[^>]*)?)>([\s\S]*?)<\/\1>/g, opener;
  while ((opener = openers.exec(page)) !== null) {
    var control = parsed(opener[1], opener[2], opener.index, opener[3]);
    control.kind = "control";
    var choices = /<option((?:\s[^>]*)?)>([\s\S]*?)<\/option>/g, choice;
    while ((choice = choices.exec(opener[3])) !== null) {
      control.appendChild(parsed("option", choice[1], opener.index, choice[2]));
    }
    controls.push(control);
  }

  /* The capability index, as a PLACE and as an ELEMENT, which is what makes "the index
     carries the control" a claim this harness can judge rather than "the page does".
     As a place: the section the version rows live in, from its own anchor down to the
     heading of whatever section follows the last row — so a control the build wrote into
     the markup is in the index when its offset falls inside it, and the pair of stepper
     buttons the page puts in the crumb bar never is.
     As an element: the section and the list of rows are handed back real, so a control the
     page BUILDS at load and appends to either is somewhere a question can read it back
     from. Everything else still answers with a fresh nothing that forgets what it is
     given, which is what every other question here wants. */
  var opensIndex = /<div[^>]*id="capabilities"[^>]*>/.exec(page);
  var opensList = /<ol[^>]*class="vers"[^>]*>/.exec(page);
  var indexFrom = opensIndex ? opensIndex.index : -1;
  var indexTo = page.indexOf("<h2", rows.length ? rows[rows.length - 1].at : 0);
  if (indexTo < 0) indexTo = page.length;
  var indexEls = [opensIndex, opensList].filter(Boolean).map(function (found) {
    var el = parsed(/^<([\w-]+)/.exec(found[0])[1], found[0], found.index);
    el.kind = "index";
    return el;
  });

  /* Everything appended inside those, however deep the page nested it: a control in a
     wrapper in the index is in the index. */
  var inside = function (roots, found) {
    (roots || []).forEach(function (root) {
      (root.children || []).forEach(function (child) {
        found.push(child);
        inside([child], found);
      });
    });
    return found;
  };

  /* The controls a reader would find in the capability index, by either route. What is NOT
     in this list is half of what it says: a control the page appended to the crumb bar, or
     to the document, is not where the choice is made. */
  globalThis.__controls = function () {
    return controls.filter(function (c) {
        return indexFrom >= 0 && c.at >= indexFrom && c.at < indexTo;
      })
      .concat(inside(indexEls, []).filter(function (el) {
        return el.tagName === "SELECT" || el.tagName === "BUTTON";
      }));
  };

  /* The kinds in one list, in the order the page prints them — which is the order a
     browser's querySelectorAll answers in, and the order a walk built from one query
     stands on. Only a hunk mark takes the name of the listing it fell in: a header states
     its own, and a row belongs to no script at all. */
  var ordered = marks.concat(heads, rows, controls, indexEls)
                     .sort(function (a, b) { return a.at - b.at; });
  var listing = "";
  ordered.forEach(function (el) {
    if (el.kind === "header") listing = el.script;
    else if (el.kind === "hunk") el.script = listing;
  });

  var crumb = node("div");
  crumb.className = "crumb";
  crumb.setAttribute("class", "crumb");

  document.createElement = function (tag) { return node(tag); };
  /* The crumb bar is the one element a question needs to be the SAME object every time it
     is asked for — the page puts its buttons there and the question reads them back out.
     Past it, the elements this stub has parsed out of the markup and whatever the page has
     appended inside the index, so a layer that goes looking for a place to put a control —
     or for the control it put there on an earlier pass — finds the same one twice.
     Everything else still answers with a fresh nothing, as above, so a layer that queries
     for something this stub does not model gets what it got before rather than a null it
     would crash on. */
  document.querySelector = function (sel) {
    if (/crumb(?!-)/.test(sel)) return crumb;
    var pool = ordered.concat(inside(indexEls, []));
    for (var q = 0; q < pool.length; q++) {
      if (selects(pool[q], sel)) return pool[q];
    }
    return element();
  };
  document.querySelectorAll = function (sel) {
    return ordered.filter(function (el) { return selects(el, sel); });
  };
  document.getElementById = function (id) {
    for (var i = 0; i < marks.length; i++) {
      if (marks[i].getAttribute("id") === id) return marks[i];
    }
    return null;
  };
  document.addEventListener = on;
  document.body = node("body");
  document.documentElement = node("html");
}

var blocks = page.match(/<script>[\s\S]*?<\/script>/g) || [];
for (var i = 0; i < blocks.length; i++) {
  (0, eval)(blocks[i].slice("<script>".length, -"</script>".length));
}
JS
}

# map_entry — how one entry of window.__VERI_HUNKS__ is read, printed on stdout: its
# (script, first, last), in either spelling the map may use, because which of the two a
# build emits is a spelling choice and not a behaviour, exactly as hunk_map_git has it.
# Shipped with the stub rather than written into each question, so two questions asked of
# the same map cannot come to disagree about what an entry is.
map_entry() {
  cat <<'JS'
function fields(entry) {
  return Array.isArray(entry) ? entry.slice(0, 3)
                              : [entry.script, entry.first, entry.last];
}
JS
}

# key_press — how a question presses a key, printed on stdout. Shipped with the stub for
# the reason map_entry is: two questions that both press `n` must not come to disagree
# about what a press is, and they would, since the event a page's keydown listener reads
# is a dozen fields long and only some of them matter.
# wired() is the precondition a pressing question states for itself — firing an event needs
# the DOM that remembers listeners, VERI_ASK_WIRED in the stub above — said before the
# question asks anything, rather than arriving as a TypeError halfway through its report.
key_press() {
  cat <<'JS'
function wired() {
  if (typeof globalThis.__fire !== "function") {
    console.error("the page was asked about its wiring without the wired DOM");
    process.exit(1);
  }
}

function press(key) {
  globalThis.__fire("keydown", {
    type: "keydown", key: key, target: document.body,
    altKey: false, ctrlKey: false, metaKey: false, shiftKey: false,
    preventDefault: function () {}, stopPropagation: function () {}
  });
}
JS
}

# whole_script — how a question tells an entry that is a whole script from one that is a run
# of lines, printed on stdout. Every run window.__VERI_HUNKS__ holds is keyed as
# `<script> <first>-<last>`; an entry that is one of those is a hunk, and an entry that is
# not is the script itself, whatever shape it arrives in. Shipped with the stub for the
# reason map_entry and key_press are: the two sides of that lookup — the key the table is
# filled with and the key it is asked for — have to agree character for character, and a
# comma where a dash went would report every hunk on the page as a whole script.
# The word is the caller's, because two questions report the same fact about different
# things: a stop the walk lands on is that script's `header`, an index row lists it as `new`.
# The table is built on the first question rather than at load, so a question that never
# asks pays nothing.
whole_script() {
  cat <<'JS'
function runKey(f) { return f[0] + " " + f[1] + "-" + f[2]; }

var RUNS = null;
function runs() {
  if (RUNS) return RUNS;
  RUNS = {};
  var hunks = window.__VERI_HUNKS__ || {};
  Object.keys(hunks).forEach(function (tag) {
    (hunks[tag] || []).forEach(function (entry) { RUNS[runKey(fields(entry))] = true; });
  });
  return RUNS;
}

function runOrWhole(entry, word) {
  var f = typeof entry === "string" ? [entry] : fields(entry);
  var run = runKey(f);
  return runs()[run] ? run : f[0] + " " + word;
}
JS
}

# index_row — how one row of window.__VERI_SINCE__.index(since) is read, printed on stdout:
# the version it is for and the entries under it, in either spelling a build may write a row
# in, because a pair and a record carry the same two facts and which one the page hands over
# is not a behaviour. Shipped with the stub for the reason map_entry is, and about the other
# half of the same map: two questions asked of the same index must not come to disagree
# about what a row is, and a question that reads `row[0]` where the page ships `row.tag`
# reports every version as `undefined` rather than failing.
index_row() {
  cat <<'JS'
function tagOf(row) { return Array.isArray(row) ? row[0] : row.tag; }
function entriesOf(row) { return (Array.isArray(row) ? row[1] : row.hunks) || []; }
JS
}

# ask_page <dir> <page> [args...]
# Ask the page a question its markup cannot answer: run <dir>/question.js — which the
# calling assertion has just written — against <page>, under the stub above and the entry
# reader, the keypress, the whole-script lookup and the row reader beside it, with node.
# The question reads its own arguments from process.argv[3] on and prints the report its
# case compares; stdout and stderr both come back, and the exit code is node's, so a
# question that cannot find what it asks for says so and fails the case.
# node is a dependency of reading the page's JS back, never of building or shipping it,
# and a case fails rather than skips when it is absent.
ask_page() {
  local d="$1" page="$2"; shift 2
  { dom_stub; map_entry; key_press; whole_script; index_row
    cat "$d/question.js"; } > "$d/ask.js"
  ( cd "$d" && node ask.js "$page" "$@" 2>&1 )
}

# since_git <name> <chosen-version> <expected-report> <mutator...>
# Every other assertion here reads what the build emitted. This one runs it: choosing a
# version is something a reader does in a browser, and no amount of reading the markup
# says which hunks that choice lights.
#
# So the page is asked through ask_page, which evaluates its own <script> blocks against
# the stub DOM above and then this question.
#
# What it asks is `window.__VERI_SINCE__.lit(tag, since)` — truthy when a hunk tagged
# `tag` is lit for a reader who last read at `since`. The decision has to be reachable
# without a browser for the same reason `window.__VERI_HUNKS__` exists: the page is the
# only place it lives, and dimming a run of lines is a class this harness cannot see.
# The CSS half — what lit and dimmed look like — is cases 19 and 20.
#
# The report is one line per hunk the page carries — `<tag> <script> <first>-<last>
# lit|dim` — and the whole of it is compared, because both halves of the claim are in it:
# a hunk the choice should light and one it should leave dimmed are the same assertion
# read from either end. Lines sort as text, which is why the report reads v0.10, v0.2,
# v0.9: the ORDER of the report is not what is under test, the verdict on each line is.
# Entries are read in either spelling the map may use, as hunk_map_git does.
since_git() {
  selected "$1" || return 0
  local name="$1" since="$2" want="$3"; shift 3
  local d code read_code page got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  cat > "$d/question.js" <<'JS'
var since = process.argv[3];

var mode = window.__VERI_SINCE__;
if (!mode || typeof mode.lit !== "function") {
  console.error("the page exposes no window.__VERI_SINCE__.lit(tag, since)");
  process.exit(1);
}

var hunks = window.__VERI_HUNKS__ || {};
var rows = [];
Object.keys(hunks).forEach(function (tag) {
  hunks[tag].forEach(function (entry) {
    var f = fields(entry);
    rows.push([tag, f[0], f[1] + "-" + f[2],
               mode.lit(tag, since) ? "lit" : "dim"].join(" "));
  });
});
rows.sort();
console.log(rows.join("\n"));
JS
  got="$(ask_page "$d" page.html "$since")" && read_code=0 || read_code=$?
  if [[ "$code" == 0 && "$read_code" == 0 && "$got" == "$want" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, since-mode read exit $read_code)"
    echo "    want, for a reader who last read at $since:"
    printf '%s\n' "$want" | sed 's/^/      /'
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -8
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# index_git <name> <chosen-version> <expected-report> <mutator...>
# since_git asks what a choice does to the LISTINGS; this asks what it does to the
# capability index, which is the other half of since-mode and a different question. The
# index at rest is every version the repo has ever cut, newest first. Choosing one
# collapses it to the versions after that — the reader is asking what they have missed,
# and a row for something they have already read is noise — and turns each surviving row
# into a table of contents for that version: the hunks it touched, so the reader can go
# straight to the lines rather than hunting the page for lit ones.
#
# Asked through ask_page for the same reason since_git is: the collapse happens when a
# reader picks a version, and the markup the build ships carries the full index, so there
# is nothing in the page to read it off. What it asks is
# `window.__VERI_SINCE__.index(since)` — the rows the index shows a reader who last read
# at `since`, each carrying its tag and the hunks it links to.
#
# What each row must KNOW is pinned, not how the link is spelt: a link to a hunk is the
# script it is in and the lines it runs between, and the label, the anchor and the <a>
# that carries them are markup this harness has no DOM to render or read back.
#
# The report is one line per surviving row — `<tag> <script> <first>-<last>, …`, or
# `<tag> -` for a row with no hunk under it — and the whole of it is compared, because the
# collapse is a claim about the rows that are NOT there as much as the ones that are. Rows
# sort as text, which is why the report reads v0.10 before v0.3: the order of the report
# is not what is under test. The links within a row sort by script and then by line, so
# they read in page order.
index_git() {
  selected "$1" || return 0
  local name="$1" since="$2" want="$3"; shift 3
  local d code read_code page got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  cat > "$d/question.js" <<'JS'
var since = process.argv[3];

var mode = window.__VERI_SINCE__;
if (!mode || typeof mode.index !== "function") {
  console.error("the page exposes no window.__VERI_SINCE__.index(since)");
  process.exit(1);
}

/* A row is its tag and its entries, in either spelling it may be written in: index_row()
   beside the stub is that reader, spelt once for both questions that make it. Its entries
   here are all hunks, entries of the map, so fields() beside the stub reads them. */
var rows = (mode.index(since) || []).map(function (row) {
  var links = entriesOf(row).map(fields);
  links.sort(function (a, b) {
    return a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : a[1] - b[1];
  });
  var text = links.map(function (f) { return f[0] + " " + f[1] + "-" + f[2]; });
  return tagOf(row) + " " + (text.length ? text.join(", ") : "-");
});
rows.sort();
console.log(rows.join("\n"));
JS
  got="$(ask_page "$d" page.html "$since")" && read_code=0 || read_code=$?
  if [[ "$code" == 0 && "$read_code" == 0 && "$got" == "$want" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, collapsed-index read exit $read_code)"
    echo "    want the index shown to a reader who last read at $since:"
    printf '%s\n' "$want" | sed 's/^/      /'
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -8
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# walk_git <name> <chosen-version> <expected-report> <mutator...>
# since_git asks which hunks a choice lights and index_git what that choice does to the
# capability index. This asks the third thing a reader does with them: getting from one to
# the next. Lit hunks are a handful of runs scattered through two thousand lines of
# listing, so a reader who has no way to step them is back to scrolling and reading every
# chip on the way past — which is what `n`, `p` and the two buttons in the crumb bar are
# for. All four step ONE sequence, and that sequence is what this pins:
# `window.__VERI_SINCE__.walk(since)`, the lit hunks in the order the page shows them.
#
# The sequence rather than the four things that step it, for the reason index_git already
# records about its links: a key binding and a button are DOM wiring, and this harness has
# no DOM to press a key in or click a button on. What it can ask is where a press has to
# land and in what order, which is the whole of the criterion that can be wrong — a walk
# in the wrong order sends the reader up the page as often as down it, whichever of the
# four started it.
#
# The report is one line per stop — `<script> <first>-<last>` — and, alone among the
# reports here, it is NOT sorted before it is compared: the order IS the assertion.
# Entries are read in either spelling the map may use, as hunk_map_git has it.
walk_git() {
  selected "$1" || return 0
  local name="$1" since="$2" want="$3"; shift 3
  local d code read_code page got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  cat > "$d/question.js" <<'JS'
var since = process.argv[3];

var mode = window.__VERI_SINCE__;
if (!mode || typeof mode.walk !== "function") {
  console.error("the page exposes no window.__VERI_SINCE__.walk(since)");
  process.exit(1);
}

/* Where pressing n from the top of the page takes the reader, stop by stop, and where
   p takes them back: one ordered sequence read in the order the page hands it over. */
var stops = (mode.walk(since) || []).map(function (hunk) {
  var f = fields(hunk);
  return f[0] + " " + f[1] + "-" + f[2];
});
console.log(stops.join("\n"));
JS
  got="$(ask_page "$d" page.html "$since")" && read_code=0 || read_code=$?
  if [[ "$code" == 0 && "$read_code" == 0 && "$got" == "$want" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, walk read exit $read_code)"
    echo "    want the stops n and p walk, for a reader who last read at $since:"
    printf '%s\n' "$want" | sed 's/^/      /'
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -8
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# new_script_git <name> <version-the-reader-read> <the-script-own-since> <expected-report> <mutator...>
# walk_git asks where a choice takes the reader among the LINES that changed. This asks
# the one stop that is not a line: a script that did not exist when the reader last read.
# `window.__VERI_HUNKS__` cannot hold it — hunks() drops every run at or below the file's
# own `since`, so a script that arrived whole has no hunk anywhere in it — which is why a
# walk built out of the map alone steps straight past it, and why the page was given each
# script's own `since` to rank it by.
#
# One page, asked twice, because the criterion has two halves that are the same sentence
# read from either end: for a reader whose version is EARLIER than the script's `since` it
# is a stop, and for one whose version IS that `since` it is not. A walk that treats every
# script as new is as wrong as one that treats none as new, and only the pair catches both.
#
# The report is one line per stop, `<version asked> <script> <where>`, in walk order and
# NOT sorted — the order is the assertion, as it is in walk_git. `<where>` is the line
# range for a stop the hunk map holds and the word `header` for one it does not, which is
# how a whole-script stop is told from a hunk without this harness deciding how a build
# spells it: an entry that is not in the map is not a run of lines, whatever shape it
# arrives in. Entries are read in either spelling the map may use, as walk_git has it,
# plus the bare file name, since a stop that is only a script has only a name to give.
new_script_git() {
  selected "$1" || return 0
  local name="$1" before="$2" after="$3" want="$4"; shift 4
  local d code read_code page got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  cat > "$d/question.js" <<'JS'
var mode = window.__VERI_SINCE__;
if (!mode || typeof mode.walk !== "function") {
  console.error("the page exposes no window.__VERI_SINCE__.walk(since)");
  process.exit(1);
}

/* A stop the hunk map holds a run for is a hunk, and a stop it does not is the script's
   header: runOrWhole() beside the stub is that lookup, spelt once for both questions that
   make it. */
var rows = [];
for (var i = 3; i < process.argv.length; i++) {
  var since = process.argv[i];
  (mode.walk(since) || []).forEach(function (stop) {
    rows.push(since + " " + runOrWhole(stop, "header"));
  });
}
console.log(rows.join("\n"));
JS
  got="$(ask_page "$d" page.html "$before" "$after")" && read_code=0 || read_code=$?
  if [[ "$code" == 0 && "$read_code" == 0 && "$got" == "$want" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, walk read exit $read_code)"
    echo "    want the stops walked by a reader who last read at $before, then at $after:"
    printf '%s\n' "$want" | sed 's/^/      /'
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -10
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# hash_git <name> <hash-the-page-is-opened-at> <version-then-chosen> <expected-report> <mutator...>
# since_git, index_git and walk_git all hand the page a version and ask what it does with
# it. This asks where that version comes from and where it goes: the URL. A reader who
# has lit the hunks they care about has nothing to send anyone and nothing to come back
# to — the choice lives in a variable that dies with the tab — unless the address bar
# carries it, which is the one piece of state a browser hands back on the next load.
#
# So this is the only assertion here that cares what the page was OPENED at. The hash goes
# into the environment rather than the question, because the question runs AFTER the page
# scripts and a reload is something they have to see at load: see VERI_ASK_HASH in the
# stub. The export is scoped to the command substitution, so no later case inherits it.
#
# What it asks is the pair that makes the round trip: `window.__VERI_SINCE__.since()`, the
# version the page came up in, and `.choose(tag)`, the reader picking one. Both have to be
# reachable without a browser for the reason walk_git records about `n` and `p` — the
# <select> that fires choose() and the chip that reads since() are DOM wiring this harness
# has no DOM to drive.
#
# The report is two lines — `opened <tag>` and `hash <what the URL carries>`, or `-` for
# neither — and both halves are needed: a hash nothing writes is never reloaded, and one
# nothing reads restores nothing. The leading `#` is stripped, because a browser puts it
# back on the getter whatever the page assigned and it is a delimiter, not the choice.
hash_git() {
  selected "$1" || return 0
  local name="$1" opened="$2" pick="$3" want="$4"; shift 4
  local d code read_code page got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  cat > "$d/question.js" <<'JS'
var pick = process.argv[3];

var mode = window.__VERI_SINCE__;
if (!mode || typeof mode.since !== "function" || typeof mode.choose !== "function") {
  console.error("the page exposes no window.__VERI_SINCE__.since() / .choose(tag)");
  process.exit(1);
}

/* Read before anything is touched: the page scripts have just run against a location
   carrying the hash this case was opened at, which is what a reload of that URL is. Then
   the other direction — a reader chooses, and the address has to follow. */
var opened = mode.since();
mode.choose(pick);

console.log("opened " + (opened || "-"));
console.log("hash " + (location.hash ? location.hash.replace(/^#/, "") : "-"));
JS
  got="$( export VERI_ASK_HASH="$opened"; ask_page "$d" page.html "$pick" )" \
    && read_code=0 || read_code=$?
  if [[ "$code" == 0 && "$read_code" == 0 && "$got" == "$want" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, URL round-trip read exit $read_code)"
    echo "    want, for a page opened at ${opened:--} whose reader then chooses $pick:"
    printf '%s\n' "$want" | sed 's/^/      /'
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -8
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# store_git <name> <expected-report> <mutator...>
# hash_git asks whether the choice survives a link being pasted. This asks whether it
# survives the reader doing nothing at all: closing the tab and coming back to the same
# bookmark they have always used, with no `#since=` on it. That is what the "mark read up
# to vX" button is for — one press says "I have read everything up to the newest version",
# and every visit after it opens on what has landed since, without the reader carrying a
# URL around.
#
# So the page is loaded THREE times, in three separate node processes, because a reload is
# precisely a process that keeps nothing but what was stored:
#
#   first load  nothing stored      -> the plain page, and the reader presses the button
#   next load   whatever that left  -> since-mode, at the newest version the page knows
#   blocked     the same store, but every read and write throws -> the plain page again
#
# The store is passed between the first two through the file VERI_ASK_STORE names, never
# by reading a key this harness picked: WHAT the page writes and under what name is its
# business, and a case that reads the key back would fail a page that changed the spelling
# of its own private storage while still restoring the mode perfectly. The only question
# is what the next load comes up in, which is `window.__VERI_SINCE__.since()` — the same
# reading hash_git takes, because "opens in since-mode" means one thing however the mode
# was reached. `.markRead()` is the button, asked directly for the reason walk_git records
# about `n` and `p`: the button is DOM wiring this harness has no DOM to click.
#
# The report is one line per load — `<which load> <the version it came up in, or `-`>`.
# All three are needed and none of them is spare. Without the first, a page whose since()
# always answers the newest version passes: the second line cannot tell a restored choice
# from a hardcoded one. Without the second, nothing has been persisted. Without the third,
# a page that reads storage unguarded passes, and it is exactly the reader whose browser
# refuses — private windows, cookies off, a locked-down corporate profile — who gets a
# blank page instead of the walkthrough. That last load fails the case if node exits
# non-zero, which is this harness's whole vocabulary for "the page did not come up".
store_git() {
  selected "$1" || return 0
  local name="$1" want="$2"; shift 2
  local d code read_code page got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  cat > "$d/question.js" <<'JS'
var label = process.argv[3], press = process.argv[4] === "mark";

var mode = window.__VERI_SINCE__;
if (!mode || typeof mode.since !== "function" || typeof mode.markRead !== "function") {
  console.error("the page exposes no window.__VERI_SINCE__.since() / .markRead()");
  process.exit(1);
}

/* What this load came up in, read before anything touches it: the page scripts have just
   run against whatever the store held, which is the whole of what the visit inherited. */
console.log(label + " " + (mode.since() || "-"));
if (press) mode.markRead();
JS
  got="$(
    export VERI_ASK_STORE="$d/store.json"
    ask_page "$d" page.html "first load" mark &&
      ask_page "$d" page.html "next load" &&
      { export VERI_ASK_STORE_BLOCKED=1; ask_page "$d" page.html "blocked" mark; }
  )" && read_code=0 || read_code=$?
  if [[ "$code" == 0 && "$read_code" == 0 && "$got" == "$want" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, three-load read exit $read_code)"
    echo "    want, across a press of the button and two loads after it:"
    printf '%s\n' "$want" | sed 's/^/      /'
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -8
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# wiring_git <name> <chosen-version> <expected-report> <mutator...>
# walk_git pins the sequence the reader is stepped through; this pins the stepping. The
# two are deliberately separate assertions of separate things: a walk in the right order
# that no key and no button moves is a list nobody can use, and it passes walk_git
# untouched, because a function returning the right array is the whole of what that case
# can see.
#
# So this one runs the page under the wired DOM — see VERI_ASK_WIRED in the stub — and
# does what a reader does: presses `n`, presses it again, clicks the next button, presses
# `p`, clicks the previous button. After each one it reads which hunk mark the page
# scrolled to.
#
# Two loads, because the criterion has two halves and the second is about the page a
# reader who has chosen NOTHING gets:
#
#   at rest    no hash, nothing stored -> the crumb bar carries no walk buttons at all
#   since-mode opened at `#since=vX`   -> both buttons, and all four steppers walking
#
# Buttons a reader cannot reach are not buttons, so they are found by the name a reader
# calls them by — the text they carry, or the label a screen reader is given — and not by
# class or by position in the bar. Absent at rest means absent: a button rendered disabled,
# or hidden by a class, is still in the crumb bar of a page that has nothing to walk.
#
# The report is one line for the buttons of each load and one per press —
# `<press> #<the mark's place in the page, top first> <its tag>` — and the whole of it is
# compared, order included, because every claim in the criterion is a line of it: that the
# keys move, that the buttons move the same walk, that `p` goes back up the page, and that
# a press lands on a stop rather than somewhere. `-` is a press that scrolled nothing.
wiring_git() {
  selected "$1" || return 0
  local name="$1" since="$2" want="$3"; shift 3
  local d code read_code page got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  cat > "$d/question.js" <<'JS'
var label = process.argv[3], presses = process.argv.slice(4);

wired();

/* What a reader would call this button: what it says, or what it tells a screen reader
   it says. Which of the two an implementation uses is a spelling choice; having neither
   is a button nobody can name. */
function named(el) {
  return [el.textContent, el.innerHTML,
          el.getAttribute("aria-label"), el.getAttribute("title")]
    .filter(function (part) { return part; }).join(" ").toLowerCase();
}

/* Every clickable thing the page put in the crumb bar, however deep it nested them: a
   pair of buttons inside a wrapper is the same two buttons to the reader. */
function clickables(el, found) {
  (el.children || []).forEach(function (child) {
    if (child.handlers && child.handlers.click) found.push(child);
    clickables(child, found);
  });
  return found;
}

var inBar = clickables(document.querySelector(".crumb"), []);
function button(word) {
  for (var i = 0; i < inBar.length; i++) {
    if (named(inBar[i]).indexOf(word) >= 0) return inBar[i];
  }
  return null;
}
var next = button("next"), previous = button("prev");

console.log(label + " buttons " +
            ([next ? "next" : "", previous ? "previous" : ""]
               .filter(function (b) { return b; }).join(" ") || "none"));

function click(btn) {
  var event = { type: "click", target: btn,
                preventDefault: function () {}, stopPropagation: function () {} };
  (btn.handlers.click || []).forEach(function (handler) { handler(event); });
}

presses.forEach(function (what) {
  globalThis.__scrolled = null;
  if (what === "n" || what === "p") press(what);
  else {
    var btn = what === "next" ? next : previous;
    if (!btn) { console.log(what + " no such button"); return; }
    click(btn);
  }
  var at = globalThis.__scrolled;
  console.log(what + " " +
              (at && at.position ? "#" + at.position + " " + at.getAttribute("data-tag")
                                 : "-"));
});
JS
  got="$(
    export VERI_ASK_WIRED=1
    ask_page "$d" page.html "at rest" &&
      { export VERI_ASK_HASH="#since=$since"
        ask_page "$d" page.html "since $since" n n next p previous; }
  )" && read_code=0 || read_code=$?
  if [[ "$code" == 0 && "$read_code" == 0 && "$got" == "$want" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, wiring read exit $read_code)"
    echo "    want, for a reader who last read at $since stepping the walk:"
    printf '%s\n' "$want" | sed 's/^/      /'
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -10
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# header_wiring_git <name> <version-the-reader-read> <the-script-own-since> <expected-report> <mutator...>
# new_script_git pins the sequence a new script belongs in; this pins the page landing the
# reader on it. The two are the same split wiring_git and walk_git already are, and it is
# load-bearing here for a reason it was not there: a walk whose entries are file names is
# not a walk anyone can take until something in the MARKUP answers to a file name. The
# hunks had marks already — the build has emitted `<span class="l hunk" data-tag=…>` since
# the version layer landed — and a script that arrived whole has nothing of the kind, so an
# implementation can compute a perfect sequence, be green on new_script_git, and step the
# reader straight past the script because the stepper collects hunk marks and finds none.
#
# So the page runs in the wired DOM — see VERI_ASK_WIRED in the stub — and the reader
# presses `n`. `n` alone, where wiring_git presses both keys and clicks both buttons: that
# case pins that all four step ONE walk, and what is new here is what that walk's stops are
# made of. `p` is pressed once at the end because the header has to be a stop from both
# directions — a reader who steps past it must be able to come back to it.
#
# One page, opened twice, as new_script_git opens it twice and for the same reason: the
# criterion is one sentence read from either end. A reader whose version is EARLIER than
# the script's `since` is taken to its header; one whose version IS that `since` is taken to
# the hunk inside it and never to the header, because they have read the script already.
#
# The report is one line per press — `<version opened at> <key> <where it landed>` — and
# where is the script the element belongs to plus what it is: the tag for a hunk mark, the
# word `header` for an element of a script's header, which is how new_script_git's report
# spells the same distinction. `-` is a press that scrolled nothing. The whole report is
# compared, order included: the order IS the claim, since a header ranked anywhere but
# before its own hunks is a reader sent to the middle of a file they have never seen.
header_wiring_git() {
  selected "$1" || return 0
  local name="$1" before="$2" after="$3" want="$4"; shift 4
  local d code read_code page got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  cat > "$d/question.js" <<'JS'
var label = process.argv[3], presses = process.argv.slice(4);

wired();

/* Where a press landed, in the page's own terms: the script whose listing or whose header
   the element sits in — which the stub read off the markup around it — and then which of
   the two it is. A hunk names the tag it carries, because that is what tells one run of
   lines from another; a header has only the script to name, and says so. */
function where(el) {
  if (!el) return "-";
  return el.script + " " + (el.kind === "header" ? "header" : el.getAttribute("data-tag"));
}

presses.forEach(function (key) {
  globalThis.__scrolled = null;
  press(key);
  console.log(label + " " + key + " " + where(globalThis.__scrolled));
});
JS
  got="$(
    export VERI_ASK_WIRED=1
    { export VERI_ASK_HASH="#since=$before"
      ask_page "$d" page.html "$before" n n n p; } &&
      { export VERI_ASK_HASH="#since=$after"
        ask_page "$d" page.html "$after" n n; }
  )" && read_code=0 || read_code=$?
  if [[ "$code" == 0 && "$read_code" == 0 && "$got" == "$want" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, wiring read exit $read_code)"
    echo "    want, for a reader stepping the page opened at $before, then at $after:"
    printf '%s\n' "$want" | sed 's/^/      /'
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -10
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# new_index_git <name> <version-the-reader-read> <the-script-own-since> <expected-report> <mutator...>
# index_git asks what a choice does to the capability index when every row is a run of
# changed lines. This asks the one row that is not a run: the version a script ARRIVED in.
# The index is where the reader makes the choice and the only place on the page that says
# WHERE a version changed something, so a version whose whole contribution was a new script
# renders there as a row with nothing under it — the reader is told that version touched
# nothing this page quotes, about a version that added a file to it. `window.__VERI_HUNKS__`
# cannot fill that row: hunks() drops every run at or below the file's own `since`, so a
# script that arrived whole has no hunk anywhere in it, which is why the page was given
# each script's own `since` to rank it by.
#
# One page, asked twice, because the criterion is one sentence read from either end, as
# new_script_git's is: for a reader whose version is EARLIER than the script's `since` the
# arrival version is a row and the script is listed in it, and for one whose version IS
# that `since` the script is listed nowhere — they have read it. A row that lists every
# script as new is as wrong as one that lists none, and only the pair catches both.
#
# The report is one line per row per load — `<version asked> <tag> <entries>`, or
# `<version asked> <tag> -` for a row with nothing under it — and the whole of it is
# compared, because the claim is as much about the rows the script is NOT listed in as the
# one it is. An entry is `<script> <first>-<last>` when the hunk map holds that run and
# `<script> new` when it does not, which is how new_script_git tells a whole-script stop
# from a hunk without this harness deciding how a build spells either: whether the row
# renders it with a middot, a badge or the word alone is markup, and there is no DOM here
# to read it back from. Rows sort as text within a load, as index_git has it — the order of
# the report is not what is under test.
new_index_git() {
  selected "$1" || return 0
  local name="$1" before="$2" after="$3" want="$4"; shift 4
  local d code read_code page got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  cat > "$d/question.js" <<'JS'
var mode = window.__VERI_SINCE__;
if (!mode || typeof mode.index !== "function") {
  console.error("the page exposes no window.__VERI_SINCE__.index(since)");
  process.exit(1);
}

/* A row is its tag and its entries, in either spelling it may be written in: index_row()
   beside the stub is that reader, the same one index_git makes.

   An entry the hunk map holds a run for is a hunk, and one it does not is the script
   itself: runOrWhole() beside the stub is that lookup, the same one new_script_git makes
   of a stop, and only the word for a whole script differs. */
var rows = [];
for (var i = 3; i < process.argv.length; i++) {
  var since = process.argv[i];
  var shown = (mode.index(since) || []).map(function (row) {
    var text = entriesOf(row).map(function (e) { return runOrWhole(e, "new"); });
    text.sort();
    return since + " " + tagOf(row) + " " + (text.length ? text.join(", ") : "-");
  });
  shown.sort();
  rows = rows.concat(shown);
}
console.log(rows.join("\n"));
JS
  got="$(ask_page "$d" page.html "$before" "$after")" && read_code=0 || read_code=$?
  if [[ "$code" == 0 && "$read_code" == 0 && "$got" == "$want" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, collapsed-index read exit $read_code)"
    echo "    want the index shown to a reader who last read at $before, then at $after:"
    printf '%s\n' "$want" | sed 's/^/      /'
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -10
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# paint_git <name> <chosen-version> <expected-report> <mutator...>
# Every since-mode case above asks the decision layer what it would answer. This asks what
# the reader SEES, which is a different claim and the one the layer exists for: an
# implementation whose lit(), index() and walk() are all perfect and which touches no
# element on the page is green on cases 21-31 and ships a walkthrough that looks exactly
# like the one that has no since-mode in it.
#
# So the page runs in the wired DOM — see VERI_ASK_WIRED in the stub — where a class the
# page adds is a class this harness can read back and a row it hides stays hidden. Two
# loads, because the criterion has two halves and neither is worth anything alone:
#
#   at rest    no hash, nothing stored -> nothing painted, every row showing
#   since-mode opened at `#since=vX`   -> every mark lit or dim, the rows collapsed
#
# The marks are asked for by the version they CARRY — `[data-tag], [data-since]` — and not
# by what they are. One query is what makes this case cover all three of the things the
# criterion names: a hunk's first line, a script's header, and the commentary chip, which
# carries a `data-tag` of its own. The report is one line per version the page carries and
# per paint the marks carrying it were given — `<load> mark <version> lit|dim|-`, `-` for
# a mark carrying neither class, `both` for one carrying the pair — so every mark on the
# page is accounted for by a line, and a layer that paints the headers and forgets the
# hunks reports two lines where the whole page agreeing reports one. Counts are left out
# deliberately: how many elements carry a version is a build detail, and the claim is that
# all of them were painted the same way.
#
# The rows are `<load> row <version> shown|hidden`, by the version each one prints. Hidden
# is read in the two spellings that need no stylesheet to interpret — the `hidden`
# attribute, or an inline `display:none` — because there is no rendering here and a class
# whose fade lives in the stylesheet would have to be spelt into this harness to be seen.
# Lines sort as text within a load, as index_git has it: the order of the report is not
# what is under test, the verdict on each line is.
paint_git() {
  selected "$1" || return 0
  local name="$1" since="$2" want="$3"; shift 3
  local d code read_code page got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  cat > "$d/question.js" <<'JS'
var label = process.argv[3];

wired();

/* Which of the two classes a mark was given, or neither. `both` is its own answer rather
   than a preference for one of them: a mark that is lit and dimmed at once is a page
   telling the reader two things, and which one the stylesheet happens to win with is not
   something this harness can see. */
function paint(el) {
  var isLit = el.classList.contains("lit"), isDim = el.classList.contains("dim");
  return isLit && isDim ? "both" : isLit ? "lit" : isDim ? "dim" : "-";
}

/* Gone from the page, in the two spellings a page can use without a stylesheet to say it
   in. The property and the attribute are both read because assigning `el.hidden = true`
   and calling setAttribute("hidden", "") are the same thing to a browser and two
   different ones to a stub. */
function gone(el) {
  return !!el.hidden || el.hasAttribute("hidden") || el.style.display === "none";
}

var lines = {};
var marks = document.querySelectorAll("[data-tag], [data-since]");
for (var i = 0; i < marks.length; i++) {
  var version = marks[i].getAttribute("data-tag") ||
                marks[i].getAttribute("data-since");
  lines[label + " mark " + version + " " + paint(marks[i])] = true;
}

var rows = document.querySelectorAll("li.ver");
for (var r = 0; r < rows.length; r++) {
  lines[label + " row " + rows[r].version + " " + (gone(rows[r]) ? "hidden" : "shown")]
    = true;
}

console.log(Object.keys(lines).sort().join("\n"));
JS
  got="$(
    export VERI_ASK_WIRED=1
    ask_page "$d" page.html "at rest" &&
      { export VERI_ASK_HASH="#since=$since"
        ask_page "$d" page.html "since $since"; }
  )" && read_code=0 || read_code=$?
  if [[ "$code" == 0 && "$read_code" == 0 && "$got" == "$want" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, paint read exit $read_code)"
    echo "    want, on the resting page and then for a reader who last read at $since:"
    printf '%s\n' "$want" | sed 's/^/      /'
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -24
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# control_git <name> <version-the-page-is-opened-at> <version-the-reader-picks> <expected-report> <mutator...>
# Every case above is about a choice the reader has already made — the hash they arrived
# with, the version they pressed the button on. This is the making of it: the control the
# whole mode is reached through, which the page does not have, so the only reader who can
# be in since-mode today is one who types `#since=vX` into the address bar themselves.
#
# The page runs in the wired DOM — see VERI_ASK_WIRED in the stub — because there is no
# other way to ask: a <select> nobody can change and a button nobody can click answer
# nothing about their own wiring. Two loads, because the claim has an end in each:
#
#   at rest    no hash, nothing stored -> the control is there, offering every version and
#                                         showing none of them; the reader picks one and the
#                                         page repaints, having never reloaded
#   since vX   opened at `#since=vX`   -> the control comes up already showing what the
#                                         address says, and follows it when it changes
#
# The steps are argv, so the same question asks both loads:
#
#   options     what the select offers — the versions it names, newest first, then `+none`
#               for the option that names none of them, or `+none-missing` for its absence.
#               The versions are ordered as the select lists them and the none option is
#               not, because where a page puts "everything" in the list is a taste and the
#               order of the versions is not: v0.10 and v0.9 sort the wrong way as text,
#               which is the trap this layer has turned on since case 21.
#   shows       the version the select is displaying, or `none`
#   button      the version the "mark read up to vX" button names, found by what it says to
#               a reader or to a screen reader and never by its class — a button found by a
#               class this harness knows is a button the reader cannot find. X is the newest
#               version, which is the whole of what the button means.
#   click       the button pressed, and what `since()` answers afterwards
#   pick=vX     the reader choosing vX in the select, and what `since()` answers afterwards:
#               the select is wired to choose(), whatever route it takes to it.
#   paint       what that choice did to the page, read exactly as case 32 reads it — one
#               line per version the marks carry — because "updates the paint" means the
#               paint case 32 pins, arrived at without a reload.
#   hash=vX     the address changing under the page, which is the reader pressing Back or
#               editing the address bar. The stub fires `hashchange` on the assignment, as
#               a browser does, so nothing here is delivered that a browser would not.
#
# A load whose control is missing reports `-` and goes on, so the first run of this case
# names everything the page lacks rather than dying on the first thing.
control_git() {
  selected "$1" || return 0
  local name="$1" opened="$2" pick="$3" want="$4"; shift 4
  local d code read_code page got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  printf '%s' "$page" > "$d/page.html"
  cat > "$d/question.js" <<'JS'
var label = process.argv[3], steps = process.argv.slice(4);

wired();

var mode = window.__VERI_SINCE__;
if (!mode || typeof mode.since !== "function") {
  console.error("the page exposes no window.__VERI_SINCE__.since()");
  process.exit(1);
}

/* What a reader would call this control: what it says, or what it tells a screen reader it
   says. Which of the four an implementation uses is a spelling choice; having none of them
   is a control nobody can name, and nobody can name is nobody can find. */
function named(el) {
  return [el.textContent, el.innerHTML,
          el.getAttribute("aria-label"), el.getAttribute("title")]
    .filter(function (part) { return part; }).join(" ").toLowerCase();
}

/* The version an option offers, or "" for the one that offers none. A tag may be the value
   the option submits or the text it shows — an implementation can put it in either and a
   reader reads the same list — so a version found in either place is that option's version,
   and an option naming no version at all is the none option however it is worded. */
function offered(opt) {
  var found = /v\d+\.\d+/.exec([opt.value, opt.getAttribute("value"),
                                opt.textContent, opt.innerHTML]
                                 .filter(function (p) { return p; }).join(" "));
  return found ? found[0] : "";
}

/* The version the select is displaying. A page may say it by assigning the select's value
   or by marking the option selected, which are the same thing to a reader. */
function showing(sel) {
  var picked = (sel.children || []).filter(function (o) { return o.selected; })[0];
  var found = /v\d+\.\d+/.exec(String(sel.value || "")) ||
              (picked ? /v\d+\.\d+/.exec(offered(picked)) : null);
  return found ? found[0] : "none";
}

/* Which of the two classes a mark was given, or neither — case 32's reading, and `both` is
   its own answer there for the reason it is here: a repaint that adds the new class without
   taking the old one off has left the reader a mark that is news and read at once. */
function paint(el) {
  var isLit = el.classList.contains("lit"), isDim = el.classList.contains("dim");
  return isLit && isDim ? "both" : isLit ? "lit" : isDim ? "dim" : "-";
}

/* An event delivered to one element, both ways a page can be listening for it. */
function fire(el, type) {
  var event = { type: type, target: el,
                preventDefault: function () {}, stopPropagation: function () {} };
  ((el.handlers || {})[type] || []).forEach(function (handler) { handler(event); });
  if (typeof el["on" + type] === "function") el["on" + type](event);
}

var offer = null, button = null;
globalThis.__controls().forEach(function (el) {
  if (!offer && el.tagName === "SELECT") offer = el;
  if (!button && el.tagName === "BUTTON" && /mark read up to/.test(named(el))) button = el;
});

function say(what) { console.log(label + " " + what); }

steps.forEach(function (step) {
  var how = step.split("=")[0], arg = step.split("=")[1];

  if (how === "options") {
    if (!offer) return say("select -");
    var all = (offer.children || []).map(offered);
    var versions = all.filter(function (v) { return v; });
    say("select " + (versions.join(" ") || "-") +
        (all.length > versions.length ? " +none" : " +none-missing"));

  } else if (how === "shows") {
    say("select " + (offer ? "shows " + showing(offer) : "-"));

  } else if (how === "button") {
    var says = button ? /mark read up to\s+(v\d+\.\d+)/.exec(named(button)) : null;
    say("button " + (says ? "mark read up to " + says[1] : "-"));

  } else if (how === "click") {
    if (!button) return say("click -");
    fire(button, "click");
    say("click -> since " + (mode.since() || "-"));

  } else if (how === "pick") {
    if (!offer) return say("pick " + arg + " -> no select");
    offer.value = arg;
    fire(offer, "change");
    say("pick " + arg + " -> since " + (mode.since() || "-"));

  } else if (how === "paint") {
    var lines = {};
    var marks = document.querySelectorAll("[data-tag], [data-since]");
    for (var i = 0; i < marks.length; i++) {
      lines["paint " + (marks[i].getAttribute("data-tag") ||
                        marks[i].getAttribute("data-since")) +
            " " + paint(marks[i])] = true;
    }
    Object.keys(lines).sort().forEach(say);

  } else if (how === "hash") {
    location.hash = "#since=" + arg;
    say("hashchange " + arg);
  }
});
JS
  got="$(
    export VERI_ASK_WIRED=1
    ask_page "$d" page.html "at rest" options shows button click "pick=$pick" paint &&
      { export VERI_ASK_HASH="#since=$opened"
        ask_page "$d" page.html "since $opened" shows "hash=$pick" shows; }
  )" && read_code=0 || read_code=$?
  if [[ "$code" == 0 && "$read_code" == 0 && "$got" == "$want" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code, control read exit $read_code)"
    echo "    want, on the resting page and then on one opened at $opened:"
    printf '%s\n' "$want" | sed 's/^/      /'
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -20
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# checks_git <name> <mutator...>
# Every other assertion here reads the page build-walkthrough.py produced. This one hands
# that page to docs/check-walkthrough.py, which reads the markup back and re-derives the
# same properties from the files on disk — so the two have to agree about what the markup
# is. A page the build is happy to emit and the checker calls drift is a broken pipeline
# even though each half passes its own tests, and `make docs-check` runs both halves.
# The page is written to disk rather than --stdout, because that is the file the checker
# opens. Failure prints the tail of the combined output: the checker's FAIL lines come
# last, and a build that died instead leaves its traceback in the same place.
checks_git() {
  selected "$1" || return 0
  local name="$1"; shift
  local d code out; d="$(sandbox_check)"
  ( cd "$d" && "$@" )
  out="$( cd "$d" && python3 docs/build-walkthrough.py >/dev/null 2>&1 \
                  && python3 docs/check-walkthrough.py 2>&1 )" && code=0 || code=$?
  if [[ "$code" == 0 ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want: check-walkthrough.py passes on the page the build just wrote"
    printf '%s\n' "$out" | sed 's/^/    | /' | tail -6
  fi
}

# names_all <text> <names-one-per-line> — true when every one of <names> appears in <text>.
# The claim a diagram has to satisfy, on its own so the assertion below reads as one line:
# a block either names them all or it does not. Not shared with tags_git's near-identical
# loop, which cannot return early — its failure message has to say WHICH span it missed.
names_all() {
  local hay="$1" want
  while IFS= read -r want; do
    [[ "$hay" == *"$want"* ]] || return 1
  done <<< "$2"
}

# diagram_blocks <open-re> <close-re> — page on stdin, one diagram block per line on
# stdout. The slice runs from the line matching <open-re> to the line matching <close-re>:
# a stage's intro, bounded by its own heading and by whatever landmark follows it. Inside
# the slice, a diagram is a <pre class="src"> sketch or an inline <svg> — the two idioms
# the page already uses — and each one comes back flattened onto a single line, so a caller
# can match a whole block with one string test.
# The awk reads to the end rather than `exit`ing at the closing landmark: exiting mid-page
# leaves the printf feeding a closed pipe, and the SIGPIPE write error lands in the suite's
# output as if a case had broken. Reading on is why `past_slice` exists — once the slice has
# closed, a later line matching <open-re> must not reopen it.
diagram_blocks() {
  awk -v open_re="$1" -v close_re="$2" '
    $0 ~ open_re && !past_slice                 { in_slice = 1 }
    in_slice && $0 ~ close_re                   { in_slice = 0; past_slice = 1 }
    in_slice && /<pre class="src"|<svg/         { blk = ""; in_block = 1 }
    in_slice && in_block                        { blk = blk " " $0 }
    in_slice && in_block && /<\/pre>|<\/svg>/   { print blk; in_block = 0 }
  '
}

# diagrams_in_slice <name> <open-re> <close-re> <what-closes-it> <names-one-per-line>
# accepts() asks its question of the whole page; this one is about one slice of it. Every
# script name a stage draws is already on the page many times over: in the rail, in the
# intro's own prose, in its own listing. So a whole-page match, or even a whole-slice one,
# would be green before anything is drawn. This demands ONE of the slice's diagram blocks
# name every one of <names> — one block, not the slice, because names scattered through
# the prose around a diagram are prose.
# <names> is one argument holding one name per line, for the same reason tags_git takes
# its spans that way: the claim is about all of them appearing together.
diagrams_in_slice() {
  selected "$1" || return 0
  local name="$1" open_re="$2" close_re="$3" ends_at="$4" wants="$5"
  local d code page blocks blk found="" n=0; d="$("$SANDBOX")"
  page="$(build "$d")" && code=0 || code=$?
  blocks="$(printf '%s\n' "$page" | diagram_blocks "$open_re" "$close_re")"
  while IFS= read -r blk; do
    [[ -n "$blk" ]] || continue
    n=$((n + 1))
    names_all "$blk" "$wants" && found="yes"
  done <<< "$blocks"
  if [[ "$code" == 0 && -n "$found" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want one diagram between $open_re and $ends_at, naming: $wants"
    echo "    got  $n diagram block(s) in that slice, none naming all of them"
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# diagrams_stage0 <name> <names-one-per-line>
# Stage 0's intro is followed by the scripts it annotates, so "up to the first <h3 id="
# cuts the intro exactly.
diagrams_stage0() { diagrams_in_slice "$1" 'id="s0"' '<h3 id=' 'the first script' "$2"; }

# diagrams_stage5 <name> <names-one-per-line>
# Stage 5 cannot borrow stage 0's closing landmark: it is the final stage, so what follows
# its scripts is the reference section — `id="reference"` — and that is the only landmark
# that closes it. Both landmarks occur once each in the page, as `id=`: the rail's links to
# the same two places are `href="#s5"` and `href="#reference"`, which this does not match.
# Why that wider slice is safe is a question about the names a case asks for, not about the
# slice, so each case below answers it for its own names.
diagrams_stage5() { diagrams_in_slice "$1" 'id="s5"' 'id="reference"' 'the reference section' "$2"; }

# --- helpers used as mutators (run with cwd = the sandbox) ---------------------

# The one script the mutators below break on purpose — the coverage guard's victim and the
# file the version-layer cases rewrite lines of. Written down once so a rename of it, or of
# the skill directory it sits in, is one edit rather than eight. It is exported rather than
# interpolated at the call sites because those run under `bash -c '…'`: single quotes keep
# the expansion out of this shell, where the sandbox is not the cwd yet, and hand it to the
# child that runs inside the sandbox — the same reason the mutator functions are exported.
SAMPLE_SCRIPT=skills/tdd/scripts/classify-bail.sh
export SAMPLE_SCRIPT

append_line_to_script() { printf '\n# a line the commentary does not cover\n' >> "$1"; }
sed_commentary() { sed -i.bak "$1" docs/wt/commentary.py && rm -f docs/wt/commentary.py.bak; }

# rewrite_hunk_as_feat <file> <first> <last> <text> <subject> <tag>
# Rewrite a RANGE of lines of a script in place, then land the whole range as ONE commit
# and cut the tag it ships in — one commit, so blame answers the same sha for every line
# in it and they are therefore one hunk, which is what a hunk needs in order to have an
# extent worth reporting. Rewriting rather than adding is deliberate: the line count does
# not move, so the coverage guard has nothing to say and the case tests only the version
# layer.
rewrite_hunk_as_feat() {
  local file="$1" first="$2" last="$3" text="$4" subject="$5" tag="$6"
  sed -i.bak "${first},${last}s|.*|$text|" "$file" && rm -f "$file.bak"
  git add -A && git commit -qm "$subject" && git tag -a "$tag" -m "what $tag can do"
}

# rewrite_line_as_feat <file> <line-no> <text> <subject> <tag>
# The one-line hunk: the range above with both ends on the same line. Most cases here
# want exactly that, and naming the line once rather than twice keeps them readable.
rewrite_line_as_feat() {
  local file="$1" lineno="$2"; shift 2
  rewrite_hunk_as_feat "$file" "$lineno" "$lineno" "$@"
}

# rewrite_line_as_refactor <file> <line-no> <text> <subject>
# The same rewrite, landed as a NON-behaviour commit — and deliberately with no tag of
# its own, because a refactor does not change what veri can do, so veri's own convention
# never cuts one for it. It ships in whatever version is tagged next, which is the point:
# the commit ends up inside a later version's range and its line must still stay plain.
rewrite_line_as_refactor() {
  local file="$1" lineno="$2" text="$3" subject="$4"
  sed -i.bak "${lineno}s|.*|$text|" "$file" && rm -f "$file.bak"
  git add -A && git commit -qm "$subject"
}
# rewrite_two_lines_as_feat <file> <first> <second> <text> <subject> <tag>
# Two lines that are NOT adjacent, rewritten by ONE commit, and the tag it ships in.
# Blame answers the same sha for both and the untouched lines between them break the run
# in two, so this is one version owning two hunks — which is what a version row listing
# "every hunk that version touched" needs in order to say more than "the hunk".
rewrite_two_lines_as_feat() {
  local file="$1" a="$2" b="$3" text="$4" subject="$5" tag="$6"
  sed -i.bak -e "${a}s|.*|$text|" -e "${b}s|.*|$text|" "$file" && rm -f "$file.bak"
  git add -A && git commit -qm "$subject" && git tag -a "$tag" -m "what $tag can do"
}

# add_script_as_feat <file> <id> <stage> <subject> <tag>
# A script the page lists that did NOT ship in the first version — the one history every
# mutator above is unable to produce, because rewriting a line leaves every script's
# `since` at v0.1 where sandbox_git put it. Three things have to land together for the
# build to accept it: the file itself, the commentary chunk claiming its lines (without
# which the coverage guard refuses the whole build), and the behaviour commit and tag it
# arrives in.
# The entry is appended, which puts the script last within its stage — stage 2 lands it
# after supervise.sh and before classify-bail.sh, which is the page order the case below
# walks through.
add_script_as_feat() {
  local file="$1" id="$2" stage="$3" subject="$4" tag="$5"
  cat > "skills/tdd/scripts/$file" <<'SH'
#!/usr/bin/env bash
# the line a later version rewrites
set -euo pipefail
printf '%s\n' "a script that arrived whole"
SH
  cat >> docs/wt/commentary.py <<PY

SCRIPTS += [dict(
    file="$file", stage=$stage, id="$id",
    tagline="arrived whole in a later version",
    blurb="<p>A script that did not exist in the first version.</p>",
    chunks=[dict(lines=(1, 4), html="<p>The whole of it, in one chunk.</p>")],
)]
PY
  git add -A && git commit -qm "$subject" && git tag -a "$tag" -m "what $tag can do"
}

# tag_feat_outside_the_scripts <subject> <tag>
# A version that changed a capability without touching a single line this page quotes —
# the conductor-only row the index already renders as "Conductor only". The commit has to
# land somewhere, so it lands in the stylesheet, which the build inlines and no listing
# shows.
tag_feat_outside_the_scripts() {
  printf '\n/* %s */\n' "$1" >> docs/wt/style.css
  git add -A && git commit -qm "$1" && git tag -a "$2" -m "what $2 can do"
}
export -f append_line_to_script sed_commentary rewrite_line_as_refactor
export -f rewrite_hunk_as_feat rewrite_line_as_feat
export -f rewrite_two_lines_as_feat tag_feat_outside_the_scripts add_script_as_feat

# 1. baseline: an unmutated tree builds, and emits real source verbatim
accepts "baseline builds" '<title>veri, Annotated</title>'
accepts "emits script source verbatim" '/veri/classify_bail.py' 

# 2. coverage guard — a script grows a line the commentary does not claim. Deleted in
#    issue #125, which reversed exactly this: that tree is the one case 3b below builds,
#    and the claim there is that it exits 0. The two cases ran the SAME mutator and
#    demanded opposite outcomes, so this one could not be left in — a suite cannot hold
#    both halves of a reversal. Its other half survives as case 3: commentary claiming
#    lines the file does not have is still a wrong range, not debt.

# 3. coverage guard — a script loses a line
refuses "a shorter script fails coverage" "file has" \
  bash -c 'sed -i.bak "3,\$d" "$SAMPLE_SCRIPT"'

# 3b. and the reversal of case 2 (issue #125). A script that grew a line the commentary
#     does not claim is DEBT, not a broken build: development moves at its own pace and
#     the prose catches up on its own, so a gap must not be able to block a script from
#     landing. The build carries it instead — exit 0, the uncovered line in the listing
#     with a mark a reader can see, and one `owed:` line per gap on stderr so whoever ran
#     the build knows what the page is behind on.
#
#     The line must render PLAIN — `<span class="l">`, the same opening every uncovered
#     line of every listing gets — because the page's one promise is the source verbatim,
#     and the half of that promise this case guards is that a gap in the prose costs the
#     reader no source at all.
#
#     The range is read off the real script rather than written down: append_line_to_script
#     adds two lines to the end of it, a blank and the comment, so the debt is that pair
#     and nothing else. Naming them by arithmetic means classify-bail.sh growing a line
#     moves the expected range with it instead of making this case wrong.
owed_from=$(( $(wc -l < "$ROOT/$SAMPLE_SCRIPT") + 1 ))
owes "an uncovered script line is owed, not refused" \
  '<span class="l"><span class="c"># a line the commentary does not cover</span></span>
commentary owed' \
  "owed: classify-bail.sh L8–$((owed_from + 1))" \
  bash -c 'append_line_to_script "$SAMPLE_SCRIPT"'

# 3c. and the gap that is NOT at the end of the file (issue #125). Case 3b's uncovered run
#     is the tail: everything after the last chunk, which is a run with no chunk after it.
#     A run between two chunks is the other shape of the same debt, and a build that
#     carried only the tail would still refuse this tree — or, worse, close the gap by
#     dropping the two lines out of the listing, which is the promise (the source,
#     verbatim) breaking quietly. So the claim is all three halves again, with the range
#     naming the interior lines rather than the ones past the end.
#
#     The debt is made by moving ONE chunk's start two lines later, not by touching the
#     script: classify-bail.sh is unchanged, the chunk before still ends at L11, the chunk
#     after still ends at L18, and L12–13 are left claimed by nobody. Those numbers are
#     the ones written in the chunk table this sed edits, so if that table ever moves, the
#     sed matches nothing, the tree owes nothing and this case fails — loudly, rather than
#     passing on a build that was never given a gap to carry.
#
#     The two source lines are asked for by their exact markup for the same reason case 3b
#     asks for its one: `<span class="l">` is the opening every unmarked line gets, so
#     finding them proves the gap cost the reader no source.
owes "an interior gap is owed with its own range" \
  '<span class="l">#!/bin/sh</span>
commentary owed' \
  "owed: classify-bail.sh L1–2" \
  bash -c 'sed_commentary "s/lines=(1, 7)/lines=(3, 7)/"'

# 4. unknown-reference guard — a typo'd id must not become a dead tooltip
refuses "unknown reference id is refused" "unknown primer ref" \
  bash -c 'sed_commentary "s/{{p-strict|set -euo pipefail}}/{{p-stirct|set -euo pipefail}}/"'

# 4b. and the half of that guard the reversal put at risk (issue #125). Case 4 typos a ref
#     in a tree that is otherwise clean, so the build has no other reason to exit 0 and
#     nothing distinguishes "the typo is fatal" from "the build had nothing to tolerate".
#     Since case 3b there IS such a reason: a gap in the commentary now buys exit 0 and a
#     line on stderr. So this case puts both in the same tree — the uncovered line AND the
#     typo — and demands the build still refuse. A typo is not debt: the page can ship
#     prose nobody has written yet, but not a tooltip that points at nothing.
refuses "a dead reference in a tree that also owes commentary is refused" "unknown primer ref" \
  bash -c 'append_line_to_script "$SAMPLE_SCRIPT"
           sed_commentary "s/{{p-strict|set -euo pipefail}}/{{p-stirct|set -euo pipefail}}/"'

# 5. expansion guard — a reference that never closes must not be emitted literally
refuses "unterminated reference is refused" "unterminated reference" \
  bash -c 'sed_commentary "s/{{p-strict|set -euo pipefail}}/{{p-strict|set -euo pipefail/"'

# 6. the regression the expansion guard was written for: display text full of braces
#    must survive whole, closing brace included.
accepts "brace-heavy display expands intact" \
  'href="#p-default">${VAR:-default}</a>'
accepts "nested-brace display expands intact" \
  'href="#p-pipe">"${PIPESTATUS[0]}"</a>' \
  bash -c 'sed_commentary "s/Twenty-three lines/{{p-pipe|\"\${PIPESTATUS[0]}\"}} lines/"'

# 7. every reference in the page resolves to an entry that exists on the page
accepts "tooltip data is emitted for the refs used" 'window.__VERI_TIPS__ = {'

# 8. the highlighting must never alter a line. The listings claim to be the real
#    source, and check-walkthrough.py re-checks that against the files — but by then
#    the page is written. This guard is the earlier one: build-walkthrough.py asserts
#    every line survives the lexer byte for byte and refuses to emit a page otherwise.
#    Broken here by making one token drop its leading character, which is what an
#    off-by-one in the lexer actually looks like.
refuses "lossy highlighting is refused" "highlighting altered a line" \
  bash -c 'sed -i.bak "s/out.append((\"v\", m.group(0)))/out.append((\"v\", m.group(0)[1:]))/" \
           docs/wt/bashlex.py && rm -f docs/wt/bashlex.py.bak'

# 9. and the shebang is code, not a comment — the one line the kernel reads
accepts "shebang is not styled as a comment" '<span class="l">#!/bin/sh</span>'

# 10. the version layer is OPTIONAL. sandbox() copies docs/ and skills/ into a bare
#    temp dir with no .git in it, which is also what a tarball or a shallow checkout
#    looks like. The build must still succeed there and simply omit the capability
#    index — never crash on the missing git, and never emit a half-built index. The
#    assertions are: it builds, there is no index, there is no rail group pointing at
#    an index that is not there (which the scrollspy would drop and
#    check-walkthrough.py would report as a build bug), and no line of any listing is
#    hunk-tagged — `git blame` has nothing to answer with here either, so the source
#    half of the page is as plain as the rest of the version layer is absent.
omits "no git: no capability index"     '<ol class="vers">'
omits "no git: no per-script badge"     'class="vbadge"'
omits "no git: no orphan rail group"    '<h4>Capabilities</h4>'
omits "no git: no hunk tag"             'class="l hunk"'

# 11. per-hunk version tags. The <b>vX.Y</b> badge dates a file as a whole; a hunk tag
#    dates a RANGE OF LINES inside the listing, so the reader can see which lines a later
#    version touched without diffing. A hunk is tagged only when the commit that last
#    touched it is a behaviour commit AND shipped in a version later than the file's own
#    `since`. Below that bar there is nothing to point at, and the listing stays plain.
#
#    These assert through omits_git and tags_git rather than omits and accepts, because
#    git blame needs a history: both build in sandbox_git().
#
#    The floor case: a script whose whole history is the feat: commit that added it, in
#    the one version that exists. Nothing has changed since it shipped, so no line in it
#    has anything to be tagged with. Tagging here would mean tagging every line of every
#    script with v0.1 — the badge already says that, once, in the header.
omits_git "one tag, only the original feat:: no hunk tag" 'class="l hunk"'

#    And the case the feature exists for: one line of classify-bail.sh is rewritten by a
#    feat: commit that ships in v0.2, a version later than the file's own `since` of v0.1.
#    That one line carries the tag and the commit's own words — subject minus the `feat:`
#    prefix and minus the `(#2)` issue reference, the same text the badges and the
#    capability index are built from — and, by the count, no other line in the page does.
tags_git "a later feat: commit tags its line, and only its line" 1 \
  '<span class="l hunk" data-tag="v0.2" title="rewrite one line of classify-bail.sh">'\
'<span class="c"># rewritten by the v0.2 commit</span></span>' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
           "# rewritten by the v0.2 commit" \
           "feat: rewrite one line of classify-bail.sh (#2)" v0.2'

#    Two versions later touched the same file, on lines 3 and 5, with line 4 still on the
#    original v0.1 commit between them. Blame groups consecutive lines by their LAST
#    toucher, so this is the case that proves the grouping does not run the two together:
#    each line has to carry its own version and its own commit's words, and the count has
#    to stay at 2 — a merged hunk would drop to 1, and a whole-file tag would run higher.
tags_git "two later commits tag their own lines separately" 2 \
  '<span class="l hunk" data-tag="v0.2" title="rewrite line 3 of classify-bail.sh">'\
'<span class="c"># rewritten by the v0.2 commit</span></span>
<span class="l hunk" data-tag="v0.3" title="rewrite line 5 of classify-bail.sh">'\
'<span class="c"># rewritten by the v0.3 commit</span></span>' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 5 \
             "# rewritten by the v0.3 commit" \
             "fix: rewrite line 5 of classify-bail.sh (#3)" v0.3'

#    Blame answers who touched a line LAST, and that is the whole answer: a `refactor:`
#    commit sitting on top of the `feat:` that introduced the line hides it, rather than
#    passing its tag down. Reaching back past the refactor for the feat: underneath would
#    be a guess about which of the two the reader wants dated.
#    The refactor is untagged but lands BEFORE v0.2 is cut, so v0.2 contains it — without
#    that, `_first_tag_containing` would return None and the line would go untagged for
#    the wrong reason, leaving the case green against an implementation that never looked
#    at the commit type at all. Line 5's tag and the count of 1 are what say line 3 was
#    passed over: the page has exactly one hunk tag and it is not on the refactored line,
#    which is asserted directly by demanding line 3's plain `<span class="l">` form.
tags_git "a refactor: on top of a feat: leaves the line untagged" 1 \
  '<span class="l hunk" data-tag="v0.2" title="rewrite line 5 of classify-bail.sh">'\
'<span class="c"># rewritten by the v0.2 commit</span></span>
<span class="l"><span class="c"># reworded by the refactor commit</span></span>' \
  bash -c 'rewrite_line_as_refactor "$SAMPLE_SCRIPT" 3 \
             "# reworded by the refactor commit" \
             "refactor: reword line 3 of classify-bail.sh (#2)"
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 5 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 5 of classify-bail.sh (#2)" v0.2'

# 12. and the other half of the pipeline has to read that tag as source. The listings
#    claim to be the real scripts, and check-walkthrough.py is what re-checks the claim
#    against the files — it pulls each line back out of the page by its `<span class="l">`
#    wrapper. A hunk tag changes that wrapper on exactly one line per hunk, and the extra
#    attributes are decoration ON the line, not content IN it: the same bytes are still
#    inside. So the checker must recognise the tagged wrapper and compare the line like
#    any other, rather than skip it and report the chunk as drift — otherwise `make
#    docs-check` goes red the moment a hunk gets tagged, and the two halves of the docs
#    pipeline disagree about the markup they share.
#    Asserted through the exit code of the whole checker, which is what `make docs-check`
#    actually branches on. It passes in this sandbox today for every other reason it
#    checks — the page is freshly built, the tags are real, SKILL.md is the real one — so
#    the verbatim comparison is the only thing left for it to fail on.
checks_git "the checker reads a hunk-tagged line as source, not drift" \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
           "# rewritten by the v0.2 commit" \
           "feat: rewrite one line of classify-bail.sh (#2)" v0.2'

# 11. the stage-0 intro must not mislabel when ensure-run-state-ignored.sh runs.
#    "Preflight" is SKILL.md step 0 — the baseline checks that happen before any branch
#    exists (SKILL.md "0. Preflight"). This script runs in step 1.4, after the per-issue
#    branch is already cut, and the two phases fail differently: a preflight bail has no
#    branch and no commits to revert, a step-1.4 failure already has both. Naming the
#    wrong one sends a reader looking in the wrong half of the procedure.
omits "no mislabeled preflight timing" 'runs once per issue, at preflight'

# 12. and stage 0 must close the loop on the script's stdout contract: a reader who has
#    just learned that it prints "added" or "already present" needs to know what the
#    conductor does with that answer without leaving the page for SKILL.md. "added" means
#    the rule becomes the branch's first commit, under one exact message; "already present"
#    means there is nothing to commit. Pinned on the commit message itself, because that is
#    the half a reader would otherwise go and grep the procedure for.
accepts "documents the ignore-rule caller contract" 'chore: ignore veri run state'

# 13. "built with itself" claims a number — how many issues veri has solved by being run
#    on its own repository — and a number in prose goes stale the moment it is typed. So it
#    is counted at build time from git, the same rule the rest of the version layer follows:
#    one `plan: scope #<n>` commit is one issue veri scoped and solved for itself.
#
#    Which makes the degraded case the one worth pinning. sandbox_git is a real repository
#    whose entire history is the one `feat:` commit that landed the tree — git answers, and
#    answers zero. The claim itself is still true and must still be on the page; only the
#    figure has nothing behind it, so only the figure goes. A build that crashed, or that
#    printed "0 issues", or that dropped the sentence along with the number, is wrong in a
#    way the reader would see.
accepts_without_git "no matching history: the built-with-itself claim, minus the figure" \
  'built with itself' 'class="solved-n"'

# 14. the page opens by making its case, and only then starts explaining. "What veri
#    actually is" describes the design to a reader who has already decided to read; someone
#    who lands here cold is owed the argument first, in a section of its own before it.
#    An argument on a page like this is only worth as much as what it can point at, so each
#    of the four claims is pinned together with the anchor that substantiates it — a reader
#    who does not believe "blind" is one click from build-verify-prompt.sh's own section:
#
#      strict TDD, not vibe coding  -> the leaf loop, stage 2       (#s2)
#      built with itself            -> (no fixed anchor: see below)
#      blind verification           -> build-verify-prompt.sh       (#build-verify-prompt)
#      observability                -> supervise.sh, classify-bail.sh
#
#    Observability has no keyword of its own here because its two anchors are the claim:
#    the heartbeat that bounds a hang and the classifier that labels it. "Built with
#    itself" is the reverse — words but no pinned anchor, because the section that
#    substantiates it is the capability index, which exists only when git does (case 10),
#    and demanding a fixed anchor for it would quietly demand a repository too.
#
#    Built in the bare sandbox for that same reason: the pitch is prose about the design,
#    so it must be on the page a tarball builds, with or without a version layer.
opens_with "a pitch section opens the page, every claim linked to what shows it" \
'<h2
TDD
built with itself
blind
href="#s2"
href="#build-verify-prompt"
href="#supervise"
href="#classify-bail"'

# 15. and the section is reachable. Case 14 proves the pitch is on the page, which is only
#    half of it: the rail is how anyone navigates this page, and a section the rail does not
#    list is one you find by scrolling past it. All three renderings of the navigation — the
#    rail, the scrollspy model in window.__VERI_NAV__ and the breadcrumb — come from
#    nav_entries(), and docs/check-walkthrough.py refuses a page where the rail's anchors and
#    the scrollspy's ids are not the same set, so pinning the rail link pins all three.
rail_lists "the pitch section is listed in the rail" '<a href="#why">Why this exists</a>'

# 16. and listed as one of THEM. Case 15 asks whether the rail mentions the pitch at all;
#    this asks where. The rail's Orientation group is the page's top-level sections, and the
#    pitch is one — not an appendix, not a heading with a group to itself. So the assertion
#    is the pitch's link and an existing section's link inside that one group, which is what
#    "alongside" means in markup this flat: same <h4>, same plain <a> form the other
#    top-level entries get (a "file" or "stage" entry would carry a <span> the want would
#    not match). Both wants together, because either alone is the wrong claim — the pitch
#    on its own could be the group's only member, and "What veri actually is" on its own is
#    just where it already was.
rail_group_lists "the pitch is a top-level rail entry, beside the other sections" \
  '<h4>Orientation</h4>' \
'<a href="#why">Why this exists</a>
<a href="#what">What veri actually is</a>'
# 17. stage 0 runs three scripts in a fixed order, and the whole point of the stage is a
#    shape — the run moves into a linked worktree while the caller's checkout stays put.
#    Prose can list the three; only a picture shows the order and the branch that does not
#    move. Every other stage that has a shape draws it (stages 2 and 4 in box-drawing, the
#    orientation figures in SVG), so stage 0 must too, in either idiom.
diagrams_stage0 "the stage-0 intro draws its three scripts" \
  'issue-worktree.sh
ensure-run-state-ignored.sh
detect-test-command.sh'

# 18. and that diagram has to draw the branches, not just the names. Each of the two
#    scripts that run inside the worktree answers in one of two ways and neither way is a
#    failure: the ignore rule was added or was already present, a test command was found
#    or none was and `exit 3` sends the conductor to ask. A picture that draws one arrow
#    out of each teaches the other answer as an error. The third fact is the left column:
#    the caller's checkout, untouched — ADR-0013's point (docs/adr/0013-issue-branch-in-
#    its-own-worktree.md) and the reason the stage exists at all, since anything symlinked
#    or served out of that checkout keeps seeing what it saw. Demanded of one diagram
#    block for the same reason as case 13: these words are in the intro's prose already.
diagrams_stage0 "the stage-0 diagram draws both outcomes and the untouched caller" \
  'added
already present
test command
exit 3
untouched'

# 19. stage 3 is where the blind-verification guarantee is made, and the guarantee is a
#    comparison: build-verify-prompt.sh is build-develop-prompt.sh with the rationale left
#    out. The stage's orientation is prose only, and the page's diagrams name the verifier
#    path — build-verify-prompt.sh → verify.sh → parse-verdict.sh — while its developer-side
#    mirror appears in no figure at all, so the one comparison the stage exists to make is
#    the one a reader has to assemble themselves.
#    So: one figure in stage 3 naming both builders and both ends of the verify path.
#    Stage-bounded and figure-bounded, because neither bound alone says anything — all four
#    names already occur inside the stage (they are its own scripts' source), and
#    build-develop-prompt.sh already appears in a figure elsewhere on the page.
stage3_figure "the stage-3 intro diagrams the two prompt builders as mirrors" \
'build-develop-prompt.sh
build-verify-prompt.sh
verify.sh
parse-verdict.sh'

# 20. and the mirror is only worth drawing where it breaks. Case 17 pins the four names in
#    one figure, which a reader can already get from two arrows; what makes the pair a
#    guarantee rather than a symmetry is the one place the two argument lists disagree.
#    Both builders take the same three phases and then part ways — the developer gets
#    `revise`, because it is the only side that can be sent back; the verifier gets `pin`,
#    and nowhere in its arguments is there a slot for the developer's rationale.
#    So: the same figure lists each builder's four phases as a run, and says "no rationale"
#    in words. The phase runs are wanted contiguous, because scattered the five words are
#    just vocabulary — "lists the four phases" is a claim about them appearing together.
#    What substring matching cannot ask is *where* "no rationale" sits; holding it in the
#    figure that carries the verifier's own phase run is as close as this idiom gets.
stage3_figure "the stage-3 diagram lists both phase sets and says the verifier gets no rationale" \
'red | green | refactor | revise
red | green | refactor | pin
no rationale'
# 21. stage 5's intro has to draw the three budgets. CLAUDE.md's invariant is that
#    VERI_STUCK_RETRIES, REVISE_BUDGET and VERI_REFACTOR_BUDGET are three axes and never
#    one knob — liveness, verdict and cost — and the thing that makes the invariant legible
#    is that each axis ends somewhere different: killed-stuck through classify-bail.sh into
#    a system bail, revise-exhausted through the same script into a process one, budget
#    spent through refactor-budget.sh into an exit 3 that is not a bail at all. That is a
#    shape, and prose reciting it is how a reader ends up believing two of the three are
#    the same thing. So the three variables and the two scripts that enforce the ends must
#    appear in one diagram block, in either of the page's existing idioms.
#    The slice reaches to the reference section, so it holds the stage's script listings as
#    well as its intro — which costs this case nothing, because the claim is about ONE block
#    naming every string: the closest any listing in the stage comes is refactor-budget.sh's
#    own source, which has neither VERI_STUCK_RETRIES nor REVISE_BUDGET anywhere in it.
diagrams_stage5 "the stage-5 intro draws the three budgets on three axes" \
'VERI_STUCK_RETRIES
REVISE_BUDGET
VERI_REFACTOR_BUDGET
refactor-budget.sh
classify-bail.sh'

# 22. stage 5's intro also has to draw the rung above the conductor. solvable-issues.sh is
#    the one script in the stage nothing in the conductor calls: it is what a scope run of
#    `/tdd` uses to pick the next issue — open, `ready-for-agent`, unblocked, unclaimed —
#    before handing it to `/tdd <n>` and recomputing, and it stops on the first bail rather
#    than working the list it computed once. So the loop is the picture: the four conditions
#    that select an issue, the conductor invocation they feed, and the rule that ends the
#    run. Demanded of one block for the usual reason — every one of these words is in the
#    intro's prose and in the script's own listing already.
#    Two of those strings are what keep this honest. The script's header comment names
#    itself and three of the four conditions in a single `<pre class="src">` block, so a
#    set without `/tdd` and `first bail` — neither of which appears anywhere in
#    solvable-issues.sh, which never names its caller — would be green against a page with
#    no new diagram at all.
#    What this cannot see is separateness: case 21's names and these do not overlap, so one
#    combined figure would satisfy both cases. That the two are drawn as two figures is a
#    judgement about the drawing, not a claim a name test can make.
diagrams_stage5 "the stage-5 intro draws the rung above the conductor" \
'solvable-issues.sh
/tdd
open
ready-for-agent
unblocked
unclaimed
first bail'

# 17. a hunk has two ends. Case 11 pinned which LINE a later version's tag lands on; the
#    tag is only half of what a hunk is. A hunk is a run of consecutive lines with one
#    last-touching commit, and everything a reader would want to do with it — rule a
#    margin down its side, link to it as `classify-bail.sh L3–4` — needs the line the run
#    ENDS on as well as the line it starts on. So gitmeta reports the extent, not just the
#    head of it.
#    Two adjacent lines rewritten by one feat: commit, with the rest of the file still on
#    the v0.1 commit that added it: exactly one hunk, running 3 to 4. An implementation
#    that reported only the first line has nothing to say here, and one that ran the hunk
#    past line 4 into the untouched v0.1 lines below would report the wrong end.
hunks_git "a hunk reports the last line of its run, not only the first" '3-4 v0.2' \
  bash -c 'rewrite_hunk_as_feat "$SAMPLE_SCRIPT" 3 4 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite lines 3 and 4 of classify-bail.sh (#2)" v0.2'

# 18. the same hunks, read the other way round. Case 17 asked gitmeta what a hunk's extent
#    is; this one asks the PAGE what each version touched. The listings answer by line —
#    a tagged <span> where a run starts — and there is no way to walk that back to "v0.3
#    changed these two places" without scraping the markup, so the build emits the
#    inversion itself as `window.__VERI_HUNKS__`, tag to the script, extent and
#    description of every hunk that version owns.
#    Two versions on one file, with an untouched v0.1 line between them: lines 3 and 4
#    rewritten together by a feat: in v0.2 — one hunk with two ends — and line 6 by a fix:
#    in v0.3. So the map has to hold two entries under two different tags, spell the
#    first one's run as 3–4 rather than 3–3 or 3–6, and carry each commit's own words. The
#    count check in the helper is what stops a map that lists v0.2 and forgets v0.3: the
#    page carries two hunk spans, so the map must carry two entries.
hunk_map_git "the page carries an inverted map, one entry per hunk span" \
  'v0.2 classify-bail.sh 3-4 rewrite lines 3 and 4 of classify-bail.sh
v0.3 classify-bail.sh 6-6 rewrite line 6 of classify-bail.sh' \
  bash -c 'rewrite_hunk_as_feat "$SAMPLE_SCRIPT" 3 4 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite lines 3 and 4 of classify-bail.sh (#2)" v0.2
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 6 \
             "# rewritten by the v0.3 commit" \
             "fix: rewrite line 6 of classify-bail.sh (#3)" v0.3'

# git_budget_git <name> <mutator...>
# How many git processes ONE build forks. Every question gitmeta asks is a process, and a
# process costs ~30 ms to start on a laptop whatever it answers — so a build's time is its
# question count, not its history: 476 processes made a 16 s build of the real tree, and
# the twenty sandboxed builds above are most of what `make docs-test` costs. The guard is
# a budget, computed rather than typed so adding a script to the walkthrough or a tag to
# a case does not silently move the line: one blame per script (blame is per file, and git
# has no batch form), one ancestry walk per tag (which commits a version contains is the
# one question with no single-call answer), and a fixed handful for the rest — the tag
# list, every tag's date and title, the whole history once, the origin, the unreleased
# check. What it catches is a question asked per commit or per line: `tag --contains` for
# every blamed sha, `show --name-only` for every commit in a range.
# Counted by wrapping gitmeta._git, the one function every git question goes through,
# and running the build in the same interpreter: build-walkthrough.py puts docs/wt on
# sys.path and imports gitmeta by that name, which resolves to the module already patched
# here. The budget's own two git questions are asked AFTER the build, through the
# unwrapped function, so they are not counted against it.
#
# The two streams are kept apart, and that is load-bearing rather than tidiness. The first
# line of stdout is the two numbers this case compares; stderr is where the BUILD talks, and
# since #125 a tree whose scripts carry lines no commentary chunk covers is a normal tree —
# it says so with a `COMMENTARY OWED:` header and one `owed:` line per gap. Folded together
# with 2>&1 that header arrives where the count was expected, and `[[ COMMENTARY -le OWED: ]]`
# is arithmetic on an unset name: under `set -u` that kills the file where it stands, so the
# suite ends with no count line, exit 0, and every case after this one never run — `make
# docs-test` and the merge gate behind it reporting success over a suite that stopped. So
# stderr lands in `$d/err.txt` — where `build` above puts a build's stderr and where every
# other case in this suite goes looking for it — and is shown in the same `| ` gutter, and
# only when the python itself came back non-zero: that is where a traceback or the build's
# own `BUILD PROBLEMS:` is worth reading. A blown budget with a clean exit is answered by
# the counts below it, and the `COMMENTARY OWED:` header says nothing about those.
git_budget_git() {
  selected "$1" || return 0
  local name="$1"; shift
  local d code got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  got="$( cd "$d" && python3 - 2>"$d/err.txt" <<'PY'
import contextlib, io, runpy, sys
from collections import Counter
sys.path.insert(0, "docs/wt")
import commentary, gitmeta
calls, real = [], gitmeta._git
def counted(root, *args):
    calls.append(args[0])
    return real(root, *args)
gitmeta._git = counted
sys.argv = ["docs/build-walkthrough.py", "--stdout"]
try:
    with contextlib.redirect_stdout(io.StringIO()):
        runpy.run_path("docs/build-walkthrough.py", run_name="__main__")
except SystemExit as e:
    if e.code not in (None, 0):
        raise
scripts = len(commentary.SCRIPTS)
tags = len((real(".", "tag", "--sort=v:refname") or "").splitlines())
print("%d %d" % (len(calls), scripts + tags + 8))
for sub, n in Counter(calls).most_common():
    print("  %4d git %s" % (n, sub))
PY
  )" && code=0 || code=$?
  local made budget; read -r made budget <<< "${got%%$'\n'*}"
  if [[ "$code" == 0 && "$made" -le "$budget" ]]; then
    passed "$name"
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want at most $budget git processes for one build: one per script, one per tag, eight more"
    echo "    got  $made:"
    printf '%s\n' "$got" | tail -n +2 | sed 's/^/    /' | head -8
    [[ "$code" != 0 ]] && sed 's/^/    | /' "$d/err.txt" | head -6
  fi
}

# 18b. and the whole version layer has to be READ within a budget of git processes. The
#     cases above pin what the layer says; this one pins what saying it costs, because the
#     cost is what decided last night: a leaf on a docs issue runs this suite after every
#     edit, a verifier runs it again, and at 140 s a run the supervisor's 900 s timeout
#     read a working leaf as a hung one. Three tags and eighteen scripts admit 29
#     processes. Asking one question per blamed commit is over the line at once.
git_budget_git "a build asks git once per script, once per tag, and a fixed handful more" \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2
           rewrite_line_as_feat skills/tdd/scripts/supervise.sh 8 \
             "# rewritten by the v0.3 commit" \
             "feat: rewrite line 8 of supervise.sh (#3)" v0.3'

# 19. and the mark has to be something a reader can see. Cases 11 and 17-18 settled where a
#     hunk is and what it owns; all of that shipped as markup nobody styled, so scrolling
#     past a run of lines a later capability rewrote looked exactly like scrolling past one
#     it never touched. Two declarations turn the wrapper into a mark:
#
#       a chip carrying the tag  -> content drawn from attr(data-tag), on a pseudo-element
#       a rule down the left     -> a left border on the hunk
#
#     The chip's text has to come from the attribute, not from anything the stylesheet
#     spells out: there is one rule for every hunk on the page and they carry different
#     tags, so a hand-written "v0.14" would be one version's chip on all of them. And it
#     has to be generated content, because the markup holds no element for a chip to be —
#     `content` on the line itself renders nothing.
#     Both halves in one case: a chip with no rule marks where a run starts and says
#     nothing about how far it goes, and a rule with no chip says a run changed without
#     saying in which version. Faintness is the one thing here not pinned — it is a colour
#     choice, and no assertion this suite can make would tell a faint rule from a loud one.
hunk_css "the stylesheet makes a hunk visible: a tag chip and a left rule" \
'::(before|after).* \| content \| .*attr\(data-tag\)
\| border-(left|inline-start)'

#     And the rule has to reach the END of the run, which is a claim about the markup: a
#     border is drawn per line, and CSS can ask "is this line in a hunk" but not "and are
#     the next four", so a class on the first line alone rules one line of a nine-line run
#     and leaves the rest looking untouched. Lines 3 and 4 rewritten by one feat: commit
#     are one hunk with two lines in it, so both have to be marked — the first carrying
#     the tag the chip is drawn from, the second carrying the class and no second chip.
#     The count of 1 is what says the second line did not become a hunk of its own: a
#     `<span class="l hunk" data-tag=…>` on both would rule the run correctly and stamp a
#     duplicate chip halfway down it, and would double every entry the inverted map owes.
tags_git "the mark covers the whole run, and the chip lands once" 1 \
  '<span class="l hunk" data-tag="v0.2" title="rewrite lines 3 and 4 of classify-bail.sh">'\
'<span class="c"># rewritten by the v0.2 commit</span></span>
<span class="l hunk cont"><span class="c"># rewritten by the v0.2 commit</span></span>' \
  bash -c 'rewrite_hunk_as_feat "$SAMPLE_SCRIPT" 3 4 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite lines 3 and 4 of classify-bail.sh (#2)" v0.2'

# 20. and a reader who has chosen nothing is owed the page unchanged. Since-mode dims the
#     hunks a reader has already seen, which gives the stylesheet two ways to spell the
#     same look and only one of them is right: fade nothing until a version is picked, or
#     fade everything and un-fade what since-mode lights. The second renders the resting
#     page — no hash, nothing in storage, which is how every first visit arrives — as a
#     wall of greyed-out code, and it passes case 19 unharmed, because a chip and a rule
#     are still there underneath the fade.
#     Built over the same two-line hunk case 19 uses, so the page genuinely carries the
#     marks the assertion is about: a build with no hunk in it would have nothing to find
#     dimmed and would pass on an empty page.
undimmed_git "nothing chosen: the marks ship undimmed" \
  bash -c 'rewrite_hunk_as_feat "$SAMPLE_SCRIPT" 3 4 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite lines 3 and 4 of classify-bail.sh (#2)" v0.2'

# 21. and a reader who HAS chosen one is owed the other state. Case 20 pinned the resting
#     page; this is what choosing v0.9 does to it — light the hunks that landed after the
#     reader last read, leave the ones they have already seen dimmed.
#
#     Three hunks on three tags, and each is in the case for a distinct reason:
#
#       v0.2  earlier than the choice   -> dim: the reader read it long ago
#       v0.9  the choice itself         -> dim: v0.9 is what they last read, not news
#       v0.10 later than the choice     -> lit: this is the answer they came for
#
#     And v0.9 against v0.10 is the case the whole criterion turns on, because those two
#     tags order one way as versions and the other way as text: `v0.10` > `v0.9` in git's
#     version sort and `v0.10` < `v0.9` as strings. An implementation that compares the
#     tags it is handed — the obvious thing to write, and the map's own keys arrive in
#     exactly that lexical order — dims v0.10 and hides the newest capability from the one
#     reader who asked to see it. The version order the build already computed is the only
#     thing that gets this right, so the case is built on tags that make the two disagree
#     rather than on v0.2/v0.3, which agree and would leave the bug green.
since_git "choosing a version lights every hunk tagged later than it and dims the rest" \
  v0.9 \
  'v0.10 classify-bail.sh 7-7 lit
v0.2 classify-bail.sh 3-3 dim
v0.9 classify-bail.sh 5-5 dim' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 5 \
             "# rewritten by the v0.9 commit" \
             "feat: rewrite line 5 of classify-bail.sh (#3)" v0.9
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 7 \
             "# rewritten by the v0.10 commit" \
             "fix: rewrite line 7 of classify-bail.sh (#4)" v0.10'

# 22. and the same choice has to reach the capability index. Case 21 is what a choice does
#     to the listings; this is what it does to the index a reader makes the choice in. The
#     index at rest lists every version veri has ever cut, which is the wrong answer to
#     "what have I missed" — so choosing v0.2 drops every row up to and including v0.2 and
#     leaves each surviving row pointing at the hunks that version touched, which is the
#     only thing on the page that says WHERE a version changed something rather than that
#     it did.
#
#     Four versions, and each is in the case for a reason the others cannot cover:
#
#       v0.1  the version the tree arrived in  -> gone: read long ago
#       v0.2  the choice itself                -> gone: it is what they last read
#       v0.3  later, and touched no script     -> a row, with nothing to link to
#       v0.9  later, one hunk                  -> a row linking classify-bail.sh 5-5
#       v0.10 later, TWO hunks in one commit   -> a row linking BOTH 7-7 and 10-10
#
#     v0.3 is the row an implementation that walks `window.__VERI_HUNKS__` cannot produce:
#     the map is keyed by the tags that own hunks, so a capability that changed something
#     this page does not quote is missing from it entirely, and the reader is told a
#     version they have not read does not exist. The index has to come from the version
#     ORDER and the map has to be read into it, not the other way round.
#     v0.10 is the row that says "every hunk", not "the hunk": one commit rewriting lines
#     7 and 10 with line 8 untouched between them is two runs under one tag, and a row
#     that links the first and stops sends the reader to half of what changed.
#     And v0.2 against v0.10 is the lexical trap again, from the other end: `v0.10` sorts
#     BEFORE `v0.2` as text, so an implementation that filters the rows by comparing tag
#     strings collapses the index onto the one version the reader most wanted to see.
index_git "choosing a version collapses the index to later ones, each linking its hunks" \
  v0.2 \
  'v0.10 classify-bail.sh 7-7, classify-bail.sh 9-9
v0.3 -
v0.9 classify-bail.sh 5-5' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2
           tag_feat_outside_the_scripts \
             "feat: a capability no script on this page carries (#3)" v0.3
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 5 \
             "# rewritten by the v0.9 commit" \
             "feat: rewrite line 5 of classify-bail.sh (#4)" v0.9
           rewrite_two_lines_as_feat "$SAMPLE_SCRIPT" 7 9 \
             "# rewritten by the v0.10 commit" \
             "fix: rewrite lines 7 and 9 of classify-bail.sh (#5)" v0.10'

# 23. and having lit them, the reader has to be able to walk them. `n`, `p` and the two
#     buttons in the crumb bar all step one sequence: the lit hunks in PAGE order, so that
#     pressing n always moves down the page and p always moves back up it.
#
#     Page order is three claims an implementation can get wrong one at a time, so the
#     fixture makes all three bite in a single walk. A reader who last read at v0.2 is
#     owed, in this order:
#
#       supervise.sh 8-8      v0.5  — the page lists supervise.sh fifth
#       supervise.sh 20-20    v0.4  — and line 8 comes before line 20 within it
#       classify-bail.sh 5-5  v0.3  — classify-bail.sh is fifteenth
#       classify-bail.sh 3-3  v0.2  — never a stop: it is what the reader last read
#
#     Walking `window.__VERI_HUNKS__` tag by tag is the obvious thing to write — the map
#     is keyed by tag and app.js already reads it that way for the index — and it answers
#     v0.3, v0.4, v0.5: classify-bail.sh before supervise.sh, and line 20 before line 8.
#     Every stop in the wrong place, and the reader jumping backwards on every press.
#     Sorting by script NAME instead gets the first stop wrong the other way, because
#     classify-bail.sh sorts before supervise.sh as text and comes after it on the page —
#     which is why the two scripts in this case are these two and not any two. Only the
#     order the page itself lists its scripts in, lowest line first inside a script,
#     produces this answer.
#     And the v0.2 hunk is the half that says the walk visits the LIT hunks rather than
#     every mark on the page: a walk that stops there is walking the reader back through
#     code they have just told it they already read.
walk_git "n and p walk the lit hunks in page order" \
  v0.2 \
  'supervise.sh 8-8
supervise.sh 20-20
classify-bail.sh 5-5' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 5 \
             "# rewritten by the v0.3 commit" \
             "feat: rewrite line 5 of classify-bail.sh (#3)" v0.3
           rewrite_line_as_feat skills/tdd/scripts/supervise.sh 20 \
             "# rewritten by the v0.4 commit" \
             "fix: rewrite line 20 of supervise.sh (#4)" v0.4
           rewrite_line_as_feat skills/tdd/scripts/supervise.sh 8 \
             "# rewritten by the v0.5 commit" \
             "feat: rewrite line 8 of supervise.sh (#5)" v0.5'

# 24. and the choice has to survive the tab being closed. Cases 21-23 are all about what a
#     chosen version does while the reader sits there; this is the choice getting into the
#     URL and back out of it, which is what makes since-mode something a reader can bookmark
#     or paste to someone else rather than a state they have to set up again every visit.
#     One round trip, both directions, because neither half is worth anything alone: a hash
#     nothing writes is never reloaded, and a hash nothing reads restores nothing.
#
#     The page is opened at `#since=v0.2` and its reader then chooses v0.9 — two different
#     versions on purpose. With one version the case passes against a `choose` that does
#     nothing at all: the address would still read what the page was opened at, and the
#     assertion could not tell a written hash from an untouched one.
#     Both tags are real versions in this fixture, so a `since()` that checks the hash names
#     a version the build knows is as green as one that does not — this case is about the
#     address carrying the choice, not about what an unknown tag should do.
hash_git "the URL carries the choice, and a page opened at that URL is in since-mode" \
  '#since=v0.2' v0.9 \
  'opened v0.2
hash since=v0.9' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 5 \
             "# rewritten by the v0.9 commit" \
             "feat: rewrite line 5 of classify-bail.sh (#3)" v0.9'

# 25. and the reader who never pastes a URL anywhere has to be able to come back too.
#     Case 24 is the choice living in the address; this is the choice living in the
#     browser, which is the one place a reader who just reopens their bookmark will find
#     it. One press of "mark read up to vX" and every later visit opens on what has landed
#     since — no hash to keep, nothing to set up again.
#
#     v0.10 is the newest version here and v0.9 is not, which is the lexical trap the
#     capability index and the dimming both already walk into from the other end: sorted as
#     text, `v0.9` is the last tag and a button that marks the reader up to it tells them,
#     for ever after, that the newest capability is one they have not read. The version the
#     button stores is the one git's version sort puts last, so the second load has to come
#     up in v0.10.
#
#     The third load is the browser that says no. Storage is not a given — a private
#     window, cookies off, a profile locked down by someone else's policy — and on those
#     browsers every read throws. The walkthrough is a page of prose and code that needs
#     none of it, so what a refusal costs the reader is since-mode, not the page: they get
#     what a reader who never pressed the button gets. An unguarded read costs them the
#     whole document instead, and the store here holds v0.10 by then, so the only way this
#     load reports `-` is by asking and surviving the answer.
store_git "the button is remembered by the browser, and a browser that refuses still comes up plain" \
  'first load -
next load v0.10
blocked -' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.9 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.9
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 5 \
             "# rewritten by the v0.10 commit" \
             "feat: rewrite line 5 of classify-bail.sh (#3)" v0.10'

# 26. and the reader has to be told what the answer they get actually means. A hunk is
#     awarded to a tag only when a `feat:` or `fix:` commit last touched it, which is the
#     design — a version is a capability — and it makes since-mode answer a narrower
#     question than the one its control seems to ask. Lines a `refactor:`, a `test:` or a
#     `docs:` commit rewrote after the reader last read are dimmed exactly like lines
#     nobody has touched since v0.1, so a reader who takes the dimming for "unchanged"
#     reads a file believing it is the one they read last time. One sentence in the index
#     says so, where the choice is made rather than in a note further down the page.
#
#     Both wants together, because each alone is green against prose that does not make
#     the claim. The index's own paragraphs are already about capabilities — "capabilities
#     that live there have no listing on this page" — so the first half is nearly true of
#     the section today; and a sentence carrying only the second half says what since-mode
#     does not answer without ever saying what it does. The contrast is the sentence.
index_says "the index says since-mode answers capabilities, not bytes" \
'capabilities changed
bytes'

# 27. and the walk has to be something the reader can actually take. Case 23 pinned the
#     sequence and stopped there, on the honest ground that a key binding and a button are
#     DOM wiring; this is that wiring, asked of a page running in a DOM it can be pressed
#     and clicked in. An implementation that computes the right stops and never scrolls
#     anywhere is green on case 23 and useless on the page.
#
#     Case 23's fixture, for its reasons — the two scripts whose page order and whose names
#     disagree, two hunks inside one of them, and a v0.2 hunk that is never a stop — with
#     the stepping laid over it. A reader who last read at v0.2 and presses n twice, clicks
#     next, then presses p and clicks previous walks:
#
#       n         #1 v0.5  supervise.sh 8    — n from the top lands on the FIRST stop
#       n         #2 v0.4  supervise.sh 20
#       next      #4 v0.3  classify-bail.sh 5 — the button continues the walk n was on
#       p         #2 v0.4  back up the page
#       previous  #1 v0.5
#
#     The two buttons are pressed AFTER the two keys, which is what says all four step one
#     walk rather than four each keeping their own place in it: a next button with a cursor
#     of its own answers #1 where this wants #4, and a previous button with one answers the
#     last stop where this wants #2. Mark #3 is the v0.2 hunk and never appears, from either
#     direction — a walk that stops there is walking the reader back through the code they
#     have just said they already read.
#     And the first line is the other half of the criterion: a reader who has chosen no
#     version has nothing to walk, so the crumb bar has no walk buttons in it. Two buttons
#     that do nothing are worse than none — they are a control that says the page offers
#     something it does not.
wiring_git "n, p and the crumb-bar buttons take the reader to the stop" \
  v0.2 \
  'at rest buttons none
since v0.2 buttons next previous
n #1 v0.5
n #2 v0.4
next #4 v0.3
p #2 v0.4
previous #1 v0.5' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 5 \
             "# rewritten by the v0.3 commit" \
             "feat: rewrite line 5 of classify-bail.sh (#3)" v0.3
           rewrite_line_as_feat skills/tdd/scripts/supervise.sh 20 \
             "# rewritten by the v0.4 commit" \
             "fix: rewrite line 20 of supervise.sh (#4)" v0.4
           rewrite_line_as_feat skills/tdd/scripts/supervise.sh 8 \
             "# rewritten by the v0.5 commit" \
             "feat: rewrite line 8 of supervise.sh (#5)" v0.5'

# 28. and the whole layer above has one thing it cannot see: a script the reader has never
#     read a line of. Every case from 21 on decides from `window.__VERI_HUNKS__`, and the
#     map holds no hunk for a script that arrived whole in a later version — hunks() drops
#     every run at or below the file's own `since`, on the sound ground that the header
#     badge already says so. Right for the badge, wrong for since-mode: a reader who opens
#     the page at v0.10 is walked past `issue-worktree.sh` entirely, because everything in
#     it is v0.18 and none of it is a hunk. The client has to be able to rank a script the
#     same way it ranks a hunk, and nothing it holds today says which version a script
#     arrived in.
#
#     The fixture is two versions with every script arriving in the first, which is the
#     shape that tells `since` apart from the two versions sitting next to it: v0.2
#     rewrites a line of classify-bail.sh, so that script's `changed` is v0.2 and the
#     repository's latest tag is v0.2, while its `since` — the only right answer — is still
#     v0.1. A build emitting either of the other two is green on a case that names any
#     other script and red on this one.
#     The count check inside the helper is the other half: one since per script the page
#     lists, so an answer holding the one script this case names and nothing else does not
#     pass. And the no-git build is in the same case because an answer that ships has to be
#     absent where there is no version layer to read it from.
since_of_git "the page carries each script's own since, and carries none without git" \
  'classify-bail.sh v0.1' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2'

# 29. and with that on the page, the walk owes the reader the stop it has been missing. A
#     script that arrived after the version they last read is not a run of changed lines
#     inside something they know — it is a file they have never seen a line of, and the
#     whole of it is news. Case 23 walks the hunks and stops there, which is the defect
#     this issue is about: a reader at v0.10 is stepped past issue-worktree.sh, arrived
#     whole in v0.18, because nothing in it is a hunk.
#
#     One fixture, walked twice, because the two halves are one sentence read from either
#     end. arrived-whole.sh ships in v0.3 and is rewritten in v0.6; supervise.sh is the
#     fifth script on the page and arrived-whole.sh the ninth (stage 2, appended) and
#     classify-bail.sh the sixteenth, so the three stops interleave and both ways of
#     dodging the sort are caught: a walk that appends the new scripts puts the header
#     after the hunk INSIDE it, and one that prepends them puts it before supervise.sh.
#     A reader who last read at v0.2 is owed the header, and one who last read at v0.3 —
#     the version it arrived in — is owed everything else on that list and not the header,
#     because they have read the script already. The rest of the walk is identical in both,
#     which is what says the header is the only thing that moved.
#     classify-bail.sh's v0.2 hunk is a stop in neither: the version the reader last read
#     is not news to them, as case 23 has it, and a new-script stop must not quietly
#     relax that.
new_script_git "a script newer than the chosen version is a stop, before any hunk inside it" \
  v0.2 v0.3 \
  'v0.2 supervise.sh 8-8
v0.2 arrived-whole.sh header
v0.2 arrived-whole.sh 2-2
v0.2 classify-bail.sh 5-5
v0.3 supervise.sh 8-8
v0.3 arrived-whole.sh 2-2
v0.3 classify-bail.sh 5-5' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2
           add_script_as_feat arrived-whole.sh arrived-whole 2 \
             "feat: a script that arrives whole (#3)" v0.3
           rewrite_line_as_feat skills/tdd/scripts/supervise.sh 8 \
             "# rewritten by the v0.4 commit" \
             "feat: rewrite line 8 of supervise.sh (#4)" v0.4
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 5 \
             "# rewritten by the v0.5 commit" \
             "feat: rewrite line 5 of classify-bail.sh (#5)" v0.5
           rewrite_line_as_feat skills/tdd/scripts/arrived-whole.sh 2 \
             "# rewritten by the v0.6 commit" \
             "feat: rewrite line 2 of arrived-whole.sh (#6)" v0.6'

# 30. and the reader has to land there. Case 29 pins the sequence and stops at the sequence,
#     which is exactly where case 23 stopped before case 27 pressed a key: a walk nothing
#     steps is a list nobody can use. It matters more here than it did there, because the
#     stepper collects MARKS — `<span class="l hunk" data-tag=…>`, the spans the version
#     layer has emitted since it landed — and a script that arrived whole has no such span
#     anywhere in it. So an implementation can return case 29's sequence exactly, be green
#     on it, and walk the reader straight past the script, because the file name it returned
#     names nothing in the markup to scroll to.
#
#     Case 29's fixture, for its reasons — arrived-whole.sh ships in v0.3 between
#     supervise.sh and classify-bail.sh on the page, and is rewritten in v0.6 — with the
#     pressing laid over it. A reader who opens the page at v0.2 presses n three times and
#     then p:
#
#       n  supervise.sh v0.4        — the first stop, a hunk in a script they have read
#       n  arrived-whole.sh header  — the script itself, before anything inside it
#       n  arrived-whole.sh v0.6    — and only then the run of lines within it
#       p  arrived-whole.sh header  — back up the page to it, which says it is a stop from
#                                     both directions rather than a place n falls through
#
#     The second load is the same page opened at v0.3, the version the script arrived in:
#     the second press lands on the hunk, never on the header, because a reader who has read
#     the script is owed what changed in it and nothing more. Both loads together are the
#     whole criterion — a header that is always a stop is as wrong as one that never is —
#     and the rest of the walk being identical in both is what says the header is the only
#     thing that moved.
header_wiring_git "n and p land the reader on a new script's header, before its first hunk" \
  v0.2 v0.3 \
  'v0.2 n supervise.sh v0.4
v0.2 n arrived-whole.sh header
v0.2 n arrived-whole.sh v0.6
v0.2 p arrived-whole.sh header
v0.3 n supervise.sh v0.4
v0.3 n arrived-whole.sh v0.6' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2
           add_script_as_feat arrived-whole.sh arrived-whole 2 \
             "feat: a script that arrives whole (#3)" v0.3
           rewrite_line_as_feat skills/tdd/scripts/supervise.sh 8 \
             "# rewritten by the v0.4 commit" \
             "feat: rewrite line 8 of supervise.sh (#4)" v0.4
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 5 \
             "# rewritten by the v0.5 commit" \
             "feat: rewrite line 5 of classify-bail.sh (#5)" v0.5
           rewrite_line_as_feat skills/tdd/scripts/arrived-whole.sh 2 \
             "# rewritten by the v0.6 commit" \
             "feat: rewrite line 2 of arrived-whole.sh (#6)" v0.6'

# 31. and the index the choice is made in owes the same script the same answer. Cases 29 and
#     30 take the reader to a new script by pressing `n`; this is the reader who does not
#     press anything and reads the index instead, which is the only place on the page that
#     says WHERE a version changed something. The version a script arrived in has no hunk
#     anywhere — hunks() drops every run at or below the file's own `since` — so its row
#     comes out empty, and an empty row is the page telling the reader that a version which
#     added a whole file to it touched nothing they can go and look at.
#
#     Case 30's fixture, for its reasons — arrived-whole.sh ships in v0.3 and is rewritten
#     in v0.6, with hunks either side of it in v0.4 and v0.5 — read as rows instead of
#     stops. A reader who last read at v0.2 is owed four rows, and the fixture makes each
#     one a different way of getting this wrong:
#
#       v0.3  the version the script arrived in  -> arrived-whole.sh new
#       v0.4  a hunk in a script they have read  -> supervise.sh 8-8
#       v0.5  another                            -> classify-bail.sh 5-5
#       v0.6  a hunk INSIDE the new script       -> arrived-whole.sh 2-2, not `new` again
#
#     v0.6 is the row that says the script is listed under the version it ARRIVED in and not
#     under every version that touched it: an implementation that awards the script to
#     whichever row it can find a reason to is green on v0.3 and lists arrived-whole.sh
#     twice. v0.4 and v0.5 are the rows it must stay out of altogether, which a row keyed by
#     the reader's choice or by the latest tag cannot manage — both are v0.6 or v0.2 here,
#     never v0.3.
#     The second load is the same page at v0.3, the version it arrived in: the script is
#     listed in no row at all, because a reader who has read it is owed what changed in it
#     and the v0.6 row is where that is. The three surviving rows being identical in both
#     loads is what says the arrival row is the only thing that moved.
new_index_git "the index lists a new script under the version it arrived in" \
  v0.2 v0.3 \
  'v0.2 v0.3 arrived-whole.sh new
v0.2 v0.4 supervise.sh 8-8
v0.2 v0.5 classify-bail.sh 5-5
v0.2 v0.6 arrived-whole.sh 2-2
v0.3 v0.4 supervise.sh 8-8
v0.3 v0.5 classify-bail.sh 5-5
v0.3 v0.6 arrived-whole.sh 2-2' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2
           add_script_as_feat arrived-whole.sh arrived-whole 2 \
             "feat: a script that arrives whole (#3)" v0.3
           rewrite_line_as_feat skills/tdd/scripts/supervise.sh 8 \
             "# rewritten by the v0.4 commit" \
             "feat: rewrite line 8 of supervise.sh (#4)" v0.4
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 5 \
             "# rewritten by the v0.5 commit" \
             "feat: rewrite line 5 of classify-bail.sh (#5)" v0.5
           rewrite_line_as_feat skills/tdd/scripts/arrived-whole.sh 2 \
             "# rewritten by the v0.6 commit" \
             "feat: rewrite line 2 of arrived-whole.sh (#6)" v0.6'

# 32. and none of cases 21-31 has yet changed a single pixel of the page. Every one of them
#     asks a function what it would answer — lit(), index(), walk(), since() — and the two
#     that press a key read where the page scrolled to. An implementation whose answers are
#     all exactly right and which puts no class on any element is green on the whole run of
#     them, and hands the reader a page indistinguishable from the one with no since-mode
#     in it: the reader chooses a version and nothing about the document says which of the
#     two thousand lines in front of them is the answer. This is that paint.
#
#     Three things carry a version and so have an answer to show — a hunk's first line
#     (`data-tag`), a script's header (`data-since`), and the commentary chip beside a
#     chunk — and the case asks for them by the attribute rather than by what they are, so
#     one report covers all three. The index is the other half: the rows a choice keeps are
#     shown and the rows it drops are gone, which is the same collapse case 22 pinned as a
#     return value, now pinned as the page.
#
#     A reader who last read at v0.9, and a fixture where each version is a different way of
#     getting this wrong:
#
#       v0.1  every script's `since`, and no hunk anywhere  -> dim: 18 headers, read long ago
#       v0.2  a hunk earlier than the choice                -> dim
#       v0.9  a hunk at the choice itself                   -> dim: what they last read
#       v0.10 a hunk later than the choice                  -> lit
#       v0.11 a script that arrived whole, later            -> lit: its header, the one mark
#                                                              in it, and the only element
#                                                              on the page for a script the
#                                                              reader has never seen
#
#     v0.9 against v0.10 and v0.11 is the lexical trap the whole layer turns on, here for
#     the third time: `v0.10` and `v0.11` both sort BEFORE `v0.9` as text and after it as
#     versions, so a paint that compares the strings it finds in the attributes dims the two
#     newest capabilities and hides the answer from the one reader who asked for it. And
#     v0.1 is the count that cannot be faked: eighteen headers, painted by the same rule as
#     the four marks that are not headers, which is what says the paint reaches every mark
#     rather than the handful the fixture touched.
#
#     The resting load is the other half, and it is case 20's claim read from the DOM
#     instead of the stylesheet: a reader who has chosen nothing is owed the page unchanged,
#     so no mark carries either class and no row is missing. `-` rather than "not dimmed",
#     because a page that lights every mark at rest is telling a reader who asked nothing
#     that the whole document is news to them.
paint_git "choosing a version paints the marks and collapses the index rows" \
  v0.9 \
  'at rest mark v0.1 -
at rest mark v0.10 -
at rest mark v0.11 -
at rest mark v0.2 -
at rest mark v0.9 -
at rest row v0.1 shown
at rest row v0.10 shown
at rest row v0.11 shown
at rest row v0.2 shown
at rest row v0.9 shown
since v0.9 mark v0.1 dim
since v0.9 mark v0.10 lit
since v0.9 mark v0.11 lit
since v0.9 mark v0.2 dim
since v0.9 mark v0.9 dim
since v0.9 row v0.1 hidden
since v0.9 row v0.10 shown
since v0.9 row v0.11 shown
since v0.9 row v0.2 hidden
since v0.9 row v0.9 hidden' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 5 \
             "# rewritten by the v0.9 commit" \
             "feat: rewrite line 5 of classify-bail.sh (#3)" v0.9
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 7 \
             "# rewritten by the v0.10 commit" \
             "fix: rewrite line 7 of classify-bail.sh (#4)" v0.10
           add_script_as_feat arrived-whole.sh arrived-whole 2 \
             "feat: a script that arrives whole (#5)" v0.11'

# 33. and case 32 painted classes onto elements that nothing renders. `lit` and `dim` land
#     on the marks exactly as they should and the stylesheet has never heard of either, so
#     the reader who picks a version is handed the same page back — the whole layer, from
#     #70 down, still invisible. This is the rule that makes the classes mean something.
#
#     Both states, because each alone is a different wrong page: dim with no lit greys out
#     what the reader has read and leaves the news at the same strength as the rest of the
#     document; lit with no dim marks the news and leaves it to compete with two thousand
#     lines at full strength. And `unmarked untouched` is the third: the fade has to be
#     gated on `.dim` rather than applied to every mark and lifted off `.lit`, which is the
#     cheaper thing to write, renders these two states identically, and greys out the page
#     for every first visit — the reading of case 20 that reaches the header marks too.
paint_css "the stylesheet renders the paint: dim faded, lit highlighted, the rest as it was" \
  'dim faded
lit highlighted
unmarked untouched' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2'

# 34. and there is still no way into any of it. Cases 21-33 are all about a reader who has
#     already chosen a version, and the only reader who can is one who knows to type
#     `#since=v0.9` into the address bar — `choose()` and `markRead()` have been on the page
#     since #70 and nothing on it calls either. The mode is a door with no handle.
#
#     The handle goes in the capability index, which is where the choice is already being
#     made in prose: the index is the one section that lists the versions, says what each
#     one did, and collapses onto the ones the reader has not read. So the claim is as much
#     about WHERE the control is as what it does — a select in the crumb bar is a control
#     in the chrome that steps the walk, and the stub's `__controls()` answers for the index
#     alone for that reason.
#
#     Both ends of the wiring, on one fixture, because either alone is a control that lies:
#
#       at rest    the select offers v0.10 v0.9 v0.2 v0.1 and a way back out, shows none of
#                  them — a reader who has chosen nothing must not be told they chose v0.1 —
#                  the button names v0.10, and pressing it puts the reader at v0.10 with no
#                  hash anywhere, which is markRead() and nothing else
#       then       the reader picks v0.9 and the page answers: since() says v0.9, and the
#                  marks repaint around it in the same process the page loaded in, which is
#                  the whole of "without a reload"
#       since v0.2 the select comes up on v0.2, because the address said so and a control
#                  that shows anything else is telling the reader they are reading something
#                  they are not; and when the address moves to v0.9 under it — Back, a
#                  pasted link, the reader's own edit — it follows
#
#     v0.9 against v0.10 is the lexical trap, here in the one place the reader looks at it:
#     `v0.10` sorts BEFORE `v0.9` as text, so an option list built by sorting the strings
#     offers the newest capability fourth and the button offers to mark the reader read up
#     to a version two behind the tip.
#     And the paint after the pick is case 32's report, four versions deep: it is not enough
#     that the choice reached the layer, the page has to change in front of the reader who
#     made it — the pick happens on a page loaded at rest, where nothing is painted at all,
#     so every one of those four lines is news the repaint put there.
control_git "the index carries the version select and the mark-read button, wired to the mode" \
  v0.2 v0.9 \
  'at rest select v0.10 v0.9 v0.2 v0.1 +none
at rest select shows none
at rest button mark read up to v0.10
at rest click -> since v0.10
at rest pick v0.9 -> since v0.9
at rest paint v0.1 dim
at rest paint v0.10 lit
at rest paint v0.2 dim
at rest paint v0.9 dim
since v0.2 select shows v0.2
since v0.2 hashchange v0.9
since v0.2 select shows v0.9' \
  bash -c 'rewrite_line_as_feat "$SAMPLE_SCRIPT" 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 5 \
             "# rewritten by the v0.9 commit" \
             "feat: rewrite line 5 of classify-bail.sh (#3)" v0.9
           rewrite_line_as_feat "$SAMPLE_SCRIPT" 7 \
             "# rewritten by the v0.10 commit" \
             "fix: rewrite line 7 of classify-bail.sh (#4)" v0.10'

# A filter that matched nothing is the typo path, and the one place a silent green is
# actively dangerous: every case skipped, nothing asserted, and `[[ $fail -eq 0 ]]` exits 0
# — so a leaf that mistyped its ONLY reads "the guards pass" off a run that guarded
# nothing. Exit 3 instead, the code every veri script uses for nothing to do (CLAUDE.md:
# exit codes are the API), and name the filter so the typo is visible in the message.
#
# Before the count line, not after it: a run that asserted nothing has no count to report,
# and printing "0 passed" would be the same false reassurance in another shape.
if [[ "$ran" -eq 0 ]]; then
  echo "no case matches ONLY='${ONLY:-}' — nothing to do"
  exit 3
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

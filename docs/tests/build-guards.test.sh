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
#   1. coverage    — a script's chunks must cover lines 1..N exactly once. Without it,
#                    adding a line to a script detaches the commentary with no signal.
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
# Each case runs against a disposable copy of the tree, so the real repo is never
# mutated even if a case aborts.
#
# Run: docs/tests/build-guards.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
pass=0 fail=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# Which sandbox the assertion helpers below build in. Most cases want the default —
# a bare tree with no .git — so the version layer stays out of the way; the cases that
# exercise it flip this to sandbox_git for the length of one call.
SANDBOX=sandbox

# sandbox — a fresh copy of everything the build reads, printed on stdout
sandbox() {
  local d; d="$(mktemp -d "$WORK/case.XXXXXX")"
  mkdir -p "$d/docs" "$d/skills/solve-issue"
  cp "$ROOT/docs/build-walkthrough.py" "$d/docs/"
  cp -R "$ROOT/docs/wt" "$d/docs/wt"
  cp -R "$ROOT/skills/solve-issue/scripts" "$d/skills/solve-issue/scripts"
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
  cp "$ROOT/skills/solve-issue/SKILL.md" "$d/skills/solve-issue/"
  printf '%s' "$d"
}

build() {  # build <dir> -> stdout=page, stderr=problems; returns the build's exit code
  ( cd "$1" && python3 docs/build-walkthrough.py --stdout 2>"$1/err.txt" )
}

# refuses <name> <expected-substring-in-stderr> <mutator...>
# The mutator runs inside the sandbox dir; the build must then FAIL and say why.
refuses() {
  local name="$1" want="$2"; shift 2
  local d code err; d="$("$SANDBOX")"
  ( cd "$d" && "$@" )
  build "$d" >/dev/null && code=0 || code=$?
  err="$(cat "$d/err.txt" 2>/dev/null)"
  if [[ "$code" != 0 && "$err" == *"$want"* ]]; then
    pass=$((pass + 1))
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
  local name="$1" want="$2"; shift 2
  local d code page; d="$("$SANDBOX")"
  [[ $# -gt 0 ]] && ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  if [[ "$code" == 0 && "$page" == *"$want"* ]]; then
    pass=$((pass + 1))
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
  local name="$1" unwanted="$2"; shift 2
  local d code page; d="$("$SANDBOX")"
  [[ $# -gt 0 ]] && ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  if [[ "$code" == 0 && "$page" != *"$unwanted"* ]]; then
    pass=$((pass + 1))
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
  local name="$1" want="$2" unwanted="$3"; shift 3
  local d code page; d="$("$SANDBOX")"
  [[ $# -gt 0 ]] && ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  if [[ "$code" == 0 && "$page" == *"$want"* && "$page" != *"$unwanted"* ]]; then
    pass=$((pass + 1))
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
  local name="$1" wants="$2"; shift 2
  local d code page region missing
  d="$("$SANDBOX")"
  [[ $# -gt 0 ]] && ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  # after the rail, the crumb and the masthead; before the old opening section
  region="$(region_between "$page" '</header>' '<h2 id="what"')"
  missing="$(missing_from "$region" "$wants")"
  if [[ "$code" == 0 && -z "$missing" ]]; then
    pass=$((pass + 1))
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
  local name="$1" wants="$2"; shift 2
  local d code page region missing
  d="$("$SANDBOX")"
  [[ $# -gt 0 ]] && ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  region="$(region_between "$page" '<aside class="rail">' '</aside>')"
  missing="$(missing_from "$region" "$wants")"
  if [[ "$code" == 0 && -z "$missing" ]]; then
    pass=$((pass + 1))
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
  local name="$1" head="$2" wants="$3"; shift 3
  local d code page region missing
  d="$("$SANDBOX")"
  [[ $# -gt 0 ]] && ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  region="$(region_between "$page" "$head" '<h4>')"
  missing="$(missing_from "$region" "$wants")"
  if [[ "$code" == 0 && -z "$missing" ]]; then
    pass=$((pass + 1))
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
  local name="$1" start="$2" end="$3" wants="$4"
  local d code page region found
  d="$("$SANDBOX")"
  page="$(build "$d")" && code=0 || code=$?
  region="$(region_between "$page" "$start" "$end")"
  found="$(figure_holding "$region" "$wants")"
  if [[ "$code" == 0 && -n "$found" ]]; then
    pass=$((pass + 1))
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

# tags_git <name> <n-hunk-tags> <expected-spans> <mutator...>
# accepts() and omits() each ask one yes/no question of the whole page, and a hunk tag
# needs two asked together: "this line carries v0.2" is only half the claim, because an
# implementation that tagged every line would satisfy it and defeat the point — the tag
# is worth reading only if it says where to look. So tags_git asserts the page contains
# every one of <expected-spans> AND carries exactly <n> hunk tags in total.
# <expected-spans> is ONE argument holding one expected span per line, because a case
# with two tags has to claim both at once: found separately they could still be the same
# line tagged twice, or one span overwritten by the other.
# Occurrences, not matching lines: grep -o then wc -l, since nothing guarantees two tags
# could not share one output line.
tags_git() {
  local name="$1" n="$2" wants="$3"; shift 3
  local d code page got want missing=""; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  page="$(build "$d")" && code=0 || code=$?
  got="$(printf '%s' "$page" | grep -o 'class="l hunk"' | wc -l | tr -d ' ')"
  while IFS= read -r want; do
    [[ "$page" == *"$want"* ]] || missing="$want"
  done <<< "$wants"
  if [[ "$code" == 0 && -z "$missing" && "$got" == "$n" ]]; then
    pass=$((pass + 1))
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
  local name="$1" want="$2"; shift 2
  local d code got; d="$(sandbox_git)"
  ( cd "$d" && "$@" )
  got="$( cd "$d" && python3 - 2>&1 <<'PY'
import sys
sys.path.insert(0, "docs/wt")
import gitmeta
meta = gitmeta.read(".", {"classify-bail.sh": "skills/solve-issue/scripts/classify-bail.sh"})
for first, (tag, description, last) in sorted(meta["marks"]["classify-bail.sh"]["hunks"].items()):
    print("%d-%d %s" % (first, last, tag))
PY
  )" && code=0 || code=$?
  if [[ "$code" == 0 && "$got" == "$want" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit $code)"
    echo "    want the hunks of classify-bail.sh to report: $want"
    echo "    got:"
    printf '%s\n' "$got" | sed 's/^/      /' | head -6
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
  local name="$1"; shift
  local d code out; d="$(sandbox_check)"
  ( cd "$d" && "$@" )
  out="$( cd "$d" && python3 docs/build-walkthrough.py >/dev/null 2>&1 \
                  && python3 docs/check-walkthrough.py 2>&1 )" && code=0 || code=$?
  if [[ "$code" == 0 ]]; then
    pass=$((pass + 1))
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
    pass=$((pass + 1))
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
append_line_to_script() { printf '\n# a line the commentary does not cover\n' >> "$1"; }
sed_commentary() { sed -i.bak "$1" docs/wt/commentary.py && rm -f docs/wt/commentary.py.bak; }

# rewrite_line_as_feat <file> <line-no> <text> <subject> <tag>
# Rewrite ONE line of a script in place, then land it as its own commit and cut the tag
# it ships in. Rewriting rather than adding is deliberate: the line count does not move,
# so the coverage guard has nothing to say and the case tests only the version layer.
rewrite_line_as_feat() {
  local file="$1" lineno="$2" text="$3" subject="$4" tag="$5"
  sed -i.bak "${lineno}s|.*|$text|" "$file" && rm -f "$file.bak"
  git add -A && git commit -qm "$subject" && git tag -a "$tag" -m "what $tag can do"
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

# rewrite_hunk_as_feat <file> <first> <last> <text> <subject> <tag>
# rewrite_line_as_feat over a RANGE of lines, landed as ONE commit — so blame answers the
# same commit for all of them and they are therefore one hunk, which is what a hunk needs
# in order to have an extent worth reporting. Rewriting rather than adding, for the same
# reason as the single-line helper: the line count does not move.
rewrite_hunk_as_feat() {
  local file="$1" first="$2" last="$3" text="$4" subject="$5" tag="$6"
  sed -i.bak "${first},${last}s|.*|$text|" "$file" && rm -f "$file.bak"
  git add -A && git commit -qm "$subject" && git tag -a "$tag" -m "what $tag can do"
}
export -f append_line_to_script sed_commentary rewrite_line_as_feat rewrite_line_as_refactor
export -f rewrite_hunk_as_feat

# 1. baseline: an unmutated tree builds, and emits real source verbatim
accepts "baseline builds" '<title>veri, Annotated</title>'
accepts "emits script source verbatim" 'echo $? &gt; "$rcfile"' 

# 2. coverage guard — a script grows a line the commentary does not claim
refuses "a longer script fails coverage" "file has" \
  bash -c 'append_line_to_script skills/solve-issue/scripts/classify-bail.sh'

# 3. coverage guard — a script loses a line
refuses "a shorter script fails coverage" "file has" \
  bash -c 'sed -i.bak "$(wc -l < skills/solve-issue/scripts/classify-bail.sh)d" \
           skills/solve-issue/scripts/classify-bail.sh'

# 4. unknown-reference guard — a typo'd id must not become a dead tooltip
refuses "unknown reference id is refused" "unknown primer ref" \
  bash -c 'sed_commentary "s/{{p-strict|set -euo pipefail}}/{{p-stirct|set -euo pipefail}}/"'

# 5. expansion guard — a reference that never closes must not be emitted literally
refuses "unterminated reference is refused" "unterminated reference" \
  bash -c 'sed_commentary "s/{{p-strict|set -euo pipefail}}/{{p-strict|set -euo pipefail/"'

# 6. the regression the expansion guard was written for: display text full of braces
#    must survive whole, closing brace included.
accepts "brace-heavy display expands intact" \
  'href="#p-default">${VAR:-default}</a>'
accepts "nested-brace display expands intact" \
  'href="#p-pipe">"${PIPESTATUS[0]}"</a>' 

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
accepts "shebang is not styled as a comment" '<span class="l">#!/usr/bin/env bash</span>'

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
  bash -c 'rewrite_line_as_feat skills/solve-issue/scripts/classify-bail.sh 3 \
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
  bash -c 'rewrite_line_as_feat skills/solve-issue/scripts/classify-bail.sh 3 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite line 3 of classify-bail.sh (#2)" v0.2
           rewrite_line_as_feat skills/solve-issue/scripts/classify-bail.sh 5 \
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
  bash -c 'rewrite_line_as_refactor skills/solve-issue/scripts/classify-bail.sh 3 \
             "# reworded by the refactor commit" \
             "refactor: reword line 3 of classify-bail.sh (#2)"
           rewrite_line_as_feat skills/solve-issue/scripts/classify-bail.sh 5 \
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
  bash -c 'rewrite_line_as_feat skills/solve-issue/scripts/classify-bail.sh 3 \
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
#    the one script in the stage nothing in the conductor calls: it is what `/solve-issues`
#    runs to pick the next issue — open, `ready-for-agent`, unblocked, unclaimed — before
#    handing it to `/solve-issue <n>` and recomputing, and it stops on the first bail rather
#    than working the list it computed once. So the loop is the picture: the four conditions
#    that select an issue, the conductor invocation they feed, and the rule that ends the
#    run. Demanded of one block for the usual reason — every one of these words is in the
#    intro's prose and in the script's own listing already.
#    Two of those strings are what keep this honest. The script's header comment names
#    itself and three of the four conditions in a single `<pre class="src">` block, so a
#    set without `/solve-issue` and `first bail` — neither of which appears anywhere in
#    solvable-issues.sh, which never names its caller — would be green against a page with
#    no new diagram at all.
#    What this cannot see is separateness: case 21's names and these do not overlap, so one
#    combined figure would satisfy both cases. That the two are drawn as two figures is a
#    judgement about the drawing, not a claim a name test can make.
diagrams_stage5 "the stage-5 intro draws the rung above the conductor" \
'solvable-issues.sh
/solve-issue
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
  bash -c 'rewrite_hunk_as_feat skills/solve-issue/scripts/classify-bail.sh 3 4 \
             "# rewritten by the v0.2 commit" \
             "feat: rewrite lines 3 and 4 of classify-bail.sh (#2)" v0.2'

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

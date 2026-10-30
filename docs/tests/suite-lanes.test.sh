#!/usr/bin/env bash
# Unit tests for the line between the repository's two test targets — like
# workflow-timeouts.test.sh this suite has no script as its
# subject: its subject is which suite each target runs. Zero-dependency plain-shell
# asserts, same idiom as the other suites under docs/tests/.
#
# Why this exists (issue #137): `make test` is what every veri leaf runs after every edit
# and what the conductor reads the baseline off, so a docs assertion inside it lets the
# docs pipeline stop development on a red the code did not cause. ADR 0016 puts the two on
# separate cadences.
#
# Contract under test:
#   No suite `make test` runs declares a subject in the docs pipeline.
#
#   And the prose a reader consults says the same lane the targets and the gate script
#   enforce: CLAUDE.md and the `Makefile` / `docs/merge-gates.sh` headers say where a docs
#   suite lives and which gate runs it, the merge gate's selection included. Which words
#   carry those facts is the author's — each probe accepts any phrasing that carries one.
#
# Both rosters are read off `make -n`, which expands a target's list and runs nothing. The
# claim is which suites a target would run, and running them to find out would cost
# minutes — and for docs-test would recurse into this file.
#
# Where this suite lives is decided by its own subject: a suite about the docs lane
# running inside `make test` is the arrangement it exists to forbid. It reads two make
# expansions and one small suite, and spawns no page build, so it costs `make docs-test`
# about a second.
#
# Run: docs/tests/suite-lanes.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
pass=0 fail=0

# What a subject line naming the docs pipeline looks like. Every suite in this repository
# declares its subject on its first comment line ("Unit tests for scripts/verify.sh — …",
# "Unit tests for the workflow files under .github/workflows/ — …"), so that one line is
# where a docs suite gives itself away: it names a path under docs/, or the page those
# paths build. Not a format anyone has to keep — a suite whose subject is a script says so
# without either word.
DOCS_SUBJECT='docs/|walkthrough'

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

# flat <text> — one line of it, for a failure message. Newlines become slashes so a roster
# or a suite's tail that came back wrong is still readable inside an indented problem line.
# The one place a here-string would not do: `<<<` appends a newline, which `tr` would turn
# into a trailing slash on every message.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# lower <text> — lowercased, so a probe's regexes can be written in one case and still meet
# prose that capitalises a sentence or a `Makefile`. `tr` and not `${text,,}` because that
# expansion is bash 4 and this tree runs on the Mac's bash 3.2. Named once because both
# probes that read prose start by doing this: says() over a whole piece, and
# probe_no_stale_trigger over the clauses it splits one into.
lower() { printf '%s' "$1" | tr 'A-Z' 'a-z'; }

# roster <target> — the suite paths <target> would run, one per line. `make -n` prints the
# recipe with the wildcard already expanded and executes none of it, so this is the
# target's own list rather than a second copy of the glob written out here.
roster() { make -C "$ROOT" -n "$1" 2>&1 | grep -o '[^ ]*\.test\.sh' | sort -u; }

# subject <path> — the first comment line after the shebang, which is where every suite in
# this tree says what it is about.
subject() { awk 'NR > 1 && /^#/ { print; exit }' "$ROOT/$1"; }

# header <path> — everything above the first `set` line, which is where every file in this
# tree keeps its rationale: a suite's is the paragraph arguing where it lives, a script's is
# the paragraph arguing what it does. One helper because both cases read it the same way —
# case 1 asks the moved suite's, case 2 asks docs/merge-gates.sh's. Takes a full path, as
# comment_above does.
header() { awk '/^set / { exit } { print }' "$1"; }

# comment_above <path> <regex> — the run of `#` lines directly above the first line of
# <path> matching <regex>, which is where a Makefile keeps a target's rationale. The run
# resets on any non-comment line, so this returns that target's own paragraph and not
# every comment in the file.
comment_above() {
  awk -v re="$2" '
    $0 ~ re { for (i = 1; i <= n; i++) print buf[i]; exit }
    /^#/ { buf[++n] = $0; next }
    { n = 0 }
  ' "$1"
}

# gate_row / gate_makefile_comment / gate_header — the three copies of the merge gate's rule
# the prose cases ask about, each located the way its own file keeps it: CLAUDE.md's table
# row by its leading cell, the Makefile target's paragraph by the run of comments above it,
# the script's rationale by everything above its first `set` line. Named rather than located
# at the call site so the case that asks all three reads as three copies of one fact, and —
# so that the two copies case 3 asks again are located by the
# same expression there as here, rather than quietly judging different prose.
#
# The `where` each one is reported under travels with it, for the other half of that reason:
# a probe puts it in front of the problem line, so two spellings of the same copy would read
# in the output as two different files being stale.
GATE_ROW_WHERE="CLAUDE.md's 'make merge-gates' row"
GATE_MAKEFILE_WHERE="the Makefile comment above the merge-gates target"
GATE_HEADER_WHERE="docs/merge-gates.sh's header"
gate_row() { grep -m1 '^| `make merge-gates`' "$ROOT/CLAUDE.md"; }
gate_makefile_comment() { comment_above "$ROOT/Makefile" '^merge-gates:'; }
gate_header() { header "$ROOT/docs/merge-gates.sh"; }

# says <where> <text> <fact> <regex>... — one fact a piece of prose has to carry, written
# as the regexes that would show it is there: all of them have to match the lowercased
# text, and "<where> does not say <fact>" names it once if any does not. Appends to
# `$problems` the way report() reads it, and each regex accepts any wording that carries the fact, so
# the case pins what the docs say and not how they are phrased.
says() {
  local where="$1" fact="$3" lc re
  lc="$(lower "$2")"
  shift 3
  for re in "$@"; do
    [[ "$lc" =~ $re ]] || { problems+=("$where does not say $fact"); return; }
  done
}

# probe_dev_lane_clean — the lane's other half, which is a sweep and not a question about one
# file: every suite `make test` would run, read for a subject line that names the docs
# pipeline. A sweep because the rule is about the lane and not about one suite — any file
# `make test` runs whose subject names something under docs/ is the same failure wearing a
# different name, so asking only whether the ADR suite left would miss the next one. Asks
# for development's roster itself because nothing else in the case reads it, and appends to
# `$problems` the way report() reads it.
probe_dev_lane_clean() {
  local suite subj
  while IFS= read -r suite; do
    [[ -n "$suite" ]] || continue
    subj="$(subject "$suite")"
    if grep -Eq "$DOCS_SUBJECT" <<< "$subj"; then
      problems+=("'make test' runs $suite, whose subject is the docs pipeline: $(flat "$subj")")
    fi
  done <<< "$(roster test)"
}

# probe_widened_selection <where> <text> — the two halves of what each copy of the merge
# gate's rule has to carry, asked of one piece of prose: which changes bring the docs
# suites out (anything under docs/ except the page, which is the build's output rather than
# one of its inputs), and which target runs them. Appends to `$problems` through says(),
# which is what makes a failure name the file whose copy is stale.
probe_widened_selection() {
  says "$1" "$2" "the merge gate owes the docs suites for a change under docs/ except the page" \
    'under [^ ]*docs/' 'except|but|other than|apart from' 'walkthrough\.html|the page'
  says "$1" "$2" "which target it runs there — it never names docs-test" 'docs-test'
}

# probe_no_stale_trigger <where> <text> — the negative half of the same rule (#164): a copy
# must not list a `Makefile` change among what brings docs-fresh out. A prose probe and not
# a behaviour one because the behaviour has its own case in merge-gates.test.sh; what this
# catches is the copy left behind, which is the one that sends the next reader to regenerate
# a page on a development branch — exactly the bill #164 removed.
#
# Written as a clause sweep rather than as a `says` regex over the whole text, because the
# text has to stay free to say the opposite: "a `Makefile` change owes nothing" mentions
# both words and is the correct prose. So the unit is the clause — a line or a
# comma-separated part of one, which is how both copies list a trigger — and a clause is a
# failure only when it names the Makefile and the gate together without negating the pair.
FRESH_GATE='docs-fresh|freshness check'
NEGATED='(^|[^a-z-])(no|not|never|nothing|neither|nor|stops|stopped|longer)([^a-z]|$)'
probe_no_stale_trigger() {
  local where="$1" clause
  while IFS= read -r clause; do
    [[ "$clause" =~ makefile   ]] || continue
    [[ "$clause" =~ $FRESH_GATE ]] || continue
    [[ "$clause" =~ $NEGATED    ]] && continue
    problems+=("$where still names a Makefile change as owing docs-fresh: $(flat "$clause")")
  done <<< "$(lower "$2" | tr ',' '\n')"
}

# probe_suite_home_prose — the lane's first half as a reader meets it: CLAUDE.md's Testing
# idiom section, which is the section that tells an author writing a suite where to put it.
# Reads that section by its heading — from `## Testing idiom` to the next `## ` — and asks
# says() for the two facts, so it appends to `$problems` the way report() reads it.
probe_suite_home_prose() {
  local idiom
  idiom="$(awk '/^## Testing idiom/ { f = 1; next } f && /^## / { exit } f' "$ROOT/CLAUDE.md")"
  says "CLAUDE.md's Testing idiom section" "$idiom" \
    "a docs-pipeline suite lives under docs/tests/ and runs there by existing" \
    'docs/tests/' 'glob|by existing'
}

# probe_gate_rule_prose — the lane's other half, asked of each of the three copies of the
# merge gate's rule: CLAUDE.md's command-table row, the Makefile comment above the target,
# and the gate script's own header. One probe over three pieces of prose because the fact
# is one — each copy goes through probe_widened_selection, whose <where> argument is what
# makes a failure name the copy that is stale. Each piece is read the way its own file
# keeps it: a table row by its leading cell, a Makefile target's paragraph by the run of
# comments above it, a script's rationale by everything above its first `set` line.
probe_gate_rule_prose() {
  probe_widened_selection "$GATE_ROW_WHERE"      "$(gate_row)"
  probe_widened_selection "$GATE_MAKEFILE_WHERE" "$(gate_makefile_comment)"
  probe_widened_selection "$GATE_HEADER_WHERE"   "$(gate_header)"
}

# probe_stale_trigger_gone — the #164 half of the same rule, over the two copies the
# criterion names. The same kind of wrapper probe_gate_rule_prose is, for the same reason:
# a case body below is a list of the facts it claims, and each probe goes and finds its own
# prose, rather than one case reaching for gate_row/gate_header at the call site while its
# neighbour does not. The Makefile's comment is not swept here — the criterion names two
# copies, and the behaviour itself has its own case in merge-gates.test.sh.
probe_stale_trigger_gone() {
  probe_no_stale_trigger "$GATE_ROW_WHERE" "$(gate_row)"
  probe_no_stale_trigger "$GATE_HEADER_WHERE" "$(gate_header)"
}

# 1. No suite development's target runs is about the docs pipeline.
name="no suite 'make test' runs is about the docs pipeline"
problems=()

probe_dev_lane_clean

report "$name"

# 2. The same lane, as the three places a reader is sent to read it: CLAUDE.md's command
#    table and Testing idiom section, the `Makefile` comment above the merge-gates target,
#    and docs/merge-gates.sh's own header. One case because it is one fact wearing three
#    copies — where a docs suite lives, and which gate runs it — and a copy that still
#    describes the narrow selection the gate had before this issue sends the next reader
#    to run the wrong thing, or to conclude the widened gate is a bug.
#
#    The merge gate's rule is the directory and not a list of its parts, so each probe asks
#    for that shape — anything under docs/ but the page, which is output rather than input
#    — and for the target it runs, rather than for the old enumeration of docs/wt/,
#    build-walkthrough.py and docs/tests/. Regexes, not fixed strings: the facts are the
#    claim, the wording is the author's.
name="CLAUDE.md and the Makefile / merge-gates.sh headers say where a docs suite lives and which gate runs it"
problems=()

probe_suite_home_prose
probe_gate_rule_prose

report "$name"

# 3. #164: and the same copies no longer name a `Makefile` change as owing docs-fresh. The
#    Makefile sat in the gate's stale pattern beside the page itself, and both copies of the
#    rule wrote that down; the pattern has been carved back to the page alone, because the
#    page goes stale by design on every tag and every script commit, so a branch that edited
#    a recipe was billed a freshness check it could not pass for a reason it had nothing to
#    do with. Prose that still lists the trigger is the half a reader meets first: it sends
#    the next person to regenerate a docs artifact on a development branch, or to read the
#    carve-out as a bug and put it back.
#
#    The two copies the criterion names, each asked separately so a failure says which one
#    is stale. A clause sweep, not a ban on the word: the copies are free to say a Makefile
#    change owes nothing, and the correct prose for this carve-out probably does.
name="CLAUDE.md's row and merge-gates.sh's header no longer name a Makefile change as owing docs-fresh"
problems=()

probe_stale_trigger_gone

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

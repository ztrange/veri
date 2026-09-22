#!/usr/bin/env bash
# Unit tests for the guard suite that keeps a `pipefail` suite from reading its own writer's
# SIGPIPE as an answer — skills/tdd/scripts/tests/no-sigpipe-pipelines.test.sh. Like
# docs-read-guard.test.sh, hermetic-suites.test.sh and count-line-guard.test.sh this suite
# has no script as its subject: its subject is what another suite reports about the tree it
# is run in. Zero-dependency plain-shell asserts, same idiom as docs-read-guard.test.sh.
#
# Why this exists (issue #422): a suite that declares `set -uo pipefail` and ends a pipeline
# in `grep -q` asks its question of the wrong process. `grep -q` exits on its first match; if
# the writer still has bytes to push, its next write lands on a closed pipe, it dies of
# SIGPIPE (141), `pipefail` makes the whole pipeline 141, and the assertion built on that
# status is inverted. It is green on the development Mac (BSD grep buffers ~16 KB, so the
# writer needs one write and the race cannot happen) and red on CI (glibc gives the pipe a
# 4096-byte buffer), which is the worst shape this can take: the leaf and the blind verifier
# both run on the Mac, so a run reports green and the PR is red. It cost two consecutive
# runs — count-line-guard.test.sh (#418) and prompt-test-tiers.test.sh (#416). Repairing
# today's sites fixes today; the guard is what stops the next suite from being written that
# way.
#
# Contract under test (this case):
#   Over a tests directory holding one suite that declares `pipefail` and ends a pipeline in
#   `grep -q`, and one that ends the same pipeline in the same `grep -q` without declaring
#   `pipefail`, no-sigpipe-pipelines.test.sh fails, names the first as `<suite>:<line>` at
#   the offending line, and says nothing about the second.
#
# The second fixture is not extra generality: `pipefail` is half of the condition the
# criterion states. Without it the case is satisfied by a guard that names every pipeline
# into a grep in the tree — a guard the first author it blocked would delete, taking the
# real check with it. A suite whose pipeline's status is grep's own is doing nothing this
# issue forbids: the writer's SIGPIPE never reaches the exit status.
#
# Both suites are planted rather than asserted about where they stand: after this issue's
# other steps this repository has no live site left, so a probe over the real tree would
# pass on both sides of the fix and pin nothing. The plant goes in a scratch tree and the
# guard is copied into it, which is how docs-read-guard.test.sh puts a guard in front of a
# tree it was not written against; the guard therefore answers about the planted tree the
# same way it answers about this one, by being run inside it.
#
# No line of this file spells a pipeline ending in `grep -q` contiguously — the fixture's
# offending line is assembled from `GREP_Q` below and printf'd into the plant. That is not
# decoration: a line of THIS suite carrying the shape is exactly what the guard exists to
# catch, and a test that trips its own subject over the real tree would make the next step
# unachievable. It is also why this suite's own probes feed grep by herestring rather than
# through a pipe.
#
# Run: skills/tdd/scripts/tests/sigpipe-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The guard, twice, and neither name substitutes for the other: repo-relative is what a
# failure message quotes, absolute is what copying it into the plant needs.
GUARD='skills/tdd/scripts/tests/no-sigpipe-pipelines.test.sh'
GUARD_PATH="$ROOT/$GUARD"
GUARD_NAME="$(basename "$GUARD")"

# Where a suite lives, and so where the plant puts one: the guard is handed a tree, not a
# list, and it has to find both fixtures by the directory they sit in.
TESTS_DIR='skills/tdd/scripts/tests'

# The two planted suites. Named for what each does with the shape rather than for a script,
# because neither has a subject — they exist to be read by the guard, and the failure
# messages below quote their names as the guard would have to.
OFFENDER='probes-under-pipefail.test.sh'
INNOCENT='probes-without-pipefail.test.sh'

# The two reader halves an offending line can end in, side by side because they are one
# kind of thing — a reader that leaves before EOF — and `probe_line` takes either. Each is
# written once because three places must spell it identically: the planters print it into
# their fixtures and a premises probe asserts it is really there. Kept apart from the `|`
# for the reason the header gives, and for one more in the head case's: once the guard
# catches that shape, a line of this suite spelling it whole would be its own first
# offender.
GREP_Q='grep -qF -- "$want"'
# `head` stops as soon as it has the lines it was asked for, and a writer with more to push
# then dies of SIGPIPE exactly as it does into `grep -q` — same inversion, a different
# reason for the reader to leave.
HEAD_R='head -n 1'

# The declaration that makes the shape a bug rather than a habit. The offender carries it;
# the innocent carries `set -u` alone.
PIPEFAIL_LINE='set -uo pipefail'

# The comment the offending line ends in, so this suite can find that line's number without
# carrying a copy of the shape of its own — see the header. Nothing about the mark is
# visible to the guard: it is an ordinary trailing comment on an ordinary line of bash.
MARK='the-probe'

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

# begin_case — the state every case starts from: an empty `problems` array, and every
# variable a plant, a run or a probe leaves behind cleared. Written once rather than copied
# into each case, because the list is what a variable added tomorrow would be forgotten
# from, and a case that reads what the one before it left is a case probing the previous
# tree — which, for `tree` itself, is a case tearing that tree down twice and its own not at
# all.
begin_case() {
  problems=()
  tree=""
  offender_path=""
  innocent_path=""
  guard_copy=""
  offender_line=""
  marked=""
  guard_out=""
  guard_code=0
}

# drop_tree — the scratch tree a case planted, removed, which every case owes before it
# reports. Guarded on the name because a case whose `open_tree` failed has no tree to
# remove.
drop_tree() {
  [[ -z "$tree" ]] || rm -rf "$tree"
}

# flat <text> — one line of it, for a failure message: newlines become slashes so a run's
# output quoted inside an indented problem line stays one line. Pure parameter expansion
# rather than a pipe into `tr`, which is two processes per problem line.
flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

# probe_line <body-variable> <reader> — the offending line, assembled: a writer whose output
# is fed into an early-exiting reader, marked so this suite can find it again. Built here,
# from the reader constants above, rather than written out whole, for the reason the header
# gives. One template for both readers, because what makes the line an offence is the writer
# feeding a reader that leaves — not which reader it is.
probe_line() {
  printf 'printf "%%s\\n" "$%s" | %s  # %s\n' "$1" "$2" "$MARK"
}

# write_plant <path> <set-line> <comment> <probe-line> — write one fixture suite, whole and
# executable. The three fixtures differ only in what they declare, what their comment says
# and which reader their marked pipeline ends in; the suite skeleton around those three is
# written once, here, rather than copied per fixture. Whole down to the count line, and
# executable, because the guard meets them in a directory of runnable suites rather than
# being handed a file.
write_plant() {
  local path="$1" set_line="$2" comment="$3" probe="$4"
  {
    echo '#!/usr/bin/env bash'
    echo "# Unit tests for a prompt template — $comment"
    echo "$set_line"
    echo 'body="$(printf "line %s\n" $(seq 1 400))"'
    echo 'want="line 3"'
    echo 'pass=0 fail=0'
    echo 'if '"$probe"
    echo 'then pass=1; else fail=1; fi'
    echo 'echo "----"'
    echo 'echo "$pass passed, $fail failed"'
    echo '[[ "$fail" -eq 0 ]]'
  } > "$path"
  chmod 755 "$path"
}

# plant_offender <reader> — write the suite the guard must catch, at `offender_path`: it
# declares `pipefail` and ends a pipeline in the reader it is handed, so the status it
# asserts on is its own printf's rather than the reader's. That is the shape of both sites
# this issue repairs, and the reader is an argument because which of the two a case plants
# changes nothing else about the fixture — as `probe_plant_is_what_it_claims` already says
# of the premises asked of it afterwards.
plant_offender() {
  write_plant "$offender_path" "$PIPEFAIL_LINE" \
    'the pipeline below is the shape the guard has to catch.' "$(probe_line body "$1")"
}

# plant_innocent — write the suite the guard must leave alone, at `innocent_path`: the same
# writer into the same `grep -q`, with no `pipefail` declared, so the pipeline's status is
# the reader's own and the writer's SIGPIPE never reaches it.
plant_innocent() {
  write_plant "$innocent_path" 'set -u' \
    'the same pipeline, with the status the readers own.' "$(probe_line body "$GREP_Q")"
}

# open_tree <offender-name> — make the scratch tree a case is asked about, leave its path in
# `tree`, and name the two files every case has one of: the offending suite at
# `offender_path` and the guard's copy at `guard_copy`. Where each file lands is named once,
# here, rather than reassembled at each place that writes, copies, greps or runs one; `tree`
# is only known from the line above them, so these cannot sit with the constants at the top
# of the file. Returns non-zero, with the broken premise recorded, when there is no tree to
# plant in.
open_tree() {
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch tree to plant this case's suites in, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR"

  offender_path="$tree/$TESTS_DIR/$1"
  guard_copy="$tree/$TESTS_DIR/$GUARD_NAME"
}

# seal_tree — what every case does once its fixtures are written: copy the guard in, stage
# the tree, and leave the offending line's number in `offender_line`.
#
# The tree is made a git repository with its fixtures staged. Nothing in the contract says
# how the guard enumerates the suites it reads, and `git ls-files` is as reasonable an
# answer as a glob; an unstaged plant would make a case report on that choice instead of on
# the detection it is asking about.
seal_tree() {
  cp "$GUARD_PATH" "$guard_copy"
  git init -q "$tree" >/dev/null 2>&1
  git -C "$tree" add -A >/dev/null 2>&1

  offender_line="$(grep -n "$MARK" "$offender_path" | cut -d: -f1)"
  # Not the status of that assignment (#183): a grep that found no mark must not make the
  # case skip its probes and report an empty `problems` array as a pass. Whether the plant
  # is what it claims is a premises probe's question, and it names the broken premise when
  # the answer is no.
  return 0
}

# plant — the tree case 1 is asked about: both fixtures, and the guard, in one directory.
# Both fixtures are whole suites down to the count line, because the guard is run over the
# directory rather than handed a file, and a directory of half-suites is not the thing it
# will meet.
plant() {
  open_tree "$OFFENDER" || return 1
  innocent_path="$tree/$TESTS_DIR/$INNOCENT"

  plant_offender "$GREP_Q"
  plant_innocent

  seal_tree
}

# probe_guard_is_there — the premise every probe below rests on, and the one that answers
# while the guard does not exist yet: there is a suite at that path and it can be run.
# Returns non-zero so the case stops here rather than reporting a plant it never made.
probe_guard_is_there() {
  [[ -f "$GUARD_PATH" ]] || {
    problems+=("there is no guard suite at $GUARD, so nothing under $TESTS_DIR is checked for a pipefail suite that ends a pipeline in an early-exiting reader")
    return 1
  }
  [[ -x "$GUARD_PATH" ]] || {
    problems+=("$GUARD is not executable, so \`make test\`'s runner cannot run it")
    return 1
  }
}

# probe_plant_declares_pipefail — the premise all three plants share, and the half of the
# condition that makes the shape a bug rather than a habit: the fixture really turns the
# option on. Without it the pipeline's status is the reader's own, the writer's SIGPIPE never
# reaches the assertion, and the guard is owed nothing about the line. One copy rather than
# three, because it is the same sentence asked of the same file by whichever premises probe
# a case runs.
probe_plant_declares_pipefail() {
  grep -qF -- "$PIPEFAIL_LINE" "$offender_path" ||
    problems+=("the planted offender never declares '$PIPEFAIL_LINE', so its pipeline's status is the reader's own and the shape is not a bug at all")
}

# probe_marked_line_is_findable — the premise every premises probe below opens with, and the
# one that answers while the mark named no line at all: the comment `probe_line` ends the
# offending line in named exactly one line, so there is an address to ask the guard for. The
# line it named is left in `marked` for the checks that follow it, which is why this is a
# probe rather than a `$(…)`: a problem recorded inside a command substitution is recorded in
# a subshell and lost. Returns non-zero so a probe that gates on it stops rather than asking
# after a line there is none of.
probe_marked_line_is_findable() {
  [[ "$offender_line" =~ ^[0-9]+$ ]] || {
    problems+=("the planted offender has no single marked line to name (found '$offender_line'), so the criterion cannot be asked")
    return 1
  }
  marked="$(sed -n "${offender_line}p" "$offender_path")"
}

# probe_plant_is_what_it_claims <reader> — a plant's premises, asserted rather than assumed.
# The offending line has to be findable by its mark, has to really feed a writer into the
# reader the case planted, and the suite holding it has to really declare `pipefail`, or
# `offender_line` is a number the guard was never owed.
#
# The reader is an argument because all three cases plant the same shape and differ in
# nothing but which reader their pipeline ends in: which one a case plants is the case's
# business, and what makes any of them a plant worth running the guard over is this probe's.
# Returns non-zero when there is no marked line, since every premise below is about a line
# there is none of, so a case that gates on it stops rather than reporting a plant it never
# made.
probe_plant_is_what_it_claims() {
  local reader="$1"
  probe_marked_line_is_findable || return 1
  [[ "$marked" == *"|"*"$reader"* ]] ||
    problems+=("the planted offender's line $offender_line does not end a pipeline in $reader, so there is nothing there to catch: $(flat "$marked")")
  probe_plant_declares_pipefail
}

# probe_innocent_is_what_it_claims — the contrast fixture's own premises, which only case 1
# plants one of: it has to carry the same reader and no `pipefail`, or "the guard said
# nothing about it" is true of a fixture with nothing to say about. Apart from the offender's
# premises above because a case that plants no innocent has no such premise to ask.
probe_innocent_is_what_it_claims() {
  grep -qF -- "$GREP_Q" "$innocent_path" ||
    problems+=("the planted innocent carries no such pipeline at all, so a guard that refuses every pipeline into a grep would still pass this case")
  ! grep -qF -- "$PIPEFAIL_LINE" "$innocent_path" ||
    problems+=("the planted innocent declares '$PIPEFAIL_LINE' too, so it is a second offender rather than the contrast this case needs")
}

# run_guard — run the guard over the planted tree once, leaving what it said in `guard_out`
# and how it exited in `guard_code`. A step of its own rather than the first line of the
# probe below, because both probes ask about that one run: as a side effect of the first,
# the second's subject existed only as long as nobody reordered them.
run_guard() {
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
}

# probe_guard_names_the_offender_with_its_line <suite> <reader> — the criterion, and it asks
# for both halves of what a guard is: a failure, and an address. Not "the output mentions the
# suite" — a guard that listed every suite it read would satisfy that — but `<suite>:<line>`,
# which is the only thing that sends the next author to the site rather than to the file.
#
# The planted suite and the reader its pipeline ends in are arguments because both cases ask
# this of their own run of the guard and differ in nothing else: which shape the plant
# carries is the case's business, and what a guard owes for either is this probe's.
probe_guard_names_the_offender_with_its_line() {
  local suite="$1" reader="$2" named
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over a suite that declares '$PIPEFAIL_LINE' and ends a pipeline in $reader; it exited 0 and said: $(flat "$guard_out")")
  named="$(grep -F "$suite" <<< "$guard_out")"
  [[ -n "$named" ]] || {
    problems+=("no line of the guard's output names $suite, whose line $offender_line ends a pipeline in $reader under '$PIPEFAIL_LINE'; it said: $(flat "$guard_out")")
    return
  }
  grep -qF -- "$suite:$offender_line" <<< "$named" ||
    problems+=("the guard named $suite but not as $suite:$offender_line, where the pipeline is; the lines naming it were: $(flat "$named")")
}

# probe_guard_leaves_the_innocent_alone — the other half of the condition the criterion
# states, and the half that keeps the guard from being a grep for `grep -q`. A suite whose
# pipeline status is the reader's own cannot read a writer's SIGPIPE as its answer, and the
# guard must have nothing to say about it — not a softer complaint, no complaint.
probe_guard_leaves_the_innocent_alone() {
  local named
  named="$(grep -F "$INNOCENT" <<< "$guard_out")"
  [[ -z "$named" ]] ||
    problems+=("the guard named $INNOCENT, which ends the same pipeline in $GREP_Q without declaring '$PIPEFAIL_LINE': $(flat "$named")")
}

# The suite the head case plants. A name of its own rather than a second use of OFFENDER
# because both plants exist in the same run, and a failure message has to say which of the
# two shapes it was asked about.
HEAD_OFFENDER='probes-head-under-pipefail.test.sh'

# plant_lone_offender <suite-name> <reader> — a tree holding one offending suite and the
# guard, and no innocent: the criterion each case below it pins is that its shape is named
# at all, and what keeps the guard from answering "every line is one" is already pinned by
# case 1, over the same guard. A tree of its own per case, rather than another file in case
# 1's, so that case's fixtures stay the pair its contract is written about — but the same
# variable names throughout, because the cases run one after another and each tears its tree
# down before the next begins, so there is only ever one plant in hand.
plant_lone_offender() {
  open_tree "$1" || return 1

  plant_offender "$2"

  seal_tree
}

# 1. One criterion, one case: the guard fails over a `pipefail` suite that ends a pipeline
#    in `grep -q`, says where, and says nothing about the same pipeline without `pipefail`.
#    Both halves are probed over one run of the guard against one tree holding both
#    fixtures, because that is the tree it ships against — a guard asked about each shape in
#    isolation could answer "every pipeline here is one" to the first and be caught by
#    nothing.
name="no-sigpipe-pipelines.test.sh names a suite that declares pipefail and ends a pipeline in grep -q as <suite>:<line>, and says nothing about the same pipeline without pipefail"
begin_case

if probe_guard_is_there && plant; then
  probe_plant_is_what_it_claims "$GREP_Q"
  probe_innocent_is_what_it_claims
  run_guard
  probe_guard_names_the_offender_with_its_line "$OFFENDER" "$GREP_Q"
  probe_guard_leaves_the_innocent_alone
fi
drop_tree

report "$name"

# 2. The same guard, the other early-exiting reader: a suite that declares `pipefail` and
#    ends a pipeline in `head` is named as `<suite>:<line>` too. `head` is the other half of
#    the shape the issue names — `docs/tests/` alone holds dozens of sites — and a guard that
#    caught only `grep -q` would let the next one in. One fixture and one run, for the reason
#    `plant_lone_offender` gives.
name="no-sigpipe-pipelines.test.sh names a suite that declares pipefail and ends a pipeline in head as <suite>:<line>"
begin_case

if probe_guard_is_there && plant_lone_offender "$HEAD_OFFENDER" "$HEAD_R"; then
  probe_plant_is_what_it_claims "$HEAD_R"
  run_guard
  probe_guard_names_the_offender_with_its_line "$HEAD_OFFENDER" "$HEAD_R"
fi
drop_tree

report "$name"

# The suite the exemption case plants, and the entry the case writes about it. A name of its
# own, like the head case's, because all three plants exist in the same run and a failure
# message has to say which of them it was asked about.
EXEMPT_OFFENDER='probes-exempted-under-pipefail.test.sh'

# The exemption table's own line, which is what an entry is added after. Named here because
# two things need it identically: the premise that asks whether the guard carries a table at
# all, and the injection that puts an entry in it.
EXEMPT_DECL='declare -A EXEMPT=('

# The reason a real entry carries — one sentence saying why the early exit is the point at
# that site, which is the only thing an exemption is ever for. Its content is nothing the
# guard reads; that it is non-empty is the whole of what the second half of this case is
# about.
EXEMPT_REASON='the early exit is the point here: the probe asks whether the first match exists at all, and its writer is one line long'

# exempt <key> <reason> — put the guard's own copy back and add exactly one entry to its
# exemption table. The copy is rewritten first because this case runs the guard twice, once
# per half of the criterion, and each run must meet a table holding only the entry its own
# probe is about rather than the one the other left behind.
#
# awk rather than sed: the reason is arbitrary prose and sed would read a `/` or a `&` in it
# as syntax. The entry goes immediately after the table's opening line, which is where a
# human adding one puts it.
exempt() {
  local key="$1" reason="$2" entry
  entry="  [$key]=\"$reason\""
  awk -v entry="$entry" -v decl="$EXEMPT_DECL" '
    { print }
    !added && index($0, decl) == 1 { print entry; added = 1 }
  ' "$GUARD_PATH" > "$tree/guard.next" && mv "$tree/guard.next" "$guard_copy"
  chmod 755 "$guard_copy"
}

# probe_guard_carries_an_exemption_table — the premise both halves rest on, and the one that
# answers while the guard has no table yet: there is somewhere to record a site where the
# early exit is the point. Returns non-zero so the case stops here rather than running a
# guard whose table it never managed to write into.
probe_guard_carries_an_exemption_table() {
  grep -qF -- "$EXEMPT_DECL" "$GUARD_PATH" || {
    problems+=("$GUARD carries no exemption table ('$EXEMPT_DECL'), so a site where leaving before EOF is the point cannot be recorded with its reason and the only way past the guard is to stop declaring pipefail")
    return 1
  }
}

# probe_entry_is_in_the_table <key> — the premise the run that follows rests on: the entry
# `exempt` wrote is really in the guard's copy. Without it, a silent guard is a guard that
# read no table rather than one that honoured an entry.
probe_entry_is_in_the_table() {
  grep -qF -- "[$1]" "$guard_copy" || {
    problems+=("the entry [$1] is not in the guard copy's exemption table, so what the run below reports is not about an exemption at all")
    return 1
  }
}

# probe_guard_exempts_the_listed_site <key> — the first half of the criterion: a site listed
# in the table with a reason is not a failure. Both halves of that, because a guard that
# named the site in a softer voice and still exited non-zero would leave the run red and the
# author with nothing to do about it: the guard passes, and says nothing about the site.
probe_guard_exempts_the_listed_site() {
  [[ "$guard_code" == 0 ]] ||
    problems+=("want the guard to pass over a site listed in its exemption table as [$1] with a reason; it exited $guard_code and said: $(flat "$guard_out")")
  local named
  named="$(grep -F "$EXEMPT_OFFENDER:$offender_line" <<< "$guard_out")"
  [[ -z "$named" ]] ||
    problems+=("the guard still named $EXEMPT_OFFENDER:$offender_line, which its exemption table lists as [$1] with a reason: $(flat "$named")")
}

# probe_guard_refuses_a_reasonless_entry <key> — the second half: an entry with no reason is
# not an exemption. A table whose entries may be bare keys is a list of sites someone once
# wanted quiet, and the next reader has no way to tell a considered exemption from a silenced
# complaint — which is why the reason is what makes the entry, and its absence has to fail
# the run rather than exempt anything.
#
# The output has to say `reason` on the line naming the key, or a guard that simply ignored
# the bare entry and reported the site as the offence it is would pass this probe while
# telling the author nothing about what is wrong with their table.
probe_guard_refuses_a_reasonless_entry() {
  local key="$1" named
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over the exemption entry [$key], which carries no reason; it exited 0 and said: $(flat "$guard_out")")
  named="$(grep -F "$key" <<< "$guard_out")"
  [[ -n "$named" ]] || {
    problems+=("no line of the guard's output names the reasonless exemption entry [$key]; it said: $(flat "$guard_out")")
    return
  }
  grep -qF -- 'reason' <<< "$named" ||
    problems+=("the guard named $key but never said its reason is what is missing, so the author is told a pipeline is there rather than that their exemption is not one: $(flat "$named")")
}

# 3. One criterion, one case: the exemption table is what lets a site where the early exit is
#    the point stay as it is, and a reason is what makes an entry one. Both halves over one
#    plant and one table, run twice — the same site, exempted with a reason and then with
#    none — because that is the pair the criterion states: what the table buys and what it
#    costs to use it. Two trees would ask the second half about a site the first never
#    silenced. The entry itself is not planted with the tree: each half of the case writes
#    its own, after the premises below have been asked about the plant they both rest on.
name="no-sigpipe-pipelines.test.sh passes over a site its exemption table lists with a reason, and fails naming an entry whose reason is missing"
begin_case

if probe_guard_is_there && probe_guard_carries_an_exemption_table && plant_lone_offender "$EXEMPT_OFFENDER" "$GREP_Q"; then
  if probe_plant_is_what_it_claims "$GREP_Q"; then
    exempt_key="$EXEMPT_OFFENDER:$offender_line"

    exempt "$exempt_key" "$EXEMPT_REASON"
    if probe_entry_is_in_the_table "$exempt_key"; then
      run_guard
      probe_guard_exempts_the_listed_site "$exempt_key"
    fi

    exempt "$exempt_key" ""
    if probe_entry_is_in_the_table "$exempt_key"; then
      run_guard
      probe_guard_refuses_a_reasonless_entry "$exempt_key"
    fi
  fi
fi
drop_tree

report "$name"

# The suite this case plants and then takes away. A name of its own, like the head and
# exemption cases', because every plant in this run must be distinguishable in a failure
# message — and here doubly so: half of what this case asserts is that the guard stops
# saying this name once the file carrying it is gone.
REMOVABLE_OFFENDER='probes-removable-under-pipefail.test.sh'

# unplant — take the planted offender back out of the tree, leaving the guard's copy alone
# in it. `rm` rather than a rewrite of the file into something innocent, because the
# criterion is about the plant being removed: a suite edited until it no longer offends
# would pin that the guard re-reads a file, not that its verdict follows the tree.
unplant() {
  rm -f "$offender_path"
}

# probe_plant_is_gone — the premise the second run rests on, and the one that answers while
# nothing has actually been removed: the offending file is no longer in the tree the guard
# is about to read. Without it a green second run is a guard that ignored an offender that
# is still there, which is the opposite of what this case is for. Returns non-zero so the
# case stops rather than asking about a tree it never changed.
probe_plant_is_gone() {
  [[ ! -e "$offender_path" ]] || {
    problems+=("the planted offender is still at $offender_path, so the run below reads the same tree as the one before it and the guard's second verdict says nothing about removal")
    return 1
  }
}

# probe_guard_is_green_once_the_plant_is_removed <suite> — the other half of the criterion,
# and the half that makes the first half evidence: a guard that fails whatever it is handed
# names a planted offender too. Both halves of green, because a guard that exited 0 while
# still printing the removed suite's address would send the next author to a file that is
# not there: it passes, and it has nothing to say about the suite that left.
probe_guard_is_green_once_the_plant_is_removed() {
  local suite="$1" named
  [[ "$guard_code" == 0 ]] ||
    problems+=("want the guard to pass over the tree once $suite is removed, since the only offending site in it left with that file; it exited $guard_code and said: $(flat "$guard_out")")
  named="$(grep -F "$suite" <<< "$guard_out")"
  [[ -z "$named" ]] ||
    problems+=("the guard still named $suite after that file was removed from the tree, so its verdict is not a read of the tree in front of it: $(flat "$named")")
}

# 4. One criterion, one case: the guard is watched to go red on a planted offender and green
#    again once the plant is removed. The pair is the case — over one tree, the same guard
#    copy, run twice with nothing changed between the runs but the presence of the offending
#    file. Red alone is satisfied by a guard that fails whatever it is handed, and green
#    alone by one that passes whatever it is handed; only the two answers from one tree say
#    the verdict follows the site. Cases 1 to 3 ask what a red verdict must say and what the
#    table buys; this one asks that the verdict is about the tree at all.
name="no-sigpipe-pipelines.test.sh is red over a planted offender, naming it, and green again once the plant is removed"
begin_case

if probe_guard_is_there && plant_lone_offender "$REMOVABLE_OFFENDER" "$GREP_Q"; then
  if probe_plant_is_what_it_claims "$GREP_Q"; then
    run_guard
    probe_guard_names_the_offender_with_its_line "$REMOVABLE_OFFENDER" "$GREP_Q"

    unplant
    if probe_plant_is_gone; then
      run_guard
      probe_guard_is_green_once_the_plant_is_removed "$REMOVABLE_OFFENDER"
    fi
  fi
fi
drop_tree

report "$name"

# The suite the wrapped case plants. A name of its own, like every other plant here, because
# all of them exist in the same run and a failure message has to say which shape it was
# asked about.
WRAPPED_OFFENDER='probes-wrapped-under-pipefail.test.sh'

# probe_line_wrapped <body-variable> <reader> — the same offending pipeline as `probe_line`,
# written the way a long one is really written: the pipe ends one line and the reader opens
# the next. Two lines of bash, one pipeline — the shell joins them, the writer still dies of
# SIGPIPE on a closed pipe, and `pipefail` still hands that 141 up as the status the suite
# asserts on. The mark goes on the reader's line, because that is the line the repair is
# made on and so the address the guard owes.
#
# Assembled by printf, like `probe_line` and for the same reason: a line of this file
# ending in a pipe with a reader on the line below would be this suite's own first offence
# once the guard reads that shape.
probe_line_wrapped() {
  printf 'printf "%%s\\n" "$%s" |\n%s  # %s\n' "$1" "$2" "$MARK"
}

# plant_wrapped_offender <suite-name> <reader> — a tree holding one suite whose pipeline is
# split across two lines, and the guard. Alongside `plant_lone_offender` rather than an
# argument to it, because the two differ in the one thing this case is about: how the
# offending pipeline is laid out on the page.
plant_wrapped_offender() {
  open_tree "$1" || return 1

  write_plant "$offender_path" "$PIPEFAIL_LINE" \
    'the pipeline below is the same shape, wrapped across two lines.' \
    "$(probe_line_wrapped body "$2")"

  seal_tree
}

# probe_line_above_ends_in_the_pipe — the premise both wrapped plants rest on: the line above
# the marked one really ends in the `|` that feeds it, so the two lines are one pipeline and
# there is something there for the guard to read across the break. Asked of the file rather
# than of what the planter meant to write, and written once because it is the same question
# whichever of the two wrapped shapes a case planted.
probe_line_above_ends_in_the_pipe() {
  local before
  before="$(sed -n "$((offender_line - 1))p" "$offender_path")"
  [[ "$before" =~ \|[[:space:]]*$ ]] ||
    problems+=("the line above the planted offender's marked line does not end in the pipe that feeds it, so the two lines are not one pipeline at all: $(flat "$before")")
}

# probe_wrapped_plant_is_what_it_claims <reader> — the wrapped plant's premises, which are
# not the contiguous plant's: the marked line has to hold the reader and no pipe of its own,
# the line above it has to end in the pipe that feeds it, and the suite has to declare
# `pipefail`. Without all three, a guard that says nothing is a guard handed something that
# is not the shape rather than one that failed to read across the line break. Returns
# non-zero when there is no marked line, since every premise after that is about a line
# there is none of.
probe_wrapped_plant_is_what_it_claims() {
  local reader="$1"
  probe_marked_line_is_findable || return 1
  [[ "$marked" == *"$reader"* ]] ||
    problems+=("the planted offender's marked line $offender_line does not open with $reader, so there is no wrapped reader there to catch: $(flat "$marked")")
  [[ "$marked" != *"|"* ]] ||
    problems+=("the planted offender's marked line $offender_line carries a pipe of its own, so it is the contiguous shape case 1 already pins rather than the wrapped one: $(flat "$marked")")
  probe_line_above_ends_in_the_pipe
  probe_plant_declares_pipefail
}

# 5. One criterion, one case: the guard reads the pipeline, not the line. A suite that
#    declares `pipefail` and ends a pipeline in an early-exiting reader is the same offence
#    whether it is written on one line or wrapped over two, and the wrapped spelling is the
#    ordinary one for a long pipeline — so a guard that only ever looks at a line on its own
#    is one an author escapes by pressing return, without ever meaning to. The address owed
#    is the reader's line: that is where the repair is made.
name="no-sigpipe-pipelines.test.sh names a suite whose pipeline is split across two lines, the pipe ending one and the early-exiting reader opening the next, as <suite>:<line>"
begin_case

if probe_guard_is_there && plant_wrapped_offender "$WRAPPED_OFFENDER" "$GREP_Q"; then
  if probe_wrapped_plant_is_what_it_claims "$GREP_Q"; then
    run_guard
    probe_guard_names_the_offender_with_its_line "$WRAPPED_OFFENDER" "$GREP_Q"
  fi
fi
drop_tree

report "$name"

# The suite the both-readings case plants. A name of its own, like every other plant here,
# because all of them exist in the same run and a failure message has to say which shape it
# was asked about.
BOTH_READINGS_OFFENDER='probes-both-readings-under-pipefail.test.sh'

# probe_line_both_readings <body-variable> <first-reader> <second-reader> — one wrapped
# pipeline whose second line answers to both of the guard's readings at once: it opens with
# an early-exiting reader, fed by the `|` ending the line above it, and it goes on to feed a
# second early-exiting reader through a pipe of its own. It is the ordinary way a long
# pipeline is written once it has three stages, not a contrivance — and it is one line of
# bash with one repair to make on it.
#
# Assembled by printf, like `probe_line` and `probe_line_wrapped`, for the reason the header
# gives: a line of this file spelling the shape whole would be the guard's own first
# offender.
probe_line_both_readings() {
  printf 'printf "%%s\\n" "$%s" |\n  %s | %s  # %s\n' "$1" "$2" "$3" "$MARK"
}

# plant_both_readings_offender <suite-name> <first-reader> <second-reader> — a tree holding
# one suite carrying that line, and the guard. Alongside the other planters rather than an
# argument to one of them, because what this case is about is the one thing they differ in:
# how the offending pipeline is laid out on the page.
plant_both_readings_offender() {
  open_tree "$1" || return 1

  write_plant "$offender_path" "$PIPEFAIL_LINE" \
    'the pipeline below is wrapped and goes on piping on the line below.' \
    "$(probe_line_both_readings body "$2" "$3")"

  seal_tree
}

# probe_both_readings_plant_is_what_it_claims <first-reader> <second-reader> — this plant's
# premises, which are neither the contiguous plant's nor the wrapped one's: the marked line
# has to open with the first reader, has to pipe into the second one further along itself,
# and has to be fed by a `|` ending the line above it — all three, or a guard that reported
# the site once did so because only one reading ever reached it, and the case would pass
# without asking anything. Returns non-zero when there is no marked line, since every
# premise after that is about a line there is none of.
probe_both_readings_plant_is_what_it_claims() {
  local first="$1" second="$2"
  probe_marked_line_is_findable || return 1
  [[ "$marked" == *"$first"* ]] ||
    problems+=("the planted offender's marked line $offender_line does not open with $first, so the wrapped reading never reaches it and one report is all there was ever going to be: $(flat "$marked")")
  [[ "$marked" == *"|"*"$second"* ]] ||
    problems+=("the planted offender's marked line $offender_line does not pipe into $second further along itself, so the contiguous reading never reaches it and one report is all there was ever going to be: $(flat "$marked")")
  probe_line_above_ends_in_the_pipe
  probe_plant_declares_pipefail
}

# probe_guard_names_the_site_once <suite> — the criterion's own half: the address is printed
# exactly once. A site is a line to repair, not a reading that matched, and an author handed
# the same `<suite>:<line>` twice is being told there are two things wrong with it — so the
# count is the assertion, and it is asserted on the guard's output rather than on how the
# guard is built, which is the only place a caller can see it. The failure message quotes
# every line that named the site, since what went wrong is how many of them there are.
probe_guard_names_the_site_once() {
  local suite="$1" named count
  named="$(grep -F "$suite:$offender_line" <<< "$guard_out")"
  count="$(grep -cF "$suite:$offender_line" <<< "$guard_out")"
  [[ "$count" -eq 1 ]] ||
    problems+=("want the guard to name $suite:$offender_line exactly once, since one line is one site to repair however many readings of the file reached it; it named it $count times: $(flat "$named")")
}

# 6. One criterion, one case: a line both readings reach is still one site. The wrapped
#    reading and the contiguous one are two ways of finding the same offence, and a line
#    that opens with an early-exiting reader fed from the line above and then pipes into a
#    second one answers to both — so the guard has to report the address once. Not a
#    cosmetic preference: the report is a work list, and a site listed twice says there are
#    two repairs to make at one line. Its address is asked for by the same probe the other
#    cases use, so this case pins the count on top of what a red verdict already owes rather
#    than in place of it.
name="no-sigpipe-pipelines.test.sh names a line both of its readings reach — opened by an early-exiting reader fed from the line above, and piping into another — exactly once"
begin_case

if probe_guard_is_there && plant_both_readings_offender "$BOTH_READINGS_OFFENDER" "$HEAD_R" "$GREP_Q"; then
  if probe_both_readings_plant_is_what_it_claims "$HEAD_R" "$GREP_Q"; then
    run_guard
    probe_guard_names_the_offender_with_its_line "$BOTH_READINGS_OFFENDER" "$GREP_Q"
    probe_guard_names_the_site_once "$BOTH_READINGS_OFFENDER"
  fi
fi
drop_tree

report "$name"

# The fragment of the guard's roster case name that a FAIL line naming that case carries —
# its subject is what `make test` runs, which is the one thing no other case of the guard
# says. Enough to tell that case's verdict apart from the directory case's, and no more of
# the sentence than that, since the rest of it is wording rather than contract.
ROSTER_CASE='`make test` runs'

# The question the roster case asks, and so the thing it has to name when it reports what it
# found: `make -n test` is where the roster comes from, and a note that never names it says
# nothing an author can act on.
ROSTER_QUESTION='make -n test'

# plant_bare_tree — a scratch tree holding nothing but the guard's own copy: no fixture, and
# so no offending site anywhere in it. What makes it the tree this case needs is what every
# plant here already lacks and no case has yet asked about — there is no Makefile in it, so
# `make -n test` can name no suite at all.
plant_bare_tree() {
  open_tree "$OFFENDER" || return 1

  cp "$GUARD_PATH" "$guard_copy"
  git init -q "$tree" >/dev/null 2>&1
  git -C "$tree" add -A >/dev/null 2>&1
}

# probe_tree_has_no_makefile — the premise this case rests on, and the one that answers while
# the tree can be asked about `make test` after all: there is no Makefile in it, so the
# roster read comes back empty and the case below is about an empty roster rather than about
# a roster that happened to hold nothing offending. Returns non-zero so the case stops rather
# than reading a verdict that is not the one it asked for.
probe_tree_has_no_makefile() {
  [[ ! -e "$tree/Makefile" ]] || {
    problems+=("the scratch tree carries a Makefile at $tree/Makefile, so \`make -n test\` there may name suites and this case is not about an empty roster at all")
    return 1
  }
}

# probe_guard_reports_the_empty_roster_without_failing — the criterion, and both halves of
# it. A roster read that comes back empty is something the guard found, not an offence it
# discovered: the tree in front of it has no Makefile, no suite it would run reads its own
# writer's SIGPIPE as an answer because there is no such suite, and failing the run there
# turns every scratch plant this suite builds into a red verdict that says nothing about the
# plant. So the roster case must not be reported as a failure — and it must still say what
# it found, naming `make -n test`, or the difference between "the roster was empty" and "the
# roster was clean" is invisible to whoever reads the output.
probe_guard_reports_the_empty_roster_without_failing() {
  local failures named said
  failures="$(grep -F 'FAIL - ' <<< "$guard_out")"
  named="$(grep -F "$ROSTER_CASE" <<< "$failures")"
  [[ -z "$named" ]] ||
    problems+=("the guard failed its roster case over a tree whose \`$ROSTER_QUESTION\` names no suite, so every scratch plant is red for the tree's missing Makefile rather than for what was planted in it: $(flat "$named")")
  said="$(grep -F "$ROSTER_QUESTION" <<< "$guard_out")"
  [[ -n "$said" ]] ||
    problems+=("no line of the guard's output names \`$ROSTER_QUESTION\` at all, so the empty roster went unsaid and a reader cannot tell a roster that held nothing from one that was never read; it said: $(flat "$guard_out")")
}

# 7. One criterion, one case: an empty roster is a finding, not a failure. The roster case
#    reads what `make test` would run, and in a tree with no Makefile it reads nothing —
#    which is every scratch tree the cases above plant, since a plant is a tests directory
#    and a guard copy and nothing else. Failing there makes the guard's verdict about the
#    plant unreadable: the run is red whatever was planted, so "the guard is green once the
#    plant is removed" cannot be asked at all. What replaces the failure is not silence: the
#    case says what it found, naming the question it asked, so an empty roster in a real
#    tree is still visible to whoever reads the output.
name="no-sigpipe-pipelines.test.sh says what its roster read found when \`make -n test\` names no suite, instead of failing the run"
begin_case

if probe_guard_is_there && plant_bare_tree; then
  if probe_tree_has_no_makefile; then
    run_guard
    probe_guard_reports_the_empty_roster_without_failing
  fi
fi
drop_tree

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

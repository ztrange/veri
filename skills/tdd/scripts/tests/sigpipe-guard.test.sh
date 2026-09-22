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

# plant_offender — write the suite the guard must catch, at `offender_path`: it declares
# `pipefail` and ends a pipeline in `grep -q`, so the status it asserts on is its own
# printf's, not grep's. That is the shape of both sites this issue repairs.
plant_offender() {
  write_plant "$offender_path" "$PIPEFAIL_LINE" \
    'the pipeline below is the shape the guard has to catch.' "$(probe_line body "$GREP_Q")"
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

  plant_offender
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

# probe_plant_is_what_it_claims — the plant's premises, asserted rather than assumed. The
# offending line has to be findable by its mark, has to really feed a writer into the
# early-exiting reader, and the suite holding it has to really declare `pipefail`, or
# `offender_line` below is a number the guard was never owed. The innocent has to carry the
# same reader and no `pipefail`, or "the guard said nothing about it" is true of a fixture
# with nothing to say about.
probe_plant_is_what_it_claims() {
  [[ "$offender_line" =~ ^[0-9]+$ ]] || {
    problems+=("the planted offender has no single marked line to name (found '$offender_line'), so the criterion cannot be asked")
    return
  }
  local marked
  marked="$(sed -n "${offender_line}p" "$offender_path")"
  [[ "$marked" == *"|"*"$GREP_Q"* ]] ||
    problems+=("the planted offender's line $offender_line does not end a pipeline in $GREP_Q, so there is nothing there to catch: $(flat "$marked")")
  grep -qF -- "$PIPEFAIL_LINE" "$offender_path" ||
    problems+=("the planted offender never declares '$PIPEFAIL_LINE', so its pipeline's status is the reader's own and the shape is not a bug at all")
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

# probe_guard_names_the_offender_with_its_line — the criterion, and it asks for both halves
# of what a guard is: a failure, and an address. Not "the output mentions the suite" — a
# guard that listed every suite it read would satisfy that — but `<suite>:<line>`, which is
# the only thing that sends the next author to the site rather than to the file.
probe_guard_names_the_offender_with_its_line() {
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over a suite that declares '$PIPEFAIL_LINE' and ends a pipeline in $GREP_Q; it exited 0 and said: $(flat "$guard_out")")
  local named
  named="$(grep -F "$OFFENDER" <<< "$guard_out")"
  [[ -n "$named" ]] || {
    problems+=("no line of the guard's output names $OFFENDER, whose line $offender_line ends a pipeline in $GREP_Q under '$PIPEFAIL_LINE'; it said: $(flat "$guard_out")")
    return
  }
  grep -qF -- "$OFFENDER:$offender_line" <<< "$named" ||
    problems+=("the guard named $OFFENDER but not as $OFFENDER:$offender_line, where the pipeline is; the lines naming it were: $(flat "$named")")
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

# plant_head_offender — write the suite the guard must catch, at `offender_path`: it
# declares `pipefail` and ends a pipeline in `head`, so the status it asserts on is its own
# printf's rather than the reader's.
plant_head_offender() {
  write_plant "$offender_path" "$PIPEFAIL_LINE" \
    'the pipeline below is the shape the guard has to catch.' "$(probe_line body "$HEAD_R")"
}

# plant_head — the tree the head case is asked about. A tree of its own rather than a third
# file in `plant`'s, so that case's fixtures stay the pair its contract is written about —
# but the same variable names, because the two cases run one after the other and each tears
# its tree down before the next begins, so there is only ever one plant in hand.
#
# One fixture here and no innocent: the criterion this case pins is that the head shape is
# named at all, and what keeps the guard from answering "every line is one" is already
# pinned by the case above, over the same guard.
plant_head() {
  open_tree "$HEAD_OFFENDER" || return 1

  plant_head_offender

  seal_tree
}

# probe_head_plant_is_what_it_claims — the head plant's premises, asserted rather than
# assumed: a single marked line, that line really feeding the writer into `head`, and the
# suite holding it really declaring `pipefail`. Without all three, `offender_line` is a
# number the guard was never owed.
probe_head_plant_is_what_it_claims() {
  [[ "$offender_line" =~ ^[0-9]+$ ]] || {
    problems+=("the planted offender has no single marked line to name (found '$offender_line'), so the criterion cannot be asked")
    return
  }
  local marked
  marked="$(sed -n "${offender_line}p" "$offender_path")"
  [[ "$marked" == *"|"*"$HEAD_R"* ]] ||
    problems+=("the planted offender's line $offender_line does not end a pipeline in $HEAD_R, so there is nothing there to catch: $(flat "$marked")")
  grep -qF -- "$PIPEFAIL_LINE" "$offender_path" ||
    problems+=("the planted offender never declares '$PIPEFAIL_LINE', so its pipeline's status is the reader's own and the shape is not a bug at all")
}

# probe_guard_names_the_head_offender_with_its_line — the criterion: the guard fails, and it
# says where. `head` is the other half of the shape the issue names — `docs/tests/` alone
# holds dozens of sites — and a guard that caught only `grep -q` would let the next one in.
probe_guard_names_the_head_offender_with_its_line() {
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over a suite that declares '$PIPEFAIL_LINE' and ends a pipeline in $HEAD_R; it exited 0 and said: $(flat "$guard_out")")
  local named
  named="$(grep -F "$HEAD_OFFENDER" <<< "$guard_out")"
  [[ -n "$named" ]] || {
    problems+=("no line of the guard's output names $HEAD_OFFENDER, whose line $offender_line ends a pipeline in $HEAD_R under '$PIPEFAIL_LINE'; it said: $(flat "$guard_out")")
    return
  }
  grep -qF -- "$HEAD_OFFENDER:$offender_line" <<< "$named" ||
    problems+=("the guard named $HEAD_OFFENDER but not as $HEAD_OFFENDER:$offender_line, where the pipeline is; the lines naming it were: $(flat "$named")")
}

# 1. One criterion, one case: the guard fails over a `pipefail` suite that ends a pipeline
#    in `grep -q`, says where, and says nothing about the same pipeline without `pipefail`.
#    Both halves are probed over one run of the guard against one tree holding both
#    fixtures, because that is the tree it ships against — a guard asked about each shape in
#    isolation could answer "every pipeline here is one" to the first and be caught by
#    nothing.
name="no-sigpipe-pipelines.test.sh names a suite that declares pipefail and ends a pipeline in grep -q as <suite>:<line>, and says nothing about the same pipeline without pipefail"
problems=()
tree=""
offender_path=""
innocent_path=""
guard_copy=""
offender_line=""
guard_out=""
guard_code=0

if probe_guard_is_there && plant; then
  probe_plant_is_what_it_claims
  run_guard
  probe_guard_names_the_offender_with_its_line
  probe_guard_leaves_the_innocent_alone
fi
[[ -z "$tree" ]] || rm -rf "$tree"

report "$name"

# 2. The same guard, the other early-exiting reader: a suite that declares `pipefail` and
#    ends a pipeline in `head` is named as `<suite>:<line>` too. One fixture and one run,
#    for the reason `plant_head` gives.
name="no-sigpipe-pipelines.test.sh names a suite that declares pipefail and ends a pipeline in head as <suite>:<line>"
problems=()
tree=""
offender_path=""
innocent_path=""
guard_copy=""
offender_line=""
guard_out=""
guard_code=0

if probe_guard_is_there && plant_head; then
  probe_head_plant_is_what_it_claims
  run_guard
  probe_guard_names_the_head_offender_with_its_line
fi
[[ -z "$tree" ]] || rm -rf "$tree"

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

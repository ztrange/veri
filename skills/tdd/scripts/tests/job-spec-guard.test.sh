#!/usr/bin/env bash
# Unit tests for the guard suite that keeps a file under skills/ from killing a background
# process by job spec — skills/tdd/scripts/tests/no-job-spec-kills.test.sh. Like
# sigpipe-guard.test.sh and docs-read-guard.test.sh this suite has no script as its subject:
# its subject is what another suite reports about the tree it is run in. Zero-dependency
# plain-shell asserts, same idiom as sigpipe-guard.test.sh.
#
# Why this exists (issue #424): a job spec names a job in one shell's own job table, and
# that table dies with the shell. A background process killed that way survives whenever the
# shell that started it went first — the child is reparented to PID 1 and nothing is left
# that knows its identity. On 2026-09-22 that left ten orphaned busy-loops on this machine,
# ~988% of CPU for twelve hours, computing nothing and quietly distorting every timing this
# repository measures. The two halves already landed — lib/background.sh kills the pid it
# recorded, and a shell that exits with a survivor says so — repair today's sites; the guard
# is what stops the next one being written, and this suite is what says the guard works.
#
# Contract under test (this step):
#   Over a tree holding one file under skills/ that kills a background process by job spec
#   and one that kills the pid it recorded, no-job-spec-kills.test.sh fails, names the first
#   as `<file>:<line>` at the offending line, and says nothing about the second — and its
#   exemption table honours an entry that carries a reason while failing, naming the entry,
#   over one whose reason is missing.
#
# The second file is not extra generality: killing a background process is not the offence,
# killing it by a name that dies with the shell is. A guard that named every `kill` in the
# tree would be deleted by the first author it blocked, taking the real check with it — and
# lib/background.sh, the fix this issue already shipped, would be its first victim.
#
# Both files are planted rather than asserted about where they stand: after this issue's
# earlier steps the repository has no live site left, so a probe over the real tree would
# pass on both sides of the fix and pin nothing. The plant goes in a scratch tree and the
# guard is copied into it, which is how sigpipe-guard.test.sh puts a guard in front of a
# tree it was not written against; the guard answers about the planted tree the way it
# answers about this one, by being run inside it.
#
# No line of this file spells `kill` followed by a job spec contiguously — the fixture's
# offending line is assembled from KILL and JOB_SPEC below and printf'd into the plant, and
# the prose says "a job spec" where it would otherwise write one out. That is not decoration:
# this suite is itself a file under skills/, so a line here carrying the shape is exactly
# what the guard exists to catch, and a test that trips its own subject would make the next
# step unachievable.
#
# Run: skills/tdd/scripts/tests/job-spec-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The guard, twice, and neither name substitutes for the other: repo-relative is what a
# failure message quotes, absolute is what copying it into the plant needs.
GUARD='skills/tdd/scripts/tests/no-job-spec-kills.test.sh'
GUARD_PATH="$ROOT/$GUARD"
GUARD_NAME="$(basename "$GUARD")"

# Where the plant's two files live, and where its copy of the guard goes. The guard is run
# from inside the planted tree, so it has to sit at the path it sits at here — its own
# notion of the repository root is counted off its own location.
SCRIPTS_DIR='skills/tdd/scripts'
TESTS_DIR='skills/tdd/scripts/tests'

# The two fixtures, repo-relative, because that is the address a guard over the whole of
# skills/ has to quote: a basename says which file only as long as no two of them share one.
# Ordinary scripts rather than suites, since the criterion is about a file under skills/ and
# the shape that cost this machine twelve hours was written in a script, not in a test.
OFFENDER_REL="$SCRIPTS_DIR/probe-load.sh"
INNOCENT_REL="$SCRIPTS_DIR/probe-load-by-pid.sh"
OFFENDER_NAME="$(basename "$OFFENDER_REL")"
INNOCENT_NAME="$(basename "$INNOCENT_REL")"

# The offending line, in halves. `KILL` and `JOB_SPEC` are apart for the reason the header
# gives — joined, this line would be the first thing the guard caught, in the suite that
# tests it.
KILL='kill'
# A job spec: the first job of the shell that started it, which is a name in that shell's
# job table and nowhere else.
JOB_SPEC='%1'
# What the innocent kills with instead: the pid it recorded in `$!` when it started the
# process. A system-wide name, so it still reaches the process from a shell that never held
# the job.
RECORDED_PID='"$victim"'

# The comments the two planted lines end in, so this suite can find each line's number
# without carrying a copy of the shape of its own — see the header. Nothing about either
# mark is visible to the guard: both are ordinary trailing comments on ordinary lines of
# bash. Distinct words rather than one, because both files carry one and the offender's line
# number is the address this case is about.
MARK='job-spec-probe'
SAFE_MARK='recorded-pid-probe'

# The exemption table's own line, which is what an entry is added after. Named here because
# two things need it identically: the premise that asks whether the guard carries a table at
# all, and the injection that puts an entry in it.
EXEMPT_DECL='declare -A EXEMPT=('

# The reason a real entry carries — one sentence saying why the job spec is the right name
# at that site, which is the only thing an exemption is ever for. Its content is nothing the
# guard reads; that it is non-empty is the whole of what the table's half of this case is
# about.
EXEMPT_REASON='the job spec is the point here: the line is quoted prose inside a heredoc, not a kill this shell ever runs'

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

# write_plant <path> <kill-argument> <mark> <comment> — write one fixture script, whole and
# executable. The two fixtures differ only in what their kill names and what their comment
# says; the script around those is written once, here, rather than copied per fixture. Both
# start a real background process, because a guard reading a kill in a file that starts
# nothing is being asked about a shape that is not the one this issue is about.
write_plant() {
  local path="$1" arg="$2" mark="$3" comment="$4"
  {
    echo '#!/usr/bin/env bash'
    echo "# A load generator for a measurement — $comment"
    echo 'set -uo pipefail'
    echo 'sleep 30 &'
    echo 'victim=$!'
    printf '%s %s 2>/dev/null  # %s\n' "$KILL" "$arg" "$mark"
  } > "$path"
  chmod 755 "$path"
}

# plant — the tree this case is asked about: both fixtures and the guard, in one repository.
# The tree is made a git repository with what is in it staged because nothing in the contract
# says how the guard enumerates the files it reads — `git ls-files` is as reasonable an answer
# as a glob, and an unstaged plant would make the case report on that choice instead of on
# the detection it asks about. Leaves the offending line's number in `offender_line`, and
# returns non-zero, with the broken premise recorded, when there is no tree to plant in.
plant() {
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch tree to plant this case's files in, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR"

  offender_path="$tree/$OFFENDER_REL"
  innocent_path="$tree/$INNOCENT_REL"
  guard_copy="$tree/$TESTS_DIR/$GUARD_NAME"

  write_plant "$offender_path" "$JOB_SPEC" "$MARK" \
    'the kill below is the shape the guard has to catch.'
  write_plant "$innocent_path" "$RECORDED_PID" "$SAFE_MARK" \
    'the same process, killed by the pid it recorded.'

  install_guard

  offender_line="$(grep -n "$MARK" "$offender_path" | cut -d: -f1)"
  # Not the status of that assignment (#183): a grep that found no mark must not make the
  # case skip its probes and report an empty `problems` array as a pass. Whether the plant is
  # what it claims is a premises probe's question, and it names the broken premise when the
  # answer is no.
  return 0
}

# install_guard — the guard's own copy put into the tree, and the tree staged. Called by the
# plant, and again by `exempt` below, which rewrites that copy: a run of the guard is only
# ever over the tree as git knows it.
install_guard() {
  cp "$GUARD_PATH" "$guard_copy"
  chmod 755 "$guard_copy"
  git init -q "$tree" >/dev/null 2>&1
  git -C "$tree" add -A >/dev/null 2>&1
}

# drop_tree — the scratch tree this case planted, removed. Guarded on the name because a
# case whose `plant` failed has no tree to remove.
drop_tree() {
  [[ -z "${tree:-}" ]] || rm -rf "$tree"
}

# exempt <key> <reason> — put the guard's own copy back and add exactly one entry to its
# exemption table. The copy is rewritten first because this case runs the guard three times
# and each run must meet a table holding only the entry its own probe is about rather than
# the one the run before it left behind.
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
  git -C "$tree" add -A >/dev/null 2>&1
}

# probe_guard_is_there — the premise every probe below rests on, and the one that answers
# while the guard does not exist yet: there is a suite at that path and it can be run.
# Returns non-zero so the case stops here rather than reporting a plant it never made.
probe_guard_is_there() {
  [[ -f "$GUARD_PATH" ]] || {
    problems+=("there is no guard suite at $GUARD, so nothing under skills/ is checked for a background process killed by a job spec")
    return 1
  }
  [[ -x "$GUARD_PATH" ]] || {
    problems+=("$GUARD is not executable, so \`make test\`'s runner cannot run it")
    return 1
  }
}

# probe_guard_carries_an_exemption_table — the premise the table's half of this case rests
# on, and the one that answers while the guard has no table yet: there is somewhere to record
# a site where the job spec is the right name, with the reason that says why. Returns
# non-zero so the case stops rather than running a guard whose table it never managed to
# write into.
probe_guard_carries_an_exemption_table() {
  grep -qF -- "$EXEMPT_DECL" "$GUARD_PATH" || {
    problems+=("$GUARD carries no exemption table ('$EXEMPT_DECL'), so a site where a job spec is the right name cannot be recorded with its reason and the only way past the guard is to delete it")
    return 1
  }
}

# probe_plant_is_what_it_claims — the plant's premises, asserted rather than assumed. The
# offending line has to be findable by its mark and has to really kill by a job spec, and the
# innocent has to really kill the pid it recorded, or `offender_line` is a number the guard
# was never owed and "the guard said nothing about the innocent" is true of a file with
# nothing to say about. Returns non-zero when there is no marked line, since every probe
# below is about a line there is none of.
probe_plant_is_what_it_claims() {
  [[ "$offender_line" =~ ^[0-9]+$ ]] || {
    problems+=("the planted offender has no single marked line to name (found '$offender_line'), so the criterion cannot be asked")
    return 1
  }
  marked="$(sed -n "${offender_line}p" "$offender_path")"
  [[ "$marked" == *"$KILL $JOB_SPEC"* ]] ||
    problems+=("the planted offender's line $offender_line does not kill by a job spec at all, so there is nothing there to catch: $(flat "$marked")")
  grep -qF -- "$KILL $RECORDED_PID" "$innocent_path" ||
    problems+=("the planted innocent kills nothing by its recorded pid, so a guard that refused every kill in the tree would still pass this case")
}

# run_guard — run the guard over the planted tree once, leaving what it said in `guard_out`
# and how it exited in `guard_code`. A step of its own rather than the first line of each
# probe, because this case runs it three times and every probe below asks about exactly one
# of those runs.
run_guard() {
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
}

# probe_guard_names_the_offender_with_its_line — the criterion, and it asks for both halves
# of what a guard is: a failure, and an address. Not "the output mentions the file" — a guard
# that listed every file it read would satisfy that — but `<file>:<line>`, which is the only
# thing that sends the next author to the site rather than to the file.
probe_guard_names_the_offender_with_its_line() {
  local named
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over a file under skills/ that kills a background process by a job spec; it exited 0 and said: $(flat "$guard_out")")
  named="$(grep -F "$OFFENDER_NAME" <<< "$guard_out")"
  [[ -n "$named" ]] || {
    problems+=("no line of the guard's output names $OFFENDER_REL, whose line $offender_line kills a background process by a job spec; it said: $(flat "$guard_out")")
    return
  }
  grep -qF -- "$OFFENDER_REL:$offender_line" <<< "$named" ||
    problems+=("the guard named $OFFENDER_NAME but not as $OFFENDER_REL:$offender_line, where the kill is; the lines naming it were: $(flat "$named")")
}

# probe_guard_leaves_the_innocent_alone — the other half of the condition the criterion
# states, and the half that keeps the guard from being a grep for `kill`. A file that kills
# the pid it recorded reaches its process from any shell, which is the repair this issue
# shipped, and the guard must have nothing to say about it — not a softer complaint, no
# complaint.
probe_guard_leaves_the_innocent_alone() {
  local named
  named="$(grep -F "$INNOCENT_NAME" <<< "$guard_out")"
  [[ -z "$named" ]] ||
    problems+=("the guard named $INNOCENT_REL, which kills the same process by the pid it recorded: $(flat "$named")")
}

# probe_entry_is_in_the_table <key> — the premise each run after an injection rests on: the
# entry `exempt` wrote is really in the guard's copy. Without it, a silent guard is a guard
# that read no table rather than one that honoured an entry.
probe_entry_is_in_the_table() {
  grep -qF -- "[$1]" "$guard_copy" || {
    problems+=("the entry [$1] is not in the guard copy's exemption table, so what the run below reports is not about an exemption at all")
    return 1
  }
}

# probe_guard_exempts_the_listed_site <key> — what the table buys: a site listed in it with a
# reason is not a failure. Both halves of that, because a guard that named the site in a
# softer voice and still exited non-zero would leave the run red and the author with nothing
# to do about it — the guard passes, and says nothing about the site.
probe_guard_exempts_the_listed_site() {
  local named
  [[ "$guard_code" == 0 ]] ||
    problems+=("want the guard to pass over a site listed in its exemption table as [$1] with a reason; it exited $guard_code and said: $(flat "$guard_out")")
  named="$(grep -F "$OFFENDER_REL:$offender_line" <<< "$guard_out")"
  [[ -z "$named" ]] ||
    problems+=("the guard still named $OFFENDER_REL:$offender_line, which its exemption table lists as [$1] with a reason: $(flat "$named")")
}

# probe_guard_refuses_a_reasonless_entry <key> — what the table costs to use: an entry with
# no reason is not an exemption. A table whose entries may be bare keys is a list of sites
# someone once wanted quiet, and the next reader has no way to tell a considered exemption
# from a silenced complaint — which is why the reason is what makes the entry, and its
# absence has to fail the run rather than exempt anything.
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
    problems+=("the guard named $key but never said its reason is what is missing, so the author is told a kill is there rather than that their exemption is not one: $(flat "$named")")
}

# 1. One criterion, one case: the guard fails over a file under skills/ that kills a
#    background process by a job spec, says where as `<file>:<line>`, says nothing about the
#    same process killed by its recorded pid, and honours an exemption entry only when it
#    carries a reason. All four over one plant, run three times — as it stands, with the site
#    exempted with a reason, and with the same entry's reason taken away — because that is
#    what the criterion states as one sentence: what the guard catches, what it must not
#    catch, and what the table buys and costs. Separate trees would ask the exemption halves
#    about a site the first run never named.
name="no-job-spec-kills.test.sh names a file under skills/ that kills a background process by a job spec as <file>:<line>, leaves a kill by recorded pid alone, and honours an exemption entry only when it carries a reason"
problems=()

if probe_guard_is_there && probe_guard_carries_an_exemption_table && plant; then
  if probe_plant_is_what_it_claims; then
    run_guard
    probe_guard_names_the_offender_with_its_line
    probe_guard_leaves_the_innocent_alone

    exempt_key="$OFFENDER_REL:$offender_line"

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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

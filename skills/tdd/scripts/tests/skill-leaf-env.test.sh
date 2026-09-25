#!/usr/bin/env bash
# Unit tests for the environment a leaf inherits from the launch lines skills/tdd/SKILL.md
# prescribes. Like skill-timeout.test.sh and skill-test-command.test.sh this suite has no
# script as its subject — it is the procedure document those scripts are called from. Unlike
# them it does not read that document as text: it RUNS the launch lines it finds in it,
# against a stub `claude`, and asks the leaf at the far end what it can see.
# Zero-dependency plain-shell asserts, same idiom as skill-test-command.test.sh.
#
# Why this exists (issue #143): the four documentation targets now refuse when VERI_TEST_CMD
# names a command that is not itself a documentation target (docs-targets-refuse.test.sh),
# and that guard is worth exactly as far as the variable reaches. A leaf that cannot see
# VERI_TEST_CMD is a leaf the guard never fires for — and a leaf is where `make docs` gets
# typed, since CLAUDE.md's "one trap" tells any agent that touched the page to run it. The
# ~5.5 min the #106 conductor spent on a page build inside a run whose test command was
# `make test` is what that costs.
#
# Every Bash call a conductor makes is a fresh shell, so a one-off `export` in preflight
# cannot carry the variable to a launch three steps later: only a prefix on the launch line
# itself can. Whether the prefix is there is not a question about the text, because a prefix
# can be spelled and still not arrive — it travels through `detach-leaf.sh` and the
# python3 `setsid` + `execvp` that detaches the leaf into a session of its own (#161),
# `supervise.sh`'s own process group and `run-leaf.sh` before anything reads it — so this
# suite runs the line rather than grepping it.
#
# The variable travels in the ENVIRONMENT and not in a prompt, which is what keeps the
# verifier blind: `build-verify-prompt.sh` takes no new argument, so there is still no
# parameter through which the developer's rationale could leak.
#
# The same argument reaches a second variable, and issue #163 measured what its absence costs:
# every `launch`, `exit` and `verdict` line a leaf leaves in the run's event log carried an
# empty `issue` and an empty `step`, because event.sh reads those from VERI_ISSUE and VERI_STEP
# and no launch line set them. That context cannot be derived downstream — `leaf-role.sh` reads
# the actor, phase and attempt out of the leaf's NAME, and no name says which issue or which
# step — so it travels the same way and for the same reason: on the launch, in the environment.
#
# Contract under test:
#   Every launch line in SKILL.md that sends a leaf through supervise.sh into run-leaf.sh,
#   run with the document's own variables supplied, gives the `claude` process at the far
#   end VERI_TEST_CMD carrying the run's test command — and leaves an event log whose every
#   line carries the run's issue and step.
#
# Run: skills/tdd/scripts/tests/skill-leaf-env.test.sh
#
# History: issue #333 made the ten launches below run concurrently instead of one after
# another, and added cases proving the overlap didn't blur which launch a failure belonged
# to — at the cost of doubling this suite's own time (9.9-11.3s serial -> 20.3-21.3s
# concurrent, interleaved on the same machine, 2026-09-19) and dropping wait-leaf.sh's
# ps-based fast-fail on a dead supervisor (issue #297) from the launches' own wait. Reverted
# here under a standing rule that this suite's cases assert BEHAVIOUR, not scheduling shape:
# launches are one round again, one after another, each waited on to completion before the
# next starts (#297's protection is back); "all ten start before any finishes" and "case 3 reads
# only after every launch has completed" were pure scheduling-shape assertions with nothing
# to prove once launches are serial, and are gone with the concurrency they were about. What
# #333 was actually protecting — a broken launch line named alone while its neighbours still
# pass, and the count-line/FAIL-line format holding still — stays, checked below against a
# small fixture fed straight into the same scan the document's own ten lines use, not by
# replaying all ten of them (or this whole suite) a second time.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root, and
# one up is the scripts directory the document calls `$S`.
ROOT="$(cd "$HERE/../../../.." && pwd)"
SCRIPTS="$(cd "$HERE/.." && pwd)"

# The document under test, twice: the path as every failure message quotes it, and the same
# path resolved for the probe to read. Both spellings come from one constant, so a message
# can never name a file the probe did not open.
skill_md="skills/tdd/SKILL.md"
md="$ROOT/$skill_md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which launch line is missing the variable rather than just that one is.
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

# problem <complaint> — record one launch line that failed the case. Every such message has
# the same three parts, and they are here rather than at each call site so the three cannot
# drift apart: where the line is, what is wrong with it, and the line itself **as the
# document spells it**, so a reader can find the text by searching for what the message
# quoted, and what they fix is the document rather than the probe's substituted copy.
# `lineno` and `line` belong to whichever function is working through the document's launch
# lines, the way `problems` is `run_case`'s: `scan_launches` reads them off a numbered grep,
# and `scan_launch_trees` reads the same pair back out of the tree a launch left behind.
problem() {
  problems+=("$skill_md:$lineno $1:$line")
}

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
stub="$WORK/stub"       # the fake `claude` every launch below ends in
run="$WORK/run"         # one tree per launch line, named for its leaf
mkdir -p "$stub" "$run"

# The test command this probe stands in for the conductor's. A command with a space in it,
# so a launch line that carries the value unquoted is caught here rather than in a real run,
# and one no recipe in this repository answers to, so nothing it reaches could act on it.
SENTINEL='make sentinel-test-cmd'

# The run context case 3 asks about, standing in for the conductor's own: the issue number the
# document spells `<n>` and the plan step it spells `<STEP>`. Both are values `runnable`
# substitutes into a launch line, so each is written once here and used both to run the line
# and to expect what came out of it — spelled a second time in the assertion, the expectation
# could drift off the launch and the case would go green against a value nothing supplied.
#
# The issue is the one this suite's own fixtures already name, so the spec file a verifier
# launch is handed and the `<n>` its line carries stay the same number. The step is a phrase
# with a space in it, for the reason SENTINEL is: `VERI_STEP` holds a ledger line, so a launch
# line that carries it unquoted has to be caught here rather than in a real run.
SENTINEL_ISSUE=143
SENTINEL_STEP='pin the sentinel step'

# How every launch below is run: `env` with the three run-context variables cleared, so the
# only way one of them can reach the far end is the launch line's own prefix. That clearing
# is the load-bearing part, and it is one array because every probe here owes it and a second
# spelling could quietly leave one variable inherited. Every `make test` of veri's own
# repository runs inside a development run and therefore already has all three in its
# environment — so a leaf inheriting them from this suite's own caller would answer for a
# launch line that carries no prefix at all. A suite's answer must be a fact about the thing
# under test, not about the shell that ran it (#87). Watched happen, not reasoned about: run
# from a #163 development leaf before the unsets were added, case 3 read back `issue='163'`
# and this run's own step text off launch lines that set neither.
cleared_run_context=(env -u VERI_TEST_CMD -u VERI_ISSUE -u VERI_STEP)

# The leaf, as far as run-leaf.sh can tell. Into the file its own launch names in `SEEN` it
# records the one thing this suite asks about — what VERI_TEST_CMD says in the leaf's own
# environment, or `<unset>` when it says nothing — and then emits the minimal stream-json for
# extract-result.sh to find a result in, the same shape run-leaf.test.sh's stub emits.
cat > "$stub/claude" <<'STUB'
#!/bin/sh
printf '%s\n' "${VERI_TEST_CMD-<unset>}" > "$SEEN"
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
STUB
chmod +x "$stub/claude"

# launched_test_cmd <leaf> <launch-line> <file>... — run one launch line to completion in a
# tree of its own and echo what VERI_TEST_CMD said inside the leaf, or `<no leaf ran>` when
# the line never reached one. Both cases below ask that one question, of the two launch
# shapes the document prescribes, so both come through here.
#
# The `<file>` arguments are what the tree must hold before the line can run, and they are
# the only thing the two shapes differ in: a developer launch names its own prompt file,
# while a verifier launch names the **spec** and the **test path** and lets verify.sh build
# the prompt from them. Each is created relative to the launch's tree; the stub reads none of
# them, so the content only says which fixture a reader is looking at.
#
# `$S` is supplied the way the document supplies it — as a variable in the launching shell
# (SKILL.md:61) — rather than substituted into the text, so the line is run as written.
# `CLAUDE_BIN` is how run-leaf.sh's own header says a test swaps the binary, and it has to
# come from here for the same reason the variable under test does: it can only reach the
# leaf by being inherited.
#
# The supervisor's windows are shrunk the way supervise.test.sh shrinks them, so nothing
# here waits on wall time; retries are pinned off because a stub leaf that failed to record
# anything should be reported, not run again.
# The runnable copy is bound as `launch`, the name `runnable` gives it, and not as `line`:
# `line` is `scan_launches`'s, holding the document's own spelling, and a local of that name
# here would shadow it — so the `origin` file below would record the substituted copy as
# though it were what the document says.

# launch_over <dir> — succeed once nothing in <dir> is supervising a leaf any more: every
# `.tdd/<name>.pid` the launch wrote names a process that is gone. This is what tells the
# wait below that no completion file is ever going to arrive, for the derived leaf name or
# for any other (#297): `wait-leaf.sh`'s own fast-fail reads the pid file of the ONE name it
# was given, and a derived name no launch writes has no pid file to read, so that fast-fail
# never fires and the wait runs to its whole fixed budget.
#
# A tree holding no pid file at all is NOT over. That is the moment between `detach-leaf.sh`
# returning and the supervisor recording itself, and it is every launch's first few
# milliseconds — read as "over", it would end every wait before the leaf had started.
#
# `kill -0` rather than `ps`-matching the supervisor's argv the way wait-leaf.sh does: a
# recycled pid here can only make this wait LONGER, never end it early, so the cheap test is
# the safe one. The tree is this launch's own, so every pid file in it belongs to this launch.
launch_over() {
  local pidfile pid found=0
  for pidfile in "$1"/.tdd/*.pid; do
    [[ -f "$pidfile" ]] || continue
    found=1
    pid="$(cat "$pidfile" 2>/dev/null)" || continue
    kill -0 "$pid" 2>/dev/null && return 1
  done
  (( found ))
}

# completion_landed <dir> — succeed once the launch in <dir> has written a completion file
# under ANY name. A pid being gone and its completion file existing are two events that
# nothing orders (#457): a detached launch's recorded pid can die before the supervisor
# behind it has written `.tdd/<name>.exit`, so `launch_over` alone ended the wait on a leaf
# that had answered and was still being recorded. Any name, not the derived one, so a launch
# that named its leaf wrongly still ends the wait as soon as its own file lands (#297).
completion_landed() {
  local exitfile
  for exitfile in "$1"/.tdd/*.exit; do
    [[ -f "$exitfile" ]] && return 0
  done
  return 1
}

# plant_ledger <tree> <step> — the committed ledger of the sentinel issue in <tree>'s `.tdd/`,
# <step> its one unchecked step: the title a launch reads with next-unchecked.sh (#437).
plant_ledger() {
  printf '# Plan for #%s\n\n- [ ] %s\n' "$SENTINEL_ISSUE" "$2" > "$1/.tdd/issue-$SENTINEL_ISSUE.md"
}

# plant_ticked_ledger <tree> <step> — the sentinel issue's committed ledger as it stands when
# develop-refactor launches: <step> ticked and awaiting its refactor, a later step unchecked.
plant_ticked_ledger() {
  printf '# Plan for #%s\n\n- [x] %s ⟂ refactor pending\n- [ ] a later step the run has not reached\n' \
    "$SENTINEL_ISSUE" "$2" > "$1/.tdd/issue-$SENTINEL_ISSUE.md"
}

launched_test_cmd() {
  local leaf="$1" launch="$2"
  shift 2
  # One tree per launch LINE, not per leaf: `$lineno` is `scan_launches`'s, read the way
  # `problem` reads it. Two of the document's lines launch the same leaf — the revise loop's
  # verifier says `verify.sh <phase>`, which is `verify red` once substituted, the same leaf
  # the red cycle's own line launches — so a tree named for the leaf alone would hold what the
  # SECOND of them did, and whatever the first one left there would be cleared or read as the
  # second's. Everything a launch leaves behind is evidence about the line that ran it, and
  # case 3 reads that evidence after both cases above are done, so each line keeps its own.
  local dir="$run/$lineno-$leaf"
  # What this launch's leaf saw, in the tree that launch ran in rather than in one file every
  # run rewrites — so each answer keeps the tree that produced it.
  local seen="$dir/seen"
  mkdir -p "$dir/.tdd"
  # Which line of the document ran here, and what it says, so a case reading these trees later
  # reports the launch a reader has to edit rather than the leaf it happened to name. The two
  # fields are `lineno` and `line` themselves — the pair `problem` quotes — so a case reading a
  # tree back restores that scope and complains through `problem` like any other, instead of
  # spelling the message's three parts a second time where the two spellings could drift. The
  # file name is not one of the fields: `problem` supplies `$skill_md` at the one place it
  # already does, so a tree can never claim to have come from another document.
  printf '%s\t%s\n' "$lineno" "$line" > "$dir/origin"
  # The committed ledger every launch of a real run has beside it, its first unchecked step the
  # one the run is on. A launch may read the step title out of it rather than off its own line
  # (#437), so a tree without one would be a run that never planned — and the step its events
  # carry, which case 3 asks about, would be the fixture's gap rather than the line's answer.
  # develop-refactor launches after the step's green commit has ticked it, so its tree holds
  # the ledger as it stands then: the step ticked with its `⟂ refactor pending` mark.
  if [[ "$leaf" == develop-refactor ]]; then
    plant_ticked_ledger "$dir" "$SENTINEL_STEP"
  else
    plant_ledger "$dir" "$SENTINEL_STEP"
  fi
  local file
  for file in "$@"; do
    printf 'the %s this launch names, which the stub never reads\n' "$file" > "$dir/$file"
  done
  # The line launches through `detach-leaf.sh`, which returns at once and leaves the leaf in
  # a session of its own — so a shell `wait` has nothing to wait on, and the tree would be
  # read while the leaf still ran. What makes this probe foreground is the completion file
  # the leaf's supervisor writes on every path, `.tdd/<leaf>.exit` — for a verifier too,
  # since verify.sh supervises its leaf under that same `verify-<phase>` name. The stub
  # writes `seen` before it exits, so the file landing means the answer is already there.
  #
  # Two things end the wait, and the second is why it is spelled here rather than left to
  # `wait-leaf.sh <leaf> 60`: the file landing, OR the launch being over without it. A
  # derived leaf name no launch writes gets no completion file AND no pid file, so the
  # fast-fail wait-leaf.sh has — a recorded pid that no longer supervises — has nothing to
  # read and never fires, and the wait ran out the full budget on an answer already
  # determined: six verifier lines × 60 s is the 5:05 issue #297 measured, with CI
  # cancelling `make test` at the `gates` job's cap. `launch_over` is that same fast-fail
  # asked of the launch instead of of one name.
  #
  # The budget stays as the last resort it was, for a launch that reached no supervisor at
  # all and so wrote no pid file to go looking at: that line still comes back as
  # `<no leaf ran>` rather than hanging the suite.
  ( cd "$dir" && "${cleared_run_context[@]}" \
      S="$SCRIPTS" CLAUDE_BIN="$stub/claude" SEEN="$seen" \
      VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.2 \
      bash -c "$launch" ) >/dev/null 2>&1
  local deadline=$(( SECONDS + 60 ))
  until [[ -f "$dir/.tdd/$leaf.exit" ]]; do
    launch_over "$dir" && completion_landed "$dir" && break
    (( SECONDS >= deadline )) && break
    sleep 0.2
  done
  # The answer, and then the one thing that ties it to the leaf name the CALLER derived.
  # The stub writes `seen` whatever the leaf is called, so a caller whose derived name no
  # launch writes would otherwise read the right answer back off a file its own name had
  # nothing to do with — passing, after waiting out the whole wait budget for a completion
  # file no supervisor will ever write (#297). `.tdd/<leaf>.exit` is written under that name
  # and no other, so its absence is exactly the fault: the name is wrong.
  #
  # Asked after `seen` rather than before it, so the two faults keep their own words: a line
  # that reached no supervisor at all writes neither file and still says `<no leaf ran>`,
  # rather than being reported for a naming fault it never got far enough to have.
  local answer
  answer="$(cat "$seen" 2>/dev/null)" || { echo '<no leaf ran>'; return; }
  [[ -f "$dir/.tdd/$leaf.exit" ]] || { echo "<no completion file under leaf $leaf>"; return; }
  printf '%s\n' "$answer"
}

# expect_sentinel <leaf> <launch-line> <file>... — run one launch line and record a problem
# unless the leaf at the far end saw the sentinel test command. The arguments are
# `launched_test_cmd`'s, passed straight through.
#
# This is the assertion both cases make, and it is written once because it is **one**
# criterion asked of two launch shapes: the shapes differ in how the line is spelled and what
# its tree must hold, not in what is wanted of it. Kept per-case, the two copies could drift
# into describing the same failure two ways — and the value they quote is the whole evidence a
# reader gets, since `<unset>` (the prefix is missing) and `<no leaf ran>` (the line never
# reached one) are different faults with the same verdict.
expect_sentinel() {
  local leaf="$1" got
  got="$(launched_test_cmd "$@")"
  [[ "$got" == "$SENTINEL" ]] ||
    problem "launches $leaf, whose leaf saw VERI_TEST_CMD=$got, want $SENTINEL"
}

# runnable <line> [step] — echo one launch line as a conductor types it, with the document's
# placeholders supplied; or echo nothing and return 1 when the line names one this probe
# cannot supply. <step> is what `<STEP>` becomes, defaulting to the sentinel the first cases
# use: it is a parameter because case 8 asks the same lines about a DIFFERENT title — one
# carrying an apostrophe — and a second copy of this table would be a second chance to get
# the substitutions wrong.
#
# Two spellings of the same launch are kept apart on purpose, and this is where the second
# one is made: the caller's `line` is what the document says, and is what every message
# quotes, while what comes back from here is the runnable copy. The substitutions are one
# table rather than one per case because a conductor supplies all of them from one place —
# the run's test command, the phase and revise attempt that name one revise leaf, the issue
# number and the plan step it is on, and the test under review with its target test id — and
# either launch shape is free to name any of them.
#
# The refusal is the load-bearing half. An unsubstituted `<…>` would be read by the shell as
# a redirection, so a case that ran it would go green while answering about nothing; the
# caller reports the line instead. `[target]` is the revise loop's spelling of an argument
# that is optional there, and is supplied the same way. The target test id is one word
# because the document leaves it unquoted, so a value with a space in it would arrive as two
# arguments and the probe would be testing its own fixture.
runnable() {
  local launch="$1" step="${2:-$SENTINEL_STEP}"
  launch="${launch//<test-cmd>/$SENTINEL}"
  launch="${launch//<phase>/red}"
  launch="${launch//<k>/1}"
  launch="${launch//<n>/$SENTINEL_ISSUE}"
  launch="${launch//<STEP>/$step}"
  launch="${launch//<test-path>/probe.test.sh}"
  launch="${launch//<target-test-id>/probe-target}"
  launch="${launch//<green-sha>/0123abc}"  # refactor's 4th slot must be a sha (#151)
  launch="${launch//<fast-cmd>/make probe-fast}"  # green's --fast-cmd (#341)
  launch="${launch//\[target\]/probe-target}"
  [[ "$launch" != *'<'*'>'* ]] || return 1
  printf '%s\n' "$launch"
}

# no_launch <shape> — record the one fault a case has when the document holds no line of
# the shape it is about: it examined nothing, and would otherwise pass while asserting about
# no launch at all. Not routed through `problem`, which quotes a line and a number this case
# never found; written once because every case that scans for a shape reports this same fault
# and only the shape differs, so kept per case the spellings could drift apart.
no_launch() {
  problems+=("$skill_md has no line launching $1 — the launch this case is about could not be found")
}

# take_line <numbered-grep-hit> [step] — open one line of the document for a case to work
# on: split the hit into the `lineno` and `line` every failure message quotes, and put its
# runnable copy in `launch`. Returns 1, having complained, when `runnable` refuses the line.
#
# It assigns rather than echoes because the three results have to reach the caller together
# and a command substitution would put the two the caller's `problem` reads in a subshell of
# its own. The assignments land on the caller's own locals, bash resolving a name through the
# functions that called this one — the same scoping `problem` and `report` already use.
#
# One copy because both halves are quiet when a copy loses them: a split spelled differently
# names the wrong line, and a dropped refusal lets an unsubstituted `<…>` reach the shell as
# a redirection, so the case goes green having run nothing. The refusal's wording is a third:
# kept per caller, the two spellings of one complaint could drift apart.
take_line() {
  lineno="${1%%:*}"
  line="${1#*:}"
  launch="$(runnable "$line" "${2-}")" || {
    problem "names a placeholder this probe cannot supply, so its launch could not be run"
    return 1
  }
}

# scan_launches <pattern> <shape> <check> — find every launch line in the document matching
# <pattern> and hand each runnable one, substituted, to the shell function named <check>,
# which asks of it whatever its case is about. <shape> names the launch the pattern is looking
# for, and is used only for `no_launch`'s complaint when the document holds no matching line
# at all.
#
# Both cases scan the same way and differ only in what they then ask, so the scan is written
# once. Each line it finds is opened by `take_line`, which carries the split and the refusal
# that go with it. `lineno`, `line` and `launch` are declared here, assigned there and read by
# `problem` from the check, which bash allows — a function sees the locals of the functions
# that called it — so they stay out of the global scope the two cases share.
scan_launches() {
  local pattern="$1" shape="$2" check="$3"
  local lines numbered lineno line launch
  lines="$(grep -nE "$pattern" "$md")"
  if [[ -z "$lines" ]]; then
    no_launch "$shape"
    return
  fi
  while IFS= read -r numbered; do
    [[ -n "$numbered" ]] || continue
    take_line "$numbered" || continue
    "$check" "$launch"
  done <<< "$lines"
}

# run_case <name> <body> [args...] — one whole case: run <body>, which collects what it found
# wrong into `problems`, then close the case under <name>.
#
# Every case is this shape, and the shared `problems` array is the part of it a copy could
# get wrong silently: a case that forgot to empty the array before scanning would report its
# predecessor's failures under its own name, and one that forgot `report` would assert
# nothing while still printing a count. Here the array is this function's own local, so
# emptying it is not a step anyone can omit — `problem` and `report` reach it the way a
# check reaches `lineno` and `line`, a bash function seeing the locals of the functions that
# called it. `local problems=()` and not a bare `local`, because under `set -u` bash 3.2 reads
# `${#problems[@]}` on a declared-but-unassigned array as an unbound variable and dies.
#
# The body is a command this is handed rather than one fixed call, because that is the only
# thing the cases differ in: two scan the launch lines the document prescribes, the third the
# trees those launches left behind. Written out per case, the scaffolding above would be
# copied once per case and the reason for it with them.
run_case() {
  local name="$1"
  shift
  local problems=()
  "$@"
  report "$name"
}

# only_complaint_about <needle> <what-was-asked> — fold the fixture launches a case just ran
# into that case's own verdict: exactly one complaint, and it names <needle>. A fixture case
# runs real launch lines of its own, and each of those reports through `problem` into
# `run_case`'s `problems` the way a document line does — so what the array holds when the
# launches are done is the launches' evidence, not the case's answer. This empties it and
# puts back the one complaint the case is actually making, `<what-was-asked> reported: …`,
# quoting whatever the launches said.
#
# Written once because two cases ask that same question of their fixtures and differ only in
# the needle and the phrase: kept per-case, the emptying and the `-ne 1` could drift, and a
# copy that forgot to empty `problems` would report its fixture's deliberate fault as the
# case's own failure while still looking like it had asserted something.
only_complaint_about() {
  local needle="$1" asked="$2"
  local got=( "${problems[@]}" )
  problems=()
  if [[ "${#got[@]}" -ne 1 || "${got[0]}" != *"$needle"* ]]; then
    problems+=("$asked reported: ${got[*]:-<nothing>}")
  fi
}

# arg_after <script> <launch> — echo the word <launch> passes <script> as its first argument:
# the leaf's name for supervise.sh, the phase for verify.sh. Both checks below read one, and
# they differ only in which script they read it after — so the `sed` is here rather than once
# per check, where the two copies would have to get the same two details right independently:
# the escaping of the script name, and the `[^ ]+` that stops at the first word instead of
# swallowing the rest of the line. The script arrives as the literal text a launch spells and
# its dots are escaped here, so a caller hands this a name and not a regex.
arg_after() {
  local script="${1//./\\.}"
  sed -E "s/.*$script +([^ ]+).*/\1/" <<< "$2"
}

# 1. The criterion, asked of every launch line the document actually prescribes. One case,
#    because it is one wiring: the same prefix on each line, and a line that lost it is a
#    phase of the run whose leaf can type `make docs` unrefused.
#
#    The lines are found by what they do rather than by which section they sit in — a line
#    running supervise.sh over run-leaf.sh is a line a conductor copies as it stands. The
#    generic shape at the head of the document (`supervise.sh <name> <cmd> [args...]`,
#    SKILL.md:216) is deliberately not among them: it names no command to launch, so there
#    is nothing to run and nothing a leaf could see.
# The two fields the probe reads out of a developer launch: the leaf's name, which is also the
# tree the launch runs in and how a failure names itself, and the prompt file the leaf is
# pointed at. Both are read from the substituted copy, since a leaf named `revise-<phase>-<k>`
# in the document is `revise-red-1` when it runs.
check_developer_launch() {
  local launch="$1" leaf prompt
  leaf="$(arg_after supervise.sh "$launch")"
  prompt="$(head -1 < <(grep -oE '\.tdd/[A-Za-z0-9_.-]+\.prompt' <<< "$launch"))"
  if [[ -z "$prompt" ]]; then
    problem "launches $leaf with no .tdd/<name>.prompt file to run, so its leaf could not be started"
    return
  fi
  expect_sentinel "$leaf" "$launch" "$prompt"
}

run_case "every leaf $skill_md launches through supervise.sh sees the run's test command as VERI_TEST_CMD" \
  scan_launches \
  '\$S/supervise\.sh .*run-leaf\.sh' \
  "a leaf through supervise.sh into run-leaf.sh" \
  check_developer_launch

# 2. The same criterion, asked of the verifier launches. A verifier is a leaf too — `claude
#    -p` in a tree, denied Write and Edit but free to run commands — so `make docs` is as
#    typeable there as in a developer leaf, and a guard the documentation targets carry is
#    worth nothing in a process that cannot see the variable it reads. It is a second case
#    rather than more lines in the first because it is a second wiring: the prefix goes on a
#    `detach-leaf.sh supervise.sh verdict-<phase> run-verdict.sh …`, the verdict launcher that
#    execs verify.sh (#426, where the `bash -c "…"` command string it replaced was found to
#    break on a step title carrying an apostrophe), and the variable then has one more process
#    to cross — verify.sh itself — before supervise.sh and run-leaf.sh carry it the rest of the
#    way. What supervises the launcher is matched as `.*` between the detacher and it, so the
#    case reads a verifier launch whatever is named there rather than only the unsupervised
#    shape #415 replaced.
#
#    The variable still travels in the ENVIRONMENT, so `build-verify-prompt.sh` keeps the
#    four parameters it has and the verifier stays blind: there is still no argument through
#    which the developer's rationale could reach it.
#
#    The lines are found by what they do, the way case 1 finds its own: a detached launch of
#    the verdict launcher naming the spec file it judges against is a line a conductor copies
#    as it stands. The shape at the head of the document (SKILL.md:247) spells its arguments as an
#    ellipsis rather than naming a spec, so — like the generic `supervise.sh` shape above —
#    there is nothing there to run and no leaf that could see anything.
# The phase is the launcher's first positional argument — verify.sh's own, passed through
# untouched — and `verify-<phase>` is both the leaf's
# name and the tree this launch runs in — read from the substituted copy, since the revise
# loop's line says `<phase>` where a run says `red`. The two files named are spelled as
# `runnable`'s table spells them, so the tree holds the spec and the test the line is about to
# hand verify.sh.
#
# The option pair `--step "<STEP>"` (#223) comes before that positional, so it is dropped here
# rather than read past: the read below takes the first word after the launcher, which would
# be the flag itself, and the leaf would be named `verify---step`. The tree that name points at is one no launch writes, so
# `wait-leaf.sh` would wait out its whole timeout on every verifier line and the case would
# still pass — six lines × 60 s, which is how this suite went from 9 s to 5 min and had CI
# cancel `make test` at its cap. The step's own text is quoted and holds spaces, so the pair is
# matched as `--step <up to the closing quote>` — in either quote, since the title moved to
# double quotes (#431) and `--fast-cmd` beside it did not.
#
# The two files the tree must hold are read off the launch rather than spelled here, because
# the phase decides the second one: a cycle phase judges a test path, and `plan` judges the
# proposed ledger (#439). `build-verify-prompt.sh` refuses a file it cannot read before any
# leaf starts, so a tree missing either would answer `<no leaf ran>` for a launch that is
# correctly wired — the probe reporting its own fixture.
check_verifier_launch() {
  local launch="$1" clean phase spec subject
  clean="$(sed -E "s/ --(step|fast-cmd) ('[^']*'|\"[^\"]*\")//g" <<< "$launch")"
  # The launcher's three positionals in one read of the words that follow it: the phase, the
  # spec file, and the file under judgement. Split by the shell rather than by a second
  # pattern naming `run-verdict.sh` again — two spellings of the launcher's name are two
  # chances for a renamed launcher to leave one of them reading a line it no longer matches.
  read -r phase spec subject _ <<< "${clean#*run-verdict.sh }"
  expect_sentinel "verify-$phase" "$launch" "$spec" "$subject"
}

run_case "every verifier $skill_md launches through verify.sh sees the run's test command as VERI_TEST_CMD" \
  scan_launches \
  '\$S/detach-leaf\.sh .*\$S/run-verdict\.sh .*\.tdd/issue-<n>-spec\.md' \
  "a verifier through run-verdict.sh against a spec file" \
  check_verifier_launch

# 3. The second thing a leaf launch has to carry, and the one #163 measured missing: the run
#    context the event log's `issue` and `step` keys are written from. `event.sh` reads them
#    out of VERI_ISSUE and VERI_STEP (event.sh:47-50) and writes an unset one as `""`, so in
#    #157's own run log every one of the 26 `launch`, 26 `exit` and 9 `verdict` lines carried
#    an empty issue and an empty step, and a leaf could be attributed to a step only by
#    interleaving its timestamp with the conductor's `step-start` marks.
#
#    Neither supervise.sh nor verify.sh can supply it: `leaf-role.sh` derives the actor, the
#    phase and the attempt from the leaf's NAME, and nothing in a name says which issue is
#    being solved or which step of its plan the leaf is on. Both already pass through whatever
#    their environment holds (supervise.test.sh case 15, verify.test.sh case 11), so what is
#    left is the launch putting it there — the same place, and the same two variables, the
#    conductor's own mark lines already spell (SKILL.md:440, 622, 693, 722, 796, 844).
#
#    Asked of the events the launches LEFT, rather than of what the leaf saw. The leaf never
#    reads VERI_ISSUE; event.sh does, from inside the supervisor, so the log is where the
#    variable arriving is observable at all — and every line of it is asked, because a context
#    that reached the `launch` mark is no evidence the `exit` or the `verdict` written after
#    the leaf ran has it too.
#
#    These are the trees cases 1 and 2 already ran the document's lines in, read now that both
#    are done rather than launched again: a launch here is a real supervisor over a real
#    detached leaf, ~0.6 s of the ~6 s this suite costs `make test` three times per step, and
#    asking a second question of a run that already happened is free. Each tree carries the
#    document line that made it, so a failure names the launch to edit.
#
# bad_context <events-log> — one `;`-joined complaint naming every event line in <log> whose
# issue and step are not the sentinels the launch was given, or nothing at all when they all
# carry them. python3 rather than jq, the dependency event.sh itself already execs.
#
# An empty or absent log is a complaint too, and a loud one: a launch that wrote no events is
# a leaf nothing recorded, and a case that read past it would pass for having found no line to
# contradict it.
# <step> is a parameter rather than the sentinel read from here, because one launch of the
# document carries no step at all: the `plan` verifier runs before the first step and belongs
# to no ledger line (#439). event.sh writes an unset VERI_STEP as `""`, and that empty value
# is the truthful one — a title invented for it would attribute the leaf to a step the run has
# not begun. The issue is asked of every launch either way.
bad_context() {
  python3 -c '
import sys, json
log, issue, step = sys.argv[1], sys.argv[2], sys.argv[3]
bad = []
lines = [l for l in open(log).read().splitlines() if l.strip()]
for line in lines:
    try:
        obj = json.loads(line)
    except Exception:
        bad.append("unparseable event line")
        continue
    if obj.get("issue") != issue or obj.get("step") != step:
        bad.append("%s issue=%r step=%r" % (obj.get("event"), obj.get("issue"), obj.get("step")))
if not lines:
    print("<<no event line written>>")
elif bad:
    print("; ".join(bad))
' "$1" "$SENTINEL_ISSUE" "$2" 2>/dev/null || echo '<<no event log>>'
}

# scan_launch_trees — the case's body, in `scan_launches`'s shape: it records what it finds
# into `run_case`'s `problems` and leaves the counting to `run_case`, reaching that array the
# way the checks above do, a bash function seeing the locals of the functions that called it.
# The tree walk's working names stay local with it rather than joining the globals the other
# two cases already share — and two of them are `lineno` and `line`, restored from the tree's
# `origin` file so `problem` builds this case's messages the way it builds the other two cases'.
scan_launch_trees() {
  local trees tree lineno line complaint want_step
  # `$run/*` unquoted is the glob; with no match bash leaves the pattern itself, which is not
  # a directory — so the guard below reports that no launch ran at all rather than iterating
  # over a literal `*` or, worse, passing the case having examined nothing.
  trees=( "$run"/* )
  if [[ ! -d "${trees[0]}" ]]; then
    problems+=("no launch line was run, so no leaf's events could be read")
  else
    for tree in "${trees[@]}"; do
      # Fail closed on a tree with no `origin`, rather than reading `$lineno` unset: under
      # `set -u` bash 3.2 kills the script there and exits with the status of the command
      # BEFORE it — routinely 0 — so the suite would stop mid-case and still look green to
      # anything reading only its exit code (#157). The complaint is spelled out here rather
      # than handed to `problem`, since there is no document line to quote: that is the fault.
      if [[ ! -f "$tree/origin" ]]; then
        problems+=("${tree#$run/} was launched with no record of which line of $skill_md ran it")
        continue
      fi
      IFS=$'\t' read -r lineno line < "$tree/origin"
      # What the line itself passes decides which step its events must carry: a launch naming
      # VERI_STEP is asked for the sentinel, and one naming none — the plan verifier — for the
      # empty step event.sh writes when the variable is unset.
      want_step=""
      [[ "$line" != *VERI_STEP* ]] || want_step="$SENTINEL_STEP"
      complaint="$(bad_context "$tree/.tdd/events.jsonl" "$want_step")"
      [[ -z "$complaint" ]] ||
        problem "leaves events that do not carry issue=$SENTINEL_ISSUE step='$want_step' ($complaint)"
    done
  fi
}

run_case "every leaf $skill_md launches leaves events carrying the run's issue and step" \
  scan_launch_trees

# 4. What issue #333 was actually protecting, kept now that the launches it made concurrent
#    are serial again: a single broken launch line is reported by name — the document's own
#    line number and text — while unrelated lines report nothing. Concurrency was never what
#    could blur that here (scan_launches runs one line fully, through `problem`, before the
#    next starts either way, serial or not); a scoping slip between `lineno`/`line` and the
#    complaint a later iteration builds could, which this fixture would catch regardless of
#    whether launches overlap.
#
#    Checked against three small developer-shaped lines of this probe's own, not the
#    document's ten and not a second run of this whole suite: the fixture costs three cheap
#    launches instead of replaying ten real ones (or all eight of this suite's cases) again.
#
# scan_fixture_naming — the case's body, in the other cases' shape. The middle line's
# VERI_TEST_CMD prefix is missing on purpose; the other two are correct, so a run that
# reports either of them, or reports nothing, or reports more than the one complaint, has
# found a real scoping bug rather than the fixture's own deliberate fault.
scan_fixture_naming() {
  local fixture i=0 lineno line launch
  read -r -d '' fixture <<'FIXTURE' || true
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP='<STEP>' $S/detach-leaf.sh $S/supervise.sh fixture-good-1 $S/run-leaf.sh .tdd/fixture-good-1.prompt
VERI_ISSUE=<n> VERI_STEP='<STEP>' $S/detach-leaf.sh $S/supervise.sh fixture-bad $S/run-leaf.sh .tdd/fixture-bad.prompt
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP='<STEP>' $S/detach-leaf.sh $S/supervise.sh fixture-good-2 $S/run-leaf.sh .tdd/fixture-good-2.prompt
FIXTURE
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    i=$((i + 1))
    lineno="fixture-naming-$i"
    launch="$(runnable "$line")" || {
      problem "fixture-naming line $i names a placeholder this probe cannot supply"
      continue
    }
    check_developer_launch "$launch"
  done <<< "$fixture"
  # The loop above leaves this case's real verdict in `problems` — the three fixture
  # launches' own complaints, not this case's question. Fold them into the one thing
  # actually being asked: exactly one complaint, naming the line that was actually broken.
  only_complaint_about "fixture-bad" "the fixture's three launches (only the middle one broken)"
}

run_case "a single broken launch line is reported by name, alone, while unrelated lines report nothing" \
  scan_fixture_naming

# 5. The other half of what issue #333 was protecting: report()'s and problem()'s own output
#    shape — the `FAIL - <name>` line, the indented `<file>:<line> <complaint>:<text>` line,
#    and a case with nothing wrong printing neither — hasn't drifted. Anything grepping a
#    run's log for them, the `test` recipe's own count-line check first of all, would stop
#    matching the day one of them moved.
#
#    Checked directly against report() and problem() with a synthetic complaint, in a
#    subshell so the synthetic pass/fail/problems this manufactures never reach this run's
#    own count — not by breaking a real launch line and re-running this whole suite a second
#    time to look for the shape in its own output.
#
# _fixture_report_case — calls problem() and report() exactly the way a real case does, with
# a synthetic `lineno`/`line` in place of ones a scan read off the document.
_fixture_report_case() {
  local lineno="999" line="sample line text"
  local problems=()
  problem "sample problem"
  report "sample case"
}

# scan_message_format — the case's body, in the other cases' shape.
scan_message_format() {
  local out want
  out="$(
    pass=0 fail=0
    _fixture_report_case
    echo "----"
    echo "$pass passed, $fail failed"
  )"
  want=$'FAIL - sample case\n    skills/tdd/SKILL.md:999 sample problem:sample line text\n----\n0 passed, 1 failed'
  [[ "$out" == "$want" ]] ||
    problems+=("report()'s and problem()'s output shape has drifted: got $(tr '\n' '|' <<< "$out")")
}

run_case "report()'s FAIL line, its indented problem line, and the count line keep their shape" \
  scan_message_format

# developer_launch_fixture <tag> — set this case's `lineno`, `line`, `launch`, `leaf` and
# `prompt` to ONE correct developer-shaped launch line of this probe's own, supervising
# `fixture-<tag>`; return 1, having recorded the problem, when the document's placeholders
# cannot be supplied. The names are assigned rather than returned because `lineno` and `line`
# are the pair `problem` and `launched_test_cmd` read out of the calling case's scope.
#
# Written once because three cases below launch the same line and differ only in what they
# ask of the answer — case 6 that a leaf name no launch writes is reported, case 7 that the
# report arrives before the wait budget, case 9 that a completion file landing late under the
# right name is still waited for. Copies of the line, its substitution and its refusal could
# drift into testing different fixtures while still claiming to be halves of one probe.
developer_launch_fixture() {
  local tag="$1"
  lineno="$tag-1"
  leaf="fixture-$tag"
  prompt=".tdd/$leaf.prompt"
  read -r line <<FIXTURE
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP='<STEP>' \$S/detach-leaf.sh \$S/supervise.sh $leaf \$S/run-leaf.sh $prompt
FIXTURE
  launch="$(runnable "$line")" || {
    problems+=("the $tag fixture names a placeholder this probe cannot supply")
    return 1
  }
}

# 6. The fault issue #297 names, which none of the cases above can answer: the leaf name a
#    launch line is expected to produce is used only to tell `wait-leaf.sh` which completion
#    file to wait for, and nothing asserts on it. The stub writes its `seen` file whatever the
#    leaf is called, so a launch whose leaf name the probe derived WRONG still reads the right
#    answer back and passes — after waiting out the whole wait budget for a completion file no
#    supervisor will ever write. Watched on purpose while fixing #223 (commit be98562):
#    renaming the derived leaf `verify-` to `verifyX-` left this suite at 3 passed, 0 failed
#    and took 5:05 instead of 10 s. That is how #223's `--step` regression stayed invisible —
#    a test that answers "slower" where it should answer "red" cannot fail for that fault.
#
#    Asked of one correct developer-shaped fixture launch of this probe's own, run under a
#    leaf name no launch writes — the injected fault, made on purpose — rather than by
#    breaking one of the document's own ten lines: the line itself is right, so the only thing
#    left to report is the completion file that never landed under the derived name.
#
# scan_wrong_leaf_name — the case's body, in the other cases' shape: it collects into
# `run_case`'s `problems` the way the scans above do, and `lineno`/`line` are its own, so
# `expect_sentinel`'s complaint quotes this fixture's line rather than one of the document's.
scan_wrong_leaf_name() {
  local lineno line launch leaf prompt
  developer_launch_fixture wrong-leaf-name || return
  # The name asked for is not the one the line supervises, and no launch anywhere writes it.
  expect_sentinel "$leaf-no-such-leaf" "$launch" "$prompt"
  # As in the fixture-naming case above, the launch's own complaint is the evidence, not this
  # case's verdict: fold it into the one thing actually being asked — exactly one complaint,
  # naming the launch line whose completion file never landed.
  only_complaint_about "$line" "a launch whose leaf name no completion file is written under"
}

run_case "a launch writing no completion file under the derived leaf name is reported, naming that line" \
  scan_wrong_leaf_name

# 7. The other half of the fault issue #297 names, and the half case 6 cannot answer: how
#    LONG the wrong answer takes to arrive. `wait-leaf.sh` ends a wait early when the leaf's
#    own `.tdd/<name>.pid` names a process that is no longer supervising it — but a derived
#    name no launch writes has no pid file either, so that fast-fail never fires and the wait
#    runs to its whole fixed budget. That is the 5:05 the issue measured: six verifier lines
#    times 60 s, with CI cancelling `make test` at the `gates` job's cap. A probe that
#    answers "slower" where it should answer "red" is the fault; answering red 60 s late is
#    still that fault, because what a reader sees is a suite that hangs.
#
#    Asked of one correct developer-shaped fixture launch of this probe's own, run under a
#    leaf name no launch writes — case 6's injected fault, timed. The launch itself is over
#    in well under a second: its supervisor writes its own completion file and exits, so from
#    that moment on there is nothing left that could ever write the derived name's, and every
#    further second of waiting is spent on an answer already determined.
#
#    The assertion is on elapsed seconds because the criterion IS elapsed seconds — this is
#    the one call's own latency, not a timing taken across a suite run, and there is no other
#    observable difference between waiting out the budget and not. The ceiling is far below
#    the budget and far above a real launch, so it can only be crossed by a wait that ran on
#    after its supervisor was gone.
#
# The wait budget `launched_test_cmd`'s own wait runs to, and the ceiling this case holds
# the answer to. Spelled apart from each other on purpose: the case is not asserting that the
# budget is any particular number, only that an answer arrives long before it.
ANSWER_CEILING=15

# scan_answer_latency — the case's body, in the other cases' shape: it collects into
# `run_case`'s `problems`, and `lineno`/`line` are its own so the tree `launched_test_cmd`
# makes records this fixture's line rather than one of the document's.
scan_answer_latency() {
  local lineno line launch leaf prompt started elapsed
  developer_launch_fixture answer-latency || return
  # Called through `launched_test_cmd` rather than `expect_sentinel`: what it answers is case
  # 6's question and is discarded here, so this case's `problems` holds its own verdict alone
  # and needs no folding.
  started=$SECONDS
  launched_test_cmd "$leaf-no-such-leaf" "$launch" "$prompt" >/dev/null
  elapsed=$(( SECONDS - started ))
  (( elapsed < ANSWER_CEILING )) ||
    problems+=("a launch whose derived leaf name no completion file is written under was answered after ${elapsed}s, want under ${ANSWER_CEILING}s: the wait ran on past the supervisor that had already exited")
}

run_case "a derived leaf name no launch writes is answered once its supervisor is gone, not at the end of the wait budget" \
  scan_answer_latency

# 8. The step's TITLE, and the one character every launch line in this document still
#    breaks on (issue #431). #426 took the verify call out of a nested `bash -c "…"` so that
#    no SECOND shell parses the title — that was the inner half. The outer half is still
#    here: every launch spells `VERI_STEP='<STEP>'`, a single-quoted literal in the shell the
#    conductor itself types the line into, so a title carrying an apostrophe — and the
#    planning leaf is what writes the titles — closes that quote early and the line dies
#    before anything is launched:
#
#        bash: -c: line 1: unexpected EOF while looking for matching `''
#
#    Two runs have already paid for it by hand: #424 crashed on it, and #297 and #426 routed
#    around it with a git-ignored `.tdd/vwrap.sh` argv wrapper or by choosing titles with no
#    apostrophe. Neither is a fix — a wrapper nobody commits is one the next run does not
#    have, and choosing the titles is not the conductor's to choose.
#
#    Asked the way cases 1 and 2 ask their own question — by RUNNING a line of the document,
#    not by grepping it — but of one launch and not of all ten, because the hazard is the
#    mechanism rather than the line: every launch carries the title the same way, and what a
#    document-wide sweep is for is the guard over the lines, not this case.
#
#    The run is shallow on purpose. `$S` here is a copy of the scripts directory whose
#    `detach-leaf.sh` records the VERI_STEP it was launched with and returns, so nothing
#    starts a supervisor, a detached session, a `claude` or a leaf, and nothing waits: the
#    quoting hazard is entirely in the ONE shell that types the line, which is the shell this
#    case runs. That the environment then crosses the supervisor and reaches the leaf is case
#    3 above, already asked — of a title with no apostrophe in it.
#
#    What the copy holds is the whole scripts directory, and the tree the line runs in holds
#    the run's committed ledger, because the criterion is that the title ARRIVES and not which
#    route the document picks for it: a launch that stops inlining the title and reaches it
#    through a shipped script, or through the ledger the title is written in, is run with both
#    present and answers this case on its own terms.
#
# stage_recorder <tag> — the scripts directory and the tree a step-title case runs its line
# against: every script the skill ships, with the detacher — the first process a launch
# starts, and so the first place the title is observable at all — replaced by a recorder.
# It writes the VERI_STEP it was launched with to `$SEEN`, and whatever follows `--step` in
# the argv it was handed — the argv a verifier's `run-verdict.sh` would have received — to
# `$SEEN.argv`; a developer launch carries no `--step`, and its case never reads that file.
# `#!/bin/sh` like every other stub here (#322): Homebrew's bash costs ~12 ms to start and a
# recorder buys nothing for it. The suites are not copied; the line names none of them, and
# copying them would be ~100 files for nothing.
#
# It assigns the caller's `stage`, `seen` and `tree` rather than echoing them, the way
# `take_line` assigns its three: all three have to reach the caller together. Written once
# because cases 8 to 8d stage the same copy, and a recorder spelled twice records two ways.
stage_recorder() {
  stage="$WORK/$1-scripts"
  seen="$WORK/$1-seen"
  tree="$WORK/$1-tree"
  mkdir -p "$stage" "$tree/.tdd"
  cp "$SCRIPTS"/*.sh "$stage/"
  cp -R "$SCRIPTS/lib" "$SCRIPTS/prompts" "$stage/"
  cat > "$stage/detach-leaf.sh" <<'STUB'
#!/bin/sh
printf '%s\n' "${VERI_STEP-<unset>}" > "$SEEN"
step='<no --step argument>'
while [ "$#" -gt 0 ]; do
  if [ "$1" = --step ]; then step="${2-<--step with no value>}"; break; fi
  shift
done
printf '%s\n' "$step" > "$SEEN.argv"
STUB
  chmod +x "$stage/detach-leaf.sh"
}

# The title under test, and the expected value at once: what the conductor is given is what
# the leaf must receive. A real ledger line from this repository's own history, in its own
# voice, carrying the one character the launch breaks on.
APOSTROPHE_STEP="A background process is killed by the pid recorded when it started, never by that shell's own job spec"

# scan_step_title [title] [tag] — the case's body, in the other cases' shape: it records what
# it finds into `run_case`'s `problems`, and `lineno`/`line` are its own locals so `problem`
# builds this case's messages out of the document line it actually ran. <title> is the step
# title the line is run with and the value the leaf must see, defaulting to the apostrophe
# this case is about; <tag> names the scratch paths, so a second title asked of the same line
# (case 8b below) reads its own recorder and never the one this case left behind. <leaf> is
# the developer leaf whose launch line is run, defaulting to develop-red, and <planter> the
# helper that writes the committed ledger the line runs beside, defaulting to `plant_ledger`
# (case 8c asks develop-refactor, whose step is already ticked when it launches).
scan_step_title() {
  local title="${1:-$APOSTROPHE_STEP}" tag="${2:-step-title}"
  local leaf="${3:-develop-red}" planter="${4:-plant_ledger}"
  local lineno line numbered launch stage seen tree err got
  numbered="$(head -1 < <(grep -nE "\\\$S/detach-leaf\\.sh .*\\\$S/supervise\\.sh $leaf \\\$S/run-leaf\\.sh" "$md"))"
  if [[ -z "$numbered" ]]; then
    no_launch "$leaf through supervise.sh into run-leaf.sh"
    return
  fi
  take_line "$numbered" "$title" || return
  stage_recorder "$tag"
  printf 'the prompt this launch names, which the recorder never reads\n' \
    > "$tree/.tdd/$leaf.prompt"
  "$planter" "$tree" "$title"
  # Run with the run context cleared, like every other probe here. The launching shell's
  # stderr is kept, because the two failures read differently and a reader has to tell them
  # apart: a line the shell refused outright launched nothing, while a title that arrived
  # truncated at the apostrophe, or wearing quotes a second parse left on it, says the launch
  # ran and mangled it.
  err="$( cd "$tree" && "${cleared_run_context[@]}" \
            S="$stage" SEEN="$seen" bash -c "$launch" 2>&1 >/dev/null )"
  got="$(cat "$seen" 2>/dev/null)" || got='<no leaf was launched>'
  [[ "$got" == "$title" ]] ||
    problem "launched with the step title <$title>, whose leaf saw VERI_STEP=<$got> (the launching shell said: ${err//$'\n'//})"
}

run_case "a step title carrying an apostrophe reaches the leaf $skill_md launches with it intact" \
  scan_step_title

# 8b. The same line, the same shallow run, and the three characters #431's double quotes do
#    NOT protect (issue #437). Inside `"…"` the shell still expands: a `$` substitutes a
#    variable, a backtick runs a command and splices in what it printed, and a `"` closes the
#    quote early. None of the three is a syntax error, so the line launches and the leaf
#    carries on with a title nobody wrote — worse than the apostrophe, which at least killed
#    the line. `$HOME` is set in every shell a conductor types into, `kill %1` fails in one
#    with no job table and prints nothing to stdout, and `"blind"` is how this repository's
#    own issues quote a term — so each character arrives as something real and silent,
#    rather than as an error a reader would notice.
EXPANDING_STEP='A title naming `kill %1`, the "blind" verifier and $HOME reaches the leaf as written'

run_case "a step title carrying a dollar sign, a backtick and a double quote reaches the leaf $skill_md launches with it byte-identical (#437)" \
  scan_step_title "$EXPANDING_STEP" expanding-step-title

# 8c. The same three characters, asked of the develop-refactor launch instead (issue #437's
#    triangulation). Every developer leaf carries the title the same way, so a fix that
#    reaches only develop-red is not the fix; and develop-refactor is the launch where the
#    title cannot be read back as "the ledger's first unchecked step", because by the time it
#    launches the step's green commit has already ticked it. The ledger it runs beside holds
#    the step ticked with its `⟂ refactor pending` mark, and an unchecked step after it — so
#    a launch that asks the ledger for the next unchecked title hands the leaf the wrong step.

run_case "a step title carrying a dollar sign, a backtick and a double quote reaches the develop-refactor leaf $skill_md launches after the step is ticked, byte-identical (#437)" \
  scan_step_title "$EXPANDING_STEP" expanding-step-title-refactor develop-refactor plant_ticked_ledger

# 8d. The same three characters, asked of a verifier launch (issue #437). A verdict line
#    carries the title twice — as VERI_STEP in the launch's environment, and as the value of
#    `run-verdict.sh --step` in its argv — and the two are separate routes, so each is asked
#    on its own: a fix that repairs the prefix and leaves `--step "<STEP>"` hand-typed hands
#    the verifier one title in its environment and another on its command line. The run is
#    8b's shallow one: the detacher is a recorder, here writing down VERI_STEP and whatever
#    follows `--step` in the argv it was handed, which is the argv `run-verdict.sh` would
#    have received. The red cycle's verdict line is the one run, because it is the first a
#    run reaches; every verdict line carries the title the same way.
scan_verdict_step_title() {
  local title="$EXPANDING_STEP" tag=expanding-step-title-verdict
  local lineno line numbered launch stage seen tree err got argv
  numbered="$(head -1 < <(grep -nE '\$S/detach-leaf\.sh .*\$S/supervise\.sh verdict-red \$S/run-verdict\.sh' "$md"))"
  if [[ -z "$numbered" ]]; then
    no_launch "verdict-red through supervise.sh into run-verdict.sh"
    return
  fi
  take_line "$numbered" "$title" || return
  stage_recorder "$tag"
  plant_ledger "$tree" "$title"
  err="$( cd "$tree" && "${cleared_run_context[@]}" \
            S="$stage" SEEN="$seen" bash -c "$launch" 2>&1 >/dev/null )"
  got="$(cat "$seen" 2>/dev/null)" || got='<no verifier was launched>'
  argv="$(cat "$seen.argv" 2>/dev/null)" || argv='<no verifier was launched>'
  [[ "$got" == "$title" ]] ||
    problem "launched with the step title <$title>, whose verifier saw VERI_STEP=<$got> (the launching shell said: ${err//$'\n'//})"
  [[ "$argv" == "$title" ]] ||
    problem "launched with the step title <$title>, whose verifier was handed --step <$argv> (the launching shell said: ${err//$'\n'//})"
}

run_case "a step title carrying a dollar sign, a backtick and a double quote reaches the verifier $skill_md launches, byte-identical in VERI_STEP and in --step (#437)" \
  scan_verdict_step_title

# 9. The race issue #457 names, made to happen every time instead of on a slow runner. A pid
#    being gone and the completion file existing are two events, and nothing orders them: a
#    detached launch returns at once, the pid its tree records can die while the supervisor
#    behind it has not yet written `.tdd/<leaf>.exit`, and a wait that stops at the last pid
#    reported `<no completion file under leaf …>` — the words #297 reserves for a leaf named
#    wrongly — for a leaf that ran, saw its environment and answered. PR #456 went red on CI
#    that way on the two verifier lines and green on a re-run of the same sha.
#
#    Asked of one correct developer-shaped fixture launch of this probe's own, run against a
#    scripts directory whose detacher stands in for the whole slow chain: it records what the
#    leaf saw, records its OWN pid — gone the moment it returns — and leaves the completion
#    file to a writer no pid file names, which lands it a second later. So by the time the wait
#    first looks, every recorded pid has exited and the completion file has not arrived yet,
#    which is exactly the order the CI runner produced by being slow.
#
# scan_late_completion — the case's body, in the other cases' shape: `lineno`/`line` are its
# own so `expect_sentinel`'s complaint quotes this fixture's line.
scan_late_completion() {
  local lineno line launch leaf prompt stage
  developer_launch_fixture late-completion || return
  stage="$WORK/late-completion-scripts"
  mkdir -p "$stage"
  cat > "$stage/detach-leaf.sh" <<'STUB'
#!/bin/sh
# $1 is supervise.sh and $2 the leaf's name, as the launch line spells them.
printf '%s\n' "${VERI_TEST_CMD-<unset>}" > "$SEEN"
printf '%s\n' "$$" > ".tdd/$2.pid"
( sleep 1; printf '0\n' > ".tdd/$2.exit" ) </dev/null >/dev/null 2>&1 &
STUB
  chmod +x "$stage/detach-leaf.sh"
  SCRIPTS="$stage" expect_sentinel "$leaf" "$launch" "$prompt"
}

run_case "a launch whose completion file lands after its last recorded pid has exited is reported by what its leaf saw (#457)" \
  scan_late_completion

# 10. The half of #297 that case 9's fix must not undo. Case 9 made the wait outlast the last
#    recorded pid until a completion file lands; a launch that named its leaf wrongly must
#    still end that wait as soon as its OWN file lands, and be reported as the naming fault it
#    is — not waited on to the end of the budget for a file under the derived name that no
#    supervisor will ever write. Case 7 asks that of a launch whose file lands before its pid
#    is gone; this asks it of the order case 9 is about, where every recorded pid has exited
#    and the completion file, under the launch's real name, arrives a second later.
#
# scan_late_wrong_leaf_name — the case's body, in the other cases' shape: `lineno`/`line` are
# its own so the tree `launched_test_cmd` makes records this fixture's line.
scan_late_wrong_leaf_name() {
  local lineno line launch leaf prompt stage started elapsed got want
  developer_launch_fixture late-wrong-leaf-name || return
  stage="$WORK/late-wrong-leaf-name-scripts"
  mkdir -p "$stage"
  cat > "$stage/detach-leaf.sh" <<'STUB'
#!/bin/sh
# $1 is supervise.sh and $2 the leaf's name, as the launch line spells them.
printf '%s\n' "${VERI_TEST_CMD-<unset>}" > "$SEEN"
printf '%s\n' "$$" > ".tdd/$2.pid"
( sleep 1; printf '0\n' > ".tdd/$2.exit" ) </dev/null >/dev/null 2>&1 &
STUB
  chmod +x "$stage/detach-leaf.sh"
  want="<no completion file under leaf $leaf-no-such-leaf>"
  started=$SECONDS
  got="$(SCRIPTS="$stage" launched_test_cmd "$leaf-no-such-leaf" "$launch" "$prompt")"
  elapsed=$(( SECONDS - started ))
  [[ "$got" == "$want" && elapsed -lt ANSWER_CEILING ]] ||
    problem "launches under a leaf name no completion file is written under, reported as <$got> after ${elapsed}s, want <$want> under ${ANSWER_CEILING}s"
}

run_case "a launch whose leaf name no completion file is written under is still reported as a naming fault, well inside the wait budget, when its own file lands late (#457)" \
  scan_late_wrong_leaf_name

# 11. The third outcome `launched_test_cmd` owes (#457), and the one no case above asks of it
#    on its own: a launch line that reaches no supervisor at all — no leaf ran, so nothing
#    wrote `seen`, a pid file or a completion file — is reported as `<no leaf ran>`, not as a
#    naming fault it never got far enough to have. Cases 1 and 2 would only say so of a
#    document line that broke; this breaks one on purpose.
#
#    Asked of one correct developer-shaped fixture launch of this probe's own, run against a
#    scripts directory whose detacher returns having started nothing. Such a launch writes no
#    pid file, so the wait runs to its budget — the last resort it is kept for — and the case
#    injects the clock rather than wait it out: inside the one command substitution that runs
#    the probe, `sleep` is a function that moves `SECONDS` past any deadline, so the wait's
#    first nap ends it. Scoped to that subshell, so no other case sees the fake.
#
# scan_no_leaf_ran — the case's body, in the other cases' shape: `lineno`/`line` are its own
# so the tree `launched_test_cmd` makes records this fixture's line.
scan_no_leaf_ran() {
  local lineno line launch leaf prompt stage got
  developer_launch_fixture no-leaf-ran || return
  stage="$WORK/no-leaf-ran-scripts"
  mkdir -p "$stage"
  cat > "$stage/detach-leaf.sh" <<'STUB'
#!/bin/sh
exit 0
STUB
  chmod +x "$stage/detach-leaf.sh"
  got="$(sleep() { SECONDS=$(( SECONDS + 3600 )); }
         SCRIPTS="$stage" launched_test_cmd "$leaf" "$launch" "$prompt")"
  [[ "$got" == '<no leaf ran>' ]] ||
    problem "launches nothing, reported as <$got>, want <no leaf ran>"
}

run_case "a launch line that reaches no supervisor at all is reported as <no leaf ran> (#457)" \
  scan_no_leaf_ran

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

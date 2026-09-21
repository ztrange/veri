#!/usr/bin/env bash
# Tests for scripts/stop-run.sh — the operator's stop command (#387), the write half of the
# stop mechanism whose read half stop-requested.sh is (#386). Typed from anywhere in the
# repository, it finds the runs under the MAIN working tree's .tdd/wt/* (the #166 rule
# status.sh:158-164 already follows), writes the mode into each live run's .tdd/stop, and —
# for `--mode now` only — sends TERM to that run's live leaf supervisors.
#
# Not the fast tier: the runs are discovered through `git worktree list`, so every case here
# builds a real repository, and liveness is a real process answering `kill -0`.
#
# Run: scripts/tests/stop-run.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STOP="$HERE/../stop-run.sh"
pass=0 fail=0

work="$(mktemp -d)"
alive=()
# The stubs standing in for live processes are killed before the tree goes, so the suite
# leaves nothing running whichever way it ends. Each is then waited for, because a kill only
# asks: case 11's stub traps TERM and writes a file under "$work" on its way out, and an
# `rm -rf` racing that write left a "No such file or directory" line on stderr after the
# count line — which the `test` recipe reads as a suite that never reached it.
cleanup() {
  local pid
  for pid in ${alive[@]+"${alive[@]}"}; do kill "$pid" 2>/dev/null; done
  for pid in ${alive[@]+"${alive[@]}"}; do wait "$pid" 2>/dev/null; done
  rm -rf "$work"
}
trap cleanup EXIT

# A repository of the case's own, so the answer never depends on the runs live in the
# repository `make test` was typed in. A `git init` with no commit is enough: `git worktree
# list` prints it as the main working tree, which is all the resolution asks of it. Same
# fixture idiom as status.test.sh's repo().
repo="$work/repo"
git init -q -b main "$repo" >/dev/null 2>&1
run="$repo/.tdd/wt/5"
mkdir -p "$run/.tdd"

# A stub standing in for a live leaf supervisor, run as `supervise.sh <name> <issue>` so its
# command line is exactly what a real launch's is — the string `ps -p <pid> -o args=` is
# asked for, since pids are reused. It loops on short sleeps rather than one long one, so
# killing it leaves no child running past the suite (wait-leaf.test.sh case 7's idiom).
stubbin="$work/stubbin"; mkdir -p "$stubbin"
cat > "$stubbin/supervise.sh" <<'S'
#!/bin/sh
while :; do sleep 0.2; done
S
chmod +x "$stubbin/supervise.sh"

# live_supervisor <run-path> <leaf-name> — a live leaf supervisor of that run, which is what
# every case that looks at a signal needs: the stub launched the way a real one is, as
# `supervise.sh <name> <issue>`, and its pid in <run>/.tdd/<name>.pid, which is the pair the
# script reads a supervisor out of. The pid is left in `supervisor_pid` for the case that
# named it and added to `alive` so the trap kills it whichever way the suite ends — the same
# shape live_conductor() below has, for the same reasons.
live_supervisor() {
  "$stubbin/supervise.sh" "$2" "$(basename "$1")" &
  supervisor_pid=$!; alive+=("$supervisor_pid")
  printf '%s\n' "$supervisor_pid" > "$1/.tdd/$2.pid"
}

live_supervisor "$run" develop-red
sup_pid="$supervisor_pid"

# live_conductor <run-path> — a run whose conductor is live, which is what every case that
# expects a write needs and what `--all` picks its runs by: the directory the run keeps its
# state in, a process standing in for the conductor, and that process's pid in
# .tdd/conductor.pid, the whole of what liveness is read from. A plain background `sleep`
# serves, since nothing looks at a conductor's command line — .tdd/conductor.pid is read for
# liveness and for nothing else. The pid is left in `conductor_pid` for a case that wants to
# check it was not signalled, and added to `alive` so the trap kills it whichever way the
# suite ends.
live_conductor() {
  mkdir -p "$1/.tdd"
  sleep 60 &
  conductor_pid=$!; alive+=("$conductor_pid")
  printf '%s\n' "$conductor_pid" > "$1/.tdd/conductor.pid"
}

# reaped_pid — a real pid that is no longer a process, left in `reaped`: a background
# `sleep 0` waited for, so the number named something once and names nothing now, and
# `kill -0` fails on it (wait-leaf.test.sh:232's idiom). Two fixtures below are built out of
# it — a conductor that is not live, and the stale pid file a finished leaf leaves behind —
# and both want a number that really was a pid rather than an invented one, since what they
# ask about is the reading of a pid file, not the parsing of it.
reaped_pid() {
  sleep 0 &
  reaped=$!
  wait "$reaped" 2>/dev/null
}

# dead_conductor <run-path> — live_conductor's opposite, and the run two cases below name:
# one whose .tdd/conductor.pid is there and readable and holds a reaped pid, so nobody
# answers for the number in it. The .tdd/ directory is made the same way, which is what makes
# a .tdd/stop missing there the script declining to write rather than nowhere to write it.
dead_conductor() {
  mkdir -p "$1/.tdd"
  reaped_pid
  printf '%s\n' "$reaped" > "$1/.tdd/conductor.pid"
}

# The conductor of run 5, live from here to the end of the suite: its pid is one a buggy stop
# could signal, so every refusal below checks it is still answering.
live_conductor "$run"
run_conductor_pid="$conductor_pid"

# 1. Every refusal the argument contract names — an unknown mode, both an issue and --all,
#    neither, and an issue that is not a positive integer — exits 2 and leaves the repository
#    exactly as it was: nothing on stdout (an operator's script reads the run names from
#    there), a complaint on stderr, no .tdd/stop for the live run the command did not name
#    properly, and both its live pids still answering `kill -0`. The last two halves are what
#    the case is really for: a stop request left behind by a refused command would ambush the
#    run at its next checkpoint, and a TERM sent before the arguments were understood would
#    take a leaf down over a typo.
problems=""

# note <what-went-wrong> — one line of the case's diff, indented and, where there is one,
# headed by the refusal being checked. Every check below says only its own half; the shape
# they share — the indent, the newline, the append — is written once here. `$label` is
# check_refused's own local, which this function reads because bash scopes `local`
# dynamically: a function called from there sees the caller's locals. A case that checks one
# command rather than a family of them sets no label, and `:+` leaves the head off for it
# rather than dying on the unset name under `set -u`.
note() { problems+="    ${label:+$label: }$1"$'\n'; }

# report <name> — close a case whose checks collected into `problems`: nothing collected is
# a pass, otherwise one FAIL line for the case and the lines note() wrote under it, so the
# output says which half of the contract broke rather than just that the case did. Same
# helper detach-leaf.test.sh:48 carries, over this suite's string rather than its array.
report() {
  local name="$1"
  if [[ -z "$problems" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1)); echo "FAIL - $name"; printf '%s' "$problems"
  fi
}

# run_stop_in <dir> <args…> — run the command under test from <dir>, leaving its stdout in
# `out`, its exit code in `code` and its stderr in `err`. Every case captures the same three,
# and all three have to be captured together: `$?` is the status of the last command run, so a
# read of stderr placed between the call and the capture is what `$?` then answers about.
# Written once here rather than per case for that reason, and it assigns to the caller's names
# for the same dynamic-scope reason note() reads `$label`. Which directory is a parameter
# because one case below builds a second repository to ask what `--all` does where nothing is
# live, and a second copy of this capture written out for it would be a second chance to get
# that `$?` ordering wrong.
run_stop_in() {
  local dir="$1"; shift
  out="$(cd "$dir" && "$STOP" "$@" 2>"$work/stderr")" && code=0 || code=$?
  err="$(cat "$work/stderr")"
}

# run_stop <args…> — the same, from the repository the suite has been building all along,
# which is where every case but that one runs.
run_stop() { run_stop_in "$repo" "$@"; }

# check_code <want> — the exit status, which every case asks about and all of them ask about
# the same way. The stderr the script wrote rides along in the message, because an unexpected
# status is nearly always explained by the complaint that came with it, and a diff that made
# the reader go and rerun the command by hand to see it would be the slower one.
check_code() { [[ "$code" == "$1" ]] || note "want exit $1, got exit $code (stderr: $err)"; }

# check_no_stop <run-path> — the half every case that expects no write asks about, and the
# half that matters more than the exit code: a request left in a run the command was not meant
# to reach is not a no-op but a trap, still sitting there when that run next reads it. The
# note names the run, so one helper serves the refused commands, the dead run `--all` skipped
# and the two runs that got exit 3, and a failure still says which file was written.
check_no_stop() {
  [[ ! -e "$1/.tdd/stop" ]] ||
    note "want no .tdd/stop for $1, found one holding '$(cat "$1/.tdd/stop")'"
}

# check_still_answering <pid> <what> — a process the command must not have signalled, read
# the way the script itself reads liveness: `kill -0` sends nothing and only says whether
# there is a process to send to. Both of a refused command's untouched pids are asked about
# through this, since what separates them is which pid and what to call it, never the check.
check_still_answering() {
  kill -0 "$1" 2>/dev/null || note "want $2 $1 untouched, it is gone"
}

# check_refused_in <dir> <label> [args…] — one refusal, checked whole: exit 2, nothing on
# stdout, the script's own complaint on stderr, no .tdd/stop for the live run the command did
# not name properly, and both its live pids still answering. The directory is a parameter
# because one refusal below is a command typed where no repository is, and that one is a
# refusal like any other — checking it by hand would be a second copy of these six checks, and
# a copy is where one of them goes missing.
check_refused_in() {
  local dir="$1" label="$2"; shift 2
  local out code err
  run_stop_in "$dir" "$@"
  check_code 2
  [[ -z "$out" ]] || note "want empty stdout, got '$out'"
  # The complaint has to be the script's own — the `stop-run: ` prefix refuse() writes — and
  # not bash's: a `set -u` death over an option's missing value names this file and a line
  # number, says nothing about what the operator got wrong, and does not exit 2.
  [[ "$err" == "stop-run: "* ]] || note "want a complaint of the script's own, got '$err'"
  check_no_stop "$run"
  check_still_answering "$sup_pid" "the live supervisor"
  check_still_answering "$run_conductor_pid" "the conductor"
  rm -f "$run/.tdd/stop"
}

# check_refused <label> [args…] — the same, from the repository the suite has been building
# all along, which is where every refusal but that one is typed.
check_refused() { check_refused_in "$repo" "$@"; }

check_refused "an unknown --mode value" --mode bogus 5
check_refused "both an issue and --all" --mode now 5 --all
check_refused "neither an issue nor --all"
check_refused "a non-integer issue" --mode now five

report "an unknown --mode, both an issue and --all, neither, and a non-integer issue each exit 2, write no .tdd/stop and signal nothing"

# 2. `--mode` typed with nothing after it is a refusal like any other, and must read as one.
#    Left to `set -u`, the option's own value expansion dies before the contract is ever
#    checked: bash says its piece, the exit code is not 2, and an operator's wrapper that
#    branches on the codes cannot tell a mistyped command from the plumbing breaking. It is
#    checked through the same helper as every other refusal, which is what holds it to the
#    same bar — the script's own complaint, no .tdd/stop, nothing signalled.
problems=""
check_refused "--mode with no value" --mode

report "--mode with no value exits 2 with the script's own complaint, writes no .tdd/stop and signals nothing"

# check_stop <run-path> <want-mode> — the three halves of a written request, checked the same
# way wherever a case looks at one: the file is there, it holds that mode, and the mode is its
# only line, since stop-requested.sh reads it as one word and a second line beside it is a
# request the conductor cannot answer. Four cases below ask exactly this of a run they have
# just stopped, so the asking is written once here; each names its own run, and the lines
# note() collects name it too, so a failure says which run's file was wrong.
check_stop() {
  local path="$1/.tdd/stop" want="$2" written lines
  if [[ ! -f "$path" ]]; then
    note "want $path holding '$want', it was not written"
    return
  fi
  written="$(cat "$path")"
  [[ "$written" == "$want" ]] || note "want $path to hold '$want', it holds '$written'"
  lines="$(grep -c '' "$path")"
  [[ "$lines" == 1 ]] || note "want '$want' as the only line of $path, it has $lines lines"
}

# 3. The write itself, on the mode that also stops a run at once: `--mode now <n>` finds the
#    named run under the MAIN working tree, writes `now` as the only line of its .tdd/stop,
#    names the run on stdout and exits 0. Three halves, all of them what a caller sees: the
#    conductor reads that file with stop-requested.sh, so a second line or a different word
#    there is a request it cannot answer; an operator reads stdout to learn which runs the
#    command actually reached, so a silent success is indistinguishable from one that found
#    nothing; and exit 0 is what separates this from the exit 3 a dead run gets.
#
#    Stdout is checked for the issue number rather than one exact spelling of the run's
#    name: naming the run by its path and naming it by its number are both the run named,
#    and the step asks for the run to be named, not for a format.
problems=""
run_stop --mode now 5
check_code 0
[[ "$out" == *5* ]] || note "want the run named on stdout, got '$out'"
check_stop "$run" now

report "--mode now <n> writes now as the only line of that run's .tdd/stop, names the run on stdout and exits 0"

# 4. The default: a command with no `--mode` at all writes `at-ledger`. That is the mode an
#    operator gets by typing the least, so it is the one the script must pick when nothing
#    says otherwise — the stop that waits for the ledger's next checkpoint, the gentlest of
#    the three, since a default that took a leaf down at once would make the shortest command
#    the most destructive one. The file written by case 3 is removed first: what this case
#    asks is which mode a bare call chooses, not what a second call does to a file already
#    there, which is its own step.
problems=""
rm -f "$run/.tdd/stop"
run_stop 5
check_code 0
check_stop "$run" at-ledger

report "<n> with no --mode writes at-ledger into that run's .tdd/stop"

# 5. A second call for the same run overwrites the mode already in .tdd/stop. The file holds
#    one request, not a history of them: stop-requested.sh reads it as one word, so a mode
#    appended beside the one already there is a request the conductor cannot answer, and an
#    operator who typed `at-ledger` and then thought better of it would find the gentler mode
#    still standing. Case 4 left `at-ledger` there, which is what makes this a second call at
#    all — the run is stopped again with `now`, and what the file holds afterwards is `now`
#    alone, on one line, with the call reported as a success like any other.
problems=""
run_stop --mode now 5
check_code 0
check_stop "$run" now

report "a second call for the same run overwrites the mode already in .tdd/stop"

# 6. `--all` writes the mode into every live run's .tdd/stop and into no other. The operator
#    who types it is stopping the queue, not one issue, so the command has to reach every run
#    that is actually running — a second live run left out would go on working after the
#    operator was told the queue was stopped — and it has to stop there: a run whose conductor
#    has exited is over, and a request left in its .tdd/stop would ambush that issue at its
#    next resume rather than stopping anything now. So the fixture holds all three kinds at
#    once: run 5, live since the top of the suite, a second live run 7, and a run 9 whose
#    conductor.pid names a pid nobody answers for. Its .tdd/ exists, so a .tdd/stop missing
#    there is the script declining to write rather than the directory not being there.
#
#    Stdout is read as one run per line, each line's basename compared against the live runs'
#    numbers, for the reason case 3 gives — the run may be named by its path or by its number,
#    and both are the run named — but a substring check cannot serve here: the temporary tree
#    these runs live under is named by mktemp, so a bare `*9*` would match the path of a run
#    the command must not have touched.
problems=""
rm -f "$run/.tdd/stop"

live2="$repo/.tdd/wt/7"
live_conductor "$live2"

dead="$repo/.tdd/wt/9"
dead_conductor "$dead"

run_stop --mode at-leaf --all
check_code 0

named="$(printf '%s\n' "$out" | while read -r line; do
  [[ -n "$line" ]] && basename "$line"
done | sort | tr '\n' ' ')"
[[ "$named" == "5 7 " ]] ||
  note "want the two live runs named on stdout, got '$named' from '$out'"

for stopped in "$run" "$live2"; do
  check_stop "$stopped" at-leaf
done

check_no_stop "$dead"

report "--all writes the mode into every live run's .tdd/stop and into no other"

# 7. The three shapes of a run that is not there to be stopped — an issue with no worktree
#    under .tdd/wt/ at all, an issue whose .tdd/conductor.pid names no live process, and
#    `--all` finding no live run anywhere — each exit 3 and write no .tdd/stop. Exit 3 is
#    this repository's "nothing to do", distinct from the 2 a misunderstood command gets:
#    the operator typed something the script understood perfectly, and there was simply no
#    run answering to it. The write is the half that matters more than the code, though: a
#    stop request left in a finished run's .tdd/stop is not a no-op but a trap, since it is
#    still sitting there when that issue is next resumed and would stop the new run at its
#    first checkpoint for a decision the operator made about the old one.
#
#    The first two are asked of the repository the suite has been building all along — run
#    404 was never created, and run 9 is the one case 6 gave a conductor.pid nobody answers
#    for. The third needs a repository of its own: this one has two live runs by now, so
#    `--all` typed here would find them. A fresh `git init` with the same dead run in it is
#    the smallest tree where `--all` can find nothing.
problems=""

label="an issue with no worktree"
run_stop 404
check_code 3
[[ ! -e "$repo/.tdd/wt/404" ]] ||
  note "want nothing written for a run that does not exist, found $repo/.tdd/wt/404"

label="an issue whose conductor is not live"
run_stop 9
check_code 3
check_no_stop "$dead"

label="--all with no live run"
quiet="$work/quiet"
git init -q -b main "$quiet" >/dev/null 2>&1
quiet_dead="$quiet/.tdd/wt/9"
dead_conductor "$quiet_dead"
run_stop_in "$quiet" --all
check_code 3
check_no_stop "$quiet_dead"

report "an issue with no worktree, an issue whose conductor names no live process, and --all with no live run each exit 3 and write no .tdd/stop"

# Cases 3 and 5 each stopped run 5 with `--mode now`, so the supervisor launched at the top of
# the suite has been signalled by then and the pid left in develop-red.pid names nothing. What
# the two cases below ask is what a command the script refuses leaves untouched, and that needs
# a live supervisor there to be untouched: one is launched here and develop-red.pid points at
# it again, so the check reads a pid that is alive for any reason but the one under test.
live_supervisor "$run" develop-red
sup_pid="$supervisor_pid"

# 8. A command typed where no main working tree can be resolved exits 2, the same as any
#    other command this script cannot make sense of. `git worktree list` says nothing
#    outside a repository, so the resolution comes back empty and there is no .tdd/wt/ to
#    look under — the script has not found a repository with no live runs in it, it has
#    found no repository, and the two are the difference between this repository's 3 and its
#    2: an operator's wrapper that branches on the codes would read "nothing to do" and stop
#    asking, when what actually happened is that the command was typed in the wrong place.
#    Nothing is written and nothing is signalled, checked against the live run this suite has
#    been carrying all along: the refusal happens before any run is looked at, so a stop
#    request left behind or a TERM sent from a command that never resolved a tree would reach
#    a run the operator's shell was not even standing in.
problems=""
rm -f "$run/.tdd/stop"

outside="$work/outside"; mkdir -p "$outside"
check_refused_in "$outside" "no main working tree" --mode now 5

report "a command typed where no main working tree resolves exits 2, writes no .tdd/stop and signals nothing"

# 9. `--mode now` is the one mode that also takes the run's leaves down at once, and the pid it
#    may send TERM to is a narrow one: the number in `<run>/.tdd/<name>.pid` whose process's
#    `ps -p <pid> -o args=` holds `supervise.sh <name> `, the check wait-leaf.sh:47-51 already
#    makes. Both halves of that are load-bearing, because a pid file outlives the process it
#    named and pids are reused: a pid whose process is gone names nothing, and a pid whose
#    process is something else is a stranger's, and a TERM sent to either is sent to whatever
#    the operating system has since given that number to. So the run is given all three kinds of
#    pid file at once, and what the case asks is that exactly the supervisor stopped.
#
#    The kill is a request, not something the caller applies: the signal is delivered to a
#    running process, which then runs its own trap (supervise.sh:350-355) and exits, so what
#    the command must produce is the supervisor finishing — checked by polling, since it is not
#    finished the instant the command returns.
problems=""
label=""
rm -f "$run/.tdd/stop"

# A live leaf supervisor of run 5, the pid this case expects a TERM to reach.
live_supervisor "$run" develop-green
green_sup="$supervisor_pid"

# A pid file of the same shape whose process is not that leaf's supervisor at all: it is live
# and answers `kill -0` exactly as the supervisor does, and a plain `sleep` is its whole command
# line, so the args check is the only thing standing between it and a TERM.
sleep 60 &
impostor=$!; alive+=("$impostor")
printf '%s\n' "$impostor" > "$run/.tdd/verify-green.pid"

# And one whose process is simply gone. No signal not sent can be watched for, so what this
# one is here for is the exit code: a stale pid file is the ordinary state of a finished leaf,
# and a run whose stop was written must not be reported as a failure over one.
reaped_pid; stale_pid="$reaped"
printf '%s\n' "$stale_pid" > "$run/.tdd/verify-refactor.pid"

# gone <pid> — whether a signalled process has finished going, in 50 ms steps rather than one
# fixed wait: a delivered signal is answered in the first step or two, and only a supervisor
# that was never signalled at all pays the whole 2 s before the case says so.
gone() {
  local pid="$1" i
  for (( i = 0; i < 40; i++ )); do
    kill -0 "$pid" 2>/dev/null || return 0
    sleep 0.05
  done
  return 1
}

run_stop --mode now 5
check_code 0
gone "$green_sup" ||
  note "want the develop-green supervisor $green_sup signalled, it is still answering"
check_still_answering "$impostor" "the pid running something other than a supervisor"

report "--mode now <n> sends TERM to the pid in <run>/.tdd/<name>.pid whose process runs supervise.sh <name>, and to no pid whose process is gone or runs something else"

# 10. The other two modes signal nothing. `at-ledger` and `at-leaf` are the modes that ask a
#     conductor to stop at its own next checkpoint, so the whole of what they do is the write:
#     a leaf they took down would be the `now` behaviour under another name, and the operator
#     who chose the gentler mode chose it precisely to let the leaf in flight finish. Case 9
#     signalled every live supervisor run 5 had, so one is launched again here — the check
#     needs a supervisor that is alive for any reason but the one under test.
#
#     Each mode is asked the same three things: exit 0, the mode written (which is what makes
#     "signalled nothing" the command declining to signal rather than the command doing nothing
#     at all), and that run's live leaf supervisor still answering `kill -0` afterwards.
problems=""

live_supervisor "$run" develop-red
quiet_sup="$supervisor_pid"

for gentle in at-ledger at-leaf; do
  label="--mode $gentle"
  rm -f "$run/.tdd/stop"
  run_stop --mode "$gentle" 5
  check_code 0
  check_stop "$run" "$gentle"
  check_still_answering "$quiet_sup" "the live supervisor"
done
label=""

report "--mode at-ledger <n> and --mode at-leaf <n> write the mode and signal nothing"

# 11. .tdd/conductor.pid is read to decide whether a run is live and for nothing else — the
#     conductor is never signalled, whatever its process happens to be running. `--mode now`
#     is the only mode that signals at all, and the pid files it reads a supervisor out of are
#     found by a glob over <run>/.tdd/*.pid, which .tdd/conductor.pid is one of. So what keeps
#     the conductor out has to be its name, and the fixture makes that the only thing that can:
#     run 11's conductor is launched with the command line a supervisor of a leaf named
#     `conductor` would have, so every other check on the way to a TERM says yes. Signalling it
#     would take down the one process that reads the request the same command has just written
#     — the stop would kill the conductor it was asking to stop.
#
#     The stub records a TERM in a file rather than merely dying of one, and that file is what
#     the check reads: a background child that has died is still a pid `kill -0` answers for
#     until the suite's shell reaps it, so liveness here could call a signalled conductor
#     untouched. The mode written and exit 0 are checked beside it, which is what makes
#     "signalled nothing" the command declining to signal rather than the command doing nothing.
problems=""
label=""

conductor_run="$repo/.tdd/wt/11"
mkdir -p "$conductor_run/.tdd"
marker="$work/conductor-signalled"
rm -f "$marker"

trapbin="$work/trapbin"; mkdir -p "$trapbin"
cat > "$trapbin/supervise.sh" <<'S'
#!/bin/sh
trap 'echo signalled > "$MARKER"; exit 0' TERM
while :; do sleep 0.05; done
S
chmod +x "$trapbin/supervise.sh"

MARKER="$marker" "$trapbin/supervise.sh" conductor 11 &
fake_conductor=$!; alive+=("$fake_conductor")
printf '%s\n' "$fake_conductor" > "$conductor_run/.tdd/conductor.pid"

run_stop --mode now 11
check_code 0
check_stop "$conductor_run" now

# The window is a short poll rather than one read: a TERM sent by the command is recorded by
# the stub's trap a moment after the command returns, and a check made the instant it does
# would call a conductor that has been signalled untouched. Only a run where nothing was sent
# pays the whole window, and it is the shortest one that a signal cannot outrun.
signalled=0
for (( i = 0; i < 12; i++ )); do
  if [[ -e "$marker" ]]; then signalled=1; break; fi
  sleep 0.05
done
(( signalled == 0 )) ||
  note "want the conductor $fake_conductor untouched, it took a TERM"

report "stop-run.sh never signals the pid in .tdd/conductor.pid"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

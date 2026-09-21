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
# leaves nothing running whichever way it ends.
cleanup() {
  local pid
  for pid in ${alive[@]+"${alive[@]}"}; do kill "$pid" 2>/dev/null; done
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

"$stubbin/supervise.sh" develop-red 5 &
sup_pid=$!; alive+=("$sup_pid")
printf '%s\n' "$sup_pid" > "$run/.tdd/develop-red.pid"

# The conductor of that run: a live process too, so the run reads as live and the pid is one
# a buggy stop could signal. It is a plain background `sleep`, since nothing looks at its
# command line — .tdd/conductor.pid is read for liveness and for nothing else.
sleep 60 &
cond_pid=$!; alive+=("$cond_pid")
printf '%s\n' "$cond_pid" > "$run/.tdd/conductor.pid"

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

# run_stop <args…> — run the command under test from the repository the case built, leaving
# its stdout in `out`, its exit code in `code` and its stderr in `err`. Every case captures
# the same three, and all three have to be captured together: `$?` is the status of the last
# command run, so a read of stderr placed between the call and the capture is what `$?` then
# answers about. Written once here rather than per case for that reason, and it assigns to
# the caller's names for the same dynamic-scope reason note() reads `$label`.
run_stop() {
  out="$(cd "$repo" && "$STOP" "$@" 2>"$work/stderr")" && code=0 || code=$?
  err="$(cat "$work/stderr")"
}

check_refused() {  # check_refused <label> [args…]
  local label="$1"; shift
  local out code err
  run_stop "$@"
  [[ "$code" == 2 ]] || note "want exit 2, got exit $code"
  [[ -z "$out" ]] || note "want empty stdout, got '$out'"
  # The complaint has to be the script's own — the `stop-run: ` prefix refuse() writes — and
  # not bash's: a `set -u` death over an option's missing value names this file and a line
  # number, says nothing about what the operator got wrong, and does not exit 2.
  [[ "$err" == "stop-run: "* ]] || note "want a complaint of the script's own, got '$err'"
  [[ ! -e "$run/.tdd/stop" ]] ||
    note "want no .tdd/stop written, found one holding '$(cat "$run/.tdd/stop")'"
  kill -0 "$sup_pid" 2>/dev/null ||
    note "want the live supervisor $sup_pid untouched, it is gone"
  kill -0 "$cond_pid" 2>/dev/null ||
    note "want the conductor $cond_pid untouched, it is gone"
  rm -f "$run/.tdd/stop"
}
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
[[ "$code" == 0 ]] || note "want exit 0, got exit $code (stderr: $err)"
[[ "$out" == *5* ]] || note "want the run named on stdout, got '$out'"
if [[ ! -f "$run/.tdd/stop" ]]; then
  note "want $run/.tdd/stop holding 'now', it was not written"
else
  written="$(cat "$run/.tdd/stop")"
  [[ "$written" == "now" ]] || note "want .tdd/stop to hold 'now', it holds '$written'"
  lines="$(grep -c '' "$run/.tdd/stop")"
  [[ "$lines" == 1 ]] || note "want 'now' as the only line of .tdd/stop, it has $lines lines"
fi

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
[[ "$code" == 0 ]] || note "want exit 0, got exit $code (stderr: $err)"
if [[ ! -f "$run/.tdd/stop" ]]; then
  note "want $run/.tdd/stop holding 'at-ledger', it was not written"
else
  written="$(cat "$run/.tdd/stop")"
  [[ "$written" == "at-ledger" ]] ||
    note "want .tdd/stop to hold 'at-ledger', it holds '$written'"
fi

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
[[ "$code" == 0 ]] || note "want exit 0, got exit $code (stderr: $err)"
if [[ ! -f "$run/.tdd/stop" ]]; then
  note "want $run/.tdd/stop holding 'now', it was not written"
else
  written="$(cat "$run/.tdd/stop")"
  [[ "$written" == "now" ]] ||
    note "want the second call's mode alone, .tdd/stop holds '$written'"
  lines="$(grep -c '' "$run/.tdd/stop")"
  [[ "$lines" == 1 ]] || note "want 'now' as the only line of .tdd/stop, it has $lines lines"
fi

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

live2="$repo/.tdd/wt/7"; mkdir -p "$live2/.tdd"
sleep 60 &
live2_pid=$!; alive+=("$live2_pid")
printf '%s\n' "$live2_pid" > "$live2/.tdd/conductor.pid"

# A real pid that is no longer a process: a background `sleep 0` already reaped, so the
# number names nothing and `kill -0` fails on it (wait-leaf.test.sh:232's idiom).
dead="$repo/.tdd/wt/9"; mkdir -p "$dead/.tdd"
sleep 0 &
dead_pid=$!
wait "$dead_pid" 2>/dev/null
printf '%s\n' "$dead_pid" > "$dead/.tdd/conductor.pid"

run_stop --mode at-leaf --all
[[ "$code" == 0 ]] || note "want exit 0, got exit $code (stderr: $err)"

named="$(printf '%s\n' "$out" | while read -r line; do
  [[ -n "$line" ]] && basename "$line"
done | sort | tr '\n' ' ')"
[[ "$named" == "5 7 " ]] ||
  note "want the two live runs named on stdout, got '$named' from '$out'"

for live_run in "$run" "$live2"; do
  if [[ ! -f "$live_run/.tdd/stop" ]]; then
    note "want $live_run/.tdd/stop holding 'at-leaf', it was not written"
  else
    written="$(cat "$live_run/.tdd/stop")"
    [[ "$written" == "at-leaf" ]] ||
      note "want $live_run/.tdd/stop to hold 'at-leaf', it holds '$written'"
    lines="$(grep -c '' "$live_run/.tdd/stop")"
    [[ "$lines" == 1 ]] ||
      note "want 'at-leaf' as the only line of $live_run/.tdd/stop, it has $lines lines"
  fi
done

[[ ! -e "$dead/.tdd/stop" ]] ||
  note "want no .tdd/stop for the run whose conductor is gone, found one holding '$(cat "$dead/.tdd/stop")'"

report "--all writes the mode into every live run's .tdd/stop and into no other"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

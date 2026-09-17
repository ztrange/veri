#!/usr/bin/env bash
# Tests for scripts/wait-leaf.sh — the foreground half of a detached leaf launch (#86).
#
# A print-mode conductor (`claude -p "/tdd <n>"`) never receives background-task
# notifications, so a turn that ends with a supervised leaf still running orphans it. The
# fix splits launch from wait: `supervise.sh` is launched detached and records its own
# final code in a completion file, and this script blocks in the foreground until that
# file appears, then exits with the code it holds.
#
# Driven against STUB WRITERS (no claude, no supervisor): a background subshell that
# creates the completion file a couple of seconds after the wait has already started, which
# is the case that matters — the file is absent when the wait begins, so the script must
# poll rather than look once.
#
# Status contract: exit 0 success · 1 leaf-failure · 2 killed-stuck (whatever the
# supervisor recorded) · 3 nothing to report yet.
#
# Run: scripts/tests/wait-leaf.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WAIT="$HERE/../wait-leaf.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/.tdd"

# timed <name> <budget> — wait for <name> in the foreground with a <budget>-second budget,
# and echo "<wait-leaf's exit code> <seconds the wait took>".
#
# Both numbers are what a case needs, whichever way it is pointed: the code is the answer,
# and the elapsed time separates the two ways of arriving at it — "returned when the file
# appeared" from "sat out the whole budget and then read it", and, where no file ever lands,
# "gave up when the budget ran out" from "never waited at all". The exit code alone cannot
# tell those apart.
#
# VERI_POLL is pinned rather than inherited (see hermetic-suites.test.sh): an ambient poll
# interval of minutes would make the elapsed time a fact about the caller's environment.
timed() {
  local t0 rc
  t0="$(date +%s)"
  ( cd "$work" && env VERI_POLL=0.2 "$WAIT" "$1" "$2" >/dev/null 2>&1 )
  rc=$?
  printf '%s %s\n' "$rc" "$(( $(date +%s) - t0 ))"
}

# waited <name> <code> — spawn a writer that records <code> in the completion file
# .tdd/<name>.exit two seconds from now, i.e. after the wait has already started, then `timed`
# the wait for <name> with a budget ten times that delay, so the answer can only come from the
# file landing and not from the budget running out.
waited() {
  ( sleep 2; printf '%s\n' "$2" > "$work/.tdd/$1.exit" ) &
  timed "$1" 20
  wait
}

# promptly <result> <want-code> — true when a `waited` result reads "<want-code> <secs>" and
# the wait took no longer than the writer's delay plus slack, i.e. it returned when the file
# landed instead of sitting out the budget. Splitting that pair apart is the same two
# parameter expansions in every arm, so it is named once here rather than spelled out thrice.
promptly() {
  local rc="${1%% *}" secs="${1#* }" want="$2"
  [[ "$rc" == "$want" ]] && [[ "$secs" =~ ^[0-9]+$ ]] && [[ "$secs" -le 10 ]]
}

# 1. the recorded supervisor code, returned as soon as the file lands. Three arms, one per
#    status in the contract, because "the recorded code" means the file's contents and not
#    a fixed answer that happens to match one of them — a script that always exited 0 would
#    pass a success-only case. Fresh names per arm, so no arm can read another's file.
w_ok="$(waited    late-ok    0)"
w_fail="$(waited  late-fail  1)"
w_stuck="$(waited late-stuck 2)"
{ promptly "$w_ok"    0 &&
  promptly "$w_fail"  1 &&
  promptly "$w_stuck" 2; } && ok \
  || no "exits with the code recorded a couple of seconds into the wait, as soon as it lands (got '<code> <secs>': success=$w_ok want '0 <=10', failure=$w_fail want '1 <=10', killed-stuck=$w_stuck want '2 <=10')"

# 2. no completion file → exit 3 ("nothing to report yet"), once the budget is spent and not
#    before, and the budget the conductor gets when it names none is short enough that one
#    call fits inside Claude Code's 10-minute foreground cap: at most 540 seconds.
#
#    Two arms, because the criterion has two halves. The first passes an explicit 1-second
#    budget, so real time can prove both the code and that the wait ended. The second names
#    no budget at all, and its length is measured rather than waited out: the script reads
#    the clock with `date +%s` (as supervise.sh does — bash 3.2 has no $EPOCHSECONDS), so a
#    stub `date` earlier on PATH hands it a VIRTUAL clock that jumps 10 seconds per reading
#    and logs every value it served. The last logged value is the virtual moment the script
#    gave up, i.e. the default budget itself — measured in well under a second of real time.
#    A default of 600 would be logged as 600 and fail the case rather than hang it.
b_given="$(timed never-lands 1)"

clockbin="$work/clockbin"; mkdir -p "$clockbin"
clocklog="$work/clock.log"; : > "$clocklog"
cat > "$clockbin/date" <<'D'
#!/usr/bin/env bash
# Virtual clock: reading N is 10*N seconds past the start, and every reading served is
# appended to $VERI_CLOCK_LOG so the caller can see how far the waiter let it run.
n="$(wc -l < "$VERI_CLOCK_LOG" | tr -d ' ')"
printf '%s\n' "$(( n * 10 ))" | tee -a "$VERI_CLOCK_LOG"
D
chmod +x "$clockbin/date"
( cd "$work" && env VERI_POLL=0 VERI_CLOCK_LOG="$clocklog" PATH="$clockbin:$PATH" \
    "$WAIT" no-budget-named >/dev/null 2>&1 )
rc_default=$?
b_default="$(tail -n 1 "$clocklog")"

{ promptly "$b_given" 3 &&
  [[ "$rc_default" == 3 ]] &&
  [[ "$b_default" =~ ^[0-9]+$ ]] && [[ "$b_default" -le 540 ]]; } && ok \
  || no "exits 3 once a budget with no completion file is spent, and the default budget is at most 540s (given 1s: got '<code> <secs>'=$b_given want '3 <=10'; default: code=$rc_default want 3, gave up at ${b_default:-<no clock reading>}s want <=540)"

# 3. no completion file and no leaf either → still exit 3, never 0. Absence of a result is
#    not success: a 0 here would tell the conductor that a leaf which was never launched had
#    passed, and it would tick the ledger on it.
#
#    Run in a pristine directory rather than the shared one — no `.tdd` at all, no writer
#    spawned, no supervisor — so the only thing the script can be answering about is the
#    absence itself, with nothing of another case's making for it to find.
bare="$work/bare"; mkdir -p "$bare"
( cd "$bare" && env VERI_POLL=0.2 "$WAIT" never-launched 1 >/dev/null 2>&1 )
rc_bare=$?
[[ "$rc_bare" == 3 ]] && ok \
  || no "exits 3, never 0, when there is no completion file and no leaf running (got $rc_bare, want 3)"

# 4. The script is only half the fix. A conductor that still ends its turn with a leaf sitting
#    in a background Bash call orphans it whatever this script does, and SKILL.md — the
#    procedure the conductor actually follows — said nothing about waiting at all when #86 was
#    written (`grep -niE 'background|notification|wait' skills/tdd/SKILL.md` matched
#    nothing), so foreground-or-background was a fresh guess at every launch and the wrong
#    guess is fatal in print mode. The document therefore carries this criterion: every leaf
#    launch in it is detached and followed by a foreground wait, and it says in so many words
#    why the background-call-plus-notification shape is the one that kills an unattended run.
#
#    The case lives in this suite rather than under `docs/tests/` because what is being written
#    down is this script's own contract, and because `make docs-check` is deliberately not part
#    of `make test` (Makefile, "Neither is part of `test` on purpose") — a documentation case
#    parked there would not run in the suite this change is verified against.
#
#    A launch site is found by what it is rather than by where it sits: a line naming one of
#    the two launchers — `$S/supervise.sh`, or `$S/verify.sh`, which goes through the
#    supervisor too — AND carrying a `.tdd/` path, i.e. a real invocation with real arguments.
#    That leaves out the Commands-reference bullets and the prose back-references, which name a
#    launcher and no path, and it survives the fix itself: prefixing the detaching launcher
#    changes neither half of the test. The count is asserted before its members, as in solvable-issues case 12:
#    five phases launch leaves (red, green, refactor, revise, verify), so an enumeration
#    finding fewer than five has stopped matching the document and must read as a failure
#    rather than pass with nothing left to check.
#
#    *Detached* is `detach-leaf.sh` on the launch line. It was `nohup` plus a trailing `&`
#    until #161: `nohup` only makes the child ignore SIGHUP and leaves it in the process group
#    of the Bash call that launched it, so a harness that signals that group when the call ends
#    takes the leaf with it — a detach on paper only, which is why the launcher now owns it and
#    returns on its own rather than being backgrounded by the launch line. That makes the probe
#    one fixed substring, asked with bash's own `==`: the two-part grep it replaced was the old
#    shape's cost — a word anywhere on the line, plus an `&` anchored at end of line so the one
#    inside a `2>&1` could not stand in for the one that actually backgrounded the call — and
#    the regex, and the process it needed, went with the shape. What the launcher must actually
#    survive is `detach-leaf.test.sh`'s subject; what every launch line must name is
#    `skill-leaf-launch.test.sh`'s. This half stays here because the pair with the foreground
#    wait below is this script's own contract.
#
#    The wait is looked for on the launch line and the six after it — the same fenced block, in
#    practice — rather than anywhere in the file, because one mention of `wait-leaf.sh` in the
#    Commands reference must not satisfy nine launches.
#
#    The warning is read as a paragraph (`awk RS=""`) naming all three of *background*,
#    *notification* and *print mode*, because prose here wraps at ~90 columns and a
#    line-by-line grep would miss a sentence split across two lines. Three file-wide greps
#    would be the other failure: those terms scattered over three sections are not a warning.
SKILL="$HERE/../../SKILL.md"
# The launcher a launch line has to name, written down once so the probe and the token it
# fails with cannot drift apart. The token quotes it rather than saying `not-detached`: the
# adjective named nothing a reader could grep the document for, and it outlived the shape it
# was coined for — it meant `nohup` plus a trailing `&` until #161 replaced both with this
# script.
detacher="detach-leaf.sh"
launches=0 launch_misses=""

# missed <token> — record one way the document fails this case, onto the space-separated
# `launch_misses` string opened empty just above. Every probe below accumulates rather than
# failing at the first one, because a document that has drifted has usually drifted at several
# launches at once and the single `no` line is worth more when it names all of them; the tokens
# carry their own line number for that reason.
missed() { launch_misses="$launch_misses $1"; }

while IFS= read -r hit; do
  launches=$(( launches + 1 ))
  n="${hit%%:*}" text="${hit#*:}"
  [[ "$text" == *"$detacher"* ]] \
    || missed "line$n:no-$detacher"
  sed -n "${n},$(( n + 6 ))p" "$SKILL" | grep -q 'wait-leaf\.sh' \
    || missed "line$n:no-foreground-wait"
done < <(grep -n -e '\$S/supervise\.sh' -e '\$S/verify\.sh' "$SKILL" | grep '\.tdd/')

warning="$(awk 'BEGIN { RS = "" }
  tolower($0) ~ /background/ && tolower($0) ~ /notification/ &&
  tolower($0) ~ /print[ -]mode/ { print; exit }' "$SKILL")"

[[ "$launches" -ge 5 ]] || missed "enumeration:only-$launches-launch-sites"
[[ -n "$warning" ]] || missed "warning:no-paragraph-naming-background-notification-print-mode"

[[ -z "$launch_misses" ]] && ok \
  || no "SKILL.md launches every leaf detached and waits for it with wait-leaf.sh in the foreground, and warns that a background call awaiting a notification never completes in print mode (launch sites=$launches, missing:$launch_misses)"

# 5. a supervisor that died without writing its completion file → exit 2, long before the
#    budget runs out, and stderr names the leaf and the dead pid (#173). A KILL cannot be
#    trapped, so the supervisor's recorded pid is the only thing that tells a dead supervisor
#    from a slow one; without it every 3 looks alike and the conductor calls again forever.
#
#    The dead pid is a real one: a background `sleep 0` that has been reaped, so it names a
#    process that existed and has exited. The budget is 20 seconds so that "gave up when the
#    budget ran out" reads as 20 and cannot pass for "noticed the death" at <=10.
( sleep 0 ) &
dead_pid=$!
wait "$dead_pid"
printf '%s\n' "$dead_pid" > "$work/.tdd/dead-sup.pid"
d_err="$work/dead-sup.err"
d_t0="$(date +%s)"
( cd "$work" && env VERI_POLL=0.2 "$WAIT" dead-sup 20 >/dev/null 2>"$d_err" )
d_rc=$?
d_secs=$(( $(date +%s) - d_t0 ))
d_stderr="$(cat "$d_err")"
{ [[ "$d_rc" == 2 ]] && [[ "$d_secs" -le 10 ]] &&
  [[ "$d_stderr" == *dead-sup* ]] && [[ "$d_stderr" == *"$dead_pid"* ]]; } && ok \
  || no "exits 2 well before its budget, naming the leaf and the dead pid on stderr, when the recorded supervisor has exited and no completion file exists (got code=$d_rc secs=$d_secs want '2 <=10'; stderr='$d_stderr' want it to name dead-sup and $dead_pid)"

# 6. a recorded pid that is alive but is not a supervise.sh for that name → the same exit 2 as
#    a dead one (#173). Pids are reused, so after the supervisor dies its number can come back
#    as any other process, and `kill -0` alone would then read the dead supervisor as alive and
#    wait out the budget — the forever-loop case 5 exists to prevent, one pid reuse away.
#
#    The impostor is a live background `sleep`: a real process, owned by this user so `kill -0`
#    succeeds on it, and plainly not `supervise.sh reused-sup`. Same 20-second budget as case 5,
#    for the same reason. It is killed afterwards so the suite leaves nothing running.
sleep 60 &
imp_pid=$!
printf '%s\n' "$imp_pid" > "$work/.tdd/reused-sup.pid"
r_err="$work/reused-sup.err"
r_t0="$(date +%s)"
( cd "$work" && env VERI_POLL=0.2 "$WAIT" reused-sup 20 >/dev/null 2>"$r_err" )
r_rc=$?
r_secs=$(( $(date +%s) - r_t0 ))
r_stderr="$(cat "$r_err")"
kill "$imp_pid" 2>/dev/null; wait "$imp_pid" 2>/dev/null
{ [[ "$r_rc" == 2 ]] && [[ "$r_secs" -le 10 ]] &&
  [[ "$r_stderr" == *reused-sup* ]] && [[ "$r_stderr" == *"$imp_pid"* ]]; } && ok \
  || no "exits 2 well before its budget when the recorded pid is alive but is not a supervise.sh for that leaf (pid reuse), naming the leaf and the pid on stderr (got code=$r_rc secs=$r_secs want '2 <=10'; stderr='$r_stderr' want it to name reused-sup and $imp_pid)"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

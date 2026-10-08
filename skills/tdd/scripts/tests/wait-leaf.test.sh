#!/usr/bin/env bash
# Tests for scripts/wait-leaf.sh — the foreground half of a detached leaf launch: it blocks
# until the completion file a detached `supervise.sh` writes appears, then exits with the
# code it holds. Driven against stub writers on a stub `date` that advances a fixed step
# per reading.
#
# Contract under test:
#   exit 0 success · 1 leaf-failure · 2 killed-stuck (whatever the supervisor recorded)
#   · 3 nothing to report yet. A completion file absent when the wait begins is polled for.
#
# Run: scripts/tests/wait-leaf.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WAIT="$HERE/../wait-leaf.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"
mkdir -p "$work/.tdd"

clockbin="$work/clockbin"; mkdir -p "$clockbin"
cat > "$clockbin/date" <<'D'
#!/bin/sh
n="$(wc -l < "$VERI_CLOCK_LOG" | tr -d ' ')"
now="$(( n * ${VERI_CLOCK_STEP:-1} ))"
if [ -n "${CLOCK_LAND_AT:-}" ] && [ "$now" -ge "$CLOCK_LAND_AT" ] && [ ! -e "$CLOCK_LAND_FILE" ]; then
  printf '%s\n' "$CLOCK_LAND_CODE" > "$CLOCK_LAND_FILE"
fi
printf '%s\n' "$now" | tee -a "$VERI_CLOCK_LOG"
D
chmod +x "$clockbin/date"

timed() {
  local name="$1" budget="$2" log="$work/$1.clock" rc
  shift 2
  : > "$log"
  ( cd "$work" && env VERI_POLL=0 VERI_CLOCK_LOG="$log" PATH="$clockbin:$PATH" "$@" \
      "$WAIT" "$name" "$budget" >/dev/null 2>"$work/$name.err" )
  rc=$?
  printf '%s %s\n' "$rc" "$(( $(tail -n 1 "$log") - $(head -n 1 "$log") ))"
}

waited() {
  timed "$1" 20 CLOCK_LAND_AT=2 CLOCK_LAND_FILE=".tdd/$1.exit" CLOCK_LAND_CODE="$2"
}

promptly() {
  local rc="${1%% *}" secs="${1#* }" want="$2"
  [[ "$rc" == "$want" ]] && [[ "$secs" =~ ^[0-9]+$ ]] && [[ "$secs" -le 10 ]]
}

names() {
  local text="$1" token
  shift
  for token in "$@"; do [[ "$text" == *"$token"* ]] || return 1; done
}

w_ok="$(waited    late-ok    0)"
w_fail="$(waited  late-fail  1)"
w_stuck="$(waited late-stuck 2)"
{ promptly "$w_ok"    0 &&
  promptly "$w_fail"  1 &&
  promptly "$w_stuck" 2; } && ok \
  || no "exits with the code recorded a couple of seconds into the wait, as soon as it lands (got '<code> <secs>': success=$w_ok want '0 <=10', failure=$w_fail want '1 <=10', killed-stuck=$w_stuck want '2 <=10')"

b_given="$(timed never-lands 1)"

clocklog="$work/clock.log"; : > "$clocklog"
( cd "$work" && env VERI_POLL=0 VERI_CLOCK_STEP=540 VERI_CLOCK_LOG="$clocklog" PATH="$clockbin:$PATH" \
    "$WAIT" no-budget-named >/dev/null 2>&1 )
rc_default=$?
b_default="$(tail -n 1 "$clocklog")"

{ promptly "$b_given" 3 &&
  [[ "$rc_default" == 3 ]] &&
  [[ "$b_default" =~ ^[0-9]+$ ]] && [[ "$b_default" -le 540 ]]; } && ok \
  || no "exits 3 once a budget with no completion file is spent, and the default budget is at most 540s (given 1s: got '<code> <secs>'=$b_given want '3 <=10'; default: code=$rc_default want 3, gave up at ${b_default:-<no clock reading>}s want <=540)"

SKILL="$HERE/../../SKILL.md"
detacher="detach-leaf.sh"
launches=0 launch_misses=""

missed() { launch_misses="$launch_misses $1"; }

while IFS= read -r hit; do
  launches=$(( launches + 1 ))
  n="${hit%%:*}" text="${hit#*:}"
  [[ "$text" == *"$detacher"* ]] \
    || missed "line$n:no-$detacher"
  grep -q 'wait-leaf\.sh' < <(sed -n "${n},$(( n + 6 ))p" "$SKILL") \
    || missed "line$n:no-foreground-wait"
done < <(grep -n -e '\$S/supervise\.sh' -e '\$S/verify\.sh' "$SKILL" | grep '\.tdd/')

warning="$(awk 'BEGIN { RS = "" }
  tolower($0) ~ /background/ && tolower($0) ~ /notification/ &&
  tolower($0) ~ /print[ -]mode/ { print; exit }' "$SKILL")"

[[ "$launches" -ge 5 ]] || missed "enumeration:only-$launches-launch-sites"
[[ -n "$warning" ]] || missed "warning:no-paragraph-naming-background-notification-print-mode"

[[ -z "$launch_misses" ]] && ok \
  || no "SKILL.md launches every leaf detached and waits for it with wait-leaf.sh in the foreground, and warns that a background call awaiting a notification never completes in print mode (launch sites=$launches, missing:$launch_misses)"

( sleep 0 ) &
dead_pid=$!
wait "$dead_pid"
printf '%s\n' "$dead_pid" > "$work/.tdd/dead-sup.pid"
d_dead="$(timed dead-sup 20)"
d_stderr="$(cat "$work/dead-sup.err")"
{ promptly "$d_dead" 2 &&
  names "$d_stderr" dead-sup "$dead_pid"; } && ok \
  || no "exits 2 well before its budget, naming the leaf and the dead pid on stderr, when the recorded supervisor has exited and no completion file exists (got '<code> <secs>'=$d_dead want '2 <=10'; stderr='$d_stderr' want it to name dead-sup and $dead_pid)"

sleep 60 &
imp_pid=$!
printf '%s\n' "$imp_pid" > "$work/.tdd/reused-sup.pid"
r_reused="$(timed reused-sup 20)"
r_stderr="$(cat "$work/reused-sup.err")"
kill "$imp_pid" 2>/dev/null; wait "$imp_pid" 2>/dev/null
{ promptly "$r_reused" 2 &&
  names "$r_stderr" reused-sup "$imp_pid"; } && ok \
  || no "exits 2 well before its budget when the recorded pid is alive but is not a supervise.sh for that leaf (pid reuse), naming the leaf and the pid on stderr (got '<code> <secs>'=$r_reused want '2 <=10'; stderr='$r_stderr' want it to name reused-sup and $imp_pid)"

stubsup="$work/stubsup"; mkdir -p "$stubsup"
cat > "$stubsup/supervise.sh" <<'S'
#!/bin/sh
while :; do sleep 0.2; done
S
chmod +x "$stubsup/supervise.sh"
"$stubsup/supervise.sh" live-sup x &
live_pid=$!
printf '%s\n' "$live_pid" > "$work/.tdd/live-sup.pid"
l_live="$(timed live-sup 2)"
kill "$live_pid" 2>/dev/null; wait "$live_pid" 2>/dev/null
l_nopid="$(timed no-pid-yet 2)"
{ [[ "${l_live%% *}" == 3 ]] && [[ "${l_live#* }" -ge 2 ]] &&
  [[ "${l_nopid%% *}" == 3 ]] && [[ "${l_nopid#* }" -ge 2 ]]; } && ok \
  || no "still exits 3 once the budget is spent while the recorded supervise.sh for that leaf is alive, and when no pid file exists yet (got '<code> <secs>': live supervisor=$l_live want '3 >=2'; no pid file=$l_nopid want '3 >=2')"

mkdir -p "$stubsup/veri"
cat > "$stubsup/veri/supervise.py" <<'S'
#!/bin/sh
while :; do sleep 0.2; done
S
chmod +x "$stubsup/veri/supervise.py"
"$stubsup/veri/supervise.py" live-py x &
py_pid=$!
printf '%s\n' "$py_pid" > "$work/.tdd/live-py.pid"
p_live="$(timed live-py 0)"
p_stderr="$(cat "$work/live-py.err")"
kill "$py_pid" 2>/dev/null; wait "$py_pid" 2>/dev/null
{ [[ "${p_live%% *}" == 3 ]] && [[ -z "$p_stderr" ]]; } && ok \
  || no "exits 3 at budget 0 while the recorded supervisor for that leaf is alive and spelled veri/supervise.py <name>, with nothing on stderr (got '<code> <secs>'=$p_live want '3 …'; stderr='$p_stderr' want empty)"

racebin="$work/racebin"; mkdir -p "$racebin"
cat > "$racebin/ps" <<'P'
#!/bin/sh
printf '1\n' > .tdd/race-sup.exit
exit 1
P
chmod +x "$racebin/ps"
printf '%s\n' "$dead_pid" > "$work/.tdd/race-sup.pid"
x_race="$(timed race-sup 20 PATH="$racebin:$clockbin:$PATH")"
promptly "$x_race" 1 && ok \
  || no "returns the recorded code when the completion file lands just before the supervisor exits, not the dead-supervisor 2 (got '<code> <secs>'=$x_race want '1 <=10')"

printf '%s\n' "$dead_pid" > "$work/.tdd/verdict-red.pid"
v_dead="$(timed verdict-red 20)"
v_stderr="$(cat "$work/verdict-red.err")"

verdict_para="$(awk 'BEGIN { RS = "" }
  /verdict-<phase>/ && tolower($0) ~ /killed-stuck/ && tolower($0) ~ /bail/ &&
  (tolower($0) ~ /without recording a status/ ||
   tolower($0) ~ /supervisor[^.]*(died|dies|exited|is gone)/) { print; exit }' "$SKILL")"

{ promptly "$v_dead" 2 && names "$v_stderr" verdict-red &&
  [[ -n "$verdict_para" ]]; } && ok \
  || no "a verifier wait whose supervisor died exits 2 well before its budget, and SKILL.md reports that 2 the way it reports a killed developer leaf (got '<code> <secs>'=$v_dead want '2 <=10'; stderr='$v_stderr' want it to name verdict-red; SKILL.md paragraph naming verdict-<phase>, a supervisor that died without recording a status, killed-stuck and the bail: ${verdict_para:-<none>})"

empty="$work/empty"; mkdir -p "$empty"
( cd "$empty" && "$WAIT" "" >"$empty/out" 2>"$empty/err" )
rc_empty=$?
printf 'usage: wait-leaf.sh <name> [max-seconds]\n' > "$empty/want"
{ [[ "$rc_empty" == 2 ]] && [[ ! -s "$empty/out" ]] && cmp -s "$empty/want" "$empty/err"; } && ok \
  || no "refuses an empty first argument with exit 2, nothing on stdout and exactly the usage line on stderr (got exit $rc_empty want 2; stdout='$(cat "$empty/out")' want empty; stderr='$(cat "$empty/err")' want 'usage: wait-leaf.sh <name> [max-seconds]')"

linked="$work/linked"; mkdir -p "$linked"
ln -s "$(cd "$HERE/.." && pwd)" "$linked/scripts"
caller="$work/caller"; mkdir -p "$caller/.tdd"
printf '1\n' > "$caller/.tdd/via-link.exit"
( cd "$caller" && env VERI_POLL=0 "$linked/scripts/wait-leaf.sh" via-link 0 >/dev/null 2>"$caller/err" )
rc_link=$?
{ [[ ! -e "$linked/scripts/.tdd/via-link.exit" ]] && [[ "$rc_link" == 1 ]]; } && ok \
  || no "wait-leaf.sh run through a symlink to the scripts directory reads the working directory's .tdd/<name>.exit, never one beside the skill, and answers a recorded 1 as 1 (got exit $rc_link want 1; stderr='$(cat "$caller/err")')"

finish

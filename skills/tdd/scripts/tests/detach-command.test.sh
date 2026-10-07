#!/usr/bin/env bash
# Tests for scripts/detach-command.sh — the conductor's detach-then-wait helper for a long
# command such as the baseline or full-suite `make test`.
#
# Contract under test:
#   detach-command.sh start <name> <cmd> [args…]  → returns at once; the command runs in a
#                                                   session of its own and its exit code is
#                                                   written to .tdd/<name>.exit when it ends
#   detach-command.sh wait <name> [max-seconds]   → the recorded code, or 3 after max-seconds
#                                                   with no completion file (call again), or
#                                                   2 when the command died recording nothing
#
# Run: scripts/tests/detach-command.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HELPER="$HERE/../detach-command.sh"

source "$HERE/lib/harness.sh"

work="$(scratch_dir)"
mkdir -p "$work/.tdd"

GO="$work/go"
BLOCKER="$work/blocker.sh"
cat > "$BLOCKER" <<'B'
#!/bin/sh
i=0
while [ ! -e "$1" ] && [ "$i" -lt 100 ]; do i=$((i + 1)); sleep 0.1; done
exit "$2"
B
chmod +x "$BLOCKER"

KILLER="$work/killer.sh"
cat > "$KILLER" <<'K'
#!/bin/sh
kill -9 "$PPID"
K
chmod +x "$KILLER"

helper() { ( cd "$work" && VERI_POLL=0.05 "$HELPER" "$@" >/dev/null 2>&1 ); }

problems=()

helper start ran "$BLOCKER" "$GO" 7
rc=$?
[[ "$rc" == 0 ]] || problems+=("start returned $rc while the command was still running; want 0")

helper wait ran 0
rc=$?
[[ "$rc" == 3 ]] || problems+=("wait on a running command returned $rc with no completion file; want 3")

: > "$GO"
helper wait ran 30
rc=$?
[[ "$rc" == 1 ]] || problems+=("wait on a command that exited 7 returned $rc; want 1")

helper start died "$KILLER"
helper wait died 30
rc=$?
[[ "$rc" == 2 ]] || problems+=("wait on a command killed before recording a code returned $rc; want 2")

report "detach-command: #601 start returns at once, wait gives the recorded code, 3 while running, 2 for a death"

problems=()

helper start red "$BLOCKER" "$GO" 2
out="$(cd "$work" && VERI_POLL=0.05 "$HELPER" wait red 30 2>/dev/null)"
rc=$?
[[ "$rc" == 1 ]] || problems+=("wait on a command that recorded 2 (make's code for a failed recipe) returned $rc; want 1")
[[ "$out" == 2 ]] || problems+=("wait on a command that recorded 2 printed '$out' on stdout; want the recorded code 2")

report "detach-command: #601 wait exits 1, printing the recorded code, for a command that finished non-zero"

PIPE_SCRIPT="$work/pipe-writer.sh"
PIPE_STATUS="$work/pipe-writer.status"
PIPE_ERR="$work/pipe-writer.err"
cat > "$PIPE_SCRIPT" <<'P'
exec 2> "$2"
s="$(printf '%070000d' 0)"
printf '%s\n' x "$s" "$s" "$s" "$s" "$s" | { IFS= read -r _; }
printf '%s\n' "${PIPESTATUS[0]}" > "$1"
P

problems=()

helper start pipe bash "$PIPE_SCRIPT" "$PIPE_STATUS" "$PIPE_ERR"
helper wait pipe 30
if [[ -f "$PIPE_STATUS" ]]; then
  [[ "$(cat "$PIPE_STATUS")" == 141 ]] ||
    problems+=("want the writer killed by SIGPIPE (status 141), got status: $(cat "$PIPE_STATUS")")
  [[ ! -s "$PIPE_ERR" ]] ||
    problems+=("want nothing on the writer's stderr, got: $(cat "$PIPE_ERR")")
else
  problems+=("the command started through detach-command.sh never wrote $PIPE_STATUS")
fi

report "detach-command: #622 a writer whose reader closes early dies of SIGPIPE silently, as it does from a shell"

problems=()

helper start whole sh -c 'echo "sid $(python3 -c "import os; print(os.getsid(0))")"; echo out-line'
helper wait whole 30
rc=$?
[[ "$rc" == 0 ]] || problems+=("wait on a command that exited 0 returned $rc; want 0")
[[ "$(cat "$work/.tdd/whole.exit" 2>/dev/null)" == 0 ]] ||
  problems+=("want .tdd/whole.exit to hold 0, got: $(cat "$work/.tdd/whole.exit" 2>&1)")
grep -Fx out-line "$work/.tdd/whole.out" > /dev/null ||
  problems+=("want the command's output in .tdd/whole.out, got: $(cat "$work/.tdd/whole.out" 2>&1)")
sid="$(sed -n 's/^sid //p' "$work/.tdd/whole.out" 2>/dev/null)"
[[ -n "$sid" && "$sid" == "$(cat "$work/.tdd/whole.pid" 2>/dev/null)" ]] ||
  problems+=("want the command in a session led by the started pid $(cat "$work/.tdd/whole.pid" 2>&1), got session: '$sid'")

report "detach-command: #622 start still runs its command in a session of its own, records .exit and .out, and wait exits 0 for a clean finish"

problems=()

WORD_GO="$work/word-go"
helper start word "$BLOCKER" "$WORD_GO" 0
out="$(cd "$work" && VERI_POLL=0.05 "$HELPER" wait word abc 2>"$work/word.err")"
rc=$?
: > "$WORD_GO"
[[ "$rc" == 2 ]] || problems+=("wait word abc on a running command returned $rc; want 2")
[[ -z "$out" ]] || problems+=("wait word abc printed '$out' on stdout; want nothing")
[[ "$(cat "$work/word.err")" == "usage: detach-command.sh start <name> <cmd> [args…] | wait <name> [max-seconds]" ]] ||
  problems+=("wait word abc printed '$(cat "$work/word.err")' on stderr; want the usage line")

report "detach-command: #964 wait refuses a max-seconds that is a word with exit 2 and the usage line while the command runs"

problems=()

printf '0\n' > "$work/.tdd/fin.exit"
out="$(cd "$work" && VERI_POLL=0.05 "$HELPER" wait fin abc 2>"$work/fin.err")"
rc=$?
[[ "$rc" == 2 ]] || problems+=("wait fin abc with .tdd/fin.exit holding 0 returned $rc; want 2")
[[ -z "$out" ]] || problems+=("wait fin abc printed '$out' on stdout; want nothing")
[[ "$(cat "$work/fin.err")" == "usage: detach-command.sh start <name> <cmd> [args…] | wait <name> [max-seconds]" ]] ||
  problems+=("wait fin abc printed '$(cat "$work/fin.err")' on stderr; want the usage line")

report "detach-command: #964 wait refuses a max-seconds that is a word with exit 2 and the usage line when the exit file already holds 0"

problems=()

out="$(cd "$work" && "$HELPER" bogus x 2>"$work/bogus.err")"
rc=$?
[[ "$rc" == 2 ]] || problems+=("bogus x returned $rc; want 2")
[[ -z "$out" ]] || problems+=("bogus x printed '$out' on stdout; want nothing")
[[ "$(cat "$work/bogus.err")" == "usage: detach-command.sh start <name> <cmd> [args…] | wait <name> [max-seconds]" ]] ||
  problems+=("bogus x printed '$(cat "$work/bogus.err")' on stderr; want exactly the usage line")

report "detach-command: a mode other than start or wait exits 2 with exactly the usage line on stderr and nothing on stdout"

finish

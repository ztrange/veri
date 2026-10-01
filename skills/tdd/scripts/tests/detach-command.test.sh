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

finish

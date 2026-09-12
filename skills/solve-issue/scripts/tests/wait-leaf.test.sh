#!/usr/bin/env bash
# Tests for scripts/wait-leaf.sh — the foreground half of a detached leaf launch (#86).
#
# A print-mode conductor (`claude -p "/solve-issue <n>"`) never receives background-task
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

# waited <name> <code> — spawn a writer that records <code> in the completion file
# .tdd/<name>.exit two seconds from now, then wait for <name> in the foreground with a
# 20-second budget. Echoes "<wait-leaf's exit code> <seconds the wait took>".
#
# The two numbers are what the case needs: the code proves the recorded status is passed
# through, and the elapsed time tells "returned when the file appeared" from "sat out the
# whole budget and then read it" — both end in the same exit code otherwise.
#
# VERI_POLL is pinned rather than inherited (see hermetic-suites.test.sh): an ambient poll
# interval of minutes would make the elapsed time a fact about the caller's environment.
waited() {
  local name="$1" code="$2" t0 rc
  ( sleep 2; printf '%s\n' "$code" > "$work/.tdd/$name.exit" ) &
  t0="$(date +%s)"
  ( cd "$work" && env VERI_POLL=0.2 "$WAIT" "$name" 20 >/dev/null 2>&1 )
  rc=$?
  printf '%s %s\n' "$rc" "$(( $(date +%s) - t0 ))"
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

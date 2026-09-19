#!/usr/bin/env bash
# RED (#12): supervise.sh should RETRY a killed-stuck leaf before giving up.
#
# New tunable VERI_STUCK_RETRIES (default 1) caps the extra attempts after the first.
# A leaf that hangs once but succeeds on a fresh attempt must be recovered.
#
# THE acceptance criterion pinned here (exactly one test):
#   A leaf killed-stuck on its FIRST attempt but that SUCCEEDS on the NEXT attempt
#   returns success (exit 0), under the DEFAULT budget of 1 retry.
#
# Status contract (unchanged): exit 0 success · 1 leaf-failure · 2 killed-stuck.
#
# This FAILS today: supervise.sh runs the leaf once and reports killed-stuck (exit 2)
# instead of retrying onto the successful second attempt (exit 0).
#
# Driven on the INJECTED CLOCK supervise.test.sh introduced (commit 500b644, "The injected
# clock" in that file): the leaf jumps the clock past its heartbeat window instead of
# sleeping through it in real time, so this case's wall time is the fork/poll overhead
# rather than the window itself. Before that port this case ran a real `sleep 60` under a
# real one-second heartbeat and a 0.2s real poll — the leaf was always killed within about a
# second, so the case cost ~1s of real time rather than the full 60s, but that second was
# still wall clock spent watching nothing happen.
#
# The rig is duplicated here rather than shared with supervise.test.sh (CLAUDE.md: "supervise.sh
# has a second suite for its retry axis" — kept separate on purpose) — a shared helper would
# couple two suites that assert different axes of the same script.
#
# Run: scripts/tests/supervise-retry.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SUP="$HERE/../supervise.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

stub="$(mktemp -d)"
work="$(mktemp -d)"
trap 'rm -rf "$stub" "$work"' EXIT

# flaky leaf: hangs (silent) the FIRST time it runs, succeeds the SECOND time.
#   first run  → drop a marker, jump the clock past the heartbeat window, then sleep so the
#                supervisor's poll loop — reading the injected clock, not real time — is what
#                notices the silence
#   later runs → see the marker, print the success line, exit 0 right away
# The marker lives in cwd ($work), which the supervisor preserves across attempts.
cat > "$stub/leaf-flaky" <<'L'
#!/bin/sh
if [ -e .retry-marker ]; then
  echo "leaf: recovered on retry"; exit 0
fi
echo "leaf: starting"; : > .retry-marker; clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"; sleep 60; echo "unreachable"
L
chmod +x "$stub"/leaf-*

# The injected clock, ported from supervise.test.sh's rig (see that file's header for the full
# explanation). supervise.sh reads time two ways, both resolved on PATH: `date +%s` for now,
# and `stat` for the leaf's log mtime (the heartbeat sensor). `clock-jump <s>` advances both by
# appending `<real time> <offset>` to ./.test-clock, so a hanging leaf can jump straight past
# its window instead of waiting it out for real. This case's leaf never needs `await-poll` —
# unlike supervise.test.sh's leaf-slow/leaf-runaway, it jumps once and then goes silent — so
# that helper is left out.
realdate="$(command -v date)"
realstat="$(command -v stat)"
cat > "$stub/date" <<D
#!/bin/sh
if [ "\$*" = "+%s" ]; then
  offset="\$(tail -n 1 .test-clock 2>/dev/null | cut -d' ' -f2)"
  printf '%s\n' "\$(( \$("$realdate" +%s) + \${offset:-0} ))"
else
  exec "$realdate" "\$@"
fi
D
cat > "$stub/stat" <<D
#!/bin/sh
if [ "\$#" -eq 3 ]; then
  if [ "\$1 \$2" = "-c %Y" ] || [ "\$1 \$2" = "-f %m" ]; then
    exec python3 -c '
import os, sys
try:
    m = os.stat(sys.argv[1]).st_mtime
except OSError:
    sys.exit(1)
offset = 0
try:
    for line in open(".test-clock"):
        at, value = line.split()
        if float(at) <= m:
            offset = int(value)
except OSError:
    pass
print(int(m) + offset)' "\$3"
  fi
fi
exec "$realstat" "\$@"
D
cat > "$stub/clock-jump" <<'C'
#!/bin/sh
exec python3 -c '
import sys, time
offset = 0
try:
    offset = int(open(".test-clock").read().split()[-1])
except (OSError, IndexError):
    pass
with open(".test-clock", "a") as f:
    f.write("%r %d\n" % (time.time(), offset + int(sys.argv[1])))' "$1"
C
chmod +x "$stub/date" "$stub/stat" "$stub/clock-jump"
export PATH="$stub:$PATH"

# Drive it through the supervisor with a tight heartbeat window and the DEFAULT retry
# budget: `env -u VERI_STUCK_RETRIES` clears the variable for the child, so the default of
# 1 must suffice and a value exported by the shell that ran `make test` cannot change the
# answer. VERI_POLL=0.02 is a real interval still (the supervisor's poll loop sleeps for
# real between clock reads), kept small so the handful of polls this case needs cost
# milliseconds rather than the 0.2s the pre-clock version paid per poll.
out="$( cd "$work" && env -u VERI_STUCK_RETRIES VERI_HEARTBEAT=1 VERI_TIMEOUT=30 VERI_POLL=0.02 \
          "$SUP" flaky "$stub/leaf-flaky" 2>"$work/err" )"
code=$?

# Acceptance: recovered on the retry → success (exit 0) with the success path captured.
{ [[ "$code" == 0 ]] && [[ "$out" == *'recovered on retry'* ]]; } && ok \
  || no "killed-stuck-then-succeeds leaf is retried → success (code=$code, err=$(cat "$work/err"))"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

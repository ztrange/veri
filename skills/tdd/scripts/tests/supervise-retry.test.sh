#!/usr/bin/env bash
# Tests for scripts/supervise.sh's retry axis: VERI_STUCK_RETRIES (default 1) caps the
# extra attempts after a killed-stuck first one.
#
# Contract under test:
#   A leaf killed-stuck on its first attempt but that succeeds on the next attempt
#   returns success (exit 0), under the default budget of 1 retry.
#   exit 0 success · 1 leaf-failure · 2 killed-stuck.
#
# Run: scripts/tests/supervise-retry.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SUP="$HERE/../supervise.sh"
source "$HERE/lib/harness.sh"

stub="$(scratch_dir)"
work="$(scratch_dir)"

cat > "$stub/leaf-flaky" <<'L'
#!/bin/sh
if [ -e .retry-marker ]; then
  echo "leaf: recovered on retry"; exit 0
fi
echo "leaf: starting"; : > .retry-marker; clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"; sleep 60; echo "unreachable"
L
chmod +x "$stub"/leaf-*

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

out="$( cd "$work" && env -u VERI_STUCK_RETRIES VERI_HEARTBEAT=1 VERI_TIMEOUT=30 VERI_POLL=0.02 \
          VERI_KILL_POLL=0.01 "$SUP" flaky "$stub/leaf-flaky" 2>"$work/err" )"
code=$?

{ [[ "$code" == 0 ]] && [[ "$out" == *'recovered on retry'* ]]; } && ok \
  || no "killed-stuck-then-succeeds leaf is retried → success (code=$code, err=$(cat "$work/err"))"

finish

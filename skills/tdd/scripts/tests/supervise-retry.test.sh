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
#   first run  → drop a marker, then sleep silently so the heartbeat window kills it
#   later runs → see the marker, print the success line, exit 0 right away
# The marker lives in cwd ($work), which the supervisor preserves across attempts.
cat > "$stub/leaf-flaky" <<'L'
#!/usr/bin/env bash
if [[ -e .retry-marker ]]; then
  echo "leaf: recovered on retry"; exit 0
fi
echo "leaf: starting"; : > .retry-marker; sleep 60; echo "unreachable"
L
chmod +x "$stub"/leaf-*

# Drive it through the supervisor with a tight heartbeat window and the DEFAULT retry
# budget: `env -u VERI_STUCK_RETRIES` clears the variable for the child, so the default of
# 1 must suffice and a value exported by the shell that ran `make test` cannot change the
# answer.
out="$( cd "$work" && env -u VERI_STUCK_RETRIES VERI_HEARTBEAT=1 VERI_TIMEOUT=30 VERI_POLL=0.2 \
          "$SUP" flaky "$stub/leaf-flaky" 2>"$work/err" )"
code=$?

# Acceptance: recovered on the retry → success (exit 0) with the success path captured.
{ [[ "$code" == 0 ]] && [[ "$out" == *'recovered on retry'* ]]; } && ok \
  || no "killed-stuck-then-succeeds leaf is retried → success (code=$code, err=$(cat "$work/err"))"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

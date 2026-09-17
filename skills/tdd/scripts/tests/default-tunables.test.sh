#!/usr/bin/env bash
# Tests for the PRODUCTION side of the supervision tunables — the half of issue #282 that must
# not move while the suites move onto a sub-second clock. Three scripts read a window or a
# budget from the environment (`supervise.sh`, `wait-leaf.sh`, `verify.sh`), and the speed work
# is only allowed to change what a SUITE pays: a run with nothing set still waits the
# documented defaults, and a value that is not a number is still refused with exit 2 rather
# than silently disabling the thing it configures.
#
# Cross-script by subject, so it belongs to no one script's suite — the shape
# hermetic-suites.test.sh already has. Zero-dependency plain-shell asserts, same idiom.
#
# Run: scripts/tests/default-tunables.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$HERE/.."
SUP="$SCRIPTS/supervise.sh"
WAIT="$SCRIPTS/wait-leaf.sh"
VERIFY="$SCRIPTS/verify.sh"
pass=0 fail=0

stub="$(mktemp -d)"
work="$(mktemp -d)"
trap 'rm -rf "$stub" "$work"' EXIT

# The leaf every supervised probe runs: one line of progress, then ~0.3s of life, then a clean
# exit. It has to outlive at least one turn of the watch loop — a leaf that exits before the
# first poll is never measured against any window at all, and a probe on it would answer about
# the launch rather than about the tunable. The wait is python3's rather than `sleep`'s because
# `sleep` is stubbed below and the leaf inherits that PATH.
cat > "$stub/leaf-brief" <<'L'
#!/usr/bin/env bash
echo "leaf: starting"
python3 -c 'import time; time.sleep(0.3)'
echo "leaf: done"
L

# The poll SENSOR: a `sleep` first on PATH that records the interval it was asked for and then
# waits a compressed 0.02s instead of it. The interval is what the default under test is — the
# grid a script polls on — and recording it is what lets this suite assert a whole-second
# default without paying a whole second per probe, which is the very waste #282 is about. The
# real `sleep` path is baked in at generation time because this stub sits on PATH as `sleep`
# itself and would otherwise re-exec into itself forever.
realsleep="$(command -v sleep)"
cat > "$stub/sleep" <<S
#!/usr/bin/env bash
printf '%s\n' "\$*" >> "\${SLEEP_LOG:-/dev/null}"
exec "$realsleep" 0.02
S
chmod +x "$stub/leaf-brief" "$stub/sleep"

# intervals <log> — the distinct intervals recorded in a sleep log, comma-joined, or a
# diagnostic when nothing was recorded at all. Distinct rather than every line, because the
# number of polls a probe happens to take is not the thing under test and would make the
# expected value depend on how loaded the box is; "nothing recorded" is reported rather than
# read as agreement, since a probe that never polled pins no grid.
intervals() {
  local joined
  joined="$(sort -u "$1" 2>/dev/null | tr '\n' ',')"
  printf '%s\n' "${joined:-<no-sleep-recorded>}"
}

# sup_code <dir> <env setting…> — supervise the brief leaf in a run directory of its own and
# echo supervise.sh's exit code. The settings are forwarded to `env` verbatim, so `-u NAME` and
# `NAME=value` both reach it as themselves. VERI_STUCK_RETRIES=0 is pinned, not inherited: a
# caller's environment must not be able to add a second attempt to a probe about one.
sup_code() {
  local dir="$1"; shift
  mkdir -p "$work/$dir"
  ( cd "$work/$dir" && env "$@" VERI_STUCK_RETRIES=0 "$SUP" probe "$stub/leaf-brief" \
      >/dev/null 2>"$work/$dir.err" )
  printf '%s\n' "$?"
}

# 1. With nothing set, the two polling scripts still poll on a whole second, and a tunable
#    value that is not a number is still refused with exit 2 by all three scripts that read one
#    (#282 criterion 4). The suites are free to run these windows in tens of milliseconds; a
#    production run is not, and the difference between the two is what this case pins.
#
#    Seven probes, one case, because the criterion is the conjunction: a change that made the
#    default fractional would pass the refusal probes, and one that dropped the refusals would
#    pass the default ones. They collect into `problems` and are reported together, the shape
#    hermetic-suites.test.sh uses, so one run says everything that moved rather than the first
#    thing.
#
#    * the poll grid (supervise.sh, wait-leaf.sh) is read off the `sleep` stub above: the
#      interval each asks for with VERI_POLL unset must be exactly `1`.
#    * the 180s silence window is NOT re-asserted here — supervise.test.sh case 11 asks the
#      running supervisor for it under an injected clock, and a second copy of that probe would
#      be a second place to fix.
#    * the refusals name a value that is a word (`abc`), the shape that makes `set -u` read it
#      as a variable name inside `(( ))` and kill the script with whatever status the previous
#      command left — which is not 2, and is routinely 0, the failure this criterion excludes.
#      Each of supervise.sh's three windows is probed, because a check written for one of them
#      says nothing about the other two.
#    * verify.sh's own tunable is VERI_NO_VERDICT_RETRIES (verify.sh:167); it reads none of the
#      three window names, so its default heartbeat and poll ARE supervise.sh's, and that is
#      probed rather than assumed — a default added there later owes an arm here.
name="with no tunables set the supervision scripts keep their production defaults, and a malformed tunable value is refused with exit 2"
problems=()

# supervise.sh's poll grid, with all three windows cleared for the child.
sup_poll_code="$(sup_code poll-sup -u VERI_POLL -u VERI_HEARTBEAT -u VERI_TIMEOUT \
  PATH="$stub:$PATH" SLEEP_LOG="$work/sleep-sup.log")"
sup_poll_grid="$(intervals "$work/sleep-sup.log")"
[[ "$sup_poll_code" == 0 ]] ||
  problems+=("supervise.sh with no tunables set did not supervise the brief leaf cleanly: want exit 0, got $sup_poll_code ($(cat "$work/poll-sup.err" 2>/dev/null))")
[[ "$sup_poll_grid" == '1,' ]] ||
  problems+=("supervise.sh with VERI_POLL unset polls on intervals '$sup_poll_grid', want '1,' — the documented whole-second default")

# wait-leaf.sh's poll grid: the completion file lands ~0.3s in, so the wait turns the loop a few
# times before it answers, and each turn records the interval it asked for.
mkdir -p "$work/poll-wait/.tdd"
( python3 -c 'import time; time.sleep(0.3)'
  printf '1\n' > "$work/poll-wait/.tdd/probe.exit" ) &
( cd "$work/poll-wait" && env -u VERI_POLL PATH="$stub:$PATH" SLEEP_LOG="$work/sleep-wait.log" \
    "$WAIT" probe 20 >/dev/null 2>&1 )
wait_poll_code=$?
wait
wait_poll_grid="$(intervals "$work/sleep-wait.log")"
[[ "$wait_poll_code" == 1 ]] ||
  problems+=("wait-leaf.sh with no tunables set did not return the recorded code: want exit 1, got $wait_poll_code")
[[ "$wait_poll_grid" == '1,' ]] ||
  problems+=("wait-leaf.sh with VERI_POLL unset polls on intervals '$wait_poll_grid', want '1,' — the documented whole-second default")

# The refusals. Every window but the malformed one is given a small number, so a probe that
# reaches the watch loop at all is bounded by that rather than by a default of minutes.
bad_hb="$(sup_code bad-hb   VERI_HEARTBEAT=abc VERI_TIMEOUT=3   VERI_POLL=0.05)"
bad_to="$(sup_code bad-to   VERI_HEARTBEAT=3   VERI_TIMEOUT=abc VERI_POLL=0.05)"
bad_poll="$(sup_code bad-poll VERI_HEARTBEAT=3 VERI_TIMEOUT=3   VERI_POLL=abc)"
[[ "$bad_hb" == 2 ]] ||
  problems+=("supervise.sh with VERI_HEARTBEAT=abc: want exit 2, got $bad_hb")
[[ "$bad_to" == 2 ]] ||
  problems+=("supervise.sh with VERI_TIMEOUT=abc: want exit 2, got $bad_to")
[[ "$bad_poll" == 2 ]] ||
  problems+=("supervise.sh with VERI_POLL=abc: want exit 2, got $bad_poll")

# wait-leaf.sh, asked to wait in a directory with no completion file at all and a one-second
# budget: a refusal is exit 2, and the budget is what bounds the probe if there is none.
( cd "$work" && env VERI_POLL=abc "$WAIT" absent 1 >/dev/null 2>&1 )
bad_wait=$?
[[ "$bad_wait" == 2 ]] ||
  problems+=("wait-leaf.sh with VERI_POLL=abc: want exit 2, got $bad_wait")

# verify.sh's own budget, refused before any leaf is launched (verify.sh:167-172), and the
# absence of a window default of its own.
printf 'slugify must lowercase the title and join words with hyphens.' > "$work/spec.md"
( cd "$work" && env VERI_NO_VERDICT_RETRIES=abc "$VERIFY" green "$work/spec.md" \
    tests/test_slugify.py test_lowercases >/dev/null 2>&1 )
bad_verify=$?
[[ "$bad_verify" == 2 ]] ||
  problems+=("verify.sh with VERI_NO_VERDICT_RETRIES=abc: want exit 2, got $bad_verify")
for window in VERI_HEARTBEAT VERI_TIMEOUT VERI_POLL; do
  grep -q "\${$window" "$VERIFY" &&
    problems+=("verify.sh reads \${$window…} itself, so it now has a window default of its own and owes a probe here")
done

if [[ "${#problems[@]}" -eq 0 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name"
  printf '    %s\n' "${problems[@]}"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

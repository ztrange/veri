#!/usr/bin/env bash
# Tests for scripts/orchestrate.sh — the loop above the conductor: it asks
# solvable-issues.sh which issues veri may take, launches one conductor per issue through
# run-conductor.sh, and stops once nothing is left to take.
#
# Contract under test:
#   orchestrate.sh  → one run-conductor.sh launch per solvable issue; exit 0 once
#                     solvable-issues.sh exits 3; exit 2, launching nothing, when it exits
#                     other than 0 or 3.
#   VERI_CONDUCTOR_CTX_BUDGET (default 120000, a whole number or exit 2)
#                   → a conductor whose context crosses it is stopped after its next step-done
#                     result and relaunched for the same issue with the same argv.
#   A conductor exiting 0 with an unchecked ledger step is relaunched; one that wrote
#   `.tdd/parked/<n>.md` is recorded as parked and the next solvable issue is taken.
#
# Run: scripts/tests/orchestrate.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

scripts="$work/scripts"
mkdir -p "$scripts"
cp "$HERE/../orchestrate.sh" "$scripts/orchestrate.sh" 2>/dev/null
cp -R "$HERE/../lib" "$HERE/../veri" "$scripts/"

cat > "$scripts/solvable-issues.sh" <<'STUB'
#!/bin/sh
calls=$(($(cat "$SOLVABLE.calls" 2>/dev/null || echo 0) + 1))
echo "$calls" > "$SOLVABLE.calls"
[ "$calls" -le 20 ] || exit 3
[ -s "$SOLVABLE" ] || exit 3
cat "$SOLVABLE"
STUB

cat > "$scripts/run-conductor.sh" <<'STUB'
#!/bin/sh
echo "$1" >> "$LAUNCHES"
grep -vx -- "$1" "$SOLVABLE" > "$SOLVABLE.next"
mv "$SOLVABLE.next" "$SOLVABLE"
STUB
chmod +x "$scripts"/*.sh

orchestrate() {
  (cd "$work" && "$1/orchestrate.sh") < /dev/null > "$work/out" 2> "$work/err"
  rc=$?
}

scratch_skill() {
  mkdir -p "$1"
  cp "$scripts/orchestrate.sh" "$scripts/solvable-issues.sh" "$1/"
  cp -R "$scripts/lib" "$scripts/veri" "$1/"
}

conductor_stub() {
  scratch_skill "$1"
  {
    printf '#!/bin/sh\n"%s/run-conductor.sh" "$1"\n' "$scripts"
    cat <<PRELUDE
# A stopped conductor must be stopped by a signal, not by its writes failing, so this stub
# IGNORES SIGPIPE — the state CI's Linux was observed in, where a write to the closed stream
# came back as plain \`echo: I/O error\` and the conductor ran on. On this Mac SIGPIPE is fatal
# and would end the stub whatever orchestrate.sh did, so without this line the cases below
# cannot go red here at all, and the regression they exist for is only visible on CI. This is
# a stub imitating a platform, not a suite repairing its own pipeline (#422).
trap '' PIPE
echo \$\$ >> "\$MARKS.pid"
heartbeats() {
  i=0
  while [ \$i -lt \$1 ]; do echo '{"type":"system","subtype":"heartbeat"}'; i=\$((i + 1)); sleep 0.01; done
}
await_context() {
  i=0
  while [ \$i -lt 200 ] && ! grep -Fx "\$1" "$work/out" > /dev/null; do i=\$((i + 1)); sleep 0.01; done
}
PRELUDE
    cat
  } > "$1/run-conductor.sh"
  chmod +x "$1"/*.sh
}

await_gone() {
  local i=0 pid alive=1
  [[ -r "$MARKS.pid" ]] || return 0
  while [[ $i -lt 400 && $alive -eq 1 ]]; do
    alive=0
    while read -r pid; do kill -0 "$pid" 2>/dev/null && alive=1; done < "$MARKS.pid"
    [[ $alive -eq 1 ]] || break
    sleep 0.01
    i=$((i + 1))
  done
}

seed() {
  export SOLVABLE="$work/solvable-$1" LAUNCHES="$work/launches-$1" MARKS="$work/marks-$1"
  shift
  printf '%s\n' "$@" > "$SOLVABLE"
  : > "$LAUNCHES"
  : > "$MARKS"
}

expect_exit0_output() {
  if [[ "$rc" -eq 0 && "$actual" == "$expected" ]]; then
    ok
  else
    no "$name"
    echo "    exit: $rc (expected 0)"
    diff <(printf '%s\n' "$expected") <(printf '%s\n' "$actual") | sed 's/^/    /'
    sed 's/^/    stderr: /' "$work/err"
  fi
}

echo
finish

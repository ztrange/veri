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

name="run through a symlink to its scripts directory from another working directory, launches that directory's run-conductor.sh, asks its solvable-issues.sh and reads .tdd/parked/ in the working directory"
realskill="$work/realskill"
mkdir -p "$realskill/.tdd/parked" "$work/elsewhere/.tdd/parked"
cp "$scripts/orchestrate.sh" "$realskill/"
cp -R "$scripts/lib" "$scripts/veri" "$realskill/"
{ printf '#!/bin/sh\necho "solvable-issues.sh linked" >> "$MARKS"\n'; tail -n +2 "$scripts/solvable-issues.sh"; } > "$realskill/solvable-issues.sh"
{ printf '#!/bin/sh\necho "run-conductor.sh linked $1" >> "$MARKS"\n'; tail -n +2 "$scripts/run-conductor.sh"; } > "$realskill/run-conductor.sh"
chmod +x "$realskill"/*.sh
ln -s "$realskill" "$work/link"
: > "$work/elsewhere/.tdd/parked/1401.md"
: > "$realskill/.tdd/parked/1402.md"
seed symlinked 1401 1402
(cd "$work/elsewhere" && "$work/link/orchestrate.sh") < /dev/null > "$work/out" 2> "$work/err"
rc=$?
expected="$(printf '%s\n' 'solvable-issues.sh linked' 'run-conductor.sh linked 1402' 'solvable-issues.sh linked' 1402)"
actual="$(cat "$MARKS" "$LAUNCHES" "$work/out")"
expect_exit0_output

name="#1130 with stdout a pipe whose reader has exited, exits 2 with one stderr line saying its stdout is gone and no traceback"
brokenpipe="$work/brokenpipe"
conductor_stub "$brokenpipe" <<STUB
[ "\$(wc -l < "\$LAUNCHES")" -eq 1 ] || exit 0
i=0
while [ \$i -lt 400 ] && { [ ! -s "\$MARKS.reader" ] || kill -0 "\$(cat "\$MARKS.reader")" 2>/dev/null; }; do i=\$((i + 1)); sleep 0.01; done
echo '{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":1000,"output_tokens":40}}}'
STUB
seed brokenpipe 1601
(cd "$work" && "$brokenpipe/orchestrate.sh") < /dev/null 2> "$work/err" | sh -c 'echo $$ > "$1"' sh "$MARKS.reader"
rc=${PIPESTATUS[0]}
await_gone
lines="$(wc -l < "$work/err" | tr -d ' ')"
if [[ "$rc" -eq 2 && "$lines" -eq 1 ]] && grep -F stdout "$work/err" > /dev/null && ! grep -F Traceback "$work/err" > /dev/null; then
  ok
else
  no "$name"
  echo "    exit: $rc (expected 2)"
  echo "    stderr lines: $lines (expected 1, naming stdout, no Traceback)"
  sed 's/^/    stderr: /' "$work/err"
fi

name="#1130 with stdout closed, exits 2 with the same one stderr line saying its stdout is gone and no traceback"
closedgone="$work/closedgone"
conductor_stub "$closedgone" <<STUB
[ "\$(wc -l < "\$LAUNCHES")" -eq 1 ] || exit 0
echo '{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":1000,"output_tokens":40}}}'
STUB
seed closedgone 1701
(cd "$work" && "$closedgone/orchestrate.sh") < /dev/null >&- 2> "$work/err"
rc=$?
await_gone
lines="$(wc -l < "$work/err" | tr -d ' ')"
if [[ "$rc" -eq 2 && "$lines" -eq 1 ]] && grep -F 'stdout is gone' "$work/err" > /dev/null && ! grep -F Traceback "$work/err" > /dev/null; then
  ok
else
  no "$name"
  echo "    exit: $rc (expected 2)"
  echo "    stderr lines: $lines (expected 1, naming \"stdout is gone\", no Traceback)"
  sed 's/^/    stderr: /' "$work/err"
fi

name="#1130 with stdout a pipe whose reader has exited, or closed, SIGTERMs its conductor's process group before it exits"
stopgroup="$work/stopgroup"
conductor_stub "$stopgroup" <<STUB
[ "\$(wc -l < "\$LAUNCHES")" -eq 1 ] || exit 0
(
  trap 'echo "group TERM" >> "\$MARKS"; exit 0' TERM
  : > "\$MARKS.ready"
  i=0
  while [ \$i -lt 400 ]; do sleep 0.01; i=\$((i + 1)); done
  echo "group never stopped" >> "\$MARKS"
) > /dev/null &
echo \$! >> "\$MARKS.pid"
trap 'echo "conductor TERM" >> "\$MARKS"; exit 0' TERM
i=0
while [ \$i -lt 400 ] && [ ! -e "\$MARKS.ready" ]; do i=\$((i + 1)); sleep 0.01; done
if [ -n "\${READER_GONE:-}" ]; then
  i=0
  while [ \$i -lt 400 ] && { [ ! -s "\$MARKS.reader" ] || kill -0 "\$(cat "\$MARKS.reader")" 2>/dev/null; }; do i=\$((i + 1)); sleep 0.01; done
fi
echo '{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":1000,"output_tokens":40}}}'
i=0
while [ \$i -lt 400 ]; do sleep 0.01; i=\$((i + 1)); done
echo "conductor never stopped" >> "\$MARKS"
STUB
seed stopbroken 1801
(cd "$work" && READER_GONE=1 "$stopgroup/orchestrate.sh") < /dev/null 2> "$work/err" | sh -c 'echo $$ > "$1"' sh "$MARKS.reader"
await_gone
broken="$(sort "$MARKS")"
seed stopclosed 1802
(cd "$work" && "$stopgroup/orchestrate.sh") < /dev/null >&- 2> "$work/err"
await_gone
closed="$(sort "$MARKS")"
expected="$(printf '%s\n' 'conductor TERM' 'group TERM')"
if [[ "$broken" == "$expected" && "$closed" == "$expected" ]]; then
  ok
else
  no "$name"
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$broken") | sed 's/^/    pipe: /'
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$closed") | sed 's/^/    closed: /'
fi

name="#1130 with stdout a pipe whose reader has exited, or closed, asks solvable-issues.sh no further time after the break"
askedonce="$work/askedonce"
conductor_stub "$askedonce" <<STUB
[ "\$(wc -l < "\$LAUNCHES")" -eq 1 ] || exit 0
if [ -n "\${READER_GONE:-}" ]; then
  i=0
  while [ \$i -lt 400 ] && { [ ! -s "\$MARKS.reader" ] || kill -0 "\$(cat "\$MARKS.reader")" 2>/dev/null; }; do i=\$((i + 1)); sleep 0.01; done
fi
echo '{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":1000,"output_tokens":40}}}'
STUB
seed askedbroken 1901 1902
(cd "$work" && READER_GONE=1 "$askedonce/orchestrate.sh") < /dev/null 2> "$work/err" | sh -c 'echo $$ > "$1"' sh "$MARKS.reader"
await_gone
broken="$(cat "$SOLVABLE.calls" 2>/dev/null)"
seed askedclosed 1903 1904
(cd "$work" && "$askedonce/orchestrate.sh") < /dev/null >&- 2> "$work/err"
await_gone
closed="$(cat "$SOLVABLE.calls" 2>/dev/null)"
if [[ "$broken" == 1 && "$closed" == 1 ]]; then
  ok
else
  no "$name"
  echo "    solvable-issues.sh asked with stdout a gone pipe: $broken (expected 1)"
  echo "    solvable-issues.sh asked with stdout closed: $closed (expected 1)"
fi

echo
finish

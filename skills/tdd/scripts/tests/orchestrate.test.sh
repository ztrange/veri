#!/usr/bin/env bash
# Tests for scripts/orchestrate.sh — the loop above the conductor (issue #217): it asks
# solvable-issues.sh which issues veri may take, launches one conductor per issue through
# run-conductor.sh, and stops once nothing is left to take.
#
# The two scripts it drives are replaced by stubs in a scratch copy of the scripts
# directory, beside the real orchestrate.sh, so no case reaches `gh`, git or a model:
#   - solvable-issues.sh prints the issue numbers left in $SOLVABLE, one per line, and exits
#     3 printing nothing once that file is empty — the real script's "nothing to do".
#   - run-conductor.sh appends the issue it was handed to $LAUNCHES, and takes that issue
#     out of $SOLVABLE, the way a finished run leaves the solvable set.
# A stubbed solvable-issues.sh answers 3 after 20 calls whatever $SOLVABLE holds, so a loop
# that never stops fails its case rather than hanging the suite.
#
# Run: scripts/tests/orchestrate.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
pass=0 fail=0

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

scripts="$work/scripts"
mkdir -p "$scripts"
cp "$HERE/../orchestrate.sh" "$scripts/orchestrate.sh" 2>/dev/null

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

# orchestrate <dir>: run the orchestrate.sh copied into <dir> from the scratch root, with no
# stdin, its stdout and stderr in $work/out and $work/err; sets rc to its exit status.
orchestrate() {
  (cd "$work" && "$1/orchestrate.sh") < /dev/null > "$work/out" 2> "$work/err"
  rc=$?
}

# 1. Every issue the solvable set holds gets one conductor, launched through
#    run-conductor.sh with that issue's number, and the loop exits 0 once the set is empty.
name="launches one conductor per solvable issue through run-conductor.sh and exits 0 on an empty set"
export SOLVABLE="$work/solvable" LAUNCHES="$work/launches"
printf '%s\n' 101 102 > "$SOLVABLE"
: > "$LAUNCHES"
orchestrate "$scripts"
expected="$(printf '%s\n' 101 102)"
actual="$(cat "$LAUNCHES")"
if [[ "$rc" -eq 0 && "$actual" == "$expected" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name"
  echo "    exit: $rc (expected 0)"
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$actual") | sed 's/^/    /'
  sed 's/^/    stderr: /' "$work/err"
fi

# 2. A solvable-issues.sh that exits with anything but 0 or 3 gave no answer about the
#    solvable set, so orchestrate.sh launches nothing and exits 2. The stub here exits 2 on
#    its first call and 3 on every later one, so a loop that ignores the 2 still ends.
name="exits 2 without launching a conductor when solvable-issues.sh exits other than 0 or 3"
broken="$work/broken"
mkdir -p "$broken"
cp "$scripts/orchestrate.sh" "$scripts/run-conductor.sh" "$broken/"
cat > "$broken/solvable-issues.sh" <<'STUB'
#!/bin/sh
calls=$(($(cat "$SOLVABLE.calls" 2>/dev/null || echo 0) + 1))
echo "$calls" > "$SOLVABLE.calls"
[ "$calls" -eq 1 ] && exit 2
exit 3
STUB
chmod +x "$broken"/*.sh
export SOLVABLE="$work/solvable-broken" LAUNCHES="$work/launches-broken"
printf '%s\n' 201 > "$SOLVABLE"
: > "$LAUNCHES"
orchestrate "$broken"
launched="$(wc -l < "$LAUNCHES" | tr -d ' ')"
if [[ "$rc" -eq 2 && "$launched" -eq 0 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name"
  echo "    exit: $rc (expected 2)"
  echo "    launches: $launched (expected 0)"
  sed 's/^/    stderr: /' "$work/err"
fi

echo
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

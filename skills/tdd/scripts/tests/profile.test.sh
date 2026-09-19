#!/usr/bin/env bash
# Unit tests for scripts/profile.sh — what `make profile` runs: every suite it is given,
# under `bash -x` with PS4='+${EPOCHREALTIME} ${LINENO} ', cut into cases at each
# top-level increment of `pass` or `fail`, and a report of the cases whose trace time is
# at or above VERI_PROFILE_THRESHOLD (seconds, default 1), slowest first.
# Zero-dependency plain-shell asserts, same idiom as refactor-budget.test.sh.
#
# Contract under test (issue #329):
#   profile.sh <suite>...  → one line `<secs> <suite> case <n> L<a>-<b>` per case at or
#                            above the threshold; exit 0 whether or not any case crossed.
#
# No case here waits on a clock. A fixture suite fabricates its own timestamps: bash stops
# treating EPOCHREALTIME as special once it is unset, so after `unset EPOCHREALTIME` an
# ordinary assignment to it is what the next trace line's PS4 expands to. The one trace
# line a fixture cannot fabricate is its first — the `unset` itself, stamped with the real
# clock — so a fixture's case 1 runs from that real stamp to a fabricated one and comes
# out hugely negative; the cases a probe measures are the ones after it.
#
# Run: scripts/tests/profile.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PROFILE="$HERE/../profile.sh"
pass=0 fail=0

scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# 1. a fixture whose case 2 spans 2.5 fabricated seconds and whose case 3 spans 0.25,
#    profiled at a threshold of 1: the report is one line, and it is case 2's. Case 1 is
#    the fixture's anchor (see the header) and must not be printed either.
name="threshold 1: the 2.5 s case is printed, the 0.25 s case is not"
problems=()
fixture="$scratch/two-cases.test.sh"
cat > "$fixture" <<'EOF'
unset EPOCHREALTIME
pass=0 fail=0
EPOCHREALTIME=100.000000
pass=$((pass + 1))
EPOCHREALTIME=102.500000
pass=$((pass + 1))
EPOCHREALTIME=102.750000
pass=$((pass + 1))
echo "$pass passed, $fail failed"
EOF
chmod +x "$fixture"
out="$(VERI_PROFILE_THRESHOLD=1 "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code")
lines=()
[[ -z "$out" ]] || mapfile -t lines <<< "$out"
[[ "${#lines[@]}" -eq 1 && "${lines[0]}" == *" case 2 "* ]] ||
  problems+=("want exactly one line, naming case 2, got: $(printf '%q' "$out")")
[[ "$out" != *" case 3 "* ]] || problems+=("case 3 (0.25 s) was printed: $(printf '%q' "$out")")
report "$name"

# 2. the printed line is exactly `<secs> <suite> case <n> L<a>-<b>`: the fixture's case 2
#    starts on line 5, the first line after case 1's boundary on line 4, and ends at its
#    own boundary on line 8, spanning 13 - 10 = 3 fabricated seconds. The seconds field is
#    pinned as a number equal to 3, not as a digit count.
name="the printed line is <secs> <suite> case 2 L5-8, secs equal to 3"
problems=()
fixture="$scratch/format.test.sh"
cat > "$fixture" <<'EOF'
unset EPOCHREALTIME
pass=0 fail=0
EPOCHREALTIME=10.000000
pass=$((pass + 1))
EPOCHREALTIME=11.000000
x=1
EPOCHREALTIME=13.000000
pass=$((pass + 1))
echo "$pass passed, $fail failed"
EOF
chmod +x "$fixture"
out="$(VERI_PROFILE_THRESHOLD=1 "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code")
secs="${out%% *}"
if [[ "$out" =~ ^[0-9]+(\.[0-9]+)?\ (.*)$ && "${BASH_REMATCH[2]}" == "$fixture case 2 L5-8" ]]; then
  awk -v s="$secs" 'BEGIN { exit !(s + 0 == 3) }' ||
    problems+=("want secs equal to 3, got $(printf '%q' "$secs")")
else
  problems+=("want exactly '<secs> $fixture case 2 L5-8', got: $(printf '%q' "$out")")
fi
report "$name"

# 3. only a top-level assignment that raises `pass` or `fail` ends a case. The fixture's
#    `pass=0 fail=0` on line 2 raises nothing, `passed=1` on line 6 names another variable,
#    the function's `local passed=1` and `local pass=9` are not top-level, and `fail=0` on
#    line 10 lowers nothing. Read right, case 2 runs from line 5 to the increment on line
#    12, 35 - 10 = 25 fabricated seconds; any of those read as a boundary would renumber
#    the cases or cut case 2 short.
name="boundaries: only top-level increments of pass/fail, so case 2 is L5-12"
problems=()
fixture="$scratch/boundaries.test.sh"
cat > "$fixture" <<'EOF'
unset EPOCHREALTIME
pass=0 fail=0
EPOCHREALTIME=10.000000
pass=$((pass + 1))
EPOCHREALTIME=20.000000
passed=1
bump() { local passed=1; local pass=9; }
EPOCHREALTIME=30.000000
bump
fail=0
EPOCHREALTIME=35.000000
pass=$((pass + 1))
echo "$pass passed, $fail failed"
EOF
chmod +x "$fixture"
out="$(VERI_PROFILE_THRESHOLD=1 "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code")
if [[ "$out" =~ ^([0-9]+(\.[0-9]+)?)\ (.*)$ && "${BASH_REMATCH[3]}" == "$fixture case 2 L5-12" ]]; then
  awk -v s="${BASH_REMATCH[1]}" 'BEGIN { exit !(s + 0 == 25) }' ||
    problems+=("want secs equal to 25, got $(printf '%q' "$out")")
else
  problems+=("want exactly '<secs> $fixture case 2 L5-12', got: $(printf '%q' "$out")")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

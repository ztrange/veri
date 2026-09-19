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
#   make -n profile          → names every suite `make -n test` names, under the offline
#                              environment test's recipe gives them. Read off `make -n`,
#                              which prints a recipe without running it, so no real suite runs.
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

# write_fixture <name> — write stdin to an executable fixture suite under $scratch and
# leave its path in `fixture`.
write_fixture() {
  fixture="$scratch/$1"
  cat > "$fixture"
  chmod +x "$fixture"
}

# expect_line <rest> <secs> — `out` is exactly one line `<secs> <rest>`, its seconds field a
# number equal to <secs> (compared as a number, not as a digit count); otherwise a problem.
expect_line() {
  local rest="$1" want="$2"
  if [[ "$out" =~ ^([0-9]+(\.[0-9]+)?)\ (.*)$ && "${BASH_REMATCH[3]}" == "$rest" ]]; then
    awk -v s="${BASH_REMATCH[1]}" -v w="$want" 'BEGIN { exit !(s + 0 == w + 0) }' ||
      problems+=("want secs equal to $want, got $(printf '%q' "$out")")
  else
    problems+=("want exactly '<secs> $rest', got: $(printf '%q' "$out")")
  fi
}

# case_order — the case numbers in `out`, in the order printed, each followed by a space.
case_order() {
  awk '{ printf "%s ", $4 }' <<< "$out"
}

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
write_fixture two-cases.test.sh <<'EOF'
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
write_fixture format.test.sh <<'EOF'
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
out="$(VERI_PROFILE_THRESHOLD=1 "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code")
expect_line "$fixture case 2 L5-8" 3
report "$name"

# 3. only a top-level assignment that raises `pass` or `fail` ends a case. The fixture's
#    `pass=0 fail=0` on line 2 raises nothing, `passed=1` on line 6 names another variable,
#    the function's `local passed=1` and `local pass=9` are not top-level, and `fail=0` on
#    line 10 lowers nothing. Read right, case 2 runs from line 5 to the increment on line
#    12, 35 - 10 = 25 fabricated seconds; any of those read as a boundary would renumber
#    the cases or cut case 2 short.
name="boundaries: only top-level increments of pass/fail, so case 2 is L5-12"
problems=()
write_fixture boundaries.test.sh <<'EOF'
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
out="$(VERI_PROFILE_THRESHOLD=1 "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code")
expect_line "$fixture case 2 L5-12" 25
report "$name"

# 4. three cases over the threshold, written out of order — case 2 spans 2 fabricated
#    seconds, case 3 spans 5, case 4 spans 3 — are printed slowest first: 3, 4, 2.
name="slowest first: cases spanning 2, 5 and 3 s print as case 3, case 4, case 2"
problems=()
write_fixture order.test.sh <<'EOF'
unset EPOCHREALTIME
pass=0 fail=0
EPOCHREALTIME=10.000000
pass=$((pass + 1))
EPOCHREALTIME=12.000000
pass=$((pass + 1))
EPOCHREALTIME=17.000000
pass=$((pass + 1))
EPOCHREALTIME=20.000000
pass=$((pass + 1))
echo "$pass passed, $fail failed"
EOF
out="$(VERI_PROFILE_THRESHOLD=1 "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code")
order="$(case_order)"
[[ "$order" == "3 4 2 " ]] ||
  problems+=("want cases in the order 3 4 2, got: $(printf '%q' "$out")")
report "$name"

# 5. case 4's fixture, the same fabricated timestamps — cases spanning 2, 5 and 3 s —
#    profiled at three thresholds: which cases print is the threshold's doing alone. At 1
#    all three do (3 4 2), at 2.5 the 2 s case drops out (3 4), at 4 only the 5 s case is
#    left (3).
name="threshold changes which cases print: 1 → 3 4 2, 2.5 → 3 4, 4 → 3"
problems=()
fixture="$scratch/order.test.sh"
for probe in "1:3 4 2 " "2.5:3 4 " "4:3 "; do
  t="${probe%%:*}" want="${probe#*:}"
  out="$(VERI_PROFILE_THRESHOLD="$t" "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
  [[ "$code" == 0 ]] || problems+=("threshold $t: want exit 0, got $code")
  order="$(case_order)"
  [[ "$order" == "$want" ]] ||
    problems+=("threshold $t: want cases '$want', got: $(printf '%q' "$out")")
done
report "$name"

# 6. no answer could be obtained, twice over: a threshold that is not a number of seconds
#    (case 4's well-formed fixture, so the threshold is the only thing wrong), and a
#    fixture whose trace never raises `pass` or `fail` (the default threshold, so the trace
#    is the only thing wrong) — nothing to cut into cases. Both are exit 2, not a report.
name="exit 2: a non-numeric threshold, and a suite that never increments pass/fail"
problems=()
out="$(VERI_PROFILE_THRESHOLD=abc "$PROFILE" "$scratch/order.test.sh" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 2 ]] || problems+=("threshold abc: want exit 2, got $code")
write_fixture no-increment.test.sh <<'EOF'
pass=0 fail=0
x=1
echo "$pass passed, $fail failed"
EOF
out="$(env -u VERI_PROFILE_THRESHOLD "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 2 ]] || problems+=("no increment: want exit 2, got $code")
report "$name"

# 7. VERI_PROFILE_THRESHOLD unset: the threshold is 1 second. A fixture whose case 2 spans
#    exactly 1 fabricated second and whose case 3 spans 0.9 prints case 2 alone, L5-6; a
#    fixture whose cases span 0.9 and 0.5 reaches the threshold nowhere, prints nothing,
#    and still exits 0 — an empty report is a report, not a failure.
name="default threshold 1: a 1 s case prints, 0.9 s does not; none reaching it exits 0"
problems=()
write_fixture default-at.test.sh <<'EOF'
unset EPOCHREALTIME
pass=0 fail=0
EPOCHREALTIME=10.000000
pass=$((pass + 1))
EPOCHREALTIME=11.000000
pass=$((pass + 1))
EPOCHREALTIME=11.900000
pass=$((pass + 1))
echo "$pass passed, $fail failed"
EOF
out="$(env -u VERI_PROFILE_THRESHOLD "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("1 s case: want exit 0, got $code")
expect_line "$fixture case 2 L5-6" 1
write_fixture default-under.test.sh <<'EOF'
unset EPOCHREALTIME
pass=0 fail=0
EPOCHREALTIME=10.000000
pass=$((pass + 1))
EPOCHREALTIME=10.900000
pass=$((pass + 1))
EPOCHREALTIME=11.400000
pass=$((pass + 1))
echo "$pass passed, $fail failed"
EOF
out="$(env -u VERI_PROFILE_THRESHOLD "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("no case reaching 1 s: want exit 0, got $code")
[[ -z "$out" ]] || problems+=("no case reaching 1 s: want no output, got: $(printf '%q' "$out")")
report "$name"

# 8. `make -n profile` is read as text beside `make -n test`: every suite `make -n test`
#    names (the TESTS glob, expanded), profile names too, and no other; and every fragment
#    of the offline environment test's recipe gives a suite — the offline shims on PATH, the
#    reach log, the real git, git's transport allowlist and proxy, the dead proxies, the C
#    locale, stdin from /dev/null — profile's recipe carries as well. `-n` prints a recipe
#    without running it, so nothing here runs a real suite.
name="make -n profile: the same suites as make -n test, in the same offline environment"
problems=()
ROOT="$(cd "$HERE/../../../.." && pwd)"
test_recipe="$(make --no-print-directory -n -C "$ROOT" test 2>&1)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("make -n test exited $code")
profile_recipe="$(make --no-print-directory -n -C "$ROOT" profile 2>&1)" && code=0 || code=$?
if [[ "$code" != 0 ]]; then
  problems+=("make -n profile exited $code: $(printf '%s' "$profile_recipe" | tr '\n' '/')")
else
  test_suites="$(grep -oE 'skills/tdd/scripts/tests/[^ ;"]+\.test\.sh' <<< "$test_recipe" | sort -u)"
  profile_suites="$(grep -oE 'skills/tdd/scripts/tests/[^ ;"]+\.test\.sh' <<< "$profile_recipe" | sort -u)"
  [[ -n "$test_suites" ]] || problems+=("make -n test names no suite")
  [[ "$profile_suites" == "$test_suites" ]] ||
    problems+=("suites differ (< test, > profile): $(diff <(echo "$test_suites") <(echo "$profile_suites") | grep '^[<>]' | tr '\n' '/')")
  for frag in 'skills/tdd/scripts/tests/offline:' 'OFFLINE_REACH_LOG=' 'xcrun -f git' \
      'GIT_CONFIG_KEY_0=http.proxy GIT_CONFIG_VALUE_0=http://127.0.0.1:1' \
      'GIT_CONFIG_KEY_1=protocol.allow GIT_CONFIG_VALUE_1=never' \
      'GIT_CONFIG_KEY_2=protocol.file.allow GIT_CONFIG_VALUE_2=always' \
      'HTTP_PROXY=http://127.0.0.1:1' 'HTTPS_PROXY=http://127.0.0.1:1' \
      'NO_PROXY=127.0.0.1,localhost' 'LC_ALL=C' '< /dev/null'; do
    [[ "$test_recipe" == *"$frag"* ]] || problems+=("make -n test lacks '$frag' — probe is stale")
    [[ "$profile_recipe" == *"$frag"* ]] || problems+=("make -n profile lacks '$frag'")
  done
fi
report "$name"

# 9. `test` and `profile` are independent targets: neither runs the other, as a prerequisite
#    or from its recipe. `make -n` prints a prerequisite's recipe ahead of the target's own
#    and runs a `$(MAKE)` line even under -n, so either route would put the other target's
#    recipe into this one's text: test's is the only one to print `all suites green`, and
#    profile's the only one to run `scripts/profile.sh`. A `make <target>` spelt out
#    literally in a recipe is looked for as text.
name="make -n test never runs profile, make -n profile never runs test"
problems=()
test_recipe="$(make --no-print-directory -n -C "$ROOT" test 2>&1)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("make -n test exited $code")
profile_recipe="$(make --no-print-directory -n -C "$ROOT" profile 2>&1)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("make -n profile exited $code")
[[ "$test_recipe" == *"all suites green"* ]] || problems+=("make -n test lacks 'all suites green' — probe is stale")
[[ "$profile_recipe" == *"scripts/profile.sh"* ]] || problems+=("make -n profile lacks 'scripts/profile.sh' — probe is stale")
[[ "$test_recipe" != *"scripts/profile.sh"* ]] || problems+=("make -n test runs profile.sh")
[[ "$profile_recipe" != *"all suites green"* ]] || problems+=("make -n profile runs test's recipe")
grep -Eq '(^|[^[:alnum:]_.-])make[^;]*[[:space:]]profile([[:space:];]|$)' <<< "$test_recipe" &&
  problems+=("make -n test calls make profile")
grep -Eq '(^|[^[:alnum:]_.-])make[^;]*[[:space:]]test([[:space:];]|$)' <<< "$profile_recipe" &&
  problems+=("make -n profile calls make test")
report "$name"

# 10. this suite costs no clock and runs no real suite, and `make test` runs it. Read as
#     text, the way no-docs-reads.test.sh reads a suite: no line outside a comment runs
#     `sleep` as a command, and every call to the profiler hands it a fixture this suite
#     wrote under $scratch — never a path under skills/tdd/scripts/tests/. Then the suite
#     is among those case 9's `make -n test` names, so the TESTS glob covers it with no
#     recipe edit. The two words searched for are spelt in halves so this case's own
#     lines do not match them.
name="this suite runs no clock and no real suite, and make -n test names it"
problems=()
self="$HERE/$(basename "$0")"
nap="sl""eep" call='"$PROF''ILE"' n=0 calls=0
runs_nap="(^|[;&|(])[[:space:]]*$nap([[:space:]]|;|\$)"
fixture_arg='^ "(\$fixture|\$scratch/[^"]+)"'
while IFS= read -r line; do
  n=$((n + 1))
  [[ "$line" =~ ^[[:space:]]*# ]] && continue
  [[ "$line" =~ $runs_nap ]] &&
    problems+=("L$n runs $nap: $line")
  if [[ "$line" == *"$call"* ]]; then
    calls=$((calls + 1))
    rest="${line#*"$call"}"
    [[ "$rest" =~ $fixture_arg ]] ||
      problems+=("L$n profiles something other than a fixture under \$scratch: $line")
  fi
done < "$self"
[[ "$calls" -gt 0 ]] || problems+=("found no call to the profiler in $self — probe is stale")
[[ "$test_recipe" == *"skills/tdd/scripts/tests/$(basename "$0")"* ]] ||
  problems+=("make -n test does not name skills/tdd/scripts/tests/$(basename "$0")")
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

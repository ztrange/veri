#!/usr/bin/env bash
# Unit tests for scripts/profile.sh — what `make profile` runs: every suite it is given,
# under `bash -x` with PS4='+${EPOCHREALTIME} ${LINENO} ', cut into cases at each
# top-level increment of `pass` or `fail`, and a report of the slowest cases.
#
# Contract under test:
#   profile.sh <suite>...  → one line `<secs> <suite> case <n> L<a>-<b>` per case at or
#                            above VERI_PROFILE_THRESHOLD (seconds, default 1), slowest
#                            first; exit 0 whether or not any case crossed.
#   make -n profile          → names every suite `make -n test` names, under the offline
#                              environment test's recipe gives them.
#
# Run: scripts/tests/profile.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
PROFILE="$HERE/../profile.sh"

scratch="$(scratch_dir)"

write_fixture() {
  fixture="$scratch/$1"
  cat > "$fixture"
  chmod +x "$fixture"
}

expect_line() {
  local rest="$1" want="$2"
  if [[ "$out" =~ ^([0-9]+(\.[0-9]+)?)\ (.*)$ && "${BASH_REMATCH[3]}" == "$rest" ]]; then
    awk -v s="${BASH_REMATCH[1]}" -v w="$want" 'BEGIN { exit !(s + 0 == w + 0) }' ||
      problems+=("want secs equal to $want, got $(printf '%q' "$out")")
  else
    problems+=("want exactly '<secs> $rest', got: $(printf '%q' "$out")")
  fi
}

name="threshold 1: the 2.5 s case is printed, the 0.25 s case is not"
problems=()
write_fixture two-cases.test.sh <<'EOF'
unset EPOCHREALTIME
pass=0; fail=0
EPOCHREALTIME=100.000000
pass=$((pass + 1))
EPOCHREALTIME=102.500000
pass=$((pass + 1))
EPOCHREALTIME=102.750000
pass=$((pass + 1))
echo "${pass:-0} passed, $fail failed"
EOF
out="$(VERI_PROFILE_THRESHOLD=1 "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code")
lines=()
[[ -z "$out" ]] || mapfile -t lines <<< "$out"
[[ "${#lines[@]}" -eq 1 && "${lines[0]}" == *" case 2 "* ]] ||
  problems+=("want exactly one line, naming case 2, got: $(printf '%q' "$out")")
[[ "$out" != *" case 3 "* ]] || problems+=("case 3 (0.25 s) was printed: $(printf '%q' "$out")")
report "$name"

write_fixture format.test.sh <<'EOF'
unset EPOCHREALTIME
pass=0; fail=0
EPOCHREALTIME=10.000000
pass=$((pass + 1))
EPOCHREALTIME=11.000000
x=1
EPOCHREALTIME=13.000000
pass=$((pass + 1))
echo "${pass:-0} passed, $fail failed"
EOF

name="exit 2: a non-numeric threshold, and a suite that never increments pass/fail"
problems=()
out="$(VERI_PROFILE_THRESHOLD=abc "$PROFILE" "$scratch/order.test.sh" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 2 ]] || problems+=("threshold abc: want exit 2, got $code")
write_fixture no-increment.test.sh <<'EOF'
pass=0; fail=0
x=1
echo "${pass:-0} passed, $fail failed"
EOF
out="$(env -u VERI_PROFILE_THRESHOLD "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 2 ]] || problems+=("no increment: want exit 2, got $code")
report "$name"

name="a command dying with 5 ends in exit 2, and the trace file is still removed"
problems=()
fixture="$scratch/format.test.sh"
shim="$scratch/sort-dies-with-5"
trace="$scratch/own-trap-trace"
mkdir -p "$shim"
printf '#!/bin/sh\ncat > /dev/null\nexit 5\n' > "$shim/sort"
printf '#!/bin/sh\n: > "%s"\necho "%s"\n' "$trace" "$trace" > "$shim/mktemp"
chmod +x "$shim/sort" "$shim/mktemp"
out="$(PATH="$shim:$PATH" VERI_PROFILE_THRESHOLD=1 "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 2 ]] || problems+=("sort dies with 5: want exit 2, got $code")
[[ ! -e "$trace" ]] || problems+=("sort dies with 5: want the trace file $trace removed, it is still there")
report "$name"

name="a traced bash that takes no PS4 from its environment still gets stamped lines"
problems=()
fixture="$scratch/format.test.sh"
real_bash="$(command -v bash)"
for mode in unset override; do
  shim="$scratch/no-ps4-$mode"
  mkdir -p "$shim"
  ps4_line='unset PS4'
  [[ "$mode" == unset ]] || ps4_line='PS4="+ "; export PS4'
  printf '#!/bin/sh\n%s\nexec "%s" "$@"\n' "$ps4_line" "$real_bash" > "$shim/bash"
  chmod +x "$shim/bash"
  out="$(PATH="$shim:$PATH" VERI_PROFILE_THRESHOLD=1 "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
  [[ "$code" == 0 ]] || problems+=("PS4 $mode: want exit 0, got $code")
  expect_line "$fixture case 2 L5-8" 3
done
report "$name"

name="threshold abc: exit 2, nothing on stdout, and stderr names the threshold it refused"
problems=()
err="$scratch/threshold-abc.err"
out="$(VERI_PROFILE_THRESHOLD=abc "$PROFILE" "$scratch/format.test.sh" 2>"$err")" && code=0 || code=$?
[[ "$code" == 2 ]] || problems+=("want exit 2, got $code")
[[ -z "$out" ]] || problems+=("want nothing on stdout, got: $(printf '%q' "$out")")
want="profile.sh: VERI_PROFILE_THRESHOLD must be a number of seconds, got 'abc'"
[[ "$(cat "$err")" == "$want" ]] ||
  problems+=("want stderr exactly '$want', got: $(printf '%q' "$(cat "$err")")")
report "$name"

name="through a symlink to the skill, from another directory: a relative suite is read there and printed as given"
problems=()
link="$scratch/skill-link"
ln -sfn "$(cd "$HERE/../.." && pwd)" "$link"
out="$(cd "$scratch" && VERI_PROFILE_THRESHOLD=1 "$link/scripts/profile.sh" format.test.sh 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code")
expect_line "format.test.sh case 2 L5-8" 3
report "$name"

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

finish

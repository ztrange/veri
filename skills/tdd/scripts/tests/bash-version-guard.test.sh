#!/usr/bin/env bash
# Unit tests for the refusal veri gives on a bash older than 5, at the three places a run or a
# test run begins: `make test`, run-conductor.sh (what starts a run) and leaf-launchable.sh (the
# preflight check SKILL.md runs before any leaf is paid for). Zero-dependency plain-shell asserts.
#
# Why this exists: veri requires bash 5 since 2026-09-18. Until then it promised bash 3.2, the
# bash macOS ships, and that promise was kept only by the development machine being a Mac — CI
# runs Linux. bash 3.2 cost that machine real time (a pattern substitution that took 3.86 s on
# CLAUDE.md's 17.5 kB of records takes ~0.2 s under bash 5), so the promise was dropped. With it
# gone, nothing tests veri on bash 3.2 any more, so a run on it must not be left to fail however
# a bash-4-only construct happens to fail: it is refused, at once, saying what to install.
#
# The major version is read from the running bash (BASH_VERSINFO) and can be stood in for with
# VERI_BASH_MAJOR — the `${VAR:-default}` injection every tunable here uses — because CI's
# runner has no bash older than 5 to ask. Where this machine does have one (/bin/bash on macOS),
# the last case asks it for real.
#
# Contract under test:
#   1. `make test` refuses, exit non-zero, naming the requirement, before any suite runs, when
#      the bash on PATH is older than 5 — and runs its suites when it is not.
#   2. run-conductor.sh refuses with exit 2, naming the requirement, before it launches anything.
#   3. leaf-launchable.sh refuses with exit 2, naming the requirement — and still answers 0 for
#      a launchable binary on bash 5.
#   4. On a real bash older than 5, the refusal comes from the bash itself, not the stand-in.
#
# Run: skills/tdd/scripts/tests/bash-version-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
SCRIPTS="$HERE/.."

REQUIREMENT='needs bash 5 or newer'

GREEN_FIXTURE='skills/tdd/scripts/tests/fixtures/live-suites/ends-green.test.sh'

pass=0 fail=0

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

flat() { printf '%s' "$1" | tr '\n' '/'; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

cat > "$work/claude" <<'C'
#!/bin/sh
: > "$LAUNCHED"
echo "2.1.0 (Claude Code)"
C
chmod +x "$work/claude"

name="make test refuses before any suite runs when the bash on PATH is older than 5, and runs them when it is not"
problems=()
old_out="$(env VERI_BASH_MAJOR=3 make -C "$ROOT" test TESTS="$GREEN_FIXTURE" 2>&1)" && old_code=0 || old_code=$?
[[ "$old_code" != 0 ]] || problems+=("want a non-zero exit with VERI_BASH_MAJOR=3, got 0: $(flat "$old_out")")
[[ "$old_out" == *"$REQUIREMENT"* ]] || problems+=("want the output to say it $REQUIREMENT: $(flat "$old_out")")
[[ "$old_out" != *"== $(basename "$GREEN_FIXTURE")"* ]] || problems+=("a suite ran before the refusal: $(flat "$old_out")")
new_out="$(env VERI_BASH_MAJOR=5 make -C "$ROOT" test TESTS="$GREEN_FIXTURE" 2>&1)" && new_code=0 || new_code=$?
[[ "$new_code" == 0 && "$new_out" == *"all suites green"* ]] ||
  problems+=("want the suite run and green with VERI_BASH_MAJOR=5, got exit $new_code: $(flat "$new_out")")
report "$name"

name="run-conductor.sh refuses with exit 2 before launching anything when bash is older than 5"
problems=()
mkdir -p "$work/conductor"
rc_err="$( cd "$work/conductor" && env VERI_BASH_MAJOR=3 CLAUDE_BIN="$work/claude" LAUNCHED="$work/conductor/launched" \
    "$SCRIPTS/run-conductor.sh" 4242 2>&1 >/dev/null )" && rc_code=0 || rc_code=$?
[[ "$rc_code" == 2 ]] || problems+=("want exit 2, got $rc_code: $(flat "$rc_err")")
[[ "$rc_err" == *"$REQUIREMENT"* ]] || problems+=("want stderr to say it $REQUIREMENT: $(flat "$rc_err")")
[[ ! -e "$work/conductor/launched" ]] || problems+=("the conductor's binary was launched before the refusal")
report "$name"

name="leaf-launchable.sh refuses with exit 2 when bash is older than 5, and still answers 0 for a launchable binary on bash 5"
problems=()
ll_err="$(env VERI_BASH_MAJOR=3 CLAUDE_BIN="$work/claude" LAUNCHED="$work/ll-launched" \
    "$SCRIPTS/leaf-launchable.sh" 2>&1 >/dev/null)" && ll_code=0 || ll_code=$?
[[ "$ll_code" == 2 ]] || problems+=("want exit 2 with VERI_BASH_MAJOR=3, got $ll_code: $(flat "$ll_err")")
[[ "$ll_err" == *"$REQUIREMENT"* ]] || problems+=("want stderr to say it $REQUIREMENT: $(flat "$ll_err")")
env VERI_BASH_MAJOR=5 CLAUDE_BIN="$work/claude" LAUNCHED="$work/ll-launched" \
  "$SCRIPTS/leaf-launchable.sh" >/dev/null 2>&1 && ll5=0 || ll5=$?
[[ "$ll5" == 0 ]] || problems+=("want exit 0 for a launchable binary with VERI_BASH_MAJOR=5, got $ll5")
report "$name"

if [[ -x /bin/bash ]] && [[ "$(/bin/bash -c 'echo "${BASH_VERSINFO[0]}"')" -lt 5 ]]; then
  name="on a real bash older than 5 (/bin/bash), leaf-launchable.sh refuses with exit 2"
  problems=()
  real_err="$(env -u VERI_BASH_MAJOR CLAUDE_BIN="$work/claude" LAUNCHED="$work/real-launched" \
      /bin/bash "$SCRIPTS/leaf-launchable.sh" 2>&1 >/dev/null)" && real_code=0 || real_code=$?
  [[ "$real_code" == 2 && "$real_err" == *"$REQUIREMENT"* ]] ||
    problems+=("want exit 2 and '$REQUIREMENT' from /bin/bash $(/bin/bash -c 'echo $BASH_VERSION'), got exit $real_code: $(flat "$real_err")")
  report "$name"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

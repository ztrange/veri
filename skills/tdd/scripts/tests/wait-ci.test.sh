#!/usr/bin/env bash
# Tests for scripts/wait-ci.sh — the resumable CI wait the Draft PR step calls after
# `gh pr ready` (#544), shaped like wait-leaf.sh: wait a bounded slice, exit 3 while a
# check is still pending, and be called again.
#
# Driven against a STUB `gh` first on PATH that answers `gh pr view <url> --json
# statusCheckRollup` with the fixture document named by $ROLLUP, and refuses every other
# call — `-q`/`--jq`/`--template` included, since jq is not a dependency of any script here —
# and on the VIRTUAL CLOCK wait-leaf.test.sh uses: a stub `date` that advances
# $VERI_CLOCK_STEP seconds a reading, so a pending check never waits on real time.
#
# Status contract: exit 0 every check completed SUCCESS, NEUTRAL or SKIPPED · 1 a completed
# check concluded anything else · 2 gh could not read the checks · 3 a check is still pending
# within the bound. An empty rollup is never 0.
#
# Run: scripts/tests/wait-ci.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WAIT="$HERE/../wait-ci.sh"
PR="https://github.com/o/r/pull/1"
pass=0 fail=0

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/.tdd" "$work/bin"

cat > "$work/bin/date" <<'D'
#!/bin/sh
n="$(wc -l < "$VERI_CLOCK_LOG" | tr -d ' ')"
now="$(( n * ${VERI_CLOCK_STEP:-1} ))"
printf '%s\n' "$now" | tee -a "$VERI_CLOCK_LOG"
D
cat > "$work/bin/gh" <<'G'
#!/bin/sh
case "$*" in
  *-q*|*--jq*|*--template*) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
  "pr view $PR_URL --json "*statusCheckRollup*)
    if [ -n "${GH_FAIL:-}" ]; then echo "HTTP 502: Bad Gateway" >&2; exit 1; fi
    echo >> "$ROLLUP.calls"
    n="$(wc -l < "$ROLLUP.calls" | tr -d ' ')"
    if [ -f "$ROLLUP.$n" ]; then cat "$ROLLUP.$n"; else cat "$ROLLUP"; fi ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
G
chmod +x "$work/bin/date" "$work/bin/gh"

report() {
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1)); echo "FAIL - $1"; printf '    %s\n' "${problems[@]}"
  fi
}

# rollup <file> <rows> [head] — write the fixture document gh serves for the PR, rows being
# the JSON array's contents and <head> its head commit. A file <name>.json.<n> beside
# <name>.json is served on the n-th read.
rollup() {
  printf '{"headRefOid":"%s","statusCheckRollup":[%s]}\n' \
    "${3:-0123456789abcdef0123456789abcdef01234567}" "$2" > "$work/$1"
}

# check <status> <conclusion> — one CheckRun row of the rollup.
check() {
  printf '{"__typename":"CheckRun","name":"gates","workflowName":"ci","status":"%s","conclusion":"%s"}' "$1" "$2"
}

# wait_in <dir> <name> <err> <bound>... — run wait-ci.sh from <dir> against fixture <name> with
# <bound>... as its limits on a clock that moves 60 s a reading, stderr to <err>, and echo its
# exit code.
wait_in() {
  ( cd "$1" && env VERI_POLL=0 VERI_CLOCK_STEP=60 VERI_CLOCK_LOG="$work/$2.clock" \
      PR_URL="$PR" ROLLUP="$work/$2.json" PATH="$work/bin:$PATH" \
      "$WAIT" "$PR" "${@:4}" >/dev/null 2>"$3" )
  echo $?
}

# waited <name> [arg...] — wait_in a working directory of its own, on a fresh clock, with
# [arg...] as wait-ci.sh's arguments after the PR (default a 1800-second limit), stderr to
# <name>.err.
waited() {
  local dir
  [[ $# -gt 1 ]] || set -- "$1" 1800
  dir="$(mktemp -d "$work/cwd.XXXXXX")"; mkdir "$dir/.tdd"
  : > "$work/$1.clock"; : > "$work/$1.json.calls"
  wait_in "$dir" "$1" "$work/$1.err" "${@:2}"
}

# expect_exit <name> <code> [bound] — waited <name> [bound], and record a problem unless it
# exited <code>.
expect_exit() {
  local got
  got="$(waited "$1" "${3:-1800}")"
  [[ "$got" == "$2" ]] || problems+=("$1, bound ${3:-1800}: want exit $2, got $got (stderr: $(cat "$work/$1.err"))")
}

rollup pending.json "$(check COMPLETED SUCCESS),$(check IN_PROGRESS '')"
rollup green.json   "$(check COMPLETED SUCCESS),$(check COMPLETED NEUTRAL),$(check COMPLETED SKIPPED)"
rollup red.json     "$(check COMPLETED SUCCESS),$(check COMPLETED FAILURE)"
rollup empty.json   ""

name="wait-ci.sh exits 3 while a check is pending, 0 when every check completed SUCCESS, NEUTRAL or SKIPPED, 1 on any other conclusion, and never 0 on an empty rollup (#544)"
problems=()
for want in pending:3 green:0 red:1; do
  expect_exit "${want%%:*}" "${want##*:}"
done
got="$(waited empty)"
[[ "$got" != 0 ]] || problems+=("empty rollup: exited 0")
report "$name"

rollup late.json "$(check COMPLETED SUCCESS)"
rollup late.json.1 "$(check IN_PROGRESS '')"
cp "$work/late.json.1" "$work/late.json.2"

name="wait-ci.sh polls a pending check until its bound runs out: a check that completes on the third read exits 0 within 1800 s and 3 within 60 s (#544)"
problems=()
expect_exit late 0 1800
expect_exit late 3 60
report "$name"

name="wait-ci.sh exits 2 and names the PR when gh cannot read its checks, rather than waiting its bound out as if they were pending (#544)"
problems=()
got="$(GH_FAIL=1 waited pending)"
[[ "$got" == 2 ]] || problems+=("failing gh: want exit 2, got $got")
grep -F "could not read the checks of $PR" "$work/pending.err" > /dev/null \
  || problems+=("failing gh: stderr does not name the PR: $(cat "$work/pending.err")")
report "$name"

name="wait-ci.sh enforces its bound across calls: a second call for the same head commit that still finds a check pending past the deadline the first call recorded exits 2, not 3 with a fresh bound (#544)"
problems=()
rollup across.json "$(check IN_PROGRESS '')" fedcba9876543210fedcba9876543210fedcba98
mkdir -p "$work/across/.tdd"
: > "$work/across.clock"; : > "$work/across.json.calls"
got_first="$(wait_in "$work/across" across "$work/across.first.err" 120)"
got_second="$(wait_in "$work/across" across "$work/across.second.err" 120)"
[[ "$got_first" == 3 ]] || problems+=("first call: want exit 3, got $got_first (stderr: $(cat "$work/across.first.err"))")
[[ "$got_second" == 2 ]] || problems+=("second call past the recorded deadline: want exit 2, got $got_second (stderr: $(cat "$work/across.second.err"))")
report "$name"

name="wait-ci.sh exits 2 and names the PR when the rollup carries no head commit, rather than recording a deadline no later call can find (#544)"
problems=()
printf '{"statusCheckRollup":[%s]}\n' "$(check IN_PROGRESS '')" > "$work/headless.json"
got="$(waited headless)"
[[ "$got" == 2 ]] || problems+=("no headRefOid: want exit 2, got $got (stderr: $(cat "$work/headless.err"))")
grep -F "could not read the checks of $PR" "$work/headless.err" > /dev/null \
  || problems+=("no headRefOid: stderr does not name the PR: $(cat "$work/headless.err")")
report "$name"

# context <state> — one legacy StatusContext row of the rollup: a state and no status key.
context() {
  printf '{"__typename":"StatusContext","context":"legacy","state":"%s"}' "$1"
}

name="wait-ci.sh reads a legacy StatusContext by its state: PENDING or EXPECTED is pending and exits 3, never 0; FAILURE or ERROR is failed and exits 1 (#544)"
problems=()
for want in PENDING:3 EXPECTED:3 FAILURE:1 ERROR:1; do
  st="${want%%:*}"
  rollup "legacy-$st.json" "$(check COMPLETED SUCCESS),$(context "$st")"
  expect_exit "legacy-$st" "${want##*:}"
done
report "$name"

name="wait-ci.sh reads a legacy StatusContext whose state is SUCCESS as a completed green check: beside a pending CheckRun it exits 3, beside only green checks it exits 0 (#544)"
problems=()
rollup legacy-success-pending.json "$(check IN_PROGRESS ''),$(context SUCCESS)"
rollup legacy-success-green.json "$(check COMPLETED SUCCESS),$(context SUCCESS)"
expect_exit legacy-success-pending 3
expect_exit legacy-success-green 0
report "$name"

name="wait-ci.sh keeps its total bound separate from one call's slice: with a total of 1800 s and a slice of 540 s, a call made 600 s after the first that still finds a check pending exits 3, not 2, and SKILL.md's Draft PR step passes that total bound (#544)"
problems=()
rollup total.json "$(check IN_PROGRESS '')" 00112233445566778899aabbccddeeff00112233
mkdir -p "$work/total/.tdd"
: > "$work/total.clock"; : > "$work/total.json.calls"
for call in first second; do
  got="$(wait_in "$work/total" total "$work/total.$call.err" 540 1800)"
  [[ "$got" == 3 ]] || problems+=("$call call, slice 540, total 1800: want exit 3, got $got (stderr: $(cat "$work/total.$call.err"))")
done
calls="$(grep -F 'wait-ci.sh <pr-url>' "$HERE/../../SKILL.md")"
[[ -n "$calls" ]] || problems+=("SKILL.md: no wait-ci.sh <pr-url> call found")
while IFS= read -r line; do
  [[ "$line" =~ wait-ci\.sh\ \<pr-url\>\ [0-9]+\ [0-9]+ ]] \
    || problems+=("SKILL.md passes wait-ci.sh no total bound: $line")
done <<< "$calls"
report "$name"

name="wait-ci.sh never reads a rollup whose every check concluded SKIPPED as green: it exits 3 while its bound lasts, since a check skipped on a draft push has not tested the head (#544)"
problems=()
rollup all-skipped.json "$(check COMPLETED SKIPPED),$(check COMPLETED SKIPPED)"
expect_exit all-skipped 3
report "$name"

name="wait-ci.sh takes the head sha it waits for, and exits 3 at the end of its slice while the PR still reports a different head, even one whose checks all completed SUCCESS (#550)"
problems=()
rollup stale-head.json "$(check COMPLETED SUCCESS)" 0123456789abcdef0123456789abcdef01234567
got="$(waited stale-head 60 60 89abcdef0123456789abcdef0123456789abcdef)"
[[ "$got" == 3 ]] || problems+=("PR reports a green previous head, waiting for 89abcdef…: want exit 3, got $got (stderr: $(cat "$work/stale-head.err"))")
report "$name"

name="wait-ci.sh records its total bound against the head sha it was given, not the PR's reported head: a later call for the same sha that still finds the PR reporting a different head past that recorded deadline exits 2 (#550)"
problems=()
rollup stale-across.json.1 "$(check COMPLETED SUCCESS)" 0123456789abcdef0123456789abcdef01234567
cp "$work/stale-across.json.1" "$work/stale-across.json.2"
rollup stale-across.json "$(check COMPLETED SUCCESS)" 76543210fedcba9876543210fedcba9876543210
mkdir -p "$work/stale-across/.tdd"
: > "$work/stale-across.clock"; : > "$work/stale-across.json.calls"
sha=89abcdef0123456789abcdef0123456789abcdef
got_first="$(wait_in "$work/stale-across" stale-across "$work/stale-across.first.err" 60 60 "$sha")"
got_second="$(wait_in "$work/stale-across" stale-across "$work/stale-across.second.err" 60 60 "$sha")"
[[ "$got_first" == 3 ]] || problems+=("first call: want exit 3, got $got_first (stderr: $(cat "$work/stale-across.first.err"))")
[[ "$got_second" == 2 ]] || problems+=("second call for $sha past the recorded deadline, PR reporting another head: want exit 2, got $got_second (stderr: $(cat "$work/stale-across.second.err"))")
report "$name"

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

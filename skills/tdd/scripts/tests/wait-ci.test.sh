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

# wait_in <dir> <name> <bound> <err> — run wait-ci.sh from <dir> against fixture <name> with a
# <bound>-second limit on a clock that moves 60 s a reading, stderr to <err>, and echo its
# exit code.
wait_in() {
  ( cd "$1" && env VERI_POLL=0 VERI_CLOCK_STEP=60 VERI_CLOCK_LOG="$work/$2.clock" \
      PR_URL="$PR" ROLLUP="$work/$2.json" PATH="$work/bin:$PATH" \
      "$WAIT" "$PR" "$3" >/dev/null 2>"$4" )
  echo $?
}

# waited <name> [bound] — wait_in a working directory of its own, on a fresh clock, with a
# <bound>-second limit (default 1800), stderr to <name>.err.
waited() {
  local dir
  dir="$(mktemp -d "$work/cwd.XXXXXX")"; mkdir "$dir/.tdd"
  : > "$work/$1.clock"; : > "$work/$1.json.calls"
  wait_in "$dir" "$1" "${2:-1800}" "$work/$1.err"
}

rollup pending.json "$(check COMPLETED SUCCESS),$(check IN_PROGRESS '')"
rollup green.json   "$(check COMPLETED SUCCESS),$(check COMPLETED NEUTRAL),$(check COMPLETED SKIPPED)"
rollup red.json     "$(check COMPLETED SUCCESS),$(check COMPLETED FAILURE)"
rollup empty.json   ""

name="wait-ci.sh exits 3 while a check is pending, 0 when every check completed SUCCESS, NEUTRAL or SKIPPED, 1 on any other conclusion, and never 0 on an empty rollup (#544)"
problems=()
for want in pending:3 green:0 red:1; do
  fx="${want%%:*}" code="${want##*:}"
  got="$(waited "$fx")"
  [[ "$got" == "$code" ]] || problems+=("$fx rollup: want exit $code, got $got (stderr: $(cat "$work/$fx.err"))")
done
got="$(waited empty)"
[[ "$got" != 0 ]] || problems+=("empty rollup: exited 0")
report "$name"

rollup late.json "$(check COMPLETED SUCCESS)"
rollup late.json.1 "$(check IN_PROGRESS '')"
cp "$work/late.json.1" "$work/late.json.2"

name="wait-ci.sh polls a pending check until its bound runs out: a check that completes on the third read exits 0 within 1800 s and 3 within 60 s (#544)"
problems=()
got="$(waited late 1800)"
[[ "$got" == 0 ]] || problems+=("bound 1800: want exit 0, got $got (stderr: $(cat "$work/late.err"))")
got="$(waited late 60)"
[[ "$got" == 3 ]] || problems+=("bound 60: want exit 3, got $got (stderr: $(cat "$work/late.err"))")
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
got_first="$(wait_in "$work/across" across 120 "$work/across.first.err")"
got_second="$(wait_in "$work/across" across 120 "$work/across.second.err")"
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

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

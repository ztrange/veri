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
served() {
  n="$(wc -l < "$ROLLUP.calls" | tr -d ' ')"
  if [ -f "$ROLLUP.$n$1" ]; then echo "$ROLLUP.$n$1"; else echo "$ROLLUP$1"; fi
}
refusal='GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)'
if [ "${GH_GRAPHQL:-}" = refused ]; then
  case "$1" in
    issue|pr|repo) echo "HTTP 403: $refusal" >&2; exit 1 ;;
  esac
  case "$*" in
    "api graphql"*) echo "HTTP 403: $refusal" >&2; exit 1 ;;
  esac
fi
case "$*" in
  *-q*|*--jq*|*--template*) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
  "api repos/o/r/pulls/1")
    if [ -n "${GH_FAIL:-}" ]; then echo "HTTP 502: Bad Gateway" >&2; exit 1; fi
    echo >> "$ROLLUP.calls"
    python3 -c 'import json, sys; print(json.dumps({"number": 1, "state": "open", "draft": False, "head": {"sha": json.load(open(sys.argv[1])).get("headRefOid")}}))' "$(served '')" ;;
  "pr view $PR_URL --json "*statusCheckRollup*)
    if [ -n "${GH_FAIL:-}" ]; then echo "HTTP 502: Bad Gateway" >&2; exit 1; fi
    echo >> "$ROLLUP.calls"
    cat "$(served '')" ;;
  "api "*"repos/o/r/commits/"*/check-runs*)
    if [ -n "${GH_API_FAIL:-}" ]; then echo '{"message":"Not Found"}'; echo "gh: Not Found (HTTP 404)" >&2; exit 1; fi
    python3 - "$(served .check-runs)" "$@" <<'P'
import json, re, sys
runs = json.load(open(sys.argv[1]))["check_runs"]
args = sys.argv[2:]
text = " ".join(args)
per = re.search(r"per_page=(\d+)", text)
per = min(int(per.group(1)) if per else 30, 100)
page = re.search(r"(?<![_a-z])page=(\d+)", text)
page = int(page.group(1)) if page else 1
def doc(p):
    return {"total_count": len(runs), "check_runs": runs[(p - 1) * per:p * per]}
if "--paginate" in args:
    pages = [doc(p) for p in range(page, max(1, -(-len(runs) // per)) + 1)]
    print(json.dumps(pages) if "--slurp" in args else "".join(json.dumps(d) for d in pages))
else:
    print(json.dumps(doc(page)))
P
    ;;
  "api repos/o/r/commits/"*/status)
    if [ -n "${GH_STATUS_FAIL:-}" ]; then echo '{"message":"Not Found"}'; echo "gh: Not Found (HTTP 404)" >&2; exit 1; fi
    cat "$(served .status)" ;;
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

rollup() {
  printf '{"headRefOid":"%s","statusCheckRollup":[%s]}\n' \
    "${3:-0123456789abcdef0123456789abcdef01234567}" "$2" > "$work/$1"
  python3 - "$work/$1" <<'P'
import json, sys
doc = json.load(open(sys.argv[1]))
rows = doc["statusCheckRollup"]
runs = [{"name": r["name"], "head_sha": doc["headRefOid"], "status": r["status"].lower(),
         "conclusion": r["conclusion"].lower() or None}
        for r in rows if r["__typename"] == "CheckRun"]
statuses = [{"context": r["context"], "state": {"EXPECTED": "pending"}.get(r["state"], r["state"].lower())}
            for r in rows if r["__typename"] == "StatusContext" and "state" in r]
json.dump({"total_count": len(runs), "check_runs": runs}, open(sys.argv[1] + ".check-runs", "w"))
json.dump({"state": "pending", "sha": doc["headRefOid"], "total_count": len(statuses), "statuses": statuses},
          open(sys.argv[1] + ".status", "w"))
P
}

check() {
  printf '{"__typename":"CheckRun","name":"gates","workflowName":"ci","status":"%s","conclusion":"%s"}' "$1" "$2"
}

sha_runs() {
  local f="$1"; shift
  local IFS=,
  printf '{"total_count":%s,"check_runs":[%s]}\n' "$#" "$*" > "$work/$f.check-runs"
  sha_statuses "$f" pending
}

sha_statuses() {
  local f="$1" state="$2"; shift 2
  local IFS=,
  printf '{"state":"%s","sha":"%s","total_count":%s,"statuses":[%s]}\n' "$state" "$sha" "$#" "$*" > "$work/$f.status"
}

sha_run() {
  printf '{"name":"%s","head_sha":"%s","status":"%s","conclusion":%s}' "$1" "$sha" "$2" "$3"
}

sha_head() {
  rollup "$1" "$(check COMPLETED SUCCESS)" "$sha"
}

wait_in() {
  ( cd "$1" && env VERI_POLL=0 VERI_CLOCK_STEP=60 VERI_CLOCK_LOG="$work/$2.clock" \
      PR_URL="$PR" ROLLUP="$work/$2.json" PATH="$work/bin:$PATH" \
      "$WAIT" "$PR" "${@:4}" >/dev/null 2>"$3" )
  echo $?
}

waited() {
  local dir
  [[ $# -gt 1 ]] || set -- "$1" 1800
  dir="$(mktemp -d "$work/cwd.XXXXXX")"; mkdir "$dir/.tdd"
  : > "$work/$1.clock"; : > "$work/$1.json.calls"
  wait_in "$dir" "$1" "$work/$1.err" "${@:2}"
}

shared() {
  mkdir -p "$work/$1/.tdd"
  : > "$work/$1.clock"; : > "$work/$1.json.calls"
}

again() {
  wait_in "$work/$1" "$1" "$work/$1.$2.err" "${@:3}"
}

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
rollup late.json.2 "$(check IN_PROGRESS '')"

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
shared across
got_first="$(again across first 120)"
got_second="$(again across second 120)"
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
shared total
for call in first second; do
  got="$(again total "$call" 540 1800)"
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
shared stale-across
sha=89abcdef0123456789abcdef0123456789abcdef
got_first="$(again stale-across first 60 60 "$sha")"
got_second="$(again stale-across second 60 60 "$sha")"
[[ "$got_first" == 3 ]] || problems+=("first call: want exit 3, got $got_first (stderr: $(cat "$work/stale-across.first.err"))")
[[ "$got_second" == 2 ]] || problems+=("second call for $sha past the recorded deadline, PR reporting another head: want exit 2, got $got_second (stderr: $(cat "$work/stale-across.second.err"))")
report "$name"

name="wait-ci.sh exits 2 on its first read of a legacy StatusContext row that carries no state key, rather than reading it as pending and waiting out its bound (#550)"
problems=()
rollup stateless.json "$(check COMPLETED SUCCESS),{\"__typename\":\"StatusContext\",\"context\":\"legacy\"}"
got="$(waited stateless)"
reads="$(wc -l < "$work/stateless.json.calls" | tr -d ' ')"
[[ "$got" == 2 ]] || problems+=("StatusContext with no state: want exit 2, got $got (stderr: $(cat "$work/stateless.err"))")
[[ "$reads" == 1 ]] || problems+=("StatusContext with no state: want 1 read of the checks, got $reads")
report "$name"

name="wait-ci.sh exits 3 while the sha's own check runs are still in progress, even when the PR already reports that sha as its head and its rollup still shows a previous head's green (#552)"
problems=()
sha=89abcdef0123456789abcdef0123456789abcdef
sha_head race.json
sha_runs race.json "$(sha_run gates in_progress null)"
got="$(waited race 60 60 "$sha")"
[[ "$got" == 3 ]] || problems+=("rollup green for $sha, its own check run in_progress: want exit 3, got $got (stderr: $(cat "$work/race.err"))")
report "$name"

name="wait-ci.sh exits 2 naming the sha when gh cannot read that sha's own check runs, even though gh printed a body (#552)"
problems=()
sha_head unread.json
got="$(GH_API_FAIL=1 waited unread 60 60 "$sha")"
[[ "$got" == 2 ]] || problems+=("gh api check-runs failed: want exit 2, got $got (stderr: $(cat "$work/unread.err"))")
grep -F "could not read the checks of $sha" "$work/unread.err" > /dev/null \
  || problems+=("gh api check-runs failed: want stderr naming $sha, got: $(cat "$work/unread.err")")
report "$name"

name="wait-ci.sh exits 1 when the sha's own check runs hold a completed failure, even while the PR rollup reads all green (#552)"
problems=()
sha_head redsha.json
sha_runs redsha.json "$(sha_run gates completed '"failure"')"
got="$(waited redsha 60 60 "$sha")"
[[ "$got" == 1 ]] || problems+=("rollup green for $sha, its own check run completed failure: want exit 1, got $got (stderr: $(cat "$work/redsha.err"))")
report "$name"

name="wait-ci.sh never reads a completed NEUTRAL or SKIPPED run among the sha's own check runs as red: with another still in progress it exits 3 (#552)"
problems=()
sha_head quietsha.json
sha_runs quietsha.json "$(sha_run lint completed '"neutral"')" "$(sha_run docs completed '"skipped"')" "$(sha_run gates in_progress null)"
got="$(waited quietsha 60 60 "$sha")"
[[ "$got" == 3 ]] || problems+=("sha's own runs neutral, skipped and in_progress: want exit 3, got $got (stderr: $(cat "$work/quietsha.err"))")
report "$name"

name="wait-ci.sh reads every page of the sha's own check runs: a failed run beyond the first page exits 1, even while the PR rollup reads all green (#552)"
problems=()
sha_head pagedsha.json
runs=()
for i in $(seq 1 100); do runs+=("$(sha_run "gates-$i" completed '"success"')"); done
runs+=("$(sha_run gates-101 completed '"failure"')")
sha_runs pagedsha.json "${runs[@]}"
got="$(waited pagedsha 60 60 "$sha")"
[[ "$got" == 1 ]] || problems+=("rollup green for $sha, a failed run on its check runs' second page: want exit 1, got $got (stderr: $(cat "$work/pagedsha.err"))")
report "$name"

name="wait-ci.sh exits 0 when the sha's own check runs and statuses have all succeeded, even while the PR rollup still shows a previous head's failed or pending checks (#552)"
problems=()
for stale in failure:"$(check COMPLETED FAILURE)" pending:"$(check IN_PROGRESS '')"; do
  f="greensha-${stale%%:*}"
  rollup "$f.json" "$(check COMPLETED SUCCESS),${stale#*:}" "$sha"
  sha_runs "$f.json" "$(sha_run gates completed '"success"')"
  sha_statuses "$f.json" success '{"context":"legacy","state":"success"}'
  got="$(waited "$f" 60 60 "$sha")"
  [[ "$got" == 0 ]] || problems+=("rollup ${stale%%:*} for $sha, its own check run and status success: want exit 0, got $got (stderr: $(cat "$work/$f.err"))")
done
report "$name"

name="wait-ci.sh exits 3, never 0, when every one of the sha's own check runs concluded skipped, even while the PR rollup reads all green (#552)"
problems=()
sha_head skippedsha.json
sha_runs skippedsha.json "$(sha_run gates completed '"skipped"')" "$(sha_run docs completed '"skipped"')"
got="$(waited skippedsha 60 60 "$sha")"
[[ "$got" == 3 ]] || problems+=("rollup green for $sha, its own check runs all skipped: want exit 3, got $got (stderr: $(cat "$work/skippedsha.err"))")
report "$name"

name="wait-ci.sh exits 1 when a legacy status context of the sha is in a failure or error state, even while the sha's own check runs all succeeded (#552)"
problems=()
for state in failure error; do
  f="statussha-$state"
  sha_head "$f.json"
  sha_runs "$f.json" "$(sha_run gates completed '"success"')"
  sha_statuses "$f.json" "$state" "{\"context\":\"legacy\",\"state\":\"$state\"}"
  got="$(waited "$f" 60 60 "$sha")"
  [[ "$got" == 1 ]] || problems+=("status $state for $sha, its own check runs success: want exit 1, got $got (stderr: $(cat "$work/$f.err"))")
done
report "$name"

name="wait-ci.sh exits 2 naming the sha when gh cannot read its /status, and reads a /status with no statuses as none, while its own check runs all succeeded (#552)"
problems=()
sha_head unstatus.json
sha_runs unstatus.json "$(sha_run gates completed '"success"')"
got="$(GH_STATUS_FAIL=1 waited unstatus 60 60 "$sha")"
[[ "$got" == 2 ]] || problems+=("gh api status failed: want exit 2, got $got (stderr: $(cat "$work/unstatus.err"))")
grep -F "could not read the checks of $sha" "$work/unstatus.err" > /dev/null \
  || problems+=("gh api status failed: want stderr naming $sha, got: $(cat "$work/unstatus.err")")
sha_head nostatuses.json
sha_runs nostatuses.json "$(sha_run gates completed '"success"')"
printf '{"state":"pending","sha":"%s","total_count":0}\n' "$sha" > "$work/nostatuses.json.status"
got="$(waited nostatuses 60 60 "$sha")"
[[ "$got" == 0 ]] || problems+=("/status with no statuses key, check runs success: want exit 0, got $got (stderr: $(cat "$work/nostatuses.err"))")
report "$name"

name="wait-ci.sh exits 3 while a legacy status context of the sha is still pending, even when the sha's own check runs all succeeded (#552)"
problems=()
sha_head pendingstatus.json
sha_runs pendingstatus.json "$(sha_run gates completed '"success"')"
sha_statuses pendingstatus.json pending '{"context":"legacy","state":"pending"}'
got="$(waited pendingstatus 60 60 "$sha")"
[[ "$got" == 3 ]] || problems+=("status pending for $sha, its own check runs success: want exit 3, got $got (stderr: $(cat "$work/pendingstatus.err"))")
report "$name"

name="wait-ci.sh exits 3, never 0, while the sha has no check runs and no statuses yet, even when the PR rollup reads all green (#552)"
problems=()
sha_head nonesha.json
sha_runs nonesha.json
got="$(waited nonesha 60 60 "$sha")"
[[ "$got" == 3 ]] || problems+=("rollup green for $sha, no check runs and no statuses of its own: want exit 3, got $got (stderr: $(cat "$work/nonesha.err"))")
report "$name"

name="wait-ci.sh called with no head-sha reads the PR's head sha and exits 3 while that sha's own check runs are in progress, even when the PR rollup reads all green (#552)"
problems=()
sha_head nohead.json
sha_runs nohead.json "$(sha_run gates in_progress null)"
got="$(waited nohead 60 60)"
[[ "$got" == 3 ]] || problems+=("no head-sha given, PR head $sha, rollup green, its own check run in_progress: want exit 3, got $got (stderr: $(cat "$work/nohead.err"))")
report "$name"

name="wait-ci.sh called with no head-sha against a gh that refuses GraphQL with the 403 and answers REST reads the PR's head sha and exits 0, 1, 3 and 2 on green, red, pending and unreadable checks, the same as against a working gh (#568)"
problems=()
sha_head gql-green.json
sha_runs gql-green.json "$(sha_run gates completed '"success"')"
sha_statuses gql-green.json success
sha_head gql-red.json
sha_runs gql-red.json "$(sha_run gates completed '"failure"')"
sha_head gql-pending.json
sha_runs gql-pending.json "$(sha_run gates in_progress null)"
sha_head gql-unread.json
for route in working refused; do
  for want in green:0 red:1 pending:3 unread:2; do
    f="gql-${want%%:*}"
    if [[ "$f" == gql-unread ]]; then
      got="$(GH_GRAPHQL="$route" GH_API_FAIL=1 waited "$f" 60 60)"
    else
      got="$(GH_GRAPHQL="$route" waited "$f" 60 60)"
    fi
    [[ "$got" == "${want##*:}" ]] || problems+=("$route GraphQL, ${want%%:*} checks on the PR's head $sha: want exit ${want##*:}, got $got (stderr: $(cat "$work/$f.err"))")
  done
done
report "$name"

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

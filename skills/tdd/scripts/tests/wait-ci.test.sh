#!/usr/bin/env bash
# Tests for scripts/wait-ci.sh — the resumable CI wait the Draft PR step calls after
# `gh pr ready`: wait a bounded slice, exit 3 while a check is still pending, and be
# called again. Driven against a stub `gh` serving the rollup in $ROLLUP and a stub `date`
# that advances $VERI_CLOCK_STEP seconds a reading.
#
# Contract under test:
#   exit 0  every check completed SUCCESS, NEUTRAL or SKIPPED; an empty rollup is never 0
#   exit 1  a completed check concluded anything else
#   exit 2  gh could not read the checks
#   exit 3  a check is still pending within the bound
#
# Run: scripts/tests/wait-ci.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
WAIT="$HERE/../wait-ci.sh"
PR="https://github.com/o/r/pull/1"

work="$(scratch_dir)"
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
  "api repos/o/r/pulls/1"|"pr view $PR_URL --json "*statusCheckRollup*)
    if [ -n "${GH_FAIL:-}" ]; then echo "HTTP 502: Bad Gateway" >&2; exit 1; fi
    echo >> "$ROLLUP.calls"
    if [ "$1" = pr ] && [ -n "${GH_PR_VIEW_HEAD:-}" ]; then printf '{"headRefOid":"%s","statusCheckRollup":[]}\n' "$GH_PR_VIEW_HEAD"
    elif [ "$1" = pr ]; then cat "$(served '')"; else
      python3 -c 'import json, sys; print(json.dumps({"number": 1, "state": "open", "draft": False, "head": {"sha": json.load(open(sys.argv[1])).get("headRefOid")}}))' "$(served '')"
    fi ;;
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
  "run list"*)
    if [ -n "${GH_RUN_LIST_FAIL:-}" ]; then echo "HTTP 502: Bad Gateway" >&2; exit 1; fi
    python3 - "$GH_RUNS" "$@" <<'P'
import json, sys
runs, args = json.load(open(sys.argv[1])), sys.argv[4:]
opt = lambda *names: next((args[i + 1] for i, a in enumerate(args[:-1]) if a in names), None)
workflow = opt("--workflow", "-w")
if workflow is not None:
    runs = [r for r in runs if workflow in (r["workflowName"], r["path"])]
status = opt("--status", "-s")
if status is not None:
    runs = [r for r in runs if status in (r["status"], r["conclusion"])]
print(json.dumps(runs[:int(opt("--limit", "-L") or 20)]))
P
    ;;
  "api repos/o/r/commits/"*/status)
    if [ -n "${GH_STATUS_FAIL:-}" ]; then echo '{"message":"Not Found"}'; echo "gh: Not Found (HTTP 404)" >&2; exit 1; fi
    cat "$(served .status)" ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
G
chmod +x "$work/bin/date" "$work/bin/gh"

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
statuses = [{"context": r["context"], **({"state": {"EXPECTED": "pending"}.get(r["state"], r["state"].lower())} if "state" in r else {})}
            for r in rows if r["__typename"] == "StatusContext"]
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
  ( cd "$1" && env VERI_POLL=0 VERI_CLOCK_STEP="${CLOCK_STEP:-60}" VERI_CLOCK_LOG="$work/$2.clock" \
      PR_URL="$PR" ROLLUP="$work/$2.json" PATH="$work/bin:$PATH" \
      "$WAIT" "$PR" "${@:4}" >/dev/null 2>"$3" )
  echo $?
}

waited() {
  local dir
  [[ $# -gt 1 ]] || set -- "$1" 1800
  dir="$(scratch_dir)"; mkdir "$dir/.tdd"
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
  if [[ -n "${CLOCK_STEP:-}" ]]; then
    local readings
    readings="$(wc -l < "$work/$1.clock" | tr -d ' ')"
    [[ "$readings" -le 3 ]] || problems+=("$1, bound ${3:-1800}: reached it in $readings clock readings, want at most 3")
  fi
}

expect_never_completes() {
  CLOCK_STEP=900 expect_exit "$1" 3
}

rollup pending.json "$(check COMPLETED SUCCESS),$(check IN_PROGRESS '')"
rollup green.json   "$(check COMPLETED SUCCESS),$(check COMPLETED NEUTRAL),$(check COMPLETED SKIPPED)"
rollup red.json     "$(check COMPLETED SUCCESS),$(check COMPLETED FAILURE)"
rollup empty.json   ""

name="wait-ci.sh exits 3 while a check is pending, 0 when every check completed SUCCESS, NEUTRAL or SKIPPED, 1 on any other conclusion, and never 0 on an empty rollup (#544)"
problems=()
for want in pending:3 green:0 red:1; do
  if [[ "${want##*:}" == 3 ]]; then expect_never_completes "${want%%:*}"; else expect_exit "${want%%:*}" "${want##*:}"; fi
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
got_first="$(again across first 120 120)"
got_second="$(again across second 120 120)"
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
  if [[ "${want##*:}" == 3 ]]; then expect_never_completes "legacy-$st"; else expect_exit "legacy-$st" "${want##*:}"; fi
done
report "$name"

name="wait-ci.sh reads a legacy StatusContext whose state is SUCCESS as a completed green check: beside a pending CheckRun it exits 3, beside only green checks it exits 0 (#544)"
problems=()
rollup legacy-success-pending.json "$(check IN_PROGRESS ''),$(context SUCCESS)"
rollup legacy-success-green.json "$(check COMPLETED SUCCESS),$(context SUCCESS)"
expect_never_completes legacy-success-pending
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
expect_never_completes all-skipped
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
    api_fail=""; [[ "$f" == gql-unread ]] && api_fail=1
    got="$(GH_GRAPHQL="$route" GH_API_FAIL="$api_fail" waited "$f" 60 60)"
    [[ "$got" == "${want##*:}" ]] || problems+=("$route GraphQL, ${want%%:*} checks on the PR's head $sha: want exit ${want##*:}, got $got (stderr: $(cat "$work/$f.err"))")
  done
done
report "$name"

name="wait-ci.sh reads the PR's head through the REST pull only: against a working gh whose pr view reports another head, it still takes the REST head and exits 0 on that sha's green checks (#568)"
problems=()
sha=89abcdef0123456789abcdef0123456789abcdef
sha_head rest-only.json
sha_runs rest-only.json "$(sha_run gates completed '"success"')"
sha_statuses rest-only.json success
got="$(GH_PR_VIEW_HEAD=fedcba9876543210fedcba9876543210fedcba98 waited rest-only 60 60 "$sha")"
[[ "$got" == 0 ]] || problems+=("working gh whose pr view reports another head: want exit 0, got $got (stderr: $(cat "$work/rest-only.err"))")
report "$name"

name="wait-ci.sh reads check-run and status documents larger than 256 KiB and gives the same output and exit code as for small ones, under a python3 that refuses any argument over 128 KiB the way Linux does (#591)"
problems=()
sha=0123456789abcdef0123456789abcdef01234567
argcap_python3_stub "$work/argcap-bin"
for size in short long; do
  sha_head "large-$size.json"
  python3 - "$work/large-$size.json" "$sha" "$size" <<'P'
import json, sys
path, sha, size = sys.argv[1:]
pad = "x" * 8192 if size == "long" else "short"
runs = [{"name": "gates-%d" % n, "head_sha": sha, "status": "completed", "conclusion": "success",
         "output": {"summary": pad}} for n in range(40)]
statuses = [{"context": "legacy-%d" % n, "state": "success", "description": pad} for n in range(40)]
json.dump({"total_count": len(runs), "check_runs": runs}, open(path + ".check-runs", "w"))
json.dump({"state": "success", "sha": sha, "total_count": len(statuses), "statuses": statuses},
          open(path + ".status", "w"))
P
done
for doc in check-runs status; do
  size="$(wc -c < "$work/large-long.json.$doc" | tr -d ' ')"
  [[ "$size" -gt 262144 ]] || problems+=("long .$doc: $size bytes (want >262144)")
done
short_code="$(PATH="$work/argcap-bin:$PATH" waited large-short 60 60 "$sha")"
code="$(PATH="$work/argcap-bin:$PATH" waited large-long 60 60 "$sha")"
[[ "$short_code" == 0 && ! -s "$work/large-short.err" ]] ||
  problems+=("short: want exit 0 and no stderr, got exit $short_code (stderr: $(cat "$work/large-short.err"))")
[[ "$code" == "$short_code" && "$(cat "$work/large-long.err")" == "$(cat "$work/large-short.err")" ]] ||
  problems+=("long: want exit $short_code and the short run's stderr, got exit $code (stderr: $(cat "$work/large-long.err"))")
report "$name"

name="wait-ci.sh reads check-runs spread over three pages through a gh that serves repos/{owner}/{repo}/…?page=N and refuses repositories/{id} with the proxy's 403, and reaches the same verdict as with the same check-runs on one page (#592)"
problems=()
sha=89abcdef0123456789abcdef0123456789abcdef
mkdir -p "$work/proxy-bin"
cat > "$work/proxy-bin/gh" <<'G'
#!/bin/sh
proxy='gh: Numeric-ID repository paths (repositories/{id}/...) are not supported through this proxy. Use repos/{owner}/{repo}/... endpoints instead. (HTTP 403)'
[ "$1" = api ] || { echo "gh stub: unexpected call: gh $*" >&2; exit 1; }
shift
paginate="" slurp="" path=""
for arg in "$@"; do
  case "$arg" in
    --paginate) paginate=1 ;;
    --slurp) slurp=1 ;;
    -*) echo "gh stub: unsupported flag $arg" >&2; exit 1 ;;
    *) path="$arg" ;;
  esac
done
case "$path" in
  *repositories/*) echo "$proxy" >&2; exit 1 ;;
  repos/o/r/pulls/1) printf '{"number": 1, "head": {"sha": "%s"}}\n' "$GH_SHA"; exit 0 ;;
  "repos/o/r/commits/$GH_SHA/status") printf '{"state": "success", "sha": "%s", "total_count": 0, "statuses": []}\n' "$GH_SHA"; exit 0 ;;
  "repos/o/r/commits/$GH_SHA/check-runs"*) ;;
  *) echo "gh stub: unexpected path $path" >&2; exit 1 ;;
esac
page="$(printf '%s\n' "$path" | sed -n 's/.*[?&]page=\([0-9][0-9]*\).*/\1/p')"
[ -n "$page" ] || page=1
if [ -n "$paginate" ] && [ -f "$GH_FX/check-runs-$((page + 1)).json" ]; then echo "$proxy" >&2; exit 1; fi
doc="$GH_FX/check-runs-$page.json"
[ -f "$doc" ] || { doc="$GH_FX/empty.json"; echo '{"total_count": 0, "check_runs": []}' > "$doc"; }
if [ -n "$slurp" ]; then printf '[%s]\n' "$(cat "$doc")"; else cat "$doc"; fi
G
chmod +x "$work/proxy-bin/gh"
paged=(
  "$(sha_run gates-1 completed '"success"'),$(sha_run gates-2 completed '"neutral"')"
  "$(sha_run gates-3 completed '"success"'),$(sha_run gates-4 completed '"skipped"')"
  "$(sha_run gates-5 completed '"failure"')"
)
mkdir -p "$work/proxy-one" "$work/proxy-three"
printf '{"total_count": 5, "check_runs": [%s]}\n' "$(IFS=,; printf '%s' "${paged[*]}")" > "$work/proxy-one/check-runs-1.json"
for i in 0 1 2; do
  printf '{"total_count": 5, "check_runs": [%s]}\n' "${paged[i]}" > "$work/proxy-three/check-runs-$((i + 1)).json"
done
for layout in one three; do
  dir="$(scratch_dir)"; mkdir "$dir/.tdd"; : > "$work/proxy-$layout.clock"
  code="$( ( cd "$dir" && env VERI_POLL=0 VERI_CLOCK_STEP=60 VERI_CLOCK_LOG="$work/proxy-$layout.clock" \
      GH_SHA="$sha" GH_FX="$work/proxy-$layout" PATH="$work/proxy-bin:$work/bin:$PATH" \
      "$WAIT" "$PR" 60 60 "$sha" >/dev/null 2>"$work/proxy-$layout.err" ); echo $? )"
  printf -v "proxy_$layout" '%s' "$code"
done
[[ "$proxy_one" == 1 ]] || problems+=("one page, a failed run among five: want exit 1, got $proxy_one (stderr: $(cat "$work/proxy-one.err"))")
[[ "$proxy_three" == "$proxy_one" ]] || problems+=("three pages, the failed run on the third: want exit $proxy_one as on one page, got $proxy_three (stderr: $(cat "$work/proxy-three.err"))")
report "$name"

name="wait-ci.sh exits 2 naming the sha when a check-runs page after the first fails with a 5xx, the same exit and stderr as when the first and only page read fails (#592)"
problems=()
sha=89abcdef0123456789abcdef0123456789abcdef
mkdir -p "$work/flaky-bin"
cat > "$work/flaky-bin/gh" <<'G'
#!/bin/sh
case "$*" in
  *"check-runs"*"page=$GH_FAIL_PAGE"*) echo "HTTP 502: Bad Gateway" >&2; exit 1 ;;
esac
exec "$GH_REAL" "$@"
G
chmod +x "$work/flaky-bin/gh"
for broken in 1 2; do
  dir="$(scratch_dir)"; mkdir "$dir/.tdd"; : > "$work/flaky-$broken.clock"
  code="$( ( cd "$dir" && env VERI_POLL=0 VERI_CLOCK_STEP=60 VERI_CLOCK_LOG="$work/flaky-$broken.clock" \
      GH_SHA="$sha" GH_FX="$work/proxy-three" GH_FAIL_PAGE="$broken" GH_REAL="$work/proxy-bin/gh" \
      PATH="$work/flaky-bin:$work/bin:$PATH" \
      "$WAIT" "$PR" 60 60 "$sha" >/dev/null 2>"$work/flaky-$broken.err" ); echo $? )"
  printf -v "flaky_$broken" '%s' "$code"
done
[[ "$flaky_1" == 2 ]] || problems+=("first page 502: want exit 2, got $flaky_1 (stderr: $(cat "$work/flaky-1.err"))")
grep -F "could not read the checks of $sha" "$work/flaky-1.err" > /dev/null \
  || problems+=("first page 502: want stderr naming $sha, got: $(cat "$work/flaky-1.err")")
[[ "$flaky_2" == "$flaky_1" ]] || problems+=("second page 502: want exit $flaky_1 as on a failed first page, got $flaky_2 (stderr: $(cat "$work/flaky-2.err"))")
[[ "$(cat "$work/flaky-2.err")" == "$(cat "$work/flaky-1.err")" ]] \
  || problems+=("second page 502: want the failed first page's stderr, got: $(cat "$work/flaky-2.err")")
report "$name"

ci_runs() {
  python3 - "$work/$1" "$2" <<'P'
import json, sys
def run(wf, status, conclusion, seconds, n):
    path = {"CI": ".github/workflows/ci.yml", "Pages": ".github/workflows/pages.yml"}[wf]
    return {"databaseId": 1000 - n, "workflowName": wf, "path": path, "status": status, "conclusion": conclusion,
            "startedAt": "2026-09-28T10:00:00Z", "updatedAt": "2026-09-28T10:%02d:%02dZ" % divmod(seconds, 60)}
json.dump([run(*r, n) for n, r in enumerate(eval(sys.argv[2]))], open(sys.argv[1], "w"))
P
}

expect_deadline() {
  local f="$1" runs="$2" want="$3" why="$4" got first deadline; shift 4
  sha_head "$f.json"
  sha_runs "$f.json" "$(sha_run gates in_progress null)"
  shared "$f"
  got="$(GH_RUNS="$runs" again "$f" first "$@")"
  first="$(head -n 1 "$work/$f.clock")"
  deadline="$(cat "$work/$f/.tdd/ci-deadline-$sha" 2>/dev/null)"
  [[ "$got" == 3 ]] || problems+=("$f: want exit 3, got $got (stderr: $(cat "$work/$f.first.err"))")
  [[ "$deadline" =~ ^[0-9]+$ && "$first" =~ ^[0-9]+$ && $(( deadline - first )) == "$want" ]] \
    || problems+=("$f: want .tdd/ci-deadline-$sha $want s after the first call ($why), got '$deadline' with the first call at '$first' (stderr: $(cat "$work/$f.first.err"))")
}

name="wait-ci.sh given no total-seconds, omitted or empty, records a deadline twice the mean wall time of the CI workflow's 5 most recent success or failure runs after the first call, read through gh run list, skipped, cancelled, in-progress and other workflows' runs not counted (#549)"
problems=()
sha=0123456789abcdef0123456789abcdef01234567
ci_runs gh-runs.json '[("CI", "in_progress", "", 3000), ("Pages", "completed", "success", 3000), ("CI", "completed", "success", 200),
        ("CI", "completed", "cancelled", 3000), ("CI", "completed", "failure", 220), ("CI", "completed", "skipped", 3000),
        ("CI", "completed", "success", 160), ("CI", "completed", "success", 230), ("CI", "completed", "failure", 190),
        ("CI", "completed", "success", 3000)]'
for form in omitted empty; do
  f="computed-$form"
  if [[ "$form" == omitted ]]; then args=(60); else args=(60 "" "$sha"); fi
  expect_deadline "$f" "$work/gh-runs.json" 400 "2 × mean of 200, 220, 160, 230, 190" "${args[@]}"
done
report "$name"

name="wait-ci.sh given no total-seconds averages the CI workflow's 5 most recent success or failure runs even when more than 20 skipped runs come before them, gh run list's default page (#549)"
problems=()
sha=0123456789abcdef0123456789abcdef01234567
ci_runs gh-runs-deep.json '[("CI", "completed", "skipped", 3000)] * 25 + [("CI", "completed", c, s) for c, s in
        [("success", 100), ("failure", 120), ("success", 80), ("success", 110), ("failure", 90)]]'
expect_deadline computed-deep "$work/gh-runs-deep.json" 200 "2 × mean of 100, 120, 80, 110, 90 behind 25 skipped runs" 60
report "$name"

name="wait-ci.sh given no total-seconds averages the CI workflow's 5 most recent success or failure runs even when 50 or more skipped runs come before them (#549)"
problems=()
sha=0123456789abcdef0123456789abcdef01234567
ci_runs gh-runs-deeper.json '[("CI", "completed", "skipped", 3000)] * 60 + [("CI", "completed", c, s) for c, s in
        [("success", 150), ("failure", 130), ("success", 170), ("success", 140), ("failure", 160)]]'
expect_deadline computed-deeper "$work/gh-runs-deeper.json" 300 "2 × mean of 150, 130, 170, 140, 160 behind 60 skipped runs" 60
report "$name"

name="wait-ci.sh given no total-seconds records a deadline no more than 600 s after the first call, however slow the CI workflow's 5 most recent success or failure runs were (#549)"
problems=()
sha=0123456789abcdef0123456789abcdef01234567
ci_runs gh-runs-slow.json '[("CI", "completed", c, s) for c, s in
        [("success", 400), ("failure", 420), ("success", 380), ("success", 450), ("failure", 350)]]'
expect_deadline computed-slow "$work/gh-runs-slow.json" 600 "2 × mean of 400, 420, 380, 450, 350 is 800, capped at 600" 60
report "$name"

name="wait-ci.sh given no total-seconds records a deadline 540 s after the first call when fewer than 5 success or failure CI runs exist, and says on stderr that fewer than 5 runs were found (#549)"
problems=()
sha=0123456789abcdef0123456789abcdef01234567
ci_runs gh-runs-few.json '[("CI", "completed", "success", 100), ("CI", "completed", "cancelled", 3000), ("CI", "completed", "failure", 120),
        ("CI", "completed", "skipped", 3000), ("CI", "completed", "success", 80)]'
expect_deadline computed-few "$work/gh-runs-few.json" 540 "fewer than 5 runs: 100, 120, 80" 60
grep -F "fewer than 5" "$work/computed-few.first.err" > /dev/null \
  || problems+=("computed-few: want stderr saying fewer than 5 runs were found, got: $(cat "$work/computed-few.first.err")")
report "$name"

name="wait-ci.sh given no total-seconds records a deadline 540 s after the first call when gh run list fails, and says on stderr that gh could not answer (#549)"
problems=()
sha=0123456789abcdef0123456789abcdef01234567
GH_RUN_LIST_FAIL=1 expect_deadline computed-gh-fail "$work/gh-runs.json" 540 "gh run list failed" 60
grep -E '^wait-ci\.sh: .*gh( |$)' "$work/computed-gh-fail.first.err" > /dev/null \
    && ! grep -F "fewer than 5" "$work/computed-gh-fail.first.err" > /dev/null \
  || problems+=("computed-gh-fail: want a wait-ci.sh line on stderr saying gh could not answer, not that fewer than 5 runs were found, got: $(cat "$work/computed-gh-fail.first.err")")
report "$name"

finish

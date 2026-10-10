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
      python3 -c '
import json, sys
doc = json.load(open(sys.argv[1]))
pull = {"number": 1, "state": "open", "draft": doc.get("draft", False), "head": {"sha": doc.get("headRefOid")}}
if "mergeable" in doc:
    pull["mergeable"], pull["mergeable_state"] = {"MERGEABLE": (True, "clean"), "CONFLICTING": (False, "dirty"), "UNKNOWN": (None, "unknown")}[doc["mergeable"]]
print(json.dumps(pull))' "$(served '')"
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

rollup pending.json "$(check COMPLETED SUCCESS),$(check IN_PROGRESS '')"
rollup green.json   "$(check COMPLETED SUCCESS),$(check COMPLETED NEUTRAL),$(check COMPLETED SKIPPED)"

sha=89abcdef0123456789abcdef0123456789abcdef

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

name="wait-ci.sh caps a slice-seconds above 540 at 540: a call given slice 900 and total 600 still exits 3 within 540 s of its first clock reading, and the 600 s deadline it records is left for the next call (#549)"
problems=()
sha=0123456789abcdef0123456789abcdef01234567
expect_deadline slice-cap "$work/gh-runs.json" 600 "an explicit total-seconds of 600" 900 600 "$sha"
first="$(head -n 1 "$work/slice-cap.clock")"
last="$(tail -n 1 "$work/slice-cap.clock")"
[[ "$first" =~ ^[0-9]+$ && "$last" =~ ^[0-9]+$ ]] && (( last - first <= 540 )) \
  || problems+=("slice 900: want the call to return within 540 s of its first clock reading, got its last reading at '$last' with the first at '$first'")
report "$name"

name="wait-ci.sh given an explicit total-seconds records that deadline without reading gh run list, but caps a total-seconds above 600 at 600 (#549)"
problems=()
sha=0123456789abcdef0123456789abcdef01234567
GH_RUN_LIST_FAIL=1 expect_deadline explicit-low "$work/gh-runs.json" 300 "an explicit total-seconds of 300" 60 300 "$sha"
GH_RUN_LIST_FAIL=1 expect_deadline explicit-high "$work/gh-runs.json" 600 "an explicit total-seconds of 1200, capped at 600" 60 1200 "$sha"
for f in explicit-low explicit-high; do
  [[ ! -s "$work/$f.first.err" ]] || problems+=("$f: want nothing on stderr, since gh run list is not read, got: $(cat "$work/$f.first.err")")
done
report "$name"

name="wait-ci.sh exits 2 at its first poll, naming the PR and its conflict with the base branch, when GitHub reports the PR mergeable CONFLICTING with no check on its head, rather than waiting out its slice or deadline (#688)"
problems=()
sha=0123456789abcdef0123456789abcdef01234567
printf '{"headRefOid":"%s","mergeable":"CONFLICTING","statusCheckRollup":[]}\n' "$sha" > "$work/conflict.json"
sha_runs conflict.json
got="$(CLOCK_STEP=60 waited conflict 540 600 "$sha")"
[[ "$got" == 2 ]] || problems+=("PR conflicting, no check on $sha: want exit 2, got $got (stderr: $(cat "$work/conflict.err"))")
polls="$(wc -l < "$work/conflict.json.calls" | tr -d ' ')"
[[ "$polls" == 1 ]] || problems+=("PR conflicting, no check on $sha: want 1 poll of the PR, got $polls")
grep -F "$PR" "$work/conflict.err" > /dev/null && grep -F "conflicts with its base branch" "$work/conflict.err" > /dev/null \
  || problems+=("PR conflicting: want a stderr line naming $PR and saying it conflicts with its base branch, got: $(cat "$work/conflict.err")")
report "$name"

name="wait-ci.sh exits 2 at its first poll, naming the PR and its conflict with the base branch, when GitHub reports the PR mergeable CONFLICTING with no check and a head other than the head-sha it was given, rather than holding it pending until its slice ends (#688)"
problems=()
sha=0123456789abcdef0123456789abcdef01234567
want=89abcdef0123456789abcdef0123456789abcdef
printf '{"headRefOid":"%s","mergeable":"CONFLICTING","statusCheckRollup":[]}\n' "$sha" > "$work/conflict-stale.json"
sha_runs conflict-stale.json
got="$(CLOCK_STEP=60 waited conflict-stale 540 600 "$want")"
[[ "$got" == 2 ]] || problems+=("PR conflicting, no check, head $sha, waiting for $want: want exit 2, got $got (stderr: $(cat "$work/conflict-stale.err"))")
polls="$(wc -l < "$work/conflict-stale.json.calls" | tr -d ' ')"
[[ "$polls" == 1 ]] || problems+=("PR conflicting, head $sha, waiting for $want: want 1 poll of the PR, got $polls")
grep -F "$PR" "$work/conflict-stale.err" > /dev/null && grep -F "conflicts with its base branch" "$work/conflict-stale.err" > /dev/null \
  || problems+=("PR conflicting, head $sha, waiting for $want: want a stderr line naming $PR and saying it conflicts with its base branch, got: $(cat "$work/conflict-stale.err")")
report "$name"

name="wait-ci.sh keeps polling a PR GitHub reports mergeable UNKNOWN with no check yet, and ends its slice in exit 3 without naming a conflict (#688)"
problems=()
sha=0123456789abcdef0123456789abcdef01234567
printf '{"headRefOid":"%s","mergeable":"UNKNOWN","statusCheckRollup":[]}\n' "$sha" > "$work/unknown.json"
sha_runs unknown.json
got="$(CLOCK_STEP=60 waited unknown 540 600 "$sha")"
[[ "$got" == 3 ]] || problems+=("PR mergeable unknown, no check on $sha: want exit 3, got $got (stderr: $(cat "$work/unknown.err"))")
polls="$(wc -l < "$work/unknown.json.calls" | tr -d ' ')"
(( polls > 1 )) || problems+=("PR mergeable unknown, no check on $sha: want more than 1 poll of the PR, got $polls")
! grep -F "conflicts with its base branch" "$work/unknown.err" > /dev/null \
  || problems+=("PR mergeable unknown: want no conflict named on stderr, got: $(cat "$work/unknown.err")")
report "$name"

name="wait-ci.sh decides a PR GitHub reports mergeable CONFLICTING whose head already has checks by those checks, as for any PR: 0 green, 1 red, 3 pending within the slice, 2 pending past the recorded deadline, never naming a conflict (#688)"
problems=()
sha=0123456789abcdef0123456789abcdef01234567
conflicting() {
  rollup "$1" "$2" "$sha"
  printf '{"headRefOid":"%s","mergeable":"CONFLICTING","statusCheckRollup":[]}\n' "$sha" > "$work/$1"
}
conflicting conflict-green.json "$(check COMPLETED SUCCESS)"
conflicting conflict-red.json "$(check COMPLETED SUCCESS),$(check COMPLETED FAILURE)"
conflicting conflict-pending.json "$(check IN_PROGRESS '')"
conflicting conflict-across.json "$(check IN_PROGRESS '')"
for want in conflict-green:0 conflict-red:1 conflict-pending:3; do
  f="${want%%:*}"
  got="$(CLOCK_STEP=60 waited "$f" 540 600 "$sha")"
  [[ "$got" == "${want##*:}" ]] || problems+=("$f: want exit ${want##*:}, got $got (stderr: $(cat "$work/$f.err"))")
  ! grep -F "conflicts with its base branch" "$work/$f.err" > /dev/null \
    || problems+=("$f: want no conflict named on stderr, got: $(cat "$work/$f.err")")
done
shared conflict-across
got_first="$(again conflict-across first 120 120 "$sha")"
got_second="$(again conflict-across second 120 120 "$sha")"
[[ "$got_first" == 3 ]] || problems+=("conflict-across first call: want exit 3, got $got_first (stderr: $(cat "$work/conflict-across.first.err"))")
[[ "$got_second" == 2 ]] || problems+=("conflict-across second call past the recorded deadline: want exit 2, got $got_second (stderr: $(cat "$work/conflict-across.second.err"))")
grep -F "still pending past the deadline" "$work/conflict-across.second.err" > /dev/null \
  || problems+=("conflict-across second call: want stderr saying the checks are still pending past the deadline, got: $(cat "$work/conflict-across.second.err")")
report "$name"

name="wait-ci.sh called with no argument, or with an empty <pr-url> and slice 60, exits 2 with nothing on stdout, no gh call, and stderr exactly its usage line"
problems=()
usage_bin="$(scratch_dir)"
cat > "$usage_bin/gh" <<'G'
#!/bin/sh
printf '%s\n' "$*" >> "$GH_LOG"
G
chmod +x "$usage_bin/gh"
want_usage="usage: wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha]"
for args in none empty; do
  : > "$work/usage-$args.gh"
  if [[ "$args" == none ]]; then set --; else set -- "" 60; fi
  ( cd "$work" && env GH_LOG="$work/usage-$args.gh" PATH="$usage_bin:$PATH" \
      "$WAIT" "$@" >"$work/usage-$args.out" 2>"$work/usage-$args.err" )
  got=$?
  [[ "$got" == 2 ]] || problems+=("$args: want exit 2, got $got")
  [[ ! -s "$work/usage-$args.out" ]] || problems+=("$args: want nothing on stdout, got: $(cat "$work/usage-$args.out")")
  [[ ! -s "$work/usage-$args.gh" ]] || problems+=("$args: want no gh call, got: $(cat "$work/usage-$args.gh")")
  [[ "$(cat "$work/usage-$args.err")" == "$want_usage" ]] \
    || problems+=("$args: want stderr exactly '$want_usage', got: '$(cat "$work/usage-$args.err")'")
done
set --
report "$name"

name="wait-ci.sh given a non-numeric slice or a non-numeric total exits 2, never 1, and names the bad argument on stderr (#775)"
problems=()
for bad in slice:abc:100 total:60:xyz; do
  what="${bad%%:*}" rest="${bad#*:}"
  slice="${rest%%:*}" total="${rest#*:}"
  if [[ "$what" == slice ]]; then word="$slice"; else word="$total"; fi
  got="$(waited pending "$slice" "$total")"
  [[ "$got" == 2 ]] || problems+=("non-numeric $what '$word': want exit 2, got $got (stderr: $(cat "$work/pending.err"))")
  grep -F -- "$word" "$work/pending.err" > /dev/null \
    || problems+=("non-numeric $what '$word': want stderr naming '$word', got: '$(cat "$work/pending.err")'")
done
report "$name"

name="wait-ci.sh run through a symlink to the skill directory and from another working directory holding its own .tdd/ exits 3 on a pending check, recording the deadline in that directory's .tdd/ci-deadline-<sha>, and 0 on a green check, as when run in place"
problems=()
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
head_sha=0123456789abcdef0123456789abcdef01234567
for where in inplace linked; do
  for want in pending:3 green:0; do
    f="${want%%:*}"
    dir="$work/$where-$f"; mkdir -p "$dir/.tdd"
    : > "$work/$where-$f.clock"; : > "$work/$f.json.calls"
    if [[ "$where" == linked ]]; then script="$work/linked-skill/scripts/wait-ci.sh"; else script="$WAIT"; fi
    ( cd "$dir" && env VERI_POLL=0 VERI_CLOCK_STEP=900 VERI_CLOCK_LOG="$work/$where-$f.clock" \
        PR_URL="$PR" ROLLUP="$work/$f.json" PATH="$work/bin:$PATH" \
        "$script" "$PR" 540 600 >"$work/$where-$f.out" 2>"$work/$where-$f.err" )
    got=$?
    [[ "$got" == "${want##*:}" ]] || problems+=("$where $f: want exit ${want##*:}, got $got (stderr: $(cat "$work/$where-$f.err"))")
    [[ ! -s "$work/$where-$f.out" ]] || problems+=("$where $f: want nothing on stdout, got: $(cat "$work/$where-$f.out")")
  done
  [[ "$(cat "$work/$where-pending/.tdd/ci-deadline-$head_sha" 2>/dev/null)" == 600 ]] \
    || problems+=("$where pending: want deadline 600 in its working directory's .tdd/ci-deadline-$head_sha, got: '$(cat "$work/$where-pending/.tdd/ci-deadline-$head_sha" 2>&1)'")
  [[ ! -e "$work/$where-green/.tdd/ci-deadline-$head_sha" ]] \
    || problems+=("$where green: want no deadline recorded, got one")
done
cmp -s "$work/inplace-pending.err" "$work/linked-pending.err" \
  || problems+=("pending: stderr differs between in place and linked: $(diff "$work/inplace-pending.err" "$work/linked-pending.err")")
report "$name"

name="#776 wait-ci.sh given a slice-seconds or total-seconds argument that is not a non-negative whole number exits 2 naming that argument on stderr, rather than giving up after one poll with exit 3"
problems=()
for value in 1.5 abc; do
  for which in slice-seconds total-seconds; do
    if [[ "$which" == slice-seconds ]]; then set -- "$value" 100; else set -- 60 "$value"; fi
    got="$(waited pending "$@")"
    [[ "$got" == 2 ]] || problems+=("$which '$value': want exit 2, got $got (stderr: $(cat "$work/pending.err"))")
    grep -F "$which" "$work/pending.err" > /dev/null \
      || problems+=("$which '$value': want stderr naming $which, got: '$(cat "$work/pending.err")'")
  done
done
set --
report "$name"

name="#894 wait-ci.sh called on a draft PR whose checks are pending records no .tdd/ci-deadline-<sha> and exits 3 when its slice runs out"
problems=()
sha=4455667788990011223344556677889900aabbcc
rollup draft.json "$(check IN_PROGRESS '')" "$sha"
printf '{"draft":true,%s\n' "$(cut -c2- < "$work/draft.json")" > "$work/draft.json.new"
mv "$work/draft.json.new" "$work/draft.json"
shared draft
got="$(again draft first 120 600 "$sha")"
[[ "$got" == 3 ]] || problems+=("draft PR: want exit 3, got $got (stderr: $(cat "$work/draft.first.err"))")
[[ ! -e "$work/draft/.tdd/ci-deadline-$sha" ]] \
  || problems+=("draft PR: want no .tdd/ci-deadline-$sha recorded, got '$(cat "$work/draft/.tdd/ci-deadline-$sha")'")
report "$name"

name="#894 after a draft call left no deadline, a call on the same PR once it is ready with the same head sha records the deadline counted from that call, and checks turning green within it exit 0"
problems=()
sha=5566778899001122334455667788990011aabbcc
rollup readied.json "$(check COMPLETED SUCCESS)" "$sha"
for n in 1 2 3 4; do
  rollup "readied.json.$n" "$(check IN_PROGRESS '')" "$sha"
done
for n in 1 2 3; do
  printf '{"draft":true,%s\n' "$(cut -c2- < "$work/readied.json.$n")" > "$work/readied.json.$n.new"
  mv "$work/readied.json.$n.new" "$work/readied.json.$n"
done
shared readied
got="$(again readied first 120 120 "$sha")"
[[ "$got" == 3 ]] || problems+=("draft call: want exit 3, got $got (stderr: $(cat "$work/readied.first.err"))")
got="$(again readied second 120 120 "$sha")"
[[ "$got" == 0 ]] || problems+=("ready call: want exit 0, got $got (stderr: $(cat "$work/readied.second.err"))")
recorded="$(cat "$work/readied/.tdd/ci-deadline-$sha" 2>/dev/null)"
[[ "$recorded" == 300 ]] \
  || problems+=("ready call: want .tdd/ci-deadline-$sha holding 300, its first clock reading 180 plus total 120, got '$recorded'")
report "$name"

name="#894 a ready PR whose checks stay pending past the deadline its first ready call recorded, after a draft call recorded none, still exits 2 naming the deadline"
problems=()
sha=6677889900112233445566778899001122aabbcc
rollup stalled.json "$(check IN_PROGRESS '')" "$sha"
for n in 1 2 3; do
  rollup "stalled.json.$n" "$(check IN_PROGRESS '')" "$sha"
  printf '{"draft":true,%s\n' "$(cut -c2- < "$work/stalled.json.$n")" > "$work/stalled.json.$n.new"
  mv "$work/stalled.json.$n.new" "$work/stalled.json.$n"
done
shared stalled
got="$(again stalled first 120 120 "$sha")"
[[ "$got" == 3 ]] || problems+=("draft call: want exit 3, got $got (stderr: $(cat "$work/stalled.first.err"))")
got="$(again stalled second 120 120 "$sha")"
[[ "$got" == 3 ]] || problems+=("first ready call: want exit 3, got $got (stderr: $(cat "$work/stalled.second.err"))")
got="$(again stalled third 120 120 "$sha")"
[[ "$got" == 2 ]] || problems+=("ready call past the recorded deadline: want exit 2, got $got (stderr: $(cat "$work/stalled.third.err"))")
grep -F "still pending past the deadline recorded for $sha" "$work/stalled.third.err" > /dev/null \
  || problems+=("ready call past the recorded deadline: want stderr saying the checks are still pending past the deadline recorded for $sha, got: $(cat "$work/stalled.third.err")")
report "$name"

finish

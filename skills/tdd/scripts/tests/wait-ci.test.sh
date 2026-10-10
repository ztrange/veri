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

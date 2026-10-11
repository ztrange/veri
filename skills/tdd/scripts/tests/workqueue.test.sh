#!/usr/bin/env bash
# Tests for scripts/workqueue.sh — the only writer of `.tdd/workqueue`, the file that assigns
# issues to named workers and records what happened to each.
#
# Contract under test:
#   workqueue.sh assign <worker> <issue>...  → appends one `<worker>\t<issue>\tqueued\t` line
#                                              per issue to `.tdd/workqueue` in the main
#                                              working tree, in the order given
#   workqueue.sh next <worker>               → prints that worker's first `queued` issue whose
#                                              `## Blocked by` names no open issue, read from
#                                              the VERI_GH_JSON fixtures
#   workqueue.sh start <worker> <issue>      → rewrites that worker's `queued` line for the
#                                              issue to `running`, in place
#   workqueue.sh done <worker> <issue> <sha> → rewrites that worker's `running` line for the
#                                              issue to `merged`, the sha as its detail
#   workqueue.sh park <worker> <issue> <why> → rewrites that worker's `running` line for the
#                                              issue to `parked`, the reason as its detail
#
# Run: scripts/tests/workqueue.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../workqueue.sh"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

seed_queue() {
  mkdir -p "$1/.tdd"
  printf "$2" > "$1/.tdd/workqueue"
}

issues_fixture() {
  mkdir -p "$work/$1.gh"
  cat > "$work/$1.gh/issues.json"
}

repo="$work/next-graphql-refused"
new_repo "$repo"
git -C "$repo" remote add origin https://github.com/ztrange/veri.git
seed_queue "$repo" 'alpha\t20\tqueued\t\nalpha\t22\tqueued\t\n'
issues_fixture next-graphql-refused <<'JSON'
[
  {"number": 5, "title": "open blocker", "labels": [], "body": "", "state": "OPEN"},
  {"number": 6, "title": "closed blocker", "labels": [], "body": "", "state": "CLOSED"},
  {"number": 20, "title": "blocked", "labels": [], "state": "OPEN",
   "body": "Work.\n\n## Blocked by\n\n- #5\n"},
  {"number": 22, "title": "unblocked", "labels": [], "state": "OPEN",
   "body": "Work.\n\n## Blocked by\n\n- #6\n"}
]
JSON
python3 -c '
import json, sys
fx = sys.argv[1]
filler = [{"number": 100 + k, "title": "filler", "labels": [], "body": "", "state": "CLOSED"} for k in range(110)]
issues = filler + json.load(open(fx + "/issues.json"))
json.dump(issues, open(fx + "/issues.json", "w"))
for i in issues:
    i["state"] = i["state"].lower()
    i["body"] = i["body"] or None
json.dump(issues, open(fx + "/rest-issues.json", "w"))
' "$work/next-graphql-refused.gh"
mkdir -p "$work/next-graphql-refused.bin"
cat > "$work/next-graphql-refused.bin/gh" <<'STUB'
#!/bin/sh
refusal='GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)'
if [ "$GH_GRAPHQL" = refused ]; then
  case "$1" in
    issue|pr|repo) echo "HTTP 403: $refusal" >&2; exit 1 ;;
  esac
  case "$*" in
    "api graphql"*) echo "HTTP 403: $refusal" >&2; exit 1 ;;
  esac
fi
case "$*" in
  "issue list"*) cat "$GH_ISSUES"; exit 0 ;;
  *-q*|*--jq*|*--template*) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
  "api "*"repos/{owner}/{repo}/issues"*|"api "*"repos/ztrange/veri/issues"*) ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
case " $* " in *" --paginate "*) paginate=1 ;; *) paginate=0 ;; esac
per_page="$(printf '%s\n' "$*" | sed -n 's/.*[?&]per_page=\([0-9]*\).*/\1/p')"
page="$(printf '%s\n' "$*" | sed -n 's/.*[?&]page=\([0-9]*\).*/\1/p')"
exec python3 -c '
import json, sys
items = json.load(open(sys.argv[1]))
size = min(int(sys.argv[3] or 30), 100)
pages = [items[k:k + size] for k in range(0, len(items), size)] or [[]]
n = int(sys.argv[4] or 1)
sys.stdout.write("".join(json.dumps(p) for p in (pages if sys.argv[2] == "1" else pages[n - 1:n] or [[]])))
' "$GH_REST_ISSUES" "$paginate" "$per_page" "$page"
STUB
chmod +x "$work/next-graphql-refused.bin/gh"
gh_next() {  # gh_next <working|refused>; sets $out and $code
  out="$(cd "$work/next-graphql-refused" && env -u VERI_GH_JSON \
    PATH="$work/next-graphql-refused.bin:$PATH" GH_GRAPHQL="$1" \
    GH_ISSUES="$work/next-graphql-refused.gh/issues.json" \
    GH_REST_ISSUES="$work/next-graphql-refused.gh/rest-issues.json" \
    "$SCRIPT" next alpha 2>"$work/next-graphql-refused.$1.err")" && code=0 || code=$?
}
gh_next working; working="$out" working_code="$code"
gh_next refused
working_err="$(cat "$work/next-graphql-refused.working.err")"
refused_err="$(cat "$work/next-graphql-refused.refused.err")"
if [[ "$working_code" -eq 0 && "$working" == 22 && "$code" -eq "$working_code" && "$out" == "$working" &&
      "$refused_err" == "$working_err" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - next, against a gh that refuses GraphQL with the 403 and answers REST a page at a time, prints the same issue, stderr and exit code as against a working gh, across more than one page of issues (#568)"
  echo "    working gh: exit $working_code (want 0), stdout: '$working' (want '22')"
  echo "    GraphQL refused: exit $code (want $working_code), stdout: '$out' (want '$working')"
  echo "    GraphQL refused stderr: '$refused_err' (want '$working_err')"
fi

finish

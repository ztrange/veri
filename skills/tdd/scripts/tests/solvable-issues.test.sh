#!/usr/bin/env bash
# Unit tests for scripts/solvable-issues.sh — the selection layer. Given a repo's issues
# and open PRs, print the numbers of the issues veri may take right now, one per line, and
# exit 0; print nothing and exit 3 when there are none.
#
# Contract under test:
#   solvable-issues.sh [--repo owner/name]
#   VERI_GH_JSON=<dir>   read <dir>/issues.json and <dir>/prs.json instead of shelling out
#                        to gh, in the shape of
#                          gh issue list --json number,title,labels,body,state
#                          gh pr list    --json body,state
#   VERI_LABEL=<name>    the opt-in label to select on, default `ready-for-agent`. Set but
#                        empty is exit 2.
#
# Run: scripts/tests/solvable-issues.test.sh
set -uo pipefail
unset VERI_GH_DRIVER

HERE="$(cd "$(dirname "$0")" && pwd)"
SOLVABLE="$HERE/../solvable-issues.sh"
REPO_ROOT="$(cd "$HERE/../../../.." && pwd)"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

no_claims="$work/no-claims"
new_repo -b main "$no_claims" >/dev/null 2>&1
cd "$no_claims" || exit 2

fixture() {  # fixture <name> -> path
  local dir="$work/$1"
  mkdir -p "$dir"
  printf '[]\n' > "$dir/prs.json"
  echo "$dir"
}

run() {  # run <fixture-dir> [script args…]; sets $out and $code
  local fixture="$1"; shift
  out="$(cd "$no_claims" && VERI_GH_JSON="$fixture" "$SOLVABLE" "$@" 2>/dev/null)" && code=0 || code=$?
}

label_run() {  # label_run <fixture-dir> <env setting…>; sets $out and $code
  local fixture="$1"; shift
  out="$(cd "$no_claims" && env "$@" VERI_GH_JSON="$fixture" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?
}

refused_run() {  # refused_run <fixture-dir> <env setting…>; sets $refused_out/$refused_err/$refused_code
  local fixture="$1"; shift
  refused_out="$fixture/refused.out" refused_err="$fixture/refused.err"
  env "$@" VERI_GH_JSON="$fixture" "$SOLVABLE" >"$refused_out" 2>"$refused_err" \
    && refused_code=0 || refused_code=$?
}

stubdir="$work/bin"
mkdir -p "$stubdir"
cat > "$stubdir/gh" <<'STUB'
#!/bin/sh
printf '%s\n' "$*" >> "$ARGV_OUT"
case "$1 $2" in
  "issue list") cat "$GH_ISSUES" ;;
  "pr list")    cat "$GH_PRS" ;;
esac
STUB
chmod +x "$stubdir/gh"

gh_run() {  # gh_run <argv-log> [script args...]; sets $out and $code
  local log="$1"; shift
  : > "$log"
  out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL VERI_GH_DRIVER=auto PATH="$stubdir:$PATH" ARGV_OUT="$log" \
         GH_ISSUES="$fx/issues.json" GH_PRS="$fx/prs.json" \
         "$SOLVABLE" "$@" 2>/dev/null)" && code=0 || code=$?
}

procedure_doc="skills/tdd/SKILL.md"


shiftdir="$work/shifting-pages"
mkdir -p "$shiftdir/bin"
python3 -c '
import json, sys
issues = [{"number": n, "title": "issue %d" % n, "state": "open", "body": "## Blocked by\n\nNone.\n",
           "labels": [] if n in (1, 130) else [{"name": "ready-for-agent"}]}
          for n in range(1, 131)]
json.dump(issues, open(sys.argv[1], "w"))
' "$shiftdir/issues.json"
cat > "$shiftdir/bin/gh" <<'STUB'
#!/bin/sh
[ "$1" = api ] || { echo "gh stub: unexpected call: gh $*" >&2; exit 1; }
shift
exec python3 -c '
import json, os, sys
from urllib.parse import parse_qs, urlsplit
fixture, closed_file, args = sys.argv[1], sys.argv[2], sys.argv[3:]
paginate = "--paginate" in args
paths = [a for a in args if not a.startswith("-")]
if len(paths) != 1 or len(paths) + paginate != len(args):
    sys.exit("gh stub: unsupported call: gh api %s" % " ".join(args))
url = urlsplit(paths[0])
query = {k: v[-1] for k, v in parse_qs(url.query).items()}
if url.path.endswith("/pulls"):
    sys.stdout.write("[]")
    sys.exit(0)
if not url.path.endswith("/issues"):
    sys.exit("gh stub: unexpected path %s" % paths[0])
size = min(int(query.get("per_page", 30)), 100)
page = int(query.get("page", 1))
def listing():
    closed = open(closed_file).read().split() if os.path.exists(closed_file) else []
    items = json.load(open(fixture))
    for item in items:
        if str(item["number"]) in closed:
            item["state"] = "closed"
    state = query.get("state", "open")
    items = [i for i in items if state == "all" or i["state"] == state]
    return sorted(items, key=lambda i: i["number"], reverse=query.get("direction", "desc") == "desc")
out = []
while True:
    served = listing()[(page - 1) * size:page * size]
    out.append(json.dumps(served))
    if served and not os.path.exists(closed_file):
        open(closed_file, "w").write("%d\n" % served[0]["number"])
    if not paginate or not served:
        break
    page += 1
sys.stdout.write("".join(out))
' "$GH_SHIFT_ISSUES" "$GH_SHIFT_CLOSED" "$@"
STUB
chmod +x "$shiftdir/bin/gh"

out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$shiftdir/bin:$PATH" \
       GH_SHIFT_ISSUES="$shiftdir/issues.json" GH_SHIFT_CLOSED="$shiftdir/closed" \
       "$SOLVABLE" 2>"$shiftdir/stderr")" && code=0 || code=$?
missing="$(comm -23 <(seq 2 129 | sort) <(printf '%s\n' "$out" | sort) | sort -n | tr '\n' ' ')"
extra="$(comm -13 <(seq 2 129 | sort) <(printf '%s\n' "$out" | sort) | sort -n | tr '\n' ' ')"

{ [[ "$code" == 0 && "$out" == "$(seq 2 129)" ]]; } \
  && ok || no "against a fake gh api whose open-only issue listing shifts between calls — the first issue it serves is closed once page 1 has gone out — solvable-issues.sh still prints every solvable issue the fake holds (#1051) (130 open issues, #2–#129 opted in, closed after page 1: #$(cat "$shiftdir/closed" 2>/dev/null | tr -d '\n'); exit=$code want 0; missing='$missing' want ''; unexpected='$extra' want ''; stderr='$(tr '\n' '|' < "$shiftdir/stderr")')"

wide="$work/shifting-pages-per-page"
mkdir -p "$wide/bin"
cat > "$wide/bin/gh" <<'STUB'
#!/bin/sh
printf '%s\n' "$*" >> "$GH_CALLS"
exec "$GH_SHIFT_STUB" "$@"
STUB
chmod +x "$wide/bin/gh"

out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$wide/bin:$PATH" \
       GH_CALLS="$wide/calls" GH_SHIFT_STUB="$shiftdir/bin/gh" \
       GH_SHIFT_ISSUES="$shiftdir/issues.json" GH_SHIFT_CLOSED="$wide/closed" \
       "$SOLVABLE" 2>"$wide/stderr")" && code=0 || code=$?
missing="$(comm -23 <(seq 2 129 | sort) <(printf '%s\n' "$out" | sort) | sort -n | tr '\n' ' ')"

{ [[ "$code" == 0 && "$out" == "$(seq 2 129)" ]] \
  && grep -F 'issues?state=all&sort=created&direction=asc&per_page=100' "$wide/calls" > /dev/null; } \
  && ok || no "against a fake gh api holding more than 100 open issues whose pages shift between calls, solvable-issues.sh reads the grow-only issue listing at per_page=100 and still prints every solvable issue (#1064) (130 open issues, #2–#129 opted in; exit=$code want 0; missing='$missing' want ''; gh calls='$(tr '\n' '|' < "$wide/calls" 2>/dev/null)' want one naming issues?state=all&sort=created&direction=asc&per_page=100; stderr='$(tr '\n' '|' < "$wide/stderr")')"

onepage="$work/open-issues-one-page"
mkdir -p "$onepage/bin"
python3 -c '
import json, sys
def labels(n):
    names = [] if n % 10 == 0 else ["ready-for-agent"]
    names += ["bug"] if n == 7 else ["priority"] if n == 33 else []
    return [{"name": name} for name in names]
def issue(n, labelled):
    return {"number": n, "title": "issue %d" % n, "state": "open", "body": "## Blocked by\n\nNone.\n",
            "labels": labelled}
json.dump([issue(n, labels(n)) for n in range(1, 41)], open(sys.argv[1], "w"))
json.dump([issue(n, [] if n in (1, 100) else [{"name": "ready-for-agent"}]) for n in range(1, 101)],
          open(sys.argv[2], "w"))
' "$onepage/issues.json" "$onepage/issues100.json"
cp "$wide/bin/gh" "$onepage/bin/gh"

out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$onepage/bin:$PATH" \
       GH_CALLS="$onepage/calls" GH_SHIFT_STUB="$shiftdir/bin/gh" \
       GH_SHIFT_ISSUES="$onepage/issues.json" GH_SHIFT_CLOSED="$onepage/closed" \
       "$SOLVABLE" 2>"$onepage/stderr")" && code=0 || code=$?
issue_calls="$(grep -F '/issues?' "$onepage/calls" || true)"
want="$(printf '%s\n' 33 7; seq 1 40 | grep -v -x -e 7 -e 33 -e 10 -e 20 -e 30 -e 40)"

out100="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$onepage/bin:$PATH" \
          GH_CALLS="$onepage/calls100" GH_SHIFT_STUB="$shiftdir/bin/gh" \
          GH_SHIFT_ISSUES="$onepage/issues100.json" GH_SHIFT_CLOSED="$onepage/closed100" \
          "$SOLVABLE" 2>"$onepage/stderr100")" && code100=0 || code100=$?

{ [[ "$code" == 0 && "$out" == "$want" ]] \
  && [[ "$(grep -c . <<<"$issue_calls")" == 1 ]] \
  && grep -F 'issues?state=open&per_page=100' <<<"$issue_calls" > /dev/null \
  && [[ "$code100" == 0 && "$out100" == "$(seq 2 99)" ]] \
  && grep -F 'issues?state=all&sort=created&direction=asc&per_page=100' "$onepage/calls100" > /dev/null; } \
  && ok || no "against a fake gh api holding fewer than 100 open issues, solvable-issues.sh makes exactly one issue listing request, issues?state=open&per_page=100, and prints the same output as before; an open issue page of 100 items falls back to the grow-only issue listing (#1064) (40 open issues: exit=$code want 0; stdout='$(tr '\n' '|' <<<"$out")' want '$(tr '\n' '|' <<<"$want")'; issue listing calls='$(tr '\n' '|' <<<"$issue_calls")' want exactly one naming issues?state=open&per_page=100; 100 open issues: exit=$code100 want 0; stdout lines=$(grep -c . <<<"$out100") want #2–#99; gh calls='$(tr '\n' '|' < "$onepage/calls100" 2>/dev/null)' want one naming issues?state=all&sort=created&direction=asc&per_page=100; stderr='$(tr '\n' '|' < "$onepage/stderr")|$(tr '\n' '|' < "$onepage/stderr100")')"


prshift="$work/shifting-pr-pages"
mkdir -p "$prshift/bin"
python3 -c '
import json, sys
issues = [{"number": n, "title": "issue %d" % n, "state": "open", "body": "## Blocked by\n\nNone.\n",
           "labels": [{"name": "ready-for-agent"}]} for n in range(1, 11)]
prs = [{"number": n, "state": "open", "body": "Closes #5" if n == 230 else "Tidies something."}
       for n in range(201, 261)]
json.dump(issues, open(sys.argv[1], "w"))
json.dump(prs, open(sys.argv[2], "w"))
' "$prshift/issues.json" "$prshift/prs.json"
cat > "$prshift/bin/gh" <<'STUB'
#!/bin/sh
[ "$1" = api ] || { echo "gh stub: unexpected call: gh $*" >&2; exit 1; }
shift
exec python3 -c '
import json, os, sys
from urllib.parse import parse_qs, urlsplit
issues_file, prs_file, closed_file, args = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
paginate = "--paginate" in args
paths = [a for a in args if not a.startswith("-")]
if len(paths) != 1 or len(paths) + paginate != len(args):
    sys.exit("gh stub: unsupported call: gh api %s" % " ".join(args))
url = urlsplit(paths[0])
query = {k: v[-1] for k, v in parse_qs(url.query).items()}
if url.path.endswith("/issues"):
    fixture, shifts = issues_file, False
elif url.path.endswith("/pulls"):
    fixture, shifts = prs_file, True
else:
    sys.exit("gh stub: unexpected path %s" % paths[0])
size = min(int(query.get("per_page", 30)), 100)
page = int(query.get("page", 1))
def listing():
    closed = open(closed_file).read().split() if shifts and os.path.exists(closed_file) else []
    items = json.load(open(fixture))
    for item in items:
        if str(item["number"]) in closed:
            item["state"] = "closed"
    state = query.get("state", "open")
    items = [i for i in items if state == "all" or i["state"] == state]
    return sorted(items, key=lambda i: i["number"], reverse=query.get("direction", "desc") == "desc")
out = []
while True:
    served = listing()[(page - 1) * size:page * size]
    out.append(json.dumps(served))
    if shifts and served and not os.path.exists(closed_file):
        open(closed_file, "w").write("%d\n" % served[0]["number"])
    if not paginate or not served:
        break
    page += 1
sys.stdout.write("".join(out))
' "$GH_SHIFT_ISSUES" "$GH_SHIFT_PRS" "$GH_SHIFT_CLOSED" "$@"
STUB
chmod +x "$prshift/bin/gh"

out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$prshift/bin:$PATH" \
       GH_SHIFT_ISSUES="$prshift/issues.json" GH_SHIFT_PRS="$prshift/prs.json" GH_SHIFT_CLOSED="$prshift/closed" \
       "$SOLVABLE" 2>"$prshift/stderr")" && code=0 || code=$?

{ [[ "$code" == 0 && "$out" == "$(printf '%s\n' 1 2 3 4 6 7 8 9 10)" ]]; } \
  && ok || no "against a fake gh api whose open-only PR listing shifts between calls — the first PR it serves is closed once page 1 has gone out — an issue claimed by an open PR on a later page is still left out of solvable-issues.sh's output (#1051) (issues #1–#10 opted in, 60 open PRs #201–#260, #230 says 'Closes #5', closed after page 1: PR #$(cat "$prshift/closed" 2>/dev/null | tr -d '\n'); exit=$code want 0; stdout='$(tr '\n' '|' <<<"$out")' want '1|2|3|4|6|7|8|9|10'; stderr='$(tr '\n' '|' < "$prshift/stderr")')"

widepr="$work/shifting-pr-pages-per-page"
mkdir -p "$widepr/bin"
python3 -c '
import json, sys
prs = [{"number": n, "state": "open", "body": "Closes #5" if n == 320 else "Tidies something."}
       for n in range(201, 331)]
json.dump(prs, open(sys.argv[1], "w"))
' "$widepr/prs.json"
cat > "$widepr/bin/gh" <<'STUB'
#!/bin/sh
printf '%s\n' "$*" >> "$GH_CALLS"
exec "$GH_SHIFT_STUB" "$@"
STUB
chmod +x "$widepr/bin/gh"

out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$widepr/bin:$PATH" \
       GH_CALLS="$widepr/calls" GH_SHIFT_STUB="$prshift/bin/gh" \
       GH_SHIFT_ISSUES="$prshift/issues.json" GH_SHIFT_PRS="$widepr/prs.json" GH_SHIFT_CLOSED="$widepr/closed" \
       "$SOLVABLE" 2>"$widepr/stderr")" && code=0 || code=$?

{ [[ "$code" == 0 && "$out" == "$(printf '%s\n' 1 2 3 4 6 7 8 9 10)" ]] \
  && grep -F 'pulls?state=all&sort=created&direction=asc&per_page=100' "$widepr/calls" > /dev/null; } \
  && ok || no "against a fake gh api holding more than 100 open PRs whose pages shift between calls, solvable-issues.sh reads the grow-only PR listing at per_page=100 and still leaves out every issue an open PR claims (#1064) (issues #1–#10 opted in, 130 open PRs #201–#330, #320 says 'Closes #5'; exit=$code want 0; stdout='$(tr '\n' '|' <<<"$out")' want '1|2|3|4|6|7|8|9|10'; gh calls='$(tr '\n' '|' < "$widepr/calls" 2>/dev/null)' want one naming pulls?state=all&sort=created&direction=asc&per_page=100; stderr='$(tr '\n' '|' < "$widepr/stderr")')"

onepr="$work/open-prs-one-page"
mkdir -p "$onepr/bin"
python3 -c '
import json, sys
def pr(n, claim):
    return {"number": n, "state": "open", "body": "Closes #5" if n == claim else "Tidies something."}
json.dump([pr(n, 230) for n in range(201, 241)], open(sys.argv[1], "w"))
json.dump([pr(n, 250) for n in range(201, 301)], open(sys.argv[2], "w"))
' "$onepr/prs.json" "$onepr/prs100.json"
cp "$widepr/bin/gh" "$onepr/bin/gh"

out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$onepr/bin:$PATH" \
       GH_CALLS="$onepr/calls" GH_SHIFT_STUB="$prshift/bin/gh" \
       GH_SHIFT_ISSUES="$prshift/issues.json" GH_SHIFT_PRS="$onepr/prs.json" GH_SHIFT_CLOSED="$onepr/closed" \
       "$SOLVABLE" 2>"$onepr/stderr")" && code=0 || code=$?
pr_calls="$(grep -F '/pulls?' "$onepr/calls" || true)"

out100="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$onepr/bin:$PATH" \
          GH_CALLS="$onepr/calls100" GH_SHIFT_STUB="$prshift/bin/gh" \
          GH_SHIFT_ISSUES="$prshift/issues.json" GH_SHIFT_PRS="$onepr/prs100.json" GH_SHIFT_CLOSED="$onepr/closed100" \
          "$SOLVABLE" 2>"$onepr/stderr100")" && code100=0 || code100=$?

{ [[ "$code" == 0 && "$out" == "$(printf '%s\n' 1 2 3 4 6 7 8 9 10)" ]] \
  && [[ "$(grep -c . <<<"$pr_calls")" == 1 ]] \
  && grep -F 'pulls?state=open&per_page=100' <<<"$pr_calls" > /dev/null \
  && [[ "$code100" == 0 && "$out100" == "$(printf '%s\n' 1 2 3 4 6 7 8 9 10)" ]] \
  && grep -F 'pulls?state=all&sort=created&direction=asc&per_page=100' "$onepr/calls100" > /dev/null; } \
  && ok || no "against a fake gh api holding fewer than 100 open PRs, solvable-issues.sh makes exactly one PR listing request, pulls?state=open&per_page=100, and prints the same output as before; an open PR page of 100 items falls back to the grow-only PR listing (#1064) (issues #1–#10 opted in; 40 open PRs, #230 says 'Closes #5': exit=$code want 0; stdout='$(tr '\n' '|' <<<"$out")' want '1|2|3|4|6|7|8|9|10'; PR listing calls='$(tr '\n' '|' <<<"$pr_calls")' want exactly one naming pulls?state=open&per_page=100; 100 open PRs, #250 says 'Closes #5': exit=$code100 want 0; stdout='$(tr '\n' '|' <<<"$out100")' want '1|2|3|4|6|7|8|9|10'; gh calls='$(tr '\n' '|' < "$onepr/calls100" 2>/dev/null)' want one naming pulls?state=all&sort=created&direction=asc&per_page=100; stderr='$(tr '\n' '|' < "$onepr/stderr")|$(tr '\n' '|' < "$onepr/stderr100")')"

fx="$(fixture graphql-refused)"
cat > "$fx/issues.json" <<'JSON'
[
  {"number": 70, "title": "unblocked", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"},
  {"number": 71, "title": "blocked by an open one", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\n#72\n"},
  {"number": 72, "title": "not opted in", "labels": [], "state": "OPEN", "body": ""},
  {"number": 73, "title": "claimed by an open PR", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"},
  {"number": 74, "title": "priority", "labels": [{"name": "ready-for-agent"}, {"name": "priority"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"}
]
JSON
cat > "$fx/prs.json" <<'JSON'
[{"state": "OPEN", "body": "Draft PR opened by a /tdd run.\n\nCloses #73\n"}]
JSON
python3 -c '
import json, sys
fx = sys.argv[1]
filler = [{"number": 100 + k, "title": "filler", "labels": [], "state": "OPEN", "body": ""} for k in range(110)]
json.dump(filler + json.load(open(fx + "/issues.json")), open(fx + "/issues.json", "w"))
json.dump([{"state": "OPEN", "body": ""}] * 105 + json.load(open(fx + "/prs.json")), open(fx + "/prs.json", "w"))
issues = json.load(open(fx + "/issues.json"))
for i in issues:
    i["state"] = i["state"].lower()
    i["body"] = i["body"] or None
    i["labels"] = [dict(l, id=100 + k, color="ededed") for k, l in enumerate(i["labels"])]
json.dump(issues, open(fx + "/rest-issues.json", "w"))
prs = json.load(open(fx + "/prs.json"))
pulls = [dict(p, number=900 + k, state=p["state"].lower(), draft=True) for k, p in enumerate(prs)]
json.dump(pulls, open(fx + "/rest-pulls.json", "w"))
' "$fx"

refusedir="$work/graphql-refusing-bin"
mkdir -p "$refusedir"
cat > "$refusedir/gh" <<'STUB'
#!/bin/sh
refusal='GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)'
case "$1" in
  issue|pr|repo) echo "HTTP 403: $refusal" >&2; exit 1 ;;
esac
case "$*" in
  "api graphql"*) echo "HTTP 403: $refusal" >&2; exit 1 ;;
  *-q*|*--jq*|*--template*) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
  "api "*"repos/{owner}/{repo}/issues"*) file="$GH_REST_ISSUES" ;;
  "api "*"repos/{owner}/{repo}/pulls"*) file="$GH_REST_PULLS" ;;
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
' "$file" "$paginate" "$per_page" "$page"
STUB
chmod +x "$refusedir/gh"

refused_run() {  # refused_run <gh-dir> [script args...]; sets $out, $err and $code
  local dir="$1"; shift
  out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL PATH="$dir:$PATH" \
         GH_REST_ISSUES="$fx/rest-issues.json" GH_REST_PULLS="$fx/rest-pulls.json" \
         "$SOLVABLE" "$@" 2>"$work/refused-stderr")" && code=0 || code=$?
  err="$(cat "$work/refused-stderr")"
}

gh_run "$work/argv-graphql-working"; working="$out" working_code="$code"

refused_run "$refusedir"

{ [[ "$working_code" == 0 && "$working" == $'74\n70' ]] \
  && [[ "$code" == "$working_code" && "$out" == "$working" ]]; } \
  && ok || no "against a gh that refuses GraphQL with the 403 and answers REST under repos/{owner}/{repo}/ a page at a time, no arguments prints the same issue numbers and exit code as a working gh, across more than one 100-item page (#568) (working gh: exit=$working_code stdout='$(tr '\n' '|' <<<"$working")' want 0 and '74|70'; GraphQL refused: exit=$code stdout='$(tr '\n' '|' <<<"$out")' want the same)"

nameddir="$work/graphql-refusing-named-bin"
mkdir -p "$nameddir"
sed 's#"repos/{owner}/{repo}/#"repos/owner/name/#' "$refusedir/gh" > "$nameddir/gh"
chmod +x "$nameddir/gh"

gh_run "$work/argv-graphql-working-named" --repo owner/name; working="$out" working_code="$code"

refused_run "$nameddir" --repo owner/name

{ [[ "$working_code" == 0 && "$working" == $'74\n70' ]] \
  && [[ "$code" == "$working_code" && "$out" == "$working" ]]; } \
  && ok || no "--repo owner/name, against a gh that refuses GraphQL and answers REST only under repos/owner/name/, prints the same issue numbers and exit code as a working gh (#568) (working gh: exit=$working_code stdout='$(tr '\n' '|' <<<"$working")' want 0 and '74|70'; GraphQL refused: exit=$code stdout='$(tr '\n' '|' <<<"$out")' want the same)"


env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL VERI_GH_DRIVER=auto PATH="$stubdir:$PATH" ARGV_OUT="$work/argv-stderr-working" \
  GH_ISSUES="$fx/issues.json" GH_PRS="$fx/prs.json" \
  "$SOLVABLE" >/dev/null 2>"$work/stderr-working" || true
refused_run "$refusedir"; refused_err="$err"
working_err="$(cat "$work/stderr-working")"

{ [[ -z "$working_err" && -z "$refused_err" ]]; } \
  && ok || no "against a gh that refuses GraphQL with the 403, solvable-issues.sh writes nothing to stderr, the same as against a working gh: the refusal is not passed through to the caller (#568) (working gh stderr='$(tr '\n' '|' <<<"$working_err")' want ''; GraphQL refused stderr='$(tr '\n' '|' <<<"$refused_err")' want '')"

python3 -c '
import json, sys
fx = sys.argv[1]
issues = [
    {"number": 70, "title": "unblocked", "labels": [{"name": "ready-for-agent"}], "state": "open", "body": "## Blocked by\n\nNone.\n"},
    {"number": 75, "title": "a pull request", "labels": [{"name": "ready-for-agent"}], "state": "open", "body": "",
     "pull_request": {"url": "https://api.github.com/repos/owner/name/pulls/75"}},
]
json.dump(issues, open(fx + "/rest-issues-with-pr.json", "w"))
' "$fx"
GH_ISSUES_WITH_PR="$fx/rest-issues-with-pr.json"
out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL PATH="$refusedir:$PATH" \
       GH_REST_ISSUES="$GH_ISSUES_WITH_PR" GH_REST_PULLS="$fx/rest-pulls.json" \
       "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?

{ [[ "$code" == 0 && "$out" == "70" ]]; } \
  && ok || no "against a gh that refuses GraphQL, a /issues REST item carrying pull_request is not counted as a solvable issue even with the opt-in label (#568) (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '70')"



issue_pages=(
  '{"number": 70, "title": "a", "labels": [{"name": "ready-for-agent"}], "body": "## Blocked by\n\n- #74\n", "state": "open"}, {"number": 71, "title": "b", "labels": [{"name": "ready-for-agent"}], "body": "", "state": "closed"}'
  '{"number": 72, "title": "c", "labels": [{"name": "ready-for-agent"}], "body": "", "state": "open"}, {"number": 73, "title": "d", "labels": [{"name": "ready-for-agent"}, {"name": "bug"}], "body": "", "state": "open"}'
  '{"number": 74, "title": "e", "labels": [], "body": "", "state": "open"}, {"number": 75, "title": "f", "labels": [{"name": "ready-for-agent"}, {"name": "priority"}], "body": "", "state": "open"}'
)
pull_pages=(
  '{"number": 1, "state": "closed", "body": "Closes #73"}, {"number": 2, "state": "open", "body": ""}'
  '{"number": 3, "state": "open", "body": ""}, {"number": 4, "state": "closed", "body": ""}'
  '{"number": 5, "state": "open", "body": "Closes #72"}, {"number": 6, "state": "closed", "body": ""}'
)
mkdir -p "$work/three-pages/one" "$work/three-pages/three" "$work/three-pages/bin"
for i in 0 1 2; do
  printf '[%s]\n' "${issue_pages[i]}" > "$work/three-pages/three/issues-$((i + 1)).json"
  printf '[%s]\n' "${pull_pages[i]}" > "$work/three-pages/three/pulls-$((i + 1)).json"
done
(IFS=,; printf '[%s]\n' "${issue_pages[*]}" > "$work/three-pages/one/issues-1.json"
 printf '[%s]\n' "${pull_pages[*]}" > "$work/three-pages/one/pulls-1.json")
cat > "$work/three-pages/bin/gh" <<'STUB'
#!/bin/sh
proxy='gh: Numeric-ID repository paths (repositories/{id}/...) are not supported through this proxy. Use repos/{owner}/{repo}/... endpoints instead. (HTTP 403)'
case "$1" in
  issue|pr|repo) echo "HTTP 403: GitHub GraphQL is not available from Claude Code sessions" >&2; exit 1 ;;
  api) shift ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
paginate="" path=""
for arg in "$@"; do
  case "$arg" in
    --paginate) paginate=1 ;;
    -*) echo "gh stub: unsupported flag $arg" >&2; exit 1 ;;
    *) path="$arg" ;;
  esac
done
case "$path" in
  *repositories/*) echo "$proxy" >&2; exit 1 ;;
  "repos/{owner}/{repo}/issues"*) list=issues ;;
  "repos/{owner}/{repo}/pulls"*) list=pulls ;;
  *) echo "gh stub: unexpected path $path" >&2; exit 1 ;;
esac
case "$path" in
  *state=open*) sed -n 's/^\[\(.*\)\]$/\1/p' "$GH_FX/$list"-*.json | paste -sd, - | sed 's/.*/[&]/'; exit 0 ;;
esac
page="$(printf '%s\n' "$path" | sed -n 's/.*[?&]page=\([0-9][0-9]*\).*/\1/p')"
[ -n "$page" ] || page=1
if [ -f "$GH_FX/$list-$page.json" ]; then cat "$GH_FX/$list-$page.json"; else echo '[]'; fi
if [ -n "$paginate" ] && [ -f "$GH_FX/$list-$((page + 1)).json" ]; then echo "$proxy" >&2; exit 1; fi
exit 0
STUB
chmod +x "$work/three-pages/bin/gh"
three_page_run() {  # three_page_run <one|three>; sets $out and $code
  out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL PATH="$work/three-pages/bin:$PATH" \
         GH_FX="$work/three-pages/$1" "$SOLVABLE" 2>"$work/three-pages/$1.err")" && code=0 || code=$?
}
three_page_run one; one_out="$out" one_code="$code"
three_page_run three

{ [[ "$one_code" == 0 && "$one_out" == $'75\n73' ]] \
  && [[ "$code" == "$one_code" && "$out" == "$one_out" ]]; } \
  && ok || no "against a gh that serves issues and PRs over three pages on repos/{owner}/{repo} and refuses repositories/{id} with the proxy's 403, prints the same issue numbers and exit code as against a single-page fixture holding the same issues and PRs (#592) (single page: exit=$one_code stdout='$(tr '\n' '|' <<<"$one_out")' want 0 and '75|73'; three pages: exit=$code stdout='$(tr '\n' '|' <<<"$out")' want the same; three pages stderr='$(tr '\n' '|' < "$work/three-pages/three.err")')"

finish

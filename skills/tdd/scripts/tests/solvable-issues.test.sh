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

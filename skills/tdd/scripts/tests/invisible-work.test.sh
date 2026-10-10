#!/usr/bin/env bash
# Unit tests for scripts/invisible-work.sh — the read-only maintenance sweep that reports work
# which is not visible, and says which invariant each finding breaks.
#
# Contract under test:
#   invisible-work.sh, run in a clone where `origin` carries a branch no PR was ever
#   opened for → that branch is reported, and the report names its tip, how many commits
#   it is ahead of the default branch, and the number and state of the issue its
#   `tdd/<n>-<slug>` name refers to.
#
# Run: scripts/tests/invisible-work.test.sh
set -uo pipefail
unset VERI_GH_DRIVER

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
INVISIBLE="$HERE/../invisible-work.sh"
work="$(scratch_dir)"

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

unpr_branch_clone() {
  local dir="$1" branch="$2" ahead="$3"
  local src="$dir/src" bare="$dir/origin.git" clone="$dir/clone" i
  mkdir -p "$src"
  new_repo -b main "$src"
  git_q "$src" commit -q --allow-empty -m "initial"
  new_repo --bare -b main "$bare"
  git_q "$src" remote add origin "$bare"
  git_q "$src" push -q -u origin main
  git_q "$src" checkout -q -b "$branch"
  for ((i = 1; i <= ahead; i++)); do
    git_q "$src" commit -q --allow-empty -m "feat: step $i of a run nobody can see (#71)"
  done
  git_q "$src" push -q origin "$branch"
  git clone -q "$bare" "$clone"
  echo "$clone"
}

read_tip() {
  local clone="$1" branch="$2"
  tip="$(git_q "$clone" rev-parse "refs/remotes/origin/$branch" 2>/dev/null)"
  [[ -n "$tip" ]] ||
    problems+=("the fixture put $branch on origin: want a tip sha for refs/remotes/origin/$branch, got none")
}

push_control_branch() {
  local dir="$1" branch="$2"
  git_q "$dir/src" checkout -q -b "$branch" main
  git_q "$dir/src" commit -q --allow-empty -m "chore: work with no PR"
  git_q "$dir/src" push -q origin "$branch"
  git_q "$dir/clone" fetch -q origin
}

fixture() {
  local dir="$1"
  mkdir -p "$dir"
  cat > "$dir/issues.json" <<'JSON'
[{"number": 71, "title": "walkthrough: version the commentary too", "labels": [], "body": "", "state": "OPEN"}]
JSON
  printf '[]\n' > "$dir/prs.json"
  echo "$dir"
}

names() {
  local label="$1" haystack="$2" needle="$3"
  [[ "$haystack" == *"$needle"* ]] ||
    problems+=("$label: want $(printf '%q' "$needle") in the report, got $(printf '%q' "$haystack")")
}

omits() {
  local label="$1" haystack="$2" needle="$3"
  [[ "$haystack" != *"$needle"* ]] ||
    problems+=("$label: want no $(printf '%q' "$needle") in the report, got $(printf '%q' "$haystack")")
}

finding() {
  local report="$1" branch="$2" hits
  mapfile -t hits < <(grep -F "$branch" <<< "$report")
  line="${hits[0]-}"
  rest="$(sed -E 's/[0-9a-f]{7,40}//g' <<< "${line//"$branch"/}")"
}

name="invisible-work.sh: reads gh's issues and PRs as JSON from the VERI_GH_JSON fixture directory, never from gh"
problems=()
branch="tdd/71-walkthrough-version-the-commentary-too"
merged="tdd/4-supervised-leaves"
control="chore/nobody-opened-a-pr"
clone="$(unpr_branch_clone "$work/case12" "$branch" 1)"
push_control_branch "$work/case12" "$merged"
push_control_branch "$work/case12" "$control"
gh_json="$work/case12/gh"
mkdir -p "$gh_json"
cat > "$gh_json/issues.json" <<'JSON'
[
  {
    "state": "OPEN",
    "labels": [],
    "number": 71
  }
]
JSON
cat > "$gh_json/prs.json" <<'JSON'
[
  {
    "state": "MERGED",
    "headRefName": "tdd\/4-supervised-leaves"
  }
]
JSON
mkdir -p "$work/case12/bin"
cat > "$work/case12/bin/gh" <<SH
#!/bin/sh
case "\$1" in
  issue) echo '[{"number": 71, "state": "CLOSED"}]' ;;
  pr) echo '[{"headRefName": "$control", "state": "OPEN"}]' ;;
esac
SH
chmod +x "$work/case12/bin/gh"
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" PATH="$work/case12/bin:$PATH" "$INVISIBLE" 2>/dev/null)"
names "the branch with no PR is still reported" "$out" "$control"
omits "the branch whose PR the fixture says merged is left out" "$out" "$merged"
finding "$out" "$branch"
names "the finding names issue 71's state as the fixture decodes it" "${rest^^}" "OPEN"
omits "the finding does not name the state gh would have given" "${rest^^}" "CLOSED"
report "$name"

ref_state() {
  local clone="$1" origin="$2"
  git -C "$clone" for-each-ref --format='clone %(refname) %(objectname) %(symref)'
  git -C "$clone" worktree list --porcelain
  git -C "$origin" for-each-ref --format='origin %(refname) %(objectname) %(symref)'
  echo "origin HEAD $(git -C "$origin" symbolic-ref HEAD)"
}
name="invisible-work.sh: writes to no ref — the clone's and origin's refs are byte-identical after a run"
problems=()
unpr="chore/nobody-opened-a-pr"
merged="tdd/4-supervised-leaves"
gone="chore/deleted-on-origin"
local_only="tdd/150-a-run-that-never-reached-origin"
clone="$(unpr_branch_clone "$work/case13" "$unpr" 1)"
origin="$work/case13/origin.git"
push_control_branch "$work/case13" "$merged"
push_control_branch "$work/case13" "$gone"
git_q "$clone" branch -q "$merged" "origin/$merged"
git_q "$clone" tag -a -m "v0.1" v0.1 main
git_q "$clone" worktree add -q -b "$local_only" "$work/case13/wt-150" main
git_q "$work/case13/wt-150" commit -q --allow-empty -m "feat: a step nobody pushed (#150)"
git_q "$work/case13/src" push -q origin --delete "$gone"
git_q "$work/case13/src" checkout -q -b "chore/pushed-after-the-fetch" main
git_q "$work/case13/src" commit -q --allow-empty -m "chore: work the clone has not fetched"
git_q "$work/case13/src" push -q origin "chore/pushed-after-the-fetch"
gh_json="$(fixture "$work/case13/gh")"
cat > "$gh_json/prs.json" <<JSON
[{"headRefName": "$merged", "state": "MERGED", "body": "Closes #4"}]
JSON
before="$(ref_state "$clone" "$origin")"
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>/dev/null)"; rc=$?
after="$(ref_state "$clone" "$origin")"
names "the run reported the branch with no PR" "$out" "$unpr"
names "the run reported the local branch origin lacks" "$out" "$local_only"
[[ "$before" == "$after" ]] ||
  problems+=("the refs after a run: want byte-identical to before, got this diff: $(diff <(echo "$before") <(echo "$after") | grep -E '^[<>]' | tr '\n' ';')")
report "$name"

run_both_ghs() {  # run_both_ghs <clone> <gh-fixture-dir> <stderr-file> -> sets working, working_rc, refused, rc
  local clone="$1" fx="$2" err="$3"
  working="$(cd "$clone" && env -u VERI_GH_JSON PATH="$work/case568/bin:$PATH" GH_GRAPHQL=working GH_FX="$fx" "$INVISIBLE" 2>/dev/null)"; working_rc=$?
  refused="$(cd "$clone" && env -u VERI_GH_JSON PATH="$work/case568/bin:$PATH" GH_GRAPHQL=refused GH_FX="$fx" "$INVISIBLE" 2> "$err")"; rc=$?
}

same_under_refusal() {
  local err="$1"
  [[ "$rc" -eq "$working_rc" && "$refused" == "$working" ]] ||
    problems+=("against a gh refusing GraphQL: want exit $working_rc and $(printf '%q' "$working"), got exit $rc and $(printf '%q' "$refused") (stderr: $(tr '\n' '|' < "$err"))")
}

name="invisible-work.sh: against a gh that refuses GraphQL with the 403 and answers REST, prints the same report and exit code as against a working gh (#568)"
problems=()
branch="tdd/71-walkthrough-version-the-commentary-too"
opened="chore/a-pr-is-open"
clone="$(unpr_branch_clone "$work/case568" "$branch" 3)"
push_control_branch "$work/case568" "$opened"
read_tip "$clone" "$branch"
gh_fx="$(fixture "$work/case568/gh")"
cat > "$gh_fx/prs.json" <<JSON
[{"headRefName": "$opened", "state": "OPEN", "body": ""}]
JSON
cat > "$gh_fx/rest-issues.json" <<'JSON'
[{"number": 70, "title": "an earlier page", "labels": [], "body": "", "state": "closed"}][{"number": 71, "title": "walkthrough: version the commentary too", "labels": [], "body": "", "state": "open"}]
JSON
cat > "$gh_fx/rest-pulls.json" <<JSON
[{"number": 4, "state": "closed", "merged_at": null, "body": "", "head": {"ref": "chore/an-earlier-page"}}][{"number": 5, "state": "open", "merged_at": null, "body": "", "head": {"ref": "$opened"}}]
JSON
refusing_gh_stub() {  # refusing_gh_stub <path> < <body> -> an executable gh that refuses GraphQL when GH_GRAPHQL=refused, then runs <body>
  mkdir -p "$(dirname "$1")"
  {
    cat <<'STUB'
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
STUB
    cat
  } > "$1"
  chmod +x "$1"
}

refusing_gh_stub "$work/case568/bin/gh" <<'STUB'
case "$*" in
  "issue list"*) exec cat "$GH_FX/issues.json" ;;
  "pr list"*) exec cat "$GH_FX/prs.json" ;;
  *-q*|*--jq*|*--template*) ;;
  "api "*[?\&]page=[!1]*|"api "*[?\&]page=1?*) echo '[]'; exit 0 ;;
  "api "*"repos/{owner}/{repo}/issues"*) exec cat "$GH_FX/rest-issues.json" ;;
  "api "*"repos/{owner}/{repo}/pulls"*) exec cat "$GH_FX/rest-pulls.json" ;;
esac
echo "gh stub: unexpected call: gh $*" >&2
exit 1
STUB
run_both_ghs "$clone" "$gh_fx" "$work/case568/stderr"
want="invariant 2 (no PR): $branch tip $tip 3 commits ahead, issue #71 OPEN"
[[ "$working_rc" -eq 0 && "$working" == "$want" ]] ||
  problems+=("against a working gh: want exit 0 and $(printf '%q' "$want"), got exit $working_rc and $(printf '%q' "$working")")
same_under_refusal "$work/case568/stderr"
report "$name"

name="invisible-work.sh: against a gh that refuses GraphQL, a local branch whose PR REST reports as \"closed\" is left out, as against a working gh (#568)"
problems=()
closed="chore/test-runner"
clone="$(unpr_branch_clone "$work/case568-closed" "$closed" 1)"
gh_fx="$(fixture "$work/case568-closed/gh")"
cat > "$gh_fx/prs.json" <<JSON
[{"headRefName": "$closed", "state": "CLOSED", "body": ""}]
JSON
printf '[]\n' > "$gh_fx/rest-issues.json"
cat > "$gh_fx/rest-pulls.json" <<JSON
[{"number": 6, "state": "closed", "merged_at": null, "body": "", "head": {"ref": "$closed"}}]
JSON
git_q "$clone" branch -q "$closed" "origin/$closed"
git_q "$work/case568-closed/src" push -q origin --delete "$closed"
git_q "$clone" fetch -q --prune origin
run_both_ghs "$clone" "$gh_fx" "$work/case568-closed/stderr"
[[ "$working_rc" -eq 3 && -z "$working" ]] ||
  problems+=("against a working gh: want exit 3 and empty stdout, got exit $working_rc and $(printf '%q' "$working")")
same_under_refusal "$work/case568-closed/stderr"
report "$name"

exits_2_after_gh() {  # exits_2_after_gh <dir> <cwd> <run> <label> [VAR=value…] -> adds to problems unless <run>, under <dir>/bin/gh, logged a call to $GH_LOG and exited 2
  local dir="$1" cwd="$2" run="$3" label="$4" argv rc
  shift 4
  read -r -a argv <<< "$run"
  : > "$dir/gh.log"
  (cd "$cwd" && env -u GH_REPO -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_PARALLEL \
    -u VERI_MAX_ISSUES PATH="$dir/bin:$PATH" GH_GRAPHQL=refused GH_LOG="$dir/gh.log" "$@" \
    "$HERE/../${argv[0]}" "${argv[@]:1}" > /dev/null 2>&1); rc=$?
  [[ -s "$dir/gh.log" ]] || problems+=("$label: never reached the gh call it fails on")
  [[ "$rc" -eq 2 ]] || problems+=("$label: want exit 2, got $rc")
}

name="every script converted to REST exits 2, never 1, when its REST call fails with a network error, a 404 or a 5xx under a gh that refuses GraphQL (#568)"
problems=()
clone="$(unpr_branch_clone "$work/case568-noanswer" "chore/nobody-opened-a-pr" 1)"
refusing_gh_stub "$work/case568-noanswer/bin/gh" <<'STUB'
echo "$*" >> "$GH_LOG"
echo "$GH_FAILURE" >&2
exit 1
STUB
for failure in "error connecting to api.github.com" "HTTP 404: Not Found (https://api.github.com/repos/o/r/issues/7)" "HTTP 502: Bad Gateway"; do
  for run in "capture-spec.sh 7" "solvable-issues.sh" "workqueue.sh next w1" \
    "tick-issue-criterion.sh 7 criterion" "coverage-blocker.sh 7" "parallel-conductors.sh" \
    "wait-ci.sh https://github.com/o/r/pull/5" "invisible-work.sh"; do
    exits_2_after_gh "$work/case568-noanswer" "$clone" "$run" "$run under '$failure'" GH_FAILURE="$failure"
  done
done
report "$name"

name="coverage-blocker.sh and tick-issue-criterion.sh exit 2, never 1, when a gh that refuses GraphQL answers the issue GET and POST over REST but fails the body PATCH with a 5xx (#568)"
problems=()
refusing_gh_stub "$work/case568-patch/bin/gh" <<'STUB'
case "$*" in
  "api -X PATCH "*) echo "$*" >> "$GH_LOG"; echo "HTTP 502: Bad Gateway" >&2; exit 1 ;;
  "api repos/{owner}/{repo}/issues -f "*) echo "https://github.com/o/r/issues/8" ;;
  "api repos/{owner}/{repo}/issues/7") printf '%s\n' '{"number": 7, "labels": [], "body": "- [ ] the criterion\n\n## Blocked by\n\nNone\n"}' ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
STUB
for run in "coverage-blocker.sh 7" "tick-issue-criterion.sh 7 criterion"; do
  exits_2_after_gh "$work/case568-patch" "$work/case568-patch" "$run" "$run"
done
report "$name"

name="invisible-work.sh reads issues and PR documents larger than 256 KiB and gives the same output and exit code as for small ones, under a python3 that refuses any argument over 128 KiB the way Linux does (#591)"
problems=()
clone="$(unpr_branch_clone "$work/case591-large" "tdd/71-version-the-commentary" 2)"
argcap_python3_stub "$work/case591-large/bin"
mkdir -p "$work/case591-large/short" "$work/case591-large/long"
python3 -c '
import json, sys
def issues(pad):
    return [{"number": n, "title": "issue %d" % n, "labels": [], "state": "OPEN", "body": pad}
            for n in range(40, 80)]
def prs(pad):
    return [{"headRefName": "tdd/%d-other" % n, "state": "MERGED", "body": pad}
            for n in range(100, 140)]
for d, pad in ((sys.argv[1], "short"), (sys.argv[2], "x" * 8192)):
    json.dump(issues(pad), open(d + "/issues.json", "w"))
    json.dump(prs(pad), open(d + "/prs.json", "w"))
' "$work/case591-large/short" "$work/case591-large/long"
for doc in issues prs; do
  size="$(wc -c < "$work/case591-large/long/$doc.json" | tr -d ' ')"
  [[ "$size" -gt 262144 ]] || problems+=("long $doc.json: $size bytes (want >262144)")
done
large_sweep() {  # large_sweep <short|long>; sets $out and $code
  out="$(cd "$clone" && PATH="$work/case591-large/bin:$PATH" VERI_GH_JSON="$work/case591-large/$1" \
    "$INVISIBLE" 2>"$work/case591-large/$1.err")" && code=0 || code=$?
}
large_sweep short; short_out="$out" short_code="$code"
large_sweep long
[[ "$short_code" -eq 0 && "$short_out" == *"tdd/71-version-the-commentary"*"issue #71 OPEN"* ]] ||
  problems+=("short: want exit 0 and a finding naming tdd/71-version-the-commentary and issue #71 OPEN, got exit $short_code and $(printf '%q' "$short_out")")
[[ "$code" == "$short_code" && "$out" == "$short_out" ]] ||
  problems+=("long: want exit $short_code and $(printf '%q' "$short_out"), got exit $code and $(printf '%q' "$out"); stderr: $(cat "$work/case591-large/long.err")")
report "$name"

name="invisible-work.sh: against a gh that serves issues and PRs over three pages on repos/{owner}/{repo} and refuses repositories/{id} with the proxy's 403, prints the same report and exit code as against a single-page fixture holding the same items (#592)"
problems=()
late="tdd/75-an-issue-on-the-last-page"
opened="chore/a-pr-on-the-last-page"
closed="chore/closed-on-page-two"
clone="$(unpr_branch_clone "$work/case592" "$late" 2)"
push_control_branch "$work/case592" "$opened"
git_q "$clone" checkout -q -b "$closed" main
git_q "$clone" commit -q --allow-empty -m "feat: a step whose PR was closed"
git_q "$clone" checkout -q main
read_tip "$clone" "$late"
issue_pages=(
  '{"number": 70, "title": "a", "labels": [], "body": "", "state": "closed"}, {"number": 71, "title": "b", "labels": [], "body": "", "state": "open"}'
  '{"number": 72, "title": "c", "labels": [], "body": "", "state": "closed"}, {"number": 73, "title": "d", "labels": [], "body": "", "state": "open"}'
  '{"number": 74, "title": "e", "labels": [], "body": "", "state": "closed"}, {"number": 75, "title": "f", "labels": [], "body": "", "state": "open"}'
)
pull_pages=(
  '{"number": 1, "state": "closed", "merged_at": null, "body": "", "head": {"ref": "chore/one"}}, {"number": 2, "state": "open", "merged_at": null, "body": "", "head": {"ref": "chore/two"}}'
  "{\"number\": 3, \"state\": \"closed\", \"merged_at\": null, \"body\": \"\", \"head\": {\"ref\": \"$closed\"}}, {\"number\": 4, \"state\": \"open\", \"merged_at\": null, \"body\": \"\", \"head\": {\"ref\": \"chore/four\"}}"
  "{\"number\": 5, \"state\": \"open\", \"merged_at\": null, \"body\": \"\", \"head\": {\"ref\": \"$opened\"}}, {\"number\": 6, \"state\": \"closed\", \"merged_at\": null, \"body\": \"\", \"head\": {\"ref\": \"chore/six\"}}"
)
mkdir -p "$work/case592/one" "$work/case592/three" "$work/case592/bin"
for i in 0 1 2; do
  printf '[%s]\n' "${issue_pages[i]}" > "$work/case592/three/issues-$((i + 1)).json"
  printf '[%s]\n' "${pull_pages[i]}" > "$work/case592/three/pulls-$((i + 1)).json"
done
(IFS=,; printf '[%s]\n' "${issue_pages[*]}" > "$work/case592/one/issues-1.json"
 printf '[%s]\n' "${pull_pages[*]}" > "$work/case592/one/pulls-1.json")
cat > "$work/case592/bin/gh" <<'STUB'
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
page="$(printf '%s\n' "$path" | sed -n 's/.*[?&]page=\([0-9][0-9]*\).*/\1/p')"
[ -n "$page" ] || page=1
if [ -f "$GH_FX/$list-$page.json" ]; then cat "$GH_FX/$list-$page.json"; else echo '[]'; fi
if [ -n "$paginate" ] && [ -f "$GH_FX/$list-$((page + 1)).json" ]; then echo "$proxy" >&2; exit 1; fi
exit 0
STUB
chmod +x "$work/case592/bin/gh"
paged_sweep() {  # paged_sweep <one|three>; sets $out and $code
  out="$(cd "$clone" && env -u VERI_GH_JSON PATH="$work/case592/bin:$PATH" GH_FX="$work/case592/$1" \
    "$INVISIBLE" 2>"$work/case592/$1.err")" && code=0 || code=$?
}
paged_sweep one; one_out="$out" one_code="$code"
paged_sweep three
want="invariant 2 (no PR): $late tip $tip 2 commits ahead, issue #75 OPEN"
[[ "$one_code" -eq 0 && "$one_out" == "$want" ]] ||
  problems+=("single page: want exit 0 and $(printf '%q' "$want"), got exit $one_code and $(printf '%q' "$one_out"); stderr: $(cat "$work/case592/one.err")")
[[ "$code" == "$one_code" && "$out" == "$one_out" ]] ||
  problems+=("three pages: want exit $one_code and $(printf '%q' "$one_out"), got exit $code and $(printf '%q' "$out"); stderr: $(cat "$work/case592/three.err")")
report "$name"

name="invisible-work.sh, run through a symlink to the skill directory and from a subdirectory of the clone, prints the same report, stderr and exit code as when run in place from the clone's root"
problems=()
local_only="tdd/150-a-run-that-never-reached-origin"
clone="$(unpr_branch_clone "$work/case-linked" "tdd/71-walkthrough-version-the-commentary-too" 2)"
gh_json="$(fixture "$work/case-linked/gh")"
git_q "$clone" checkout -q -b "$local_only" main
git_q "$clone" commit -q --allow-empty -m "feat: a step nobody pushed (#150)"
git_q "$clone" checkout -q main
mkdir -p "$clone/sub/dir"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/case-linked/linked-skill"
in_code=0
(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE") \
  > "$work/case-linked/in-place.out" 2> "$work/case-linked/in-place.err" || in_code=$?
linked_code=0
(cd "$clone/sub/dir" && VERI_GH_JSON="$gh_json" "$work/case-linked/linked-skill/scripts/invisible-work.sh") \
  > "$work/case-linked/linked.out" 2> "$work/case-linked/linked.err" || linked_code=$?
[[ "$in_code" == 0 ]] && grep -F "$local_only" "$work/case-linked/in-place.out" > /dev/null ||
  problems+=("in place: want exit 0 with a finding naming $local_only, got exit $in_code; stderr: $(cat "$work/case-linked/in-place.err")")
[[ "$linked_code" == "$in_code" ]] ||
  problems+=("exit through the symlink want $in_code got $linked_code; stderr: $(cat "$work/case-linked/linked.err")")
cmp -s "$work/case-linked/in-place.out" "$work/case-linked/linked.out" ||
  problems+=("stdout through the symlink differs: $(diff "$work/case-linked/in-place.out" "$work/case-linked/linked.out")")
cmp -s "$work/case-linked/in-place.err" "$work/case-linked/linked.err" ||
  problems+=("stderr through the symlink differs: $(diff "$work/case-linked/in-place.err" "$work/case-linked/linked.err")")
report "$name"

name="invisible-work.sh, in a clone with no refs/remotes/origin/HEAD, resolves the default branch from the remote and prints the same report and exit code as when the ref is set (#865)"
problems=()
branch="tdd/71-walkthrough-version-the-commentary-too"
clone="$(unpr_branch_clone "$work/case865" "$branch" 3)"
gh_json="$(fixture "$work/case865/gh")"
set_code=0
set_out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>"$work/case865/set.err")" || set_code=$?
git_q "$clone" config remote.origin.followRemoteHEAD never
git_q "$clone" symbolic-ref --delete refs/remotes/origin/HEAD
unset_code=0
unset_out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>"$work/case865/unset.err")" || unset_code=$?
[[ "$set_code" == 0 && "$set_out" == *"$branch"* ]] ||
  problems+=("with origin/HEAD set: want exit 0 and a finding naming $branch, got exit $set_code and $(printf '%q' "$set_out"); stderr: $(cat "$work/case865/set.err")")
[[ "$unset_code" == "$set_code" && "$unset_out" == "$set_out" ]] ||
  problems+=("with no origin/HEAD: want exit $set_code and $(printf '%q' "$set_out"), got exit $unset_code and $(printf '%q' "$unset_out"); stderr: $(cat "$work/case865/unset.err")")
report "$name"

name="invisible-work.sh, in a clone with no refs/remotes/origin/HEAD and a remote whose default cannot be resolved, exits 2 with stderr naming refs/remotes/origin/HEAD (#865)"
problems=()
clone="$(unpr_branch_clone "$work/case865-unresolvable" "tdd/71-walkthrough-version-the-commentary-too" 1)"
gh_json="$(fixture "$work/case865-unresolvable/gh")"
git_q "$clone" config remote.origin.followRemoteHEAD never
git_q "$clone" symbolic-ref --delete refs/remotes/origin/HEAD
bare="$work/case865-unresolvable/origin.git"
git_q "$bare" update-ref --no-deref HEAD "$(git_q "$bare" rev-parse refs/heads/main)"
code=0
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>"$work/case865-unresolvable/err")" || code=$?
[[ "$code" == 2 ]] && grep -F 'refs/remotes/origin/HEAD' "$work/case865-unresolvable/err" > /dev/null ||
  problems+=("want exit 2 and stderr naming refs/remotes/origin/HEAD, got exit $code and stderr $(printf '%q' "$(cat "$work/case865-unresolvable/err")"); stdout: $(printf '%q' "$out")")
report "$name"

finish

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

#!/usr/bin/env bash
# Unit tests for scripts/invisible-work.sh — the maintenance sweep that reports work which
# is not visible, and says which invariant each finding breaks (issue #197).
#
# Two invariants keep a run's work findable, and both have already been violated silently:
# a branch on `origin` that never got a PR (#195), and a local branch that never reached
# `origin` at all (#191). Nothing checked either; this script is that check, and it reads
# and never writes.
#
# Contract under test, case 1:
#   invisible-work.sh, run in a clone where `origin` carries a branch no PR was ever
#   opened for → that branch is reported, and the report names its tip, how many commits
#   it is ahead of the default branch, and the number and state of the issue its
#   `tdd/<n>-<slug>` name refers to.
#
# What the report LOOKS like is deliberately not pinned. The criterion asks for four facts
# about the branch, not for a layout, so each probe below asks whether the finding line
# carries its fact: the branch name, the tip sha, the count, the issue's number and state.
# The sha and the branch name are cut out of the line before the numbers are read, so a
# count of 3 is the script's answer rather than a digit that happened to fall inside a
# sha (#197's plan, criterion 1).
#
# The exit code is asserted in one case only, case 9: which code goes with a finding and
# which with nothing to report is criterion 4's own step, pinned there and nowhere else.
#
# `origin` is a bare repository on disk. The behaviour under test IS a branch's presence on
# a remote, so there is a real remote — a local path, which costs no network and is what the
# `test` recipe's `protocol.file.allow=always` exists for.
#
# Run: scripts/tests/invisible-work.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
INVISIBLE="$HERE/../invisible-work.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which of the four facts is missing rather than just that the case broke.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# git_q <repo> <args…> — git with an identity of its own, so the suite does not depend on
# whatever user.name/user.email the machine running it happens to carry (CI carries none).
git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

# unpr_branch_clone <dir> <branch> <ahead> — a clone in the shape invariant 2 is broken in:
# `origin` carries <branch>, <ahead> commits past the default branch `main`, and the clone
# knows it only as a remote-tracking ref. Nothing local is off `origin`, so the only thing
# there is to report is the branch with no PR. Prints the clone's path, and nothing else: the
# case reads the tip out of the clone afterwards, because a command substitution runs this in
# a subshell and any variable it set there would be gone by the time the case asked for it.
unpr_branch_clone() {
  # Two statements rather than one: bash makes every name in a `local` local before it
  # assigns any of them, so `src="$dir/src"` on the same line would read `dir` while it is
  # still unset and die under `set -u`.
  local dir="$1" branch="$2" ahead="$3"
  local src="$dir/src" bare="$dir/origin.git" clone="$dir/clone" i
  mkdir -p "$src"
  git init -q -b main "$src"
  git_q "$src" commit -q --allow-empty -m "initial"
  git init -q --bare -b main "$bare"
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

# read_tip <clone> <branch> — set `tip` to <branch>'s tip as `origin` holds it, which is the
# sha the finding has to name. Set as a variable rather than printed, because a command
# substitution would run this in a subshell and lose the problem it records; and checked for
# being there at all: an empty `tip` would make a probe ask whether the empty string is in
# the report, which anything answers.
read_tip() {
  local clone="$1" branch="$2"
  tip="$(git_q "$clone" rev-parse "refs/remotes/origin/$branch" 2>/dev/null)"
  [[ -n "$tip" ]] ||
    problems+=("the fixture put $branch on origin: want a tip sha for refs/remotes/origin/$branch, got none")
}

# push_control_branch <dir> <branch> — a second branch with no PR, pushed to the `origin` of
# the case unpr_branch_clone built in <dir> and fetched into its clone, so a case that
# expects a branch left out can tell "left out" from "the script printed nothing at all".
push_control_branch() {
  local dir="$1" branch="$2"
  git_q "$dir/src" checkout -q -b "$branch" main
  git_q "$dir/src" commit -q --allow-empty -m "chore: work with no PR"
  git_q "$dir/src" push -q origin "$branch"
  git_q "$dir/clone" fetch -q origin
}

# fixture <dir> — the `VERI_GH_JSON` override's two documents, in the exact shape
# solvable-issues.sh already establishes for them: what `gh issue list --json …` and
# `gh pr list --json …` emit. `prs.json` is an empty list because the whole of the case is
# that no PR was ever opened — not open, not closed, not merged. Prints the directory.
fixture() {
  local dir="$1"
  mkdir -p "$dir"
  cat > "$dir/issues.json" <<'JSON'
[{"number": 71, "title": "walkthrough: version the commentary too", "labels": [], "body": "", "state": "OPEN"}]
JSON
  printf '[]\n' > "$dir/prs.json"
  echo "$dir"
}

# names <label> <haystack> <needle> — one probe: the report carries this fact. `%q` on the
# haystack because a report that came back empty, or multi-line, would otherwise break the
# one-problem-per-line shape the case reports in.
names() {
  local label="$1" haystack="$2" needle="$3"
  [[ "$haystack" == *"$needle"* ]] ||
    problems+=("$label: want $(printf '%q' "$needle") in the report, got $(printf '%q' "$haystack")")
}

# omits <label> <haystack> <needle> — the other probe: the report leaves this out. Paired
# with a `names` on a control in the same case, so an empty report cannot pass it alone.
omits() {
  local label="$1" haystack="$2" needle="$3"
  [[ "$haystack" != *"$needle"* ]] ||
    problems+=("$label: want no $(printf '%q' "$needle") in the report, got $(printf '%q' "$haystack")")
}

# finding <report> <branch> — set `line` to the one line of the report that names the
# branch, and `rest` to that line with the branch name and every sha cut out of it: both
# carry digits of their own — a sha is hex, and the branch name carries the issue number —
# so a number left in `rest` is one the script stated. Read with mapfile rather than `head`,
# which would leave the pipeline before EOF and hand grep's SIGPIPE up as the status under
# `pipefail` (#422).
finding() {
  local report="$1" branch="$2" hits
  mapfile -t hits < <(grep -F "$branch" <<< "$report")
  line="${hits[0]-}"
  rest="$(sed -E 's/[0-9a-f]{7,40}//g' <<< "${line//"$branch"/}")"
}

# states <label> <rest> <n> — one probe: <n> stands in <rest> as a number of its own, not as
# the digits of a larger one.
states() {
  local label="$1" rest="$2" n="$3"
  [[ "$rest" =~ (^|[^0-9])$n([^0-9]|$) ]] ||
    problems+=("$label: want $n stated apart from the branch name and the sha, got $(printf '%q' "$rest")")
}

# 1. Issue #197, criterion 1: a branch on `origin` for which no PR has ever been opened is
#    reported, naming the branch, its tip, its commit count ahead of the default branch, and
#    the number and state of the issue its `tdd/<n>-<slug>` name refers to. This is the shape
#    that went unnoticed for two days on 2026-09-12: 12 commits on `origin`, no PR, so
#    neither GitHub's review queue nor solvable-issues.sh listed it, and no human did either.
name="invisible-work.sh: a branch on origin with no PR is reported with its tip, its commits ahead and its issue's state"
problems=()
branch="tdd/71-walkthrough-version-the-commentary-too"
clone="$(unpr_branch_clone "$work/case1" "$branch" 3)"
gh_json="$(fixture "$work/case1/gh")"
read_tip "$clone" "$branch"
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>/dev/null)"

finding "$out" "$branch"
names "the report names the branch" "$out" "$branch"
names "the finding names the branch's tip" "$line" "${tip:0:7}"
# A `3` left in `rest` is the script having counted the commits ahead, and a `71` there is it
# having resolved the slug to an issue rather than just echoing the name.
states "the finding states the commits ahead of main" "$rest" 3
states "the finding names the issue the slug refers to" "$rest" 71
names "the finding names that issue's state" "${rest^^}" "OPEN"
report "$name"

# 2. Issue #197, criterion 1, the other side of it: invariant 2 is a branch with NO PR at all,
#    so a branch on `origin` whose PR is still open is left out of the report — that branch is
#    visible in GitHub's review queue already. A second branch on the same `origin` has no PR
#    and must still be reported: without it, a script that printed nothing, or died before
#    printing, would leave the open-PR branch out too and pass this case for the wrong reason.
#    `prs.json` is what `gh pr list --state all --json headRefName,state` emits.
name="invisible-work.sh: a branch on origin whose PR is still open is left out of the report"
problems=()
branch="tdd/71-walkthrough-version-the-commentary-too"
control="chore/nobody-opened-a-pr"
clone="$(unpr_branch_clone "$work/case2" "$branch" 2)"
push_control_branch "$work/case2" "$control"
gh_json="$(fixture "$work/case2/gh")"
cat > "$gh_json/prs.json" <<JSON
[{"headRefName": "$branch", "state": "OPEN", "body": "Closes #71"}]
JSON
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>/dev/null)"
names "the branch with no PR is still reported" "$out" "$control"
omits "the branch with an open PR is left out" "$out" "$branch"
report "$name"

# 3. Issue #197, criterion 1, when the slug names an issue the repository does not have: a
#    `tdd/<n>-<slug>` branch whose <n> is absent from `issues.json` — a typo'd number, an
#    issue transferred or deleted — is still a branch with no PR, so it is still reported with
#    its tip and its commits ahead, and its issue's state is named as unknown rather than
#    guessed. The lookup that fails must not take the report down with it: a second branch
#    with no PR sorts ahead of it on `origin`, so a script that dies on the lookup has already
#    printed that one — partial output a caller could mistake for the whole report — and
#    leaves a traceback on stderr.
name="invisible-work.sh: a tdd branch whose issue is not in the repository is reported with its issue state unknown, with no traceback"
problems=()
branch="tdd/999-an-issue-nobody-filed"
control="chore/nobody-opened-a-pr"
clone="$(unpr_branch_clone "$work/case3" "$branch" 3)"
push_control_branch "$work/case3" "$control"
gh_json="$(fixture "$work/case3/gh")"
read_tip "$clone" "$branch"
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2> "$work/case3/stderr")"
err="$(cat "$work/case3/stderr")"
names "the other branch with no PR is reported too" "$out" "$control"
names "the report names the branch" "$out" "$branch"
finding "$out" "$branch"
names "the finding names the branch's tip" "$line" "${tip:0:7}"
states "the finding states the commits ahead of main" "$rest" 3
names "the finding names the issue's state as unknown" "${rest,,}" "unknown"
[[ "$err" != *Traceback* ]] ||
  problems+=("the script does not die on the lookup: want no traceback on stderr, got $(printf '%q' "$err")")
report "$name"

# 4. Issue #197, criterion 2: a local branch absent from `origin` is reported, naming the
#    branch, its tip, how many commits it holds that `origin` does not, and the worktree
#    holding it. This is invariant 1 (#191), the shape that nearly lost 71 commits across
#    #150, #163, #170 and #174: runs that lived only in worktrees on one machine, with no
#    branch on `origin` for any of them. The branch is cut from `main`, which `origin` does
#    hold, so of its four commits past the initial one exactly four are ones `origin` lacks.
#    The worktree path is matched as the case wrote it or as the filesystem resolves it,
#    since a temporary directory on macOS sits behind the `/var` -> `/private/var` symlink.
name="invisible-work.sh: a local branch absent from origin is reported with its tip, the commits origin lacks and its worktree"
problems=()
clone="$(unpr_branch_clone "$work/case4" "chore/pushed-already" 1)"
gh_json="$(fixture "$work/case4/gh")"
branch="tdd/150-a-run-that-never-reached-origin"
wt="$work/case4/wt-150"
git_q "$clone" worktree add -q -b "$branch" "$wt" main
for ((i = 1; i <= 4; i++)); do
  git_q "$wt" commit -q --allow-empty -m "feat: step $i of a run only this machine holds (#150)"
done
tip="$(git_q "$wt" rev-parse HEAD)"
wt_real="$(cd "$wt" && pwd -P)"
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>/dev/null)"

finding "$out" "$branch"
names "the report names the branch" "$out" "$branch"
names "the finding names the branch's tip" "$line" "${tip:0:7}"
[[ "$line" == *"$wt"* || "$line" == *"$wt_real"* ]] ||
  problems+=("the finding names the worktree holding it: want $(printf '%q' "$wt_real") in the finding, got $(printf '%q' "$line")")
# The worktree path carries digits of its own (`wt-150`, and the temporary directory's
# name), so it is cut out of the line before `finding` cuts the rest and the count is read.
line="${line//"$wt_real"/}"; line="${line//"$wt"/}"
finding "$line" "$branch"
states "the finding states the commits origin does not hold" "$rest" 4
report "$name"

# 5. Issue #197, criterion 2, the other side of it: invariant 1 is a local branch `origin`
#    does NOT carry, so a local branch that is on `origin` too is left out of the report. The
#    case's local branch shares its name with a branch on `origin` whose PR is open, which
#    keeps it out of the invariant-2 half as well — so any line naming it is an invariant-1
#    finding the filter should have withheld. A second local branch, never pushed, must still
#    be reported: without it, a script that printed nothing would pass this case too.
name="invisible-work.sh: a local branch that origin carries too is left out of the report"
problems=()
pushed="chore/pushed-already"
clone="$(unpr_branch_clone "$work/case5" "$pushed" 1)"
gh_json="$(fixture "$work/case5/gh")"
cat > "$gh_json/prs.json" <<JSON
[{"headRefName": "$pushed", "state": "OPEN", "body": ""}]
JSON
git_q "$clone" branch -q "$pushed" "origin/$pushed"
control="tdd/163-a-run-only-this-machine-holds"
git_q "$clone" branch -q "$control" main
git_q "$clone" checkout -q "$control"
git_q "$clone" commit -q --allow-empty -m "feat: a step nobody pushed (#163)"
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>/dev/null)"
names "the local branch origin lacks is still reported" "$out" "$control"
omits "the local branch origin carries is left out" "$out" "$pushed"
report "$name"

# 6. Issue #197, criterion 2, the worktree clause's other side: the worktree is named "if
#    any", so a local branch origin lacks that no worktree holds is still reported, and its
#    finding says nothing about a worktree — not an empty one, not the clone's own. The
#    branch is committed to from the clone's main checkout, which then returns to `main`,
#    so the branch exists only as a ref, checked out nowhere.
name="invisible-work.sh: a local branch absent from origin that no worktree holds is reported with no worktree"
problems=()
clone="$(unpr_branch_clone "$work/case6" "chore/pushed-already" 1)"
gh_json="$(fixture "$work/case6/gh")"
branch="tdd/170-a-run-checked-out-nowhere"
git_q "$clone" checkout -q -b "$branch" main
git_q "$clone" commit -q --allow-empty -m "feat: a step nobody pushed (#170)"
git_q "$clone" checkout -q main
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>/dev/null)"
finding "$out" "$branch"
names "the report names the branch" "$out" "$branch"
[[ "${line,,}" != *worktree* ]] ||
  problems+=("the finding names no worktree: want no worktree in the finding, got $(printf '%q' "$line")")
report "$name"

# 7. Issue #197, criterion 3: a branch whose PR is merged or closed is residue — a cleanup
#    question, not a violation — so it is left out of the report, and so is the default
#    branch itself, whether `origin` names it as `main` or through its `HEAD` alias. None of
#    the three has a PR open, so a script that filters on open PRs alone would report them.
#    A second branch with no PR must still be reported, so an empty report cannot pass. No
#    branch name in the case carries `main` or `HEAD`, so either word in the report can only
#    be the default branch reported.
name="invisible-work.sh: a branch whose PR is merged or closed is left out of the report, and so is the default branch"
problems=()
merged="tdd/4-supervised-leaves"
closed="chore/test-runner"
control="chore/nobody-opened-a-pr"
clone="$(unpr_branch_clone "$work/case7" "$merged" 2)"
push_control_branch "$work/case7" "$closed"
push_control_branch "$work/case7" "$control"
gh_json="$(fixture "$work/case7/gh")"
cat > "$gh_json/prs.json" <<JSON
[{"headRefName": "$merged", "state": "MERGED", "body": "Closes #4"},
 {"headRefName": "$closed", "state": "CLOSED", "body": ""}]
JSON
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>/dev/null)"
names "the branch with no PR is still reported" "$out" "$control"
omits "the branch with a merged PR is left out" "$out" "$merged"
omits "the branch with a closed PR is left out" "$out" "$closed"
omits "the default branch is left out" "$out" "main"
omits "the default branch's HEAD alias is left out" "$out" "HEAD"
report "$name"

# 8. Issue #197, criterion 3, on the invariant-1 side: a local branch whose PR was merged or
#    closed, and whose branch on `origin` was deleted after it — what GitHub's "delete branch
#    on merge" leaves behind in every clone — is residue too, a cleanup question, so it is not
#    reported as a local branch `origin` lacks. Both branches reached `origin`, got a decided
#    PR, and were then deleted there and pruned here, so each exists only as a local ref. A
#    third local branch, never pushed and with no PR, must still be reported, so an empty
#    report cannot pass. A fourth took the same path but its PR is still OPEN: nothing was
#    decided, so it is not residue, and with its branch gone from `origin` it is exactly the
#    work invariant 1 is about — reported, so a skip keyed on "has any PR" cannot pass.
name="invisible-work.sh: a local branch absent from origin whose PR was merged or closed is not reported as an invariant-1 finding"
problems=()
merged="tdd/4-supervised-leaves"
closed="chore/test-runner"
control="tdd/174-a-run-only-this-machine-holds"
opened="tdd/150-a-run-whose-pr-is-still-open"
clone="$(unpr_branch_clone "$work/case8" "$merged" 2)"
push_control_branch "$work/case8" "$closed"
push_control_branch "$work/case8" "$opened"
gh_json="$(fixture "$work/case8/gh")"
cat > "$gh_json/prs.json" <<JSON
[{"headRefName": "$merged", "state": "MERGED", "body": "Closes #4"},
 {"headRefName": "$closed", "state": "CLOSED", "body": ""},
 {"headRefName": "$opened", "state": "OPEN", "body": "Closes #150"}]
JSON
for branch in "$merged" "$closed" "$opened"; do
  git_q "$clone" branch -q "$branch" "origin/$branch"
done
git_q "$work/case8/src" push -q origin --delete "$merged" "$closed" "$opened"
git_q "$clone" fetch -q --prune origin
git_q "$clone" checkout -q -b "$control" main
git_q "$clone" commit -q --allow-empty -m "feat: a step nobody pushed (#174)"
git_q "$clone" checkout -q main
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>/dev/null)"
names "the local branch with no PR is still reported" "$out" "$control"
names "the local branch whose PR is still open is still reported" "$out" "$opened"
omits "the local branch whose PR was merged is left out" "$out" "$merged"
omits "the local branch whose PR was closed is left out" "$out" "$closed"
report "$name"

# 9. Issue #197, criterion 4: the exit code is the report's first answer. A finding printed
#    is exit 0; nothing to report is exit 3 with nothing on stdout — the healthy state, not an
#    error, and a caller must be able to tell it from a report without reading the text.
#    Three clones: one whose `origin` carries a branch no PR was ever opened for; one whose
#    only finding is a local branch `origin` lacks, since each invariant's half has to answer
#    0 on its own; and one whose only branch off `main` has a merged PR, which is residue and
#    so leaves nothing to report.
name="invisible-work.sh: exits 0 when it printed a finding and 3 with empty stdout when there is nothing to report"
problems=()
clone="$(unpr_branch_clone "$work/case9-finding" "chore/nobody-opened-a-pr" 1)"
gh_json="$(fixture "$work/case9-finding/gh")"
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>/dev/null)"; rc=$?
names "the report names the branch with no PR" "$out" "chore/nobody-opened-a-pr"
[[ "$rc" -eq 0 ]] ||
  problems+=("a finding printed: want exit 0, got $rc")
merged="tdd/4-supervised-leaves"
local_only="tdd/150-a-run-that-never-reached-origin"
clone="$(unpr_branch_clone "$work/case9-local" "$merged" 1)"
gh_json="$(fixture "$work/case9-local/gh")"
cat > "$gh_json/prs.json" <<JSON
[{"headRefName": "$merged", "state": "MERGED", "body": "Closes #4"}]
JSON
git_q "$clone" checkout -q -b "$local_only" main
git_q "$clone" commit -q --allow-empty -m "feat: a step nobody pushed (#150)"
git_q "$clone" checkout -q main
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>/dev/null)"; rc=$?
names "the report names the local branch origin lacks" "$out" "$local_only"
omits "the report leaves out the branch with a merged PR" "$out" "$merged"
[[ "$rc" -eq 0 ]] ||
  problems+=("a local-only branch printed: want exit 0, got $rc")
# The clean clone reuses the local clone's fixture: the same merged PR for the same branch.
clone="$(unpr_branch_clone "$work/case9-clean" "$merged" 1)"
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>/dev/null)"; rc=$?
[[ -z "$out" ]] ||
  problems+=("nothing to report: want empty stdout, got $(printf '%q' "$out")")
[[ "$rc" -eq 3 ]] ||
  problems+=("nothing to report: want exit 3, got $rc")
report "$name"

# 10. Issue #197, criterion 4, the third code: when no answer could be obtained the script
#     exits 2, says why on stderr, and prints nothing on stdout — so a caller can never read a
#     fetch failure as a clean repository, nor a partial report as the whole one. Two clones,
#     one per way of not knowing. In the first, `origin` is gone from disk after the clone was
#     made: its remote-tracking refs still name a branch with no PR, so a script that trusts
#     them without reaching `origin` prints a finding for work it cannot vouch for. In the
#     second, `origin` is fine and `gh` cannot be read: no `VERI_GH_JSON`, and a `gh` stub
#     first on PATH exits 4, gh's own code for an unauthenticated call. The stub says nothing
#     on stderr, so whatever the script leaves there is its own diagnostic, not gh's.
# no_answer <label> <stderr-file> — the three probes of one way of not knowing, read off the
# run just made (`rc`, `out`) and the file its stderr went to: exit 2, nothing on stdout, and
# something on stderr.
no_answer() {
  local label="$1" err
  err="$(cat "$2")"
  [[ "$rc" -eq 2 ]] ||
    problems+=("$label: want exit 2, got $rc")
  [[ -z "$out" ]] ||
    problems+=("$label: want empty stdout, got $(printf '%q' "$out")")
  [[ -n "$err" ]] ||
    problems+=("$label: want a diagnostic on stderr, got none")
}
name="invisible-work.sh: exits 2 with a stderr diagnostic and empty stdout when the remote or gh cannot be read"
problems=()
clone="$(unpr_branch_clone "$work/case10-remote" "chore/nobody-opened-a-pr" 1)"
gh_json="$(fixture "$work/case10-remote/gh")"
rm -rf "$work/case10-remote/origin.git"
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2> "$work/case10-remote/stderr")"; rc=$?
no_answer "origin unreachable" "$work/case10-remote/stderr"
clone="$(unpr_branch_clone "$work/case10-gh" "chore/nobody-opened-a-pr" 1)"
mkdir -p "$work/case10-gh/bin"
printf '#!/bin/sh\nexit 4\n' > "$work/case10-gh/bin/gh"
chmod +x "$work/case10-gh/bin/gh"
out="$(cd "$clone" && env -u VERI_GH_JSON PATH="$work/case10-gh/bin:$PATH" "$INVISIBLE" 2> "$work/case10-gh/stderr")"; rc=$?
no_answer "gh unreadable" "$work/case10-gh/stderr"
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

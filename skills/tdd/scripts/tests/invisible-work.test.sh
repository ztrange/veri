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
# The exit code is not asserted here: which code goes with a finding, with nothing to
# report and with a remote that cannot be read is criterion 4's own step.
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
# The tip as `origin` holds it, which is the sha the finding has to name. Read here rather
# than handed back by the helper, and checked for being there at all: an empty `tip` would
# make the probe below ask whether the empty string is in the report, which anything answers.
tip="$(git_q "$clone" rev-parse "refs/remotes/origin/$branch" 2>/dev/null)"
[[ -n "$tip" ]] ||
  problems+=("the fixture put $branch on origin: want a tip sha for refs/remotes/origin/$branch, got none")
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>/dev/null)"

# The finding line — the one line of the report that names the branch. Read with mapfile
# rather than `head`, which would leave the pipeline before EOF and hand grep's SIGPIPE up
# as the status under `pipefail` (#422).
mapfile -t hits < <(grep -F "$branch" <<< "$out")
line="${hits[0]-}"
names "the report names the branch" "$out" "$branch"
names "the finding names the branch's tip" "$line" "${tip:0:7}"


# The numbers the finding states, read off the line with the sha and the branch name cut
# out of it: both carry digits of their own — a sha is hex, and the branch name carries the
# issue number — so a `3` left in `rest` is the script having counted the commits ahead, and
# a `71` there is it having resolved the slug to an issue rather than just echoing the name.
rest="$(sed -E 's/[0-9a-f]{7,40}//g' <<< "${line//"$branch"/}")"
[[ "$rest" =~ (^|[^0-9])3([^0-9]|$) ]] ||
  problems+=("the finding states the commits ahead of main: want 3 stated apart from the branch name and the sha, got $(printf '%q' "$rest")")
[[ "$rest" =~ (^|[^0-9])71([^0-9]|$) ]] ||
  problems+=("the finding names the issue the slug refers to: want 71 stated apart from the branch name, got $(printf '%q' "$rest")")
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
git_q "$work/case2/src" checkout -q -b "$control" main
git_q "$work/case2/src" commit -q --allow-empty -m "chore: work with no PR"
git_q "$work/case2/src" push -q origin "$control"
git_q "$clone" fetch -q origin
gh_json="$(fixture "$work/case2/gh")"
cat > "$gh_json/prs.json" <<JSON
[{"headRefName": "$branch", "state": "OPEN", "body": "Closes #71"}]
JSON
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2>/dev/null)"
names "the branch with no PR is still reported" "$out" "$control"
[[ "$out" != *"$branch"* ]] ||
  problems+=("the branch with an open PR is left out: want no $(printf '%q' "$branch") in the report, got $(printf '%q' "$out")")
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
git_q "$work/case3/src" checkout -q -b "$control" main
git_q "$work/case3/src" commit -q --allow-empty -m "chore: work with no PR"
git_q "$work/case3/src" push -q origin "$control"
git_q "$clone" fetch -q origin
gh_json="$(fixture "$work/case3/gh")"
tip="$(git_q "$clone" rev-parse "refs/remotes/origin/$branch" 2>/dev/null)"
[[ -n "$tip" ]] ||
  problems+=("the fixture put $branch on origin: want a tip sha for refs/remotes/origin/$branch, got none")
out="$(cd "$clone" && VERI_GH_JSON="$gh_json" "$INVISIBLE" 2> "$work/case3/stderr")"
err="$(cat "$work/case3/stderr")"
names "the other branch with no PR is reported too" "$out" "$control"
names "the report names the branch" "$out" "$branch"
mapfile -t hits < <(grep -F "$branch" <<< "$out")
line="${hits[0]-}"
names "the finding names the branch's tip" "$line" "${tip:0:7}"
rest="$(sed -E 's/[0-9a-f]{7,40}//g' <<< "${line//"$branch"/}")"
[[ "$rest" =~ (^|[^0-9])3([^0-9]|$) ]] ||
  problems+=("the finding states the commits ahead of main: want 3 stated apart from the branch name and the sha, got $(printf '%q' "$rest")")
names "the finding names the issue's state as unknown" "${rest,,}" "unknown"
[[ "$err" != *Traceback* ]] ||
  problems+=("the script does not die on the lookup: want no traceback on stderr, got $(printf '%q' "$err")")
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

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

finish

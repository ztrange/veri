#!/usr/bin/env bash
# Unit tests for scripts/ensure-run-state-ignored.sh — installs veri's run-state rule into
# a target repo's .gitignore, so the first `git add -A` cannot sweep run scratch (leaf logs,
# .rc markers, .prompt files, the blind spec) into history while still committing the ledger.
#
# Contract under test (issue #27):
#   ensure-run-state-ignored.sh [repo-root]   (default: the current directory)
#   afterwards, in that repo, `git check-ignore` says
#     .tdd/develop-red.log  IS ignored      (exit 0)
#     .tdd/issue-7.md       is NOT ignored  (exit 1)
#
# The assertion is on git's own ignore decision, not on the text of .gitignore: the rule is
# order-sensitive (`.tdd/*`, then a negation, then a re-ignore) and grepping for lines would
# pass on an ordering git rejects.
#
# Run: scripts/tests/ensure-run-state-ignored.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ENSURE="$HERE/../ensure-run-state-ignored.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
source "$HERE/lib/harness.sh"

new_repo() {
  mkdir -p "$1"
  git init -q "$1" >/dev/null 2>&1
}

ignored() {
  git -C "$1" check-ignore -q "$2" 2>/dev/null
}

repo="$work/fresh"
new_repo "$repo"

"$ENSURE" "$repo" >/dev/null 2>&1

ignored "$repo" .tdd/develop-red.log && log_code=0 || log_code=$?
ignored "$repo" .tdd/issue-7.md && ledger_code=0 || ledger_code=$?

{ [[ "$log_code" == 0 ]] && [[ "$ledger_code" == 1 ]]; } \
  && ok || no "no .gitignore: creates one ignoring .tdd/develop-red.log but not .tdd/issue-7.md (develop-red.log=$log_code want 0 ignored, issue-7.md=$ledger_code want 1 not ignored)"

repo="$work/twice"
new_repo "$repo"

"$ENSURE" "$repo" >/dev/null 2>&1
before="$work/twice.gitignore.before"
cp "$repo/.gitignore" "$before"

out="$("$ENSURE" "$repo" 2>/dev/null)" && code=0 || code=$?
cmp -s "$before" "$repo/.gitignore" && same=0 || same=$?

{ [[ "$same" == 0 ]] && [[ "$code" == 0 ]] && [[ "$out" == *"already present"* ]]; } \
  && ok || no "already carries the rule: leaves .gitignore byte-identical and reports already present (cmp=$same want 0 identical, exit=$code want 0, stdout='$out' want it to contain 'already present')"

repo="$work/unrelated"
new_repo "$repo"
printf 'node_modules/\n*.log' > "$repo/.gitignore"

out="$("$ENSURE" "$repo" 2>/dev/null)" && code=0 || code=$?

ignored "$repo" node_modules/x && modules_code=0 || modules_code=$?
ignored "$repo" debug.log && debuglog_code=0 || debuglog_code=$?
ignored "$repo" .tdd/develop-red.log && log_code=0 || log_code=$?
ignored "$repo" .tdd/issue-7.md && ledger_code=0 || ledger_code=$?

{ [[ "$modules_code" == 0 ]] && [[ "$debuglog_code" == 0 ]] \
  && [[ "$log_code" == 0 ]] && [[ "$ledger_code" == 1 ]] \
  && [[ "$code" == 0 ]] && [[ "$out" == *"added"* ]]; } \
  && ok || no "unrelated .gitignore: keeps every existing line and reports added (node_modules/x=$modules_code want 0 still ignored, debug.log=$debuglog_code want 0 still ignored, develop-red.log=$log_code want 0 ignored, issue-7.md=$ledger_code want 1 not ignored, exit=$code want 0, stdout='$out' want it to contain 'added')"

refuses() {
  local slug="$1" why="$2"; shift 2
  local repo="$work/$slug" before="$work/$slug.before" err="$work/$slug.stderr" code same diag
  new_repo "$repo"
  printf '%s\n' "$@" > "$repo/.gitignore"
  cp "$repo/.gitignore" "$before"

  "$ENSURE" "$repo" >/dev/null 2>"$err" && code=0 || code=$?
  cmp -s "$before" "$repo/.gitignore" && same=0 || same=$?
  [[ -s "$err" ]] && diag=0 || diag=1

  { [[ "$code" != 0 ]] && [[ "$diag" == 0 ]] && [[ "$same" == 0 ]]; } \
    && ok || no "$slug rule ($why): refuses with a diagnostic and touches nothing (exit=$code want non-zero, stderr-non-empty=$diag want 0, cmp=$same want 0 identical)"
}

refuses partial 'only .tdd/issue-*-spec.md' '.tdd/issue-*-spec.md'

refuses misordered 'negation last' '.tdd/*' '.tdd/issue-*-spec.md' '!.tdd/issue-*.md'

repo="$work/trailing-newline"
new_repo "$repo"
printf 'node_modules/\n' > "$repo/.gitignore"
want="$work/trailing-newline.want"
printf 'node_modules/\n.tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-spec.md\n' > "$want"

out="$("$ENSURE" "$repo" 2>/dev/null)" && code=0 || code=$?
cmp -s "$want" "$repo/.gitignore" && same=0 || same=$?

{ [[ "$same" == 0 ]] && [[ "$code" == 0 ]] && [[ "$out" == *"added"* ]]; } \
  && ok || no "newline-terminated .gitignore: appends the block with no blank line before it and reports added (cmp=$same want 0 identical to node_modules/ + the three rule lines, exit=$code want 0, stdout='$out' want it to contain 'added')"

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

repo="$work/caller"
mkdir -p "$repo"
git init -q -b main "$repo" >/dev/null 2>&1
git_q "$repo" commit -q --allow-empty -m "initial" >/dev/null 2>&1
git_q "$repo" worktree add "$repo/.tdd/wt/1" -b tdd/1 >/dev/null 2>&1

"$ENSURE" "$repo/.tdd/wt/1" >/dev/null 2>&1
git_q "$repo/.tdd/wt/1" add .gitignore >/dev/null 2>&1
git_q "$repo/.tdd/wt/1" commit -q -m "chore: ignore veri run state (#1)" >/dev/null 2>&1

caller_status="$(git -C "$repo" status --porcelain 2>&1)"
[[ -d "$repo/.tdd/wt/1" ]] && wt_there=0 || wt_there=1

{ [[ -z "$caller_status" ]] && [[ "$wt_there" == 0 ]]; } \
  && ok || no "caller's checkout: git status --porcelain is empty while the worktree at .tdd/wt/1 exists (status='$caller_status' want empty, worktree-present=$wt_there want 0)"

wt="$repo/.tdd/wt/1"
ignored "$wt" .tdd/develop-red.log && log_code=0 || log_code=$?
ignored "$wt" .tdd/issue-1.md && ledger_code=0 || ledger_code=$?

{ [[ "$log_code" == 0 ]] && [[ "$ledger_code" == 1 ]]; } \
  && ok || no "worktree with the rule in info/exclude too: still ignores .tdd/develop-red.log and still does not ignore the ledger (develop-red.log=$log_code want 0 ignored, issue-1.md=$ledger_code want 1 not ignored)"

repo="$work/twice-both"
mkdir -p "$repo"
git init -q -b main "$repo" >/dev/null 2>&1
git_q "$repo" commit -q --allow-empty -m "initial" >/dev/null 2>&1
git_q "$repo" worktree add "$repo/.tdd/wt/1" -b tdd/1 >/dev/null 2>&1
wt="$repo/.tdd/wt/1"
exclude="$repo/.git/info/exclude"

"$ENSURE" "$wt" >/dev/null 2>&1
cp "$wt/.gitignore" "$work/twice-both.gitignore.before"
cp "$exclude" "$work/twice-both.exclude.before"

"$ENSURE" "$wt" >/dev/null 2>&1 && code=0 || code=$?
cmp -s "$work/twice-both.gitignore.before" "$wt/.gitignore" && gi_same=0 || gi_same=$?
cmp -s "$work/twice-both.exclude.before" "$exclude" && ex_same=0 || ex_same=$?

{ [[ "$gi_same" == 0 ]] && [[ "$ex_same" == 0 ]] && [[ "$code" == 0 ]]; } \
  && ok || no "second run on the same repo: leaves the worktree .gitignore and info/exclude byte-identical and exits 0 (.gitignore cmp=$gi_same want 0 identical, info/exclude cmp=$ex_same want 0 identical, exit=$code want 0)"

finish

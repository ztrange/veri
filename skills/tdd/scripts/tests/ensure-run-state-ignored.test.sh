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
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# new_repo <path> — an empty git repo at <path>, so check-ignore has a repo to answer within.
new_repo() {
  mkdir -p "$1"
  git init -q "$1" >/dev/null 2>&1
}

# ignored <repo> <path> — git's verdict on one path, as an exit code we can assert on.
# 0 = ignored, 1 = not ignored, anything else = git errored (a broken test, not a verdict).
ignored() {
  git -C "$1" check-ignore -q "$2" 2>/dev/null
}

# 1. a repo with no .gitignore at all gets one that separates run scratch from the ledger
repo="$work/fresh"
new_repo "$repo"

"$ENSURE" "$repo" >/dev/null 2>&1

ignored "$repo" .tdd/develop-red.log && log_code=0 || log_code=$?
ignored "$repo" .tdd/issue-7.md && ledger_code=0 || ledger_code=$?

{ [[ "$log_code" == 0 ]] && [[ "$ledger_code" == 1 ]]; } \
  && ok || no "no .gitignore: creates one ignoring .tdd/develop-red.log but not .tdd/issue-7.md (develop-red.log=$log_code want 0 ignored, issue-7.md=$ledger_code want 1 not ignored)"

# 2. a repo that already carries the rule — running it a second time changes nothing and says so
repo="$work/twice"
new_repo "$repo"

"$ENSURE" "$repo" >/dev/null 2>&1
before="$work/twice.gitignore.before"
cp "$repo/.gitignore" "$before"

out="$("$ENSURE" "$repo" 2>/dev/null)" && code=0 || code=$?
cmp -s "$before" "$repo/.gitignore" && same=0 || same=$?

{ [[ "$same" == 0 ]] && [[ "$code" == 0 ]] && [[ "$out" == *"already present"* ]]; } \
  && ok || no "already carries the rule: leaves .gitignore byte-identical and reports already present (cmp=$same want 0 identical, exit=$code want 0, stdout='$out' want it to contain 'already present')"

# 3. a repo whose .gitignore already has unrelated rules — they survive, and the run gets reported.
# The seed deliberately ends WITHOUT a trailing newline: that is where a naive append fuses `*.log`
# and `.tdd/*` into one line, silently destroying both rules. We assert the old rules still *work*
# (via git, not by grepping) rather than that the bytes are still somewhere in the file.
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

# refuses <slug> <why> <gitignore-line>... — seed a repo with exactly those .gitignore lines and
# assert the refusal in full: non-zero exit, a diagnostic on stderr, and the file left byte for
# byte as it was. Both un-appendable .gitignores below fail the same three ways, so the assertion
# is written once; <slug> names the scratch repo and <why> says what is wrong with that seed.
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

# 4. a repo whose .gitignore carries ONLY the rule's last line — a partial block, not the rule.
# Appending to it cannot repair it (`.tdd/*` after the spec re-ignore reads differently).
refuses partial 'only .tdd/issue-*-spec.md' '.tdd/issue-*-spec.md'

# 5. a repo whose .gitignore carries all three lines but in an order git reads differently:
# the negation last, so `!.tdd/issue-*.md` un-ignores the spec the line above just re-ignored.
# Every line is present, yet the rule is not — so this is the same refusal as case 4, and the
# script must not mistake "all three lines somewhere" for "the block, in order".
refuses misordered 'negation last' '.tdd/*' '.tdd/issue-*-spec.md' '!.tdd/issue-*.md'

# 6. the newline guard's other branch: a seed that ALREADY ends in a newline must not gain a blank
# line before the block. Case 3 pins the newline-less seed via git; this one has to assert exact
# bytes, because a stray empty line changes nothing git would report — `check-ignore` answers the
# same either way — and would only show up as noise in someone's .gitignore. So build the file we
# expect with printf and compare with cmp.
repo="$work/trailing-newline"
new_repo "$repo"
printf 'node_modules/\n' > "$repo/.gitignore"
want="$work/trailing-newline.want"
printf 'node_modules/\n.tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-spec.md\n' > "$want"

out="$("$ENSURE" "$repo" 2>/dev/null)" && code=0 || code=$?
cmp -s "$want" "$repo/.gitignore" && same=0 || same=$?

{ [[ "$same" == 0 ]] && [[ "$code" == 0 ]] && [[ "$out" == *"added"* ]]; } \
  && ok || no "newline-terminated .gitignore: appends the block with no blank line before it and reports added (cmp=$same want 0 identical to node_modules/ + the three rule lines, exit=$code want 0, stdout='$out' want it to contain 'added')"

# 7. the caller's checkout — the primary clone the conductor was invoked from — stays clean while
# the run's worktree sits under .tdd/ (issue #72). The rule the script writes into the worktree's
# .gitignore is committed on the issue branch, so the primary checkout, still on `main`, never sees
# it and keeps reporting `?? .tdd/`; the next preflight then refuses to start. The assertion is on
# `git status --porcelain` in the primary checkout, because that is the command preflight runs.
#
# The seed reproduces the conductor's own step 1.4 in order: a repo with one commit and no
# .gitignore, a worktree at .tdd/wt/1 on its own branch, the script, then the commit of what it
# wrote — on the worktree's branch only, exactly as the conductor does it.
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

# 8. the #27 contract survives the #72 fix, inside the worktree. Cases 1 and 3 pin it in a plain
# repo whose only ignore source is .gitignore; here the shared info/exclude carries `.tdd/*` as well,
# and that line would ignore the ledger on its own. It must not: a .gitignore in the path's own
# directory outranks info/exclude, so the committed `!.tdd/issue-*.md` still un-ignores the ledger.
# Same repo as case 7 — the point is that the fix that emptied the caller's status changed nothing
# about what the worktree reports.
wt="$repo/.tdd/wt/1"
ignored "$wt" .tdd/develop-red.log && log_code=0 || log_code=$?
ignored "$wt" .tdd/issue-1.md && ledger_code=0 || ledger_code=$?

{ [[ "$log_code" == 0 ]] && [[ "$ledger_code" == 1 ]]; } \
  && ok || no "worktree with the rule in info/exclude too: still ignores .tdd/develop-red.log and still does not ignore the ledger (develop-red.log=$log_code want 0 ignored, issue-1.md=$ledger_code want 1 not ignored)"

# 9. the script is idempotent across BOTH destinations. Case 2 pins the .gitignore half in a plain
# repo; the exclude file is the half a second run can quietly double, because nothing commits it and
# nothing reads it back — the duplicate would sit in the primary checkout's ignore rules forever,
# growing by three lines per conductor run. A run is resumable (the conductor re-runs step 1.4 on a
# resume), so "run it twice" is the normal case, not a pathological one.
#
# Same worktree layout as case 7, freshly built: the exclude file lives under the *common* git dir,
# which for the linked worktree at .tdd/wt/1 is the primary's own $repo/.git — so one write from
# inside the worktree has to stay one block when seen from there.
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

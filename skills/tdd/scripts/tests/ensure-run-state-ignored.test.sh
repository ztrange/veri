#!/usr/bin/env bash
# Unit tests for scripts/ensure-run-state-ignored.sh — installs veri's run-state rule into
# a target repo's .gitignore.
#
# Contract under test:
#   ensure-run-state-ignored.sh [repo-root]   (default: the current directory)
#   afterwards, in that repo, `git check-ignore` says
#     .tdd/develop-red.log  IS ignored      (exit 0)
#     .tdd/issue-7.md       is NOT ignored  (exit 1)
#
# Run: scripts/tests/ensure-run-state-ignored.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ENSURE="$HERE/../ensure-run-state-ignored.sh"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

make_repo() {
  mkdir -p "$1"
  new_repo "$1" >/dev/null 2>&1
}

ignored() {
  git -C "$1" check-ignore -q "$2" 2>/dev/null
}

repo="$work/fresh"
make_repo "$repo"

"$ENSURE" "$repo" >/dev/null 2>&1

ignored "$repo" .tdd/develop-red.log && log_code=0 || log_code=$?
ignored "$repo" .tdd/issue-7.md && ledger_code=0 || ledger_code=$?

{ [[ "$log_code" == 0 ]] && [[ "$ledger_code" == 1 ]]; } \
  && ok || no "no .gitignore: creates one ignoring .tdd/develop-red.log but not .tdd/issue-7.md (develop-red.log=$log_code want 0 ignored, issue-7.md=$ledger_code want 1 not ignored)"

repo="$work/unrelated"
make_repo "$repo"
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

repo="$work/diagnostic"
make_repo "$repo"
printf '%s\n' '.tdd/issue-*-spec.md' > "$repo/.gitignore"
want_err="ensure-run-state-ignored: $repo/.gitignore carries veri's run-state rule only in part, or with its lines out of order — fix it by hand"

out="$("$ENSURE" "$repo" 2>"$work/diagnostic.stderr")" && code=0 || code=$?
err="$(cat "$work/diagnostic.stderr")"

{ [[ "$code" == 2 ]] && [[ -z "$out" ]] && [[ "$err" == "$want_err" ]]; } \
  && ok || no "only the spec line: exits 2, prints nothing on stdout and names the file in the refusal diagnostic byte for byte (exit=$code want 2, stdout='$out' want empty, stderr='$err' want '$want_err')"

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

repo="$work/caller"
mkdir -p "$repo"
new_repo -b main "$repo" >/dev/null 2>&1
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

dir="$work/not-a-repo"
mkdir -p "$dir"
want_err="$(GIT_CEILING_DIRECTORIES="$work" git -C "$dir" rev-parse --git-common-dir 2>&1 >/dev/null)"

out="$(GIT_CEILING_DIRECTORIES="$work" "$ENSURE" "$dir" 2>"$work/not-a-repo.stderr")" && code=0 || code=$?
err="$(cat "$work/not-a-repo.stderr")"

{ [[ "$code" == 2 ]] && [[ -z "$out" ]] && [[ -n "$want_err" ]] && [[ "$err" == "$want_err" ]]; } \
  && ok || no "not a git repository: exits 2, prints nothing on stdout and lets git's own diagnostic through (exit=$code want 2, stdout='$out' want empty, stderr='$err' want '$want_err')"

repo="$work/gitignore-dir"
make_repo "$repo"
mkdir -p "$repo/.gitignore"
want_exclude="$(cat "$repo/.git/info/exclude" 2>/dev/null)"

out="$("$ENSURE" "$repo" 2>"$work/gitignore-dir.stderr")" && code=0 || code=$?
[[ -s "$work/gitignore-dir.stderr" ]] && diag=0 || diag=1
ex_now="$(cat "$repo/.git/info/exclude" 2>/dev/null)"

{ [[ "$code" == 2 ]] && [[ -z "$out" ]] && [[ "$diag" == 0 ]] && [[ "$ex_now" == "$want_exclude" ]]; } \
  && ok || no ".gitignore is a directory: exits 2, prints nothing on stdout, says why on stderr, and info/exclude is unchanged (exit=$code want 2, stdout='$out' want empty, stderr-non-empty=$diag want 0, info/exclude='$ex_now' want '$want_exclude')"

ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
make_repo "$work/in-place"
make_repo "$work/linked"
in_place="$(cd "$work/in-place" && "$ENSURE" 2>&1)" && in_place_code=0 || in_place_code=$?
linked="$(cd "$work/linked" && "$work/linked-skill/scripts/ensure-run-state-ignored.sh" 2>&1)" && linked_code=0 || linked_code=$?
cmp -s "$work/in-place/.gitignore" "$work/linked/.gitignore" && same=0 || same=$?

{ [[ "$linked" == "$in_place" ]] && [[ "$linked_code" == "$in_place_code" ]] && [[ "$in_place" == "added" ]] && [[ "$same" == 0 ]]; } \
  && ok || no "run through a symlink to the skill directory and from another working directory with no argument, answers as it does when run in place, the caller's working directory the root (linked='$linked' exit=$linked_code, in place='$in_place' exit=$in_place_code want both 'added' exit 0, .gitignore cmp=$same want 0 identical)"

repo="$work/pinned-scratch"
make_repo "$repo"
decoy="$work/decoy"
make_repo "$decoy"
decoy_exclude_before="$(cat "$decoy/.git/info/exclude" 2>/dev/null)"
mutant="$decoy/skills/tdd/scripts"
mkdir -p "$mutant"
cp -R "$HERE/../veri" "$mutant/veri"
awk '/^exec python3/ { print "cd \"$(dirname \"$0\")\""; sub(/ "\$@"/, "") } { print }' "$ENSURE" > "$mutant/ensure-run-state-ignored.sh"
chmod +x "$mutant/ensure-run-state-ignored.sh"
out="$("$mutant/ensure-run-state-ignored.sh" "$repo" 2>"$work/pinned-scratch.stderr")" && code=0 || code=$?
problems=""
for found in "$decoy/.gitignore" "$mutant/.gitignore"; do
  [[ ! -e "$found" ]] || problems+="; ${found#"$work"/} was written"
done
[[ "$(cat "$decoy/.git/info/exclude" 2>/dev/null)" == "$decoy_exclude_before" ]] || problems+="; decoy/.git/info/exclude changed"
if [[ "$code" == 0 ]]; then
  ignored "$repo" .tdd/develop-red.log || problems+="; exit 0 (stdout='$out') but the scratch repository does not ignore .tdd/develop-red.log"
else
  [[ ! -e "$repo/.gitignore" ]] || problems+="; exit $code but the scratch repository's .gitignore was written"
fi
{ [[ -z "$problems" ]]; } \
  && ok || no "#1158: an ensure-run-state-ignored.sh that drops its root argument and runs from its own directory writes no .gitignore or info/exclude outside the suite's scratch repository (${problems#; }; stderr='$(cat "$work/pinned-scratch.stderr")')"

finish

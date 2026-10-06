#!/usr/bin/env bash
# Tests for scripts/preserve-attempt.sh — the side-ref snapshot a troubled step leaves behind,
# so the tree a rejected or stuck leaf produced is still readable after the run.
#
# Contract under test:
#   preserve-attempt.sh <issue> <step> <phase> <attempt>   # run from the issue's worktree
#       commits the worktree as it stands to refs/veri/attempts/<issue>/<step>/<phase>-<attempt>
#
# Run: scripts/tests/preserve-attempt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PRESERVE="$HERE/../preserve-attempt.sh"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

ident=(GIT_AUTHOR_NAME=veri GIT_AUTHOR_EMAIL=veri@example.test
       GIT_COMMITTER_NAME=veri GIT_COMMITTER_EMAIL=veri@example.test)

git_q() { local repo="$1"; shift; env "${ident[@]}" git -C "$repo" "$@"; }

REF="refs/veri/attempts/409/3/develop-green-1"

ref_resolves() { git_q "$1" rev-parse --verify --quiet "${2:-$REF}^{commit}" >/dev/null 2>&1; }

attempts_dir() { printf '%s/.tdd/attempts' "$1"; }

copies_in() { ls "$(attempts_dir "$1")" 2>/dev/null | tr '\n' ' '; }

copy_path() { printf '%s/%s-develop-green-1-%s.%s' "$(attempts_dir "$1")" "$2" "$3" "$4"; }

copy_text() { if [[ -f "$1" ]]; then cat "$1"; else echo "<missing>"; fi; }

unborn_repo() {
  mkdir -p "$1"
  new_repo -b main "$1" >/dev/null 2>&1
}

make_repo() {
  unborn_repo "$1"
  printf 'committed\n' > "$1/stop-run.sh"
  git_q "$1" add stop-run.sh >/dev/null 2>&1
  git_q "$1" commit -q -m "initial" >/dev/null 2>&1
}

REJECTED="rejected work"

dirty_repo() {
  make_repo "$1"
  printf '%s\n' "$REJECTED" > "$1/stop-run.sh"
}

write_ledger() {
  local repo="$1"; shift
  local box='x' step
  mkdir -p "$repo/.tdd"
  { printf '# Plan for #409\n\n'
    for step in "$@"; do printf -- '- [%s] %s\n' "$box" "$step"; box=' '; done
  } > "$repo/.tdd/issue-409.md"
  git_q "$repo" add .tdd/issue-409.md >/dev/null 2>&1
  git_q "$repo" commit -q -m "plan: scope #409" >/dev/null 2>&1
}

leaf_output() {
  local repo="$1" log_text="$2" out_text="${3:-}"
  mkdir -p "$repo/.tdd"
  printf '%s\n' "$log_text" > "$repo/.tdd/develop-green.log"
  if [[ -n "$out_text" ]]; then printf '%s\n' "$out_text" > "$repo/.tdd/develop-green.out"; fi
}

preserve() {
  local repo="$1"; shift
  ( cd "$repo" && env "${ident[@]}" "$PRESERVE" "$@" )
}

repo="$work/repo"
dirty_repo "$repo"
preserve "$repo" 409 3 develop-green 1 >/dev/null 2>&1; code=$?
ref_resolves "$repo"; resolved=$?
shown="$(git_q "$repo" show "$REF:stop-run.sh" 2>&1)"
{ [[ "$code" == 0 ]] && [[ "$resolved" == 0 ]] && [[ "$shown" == "$REJECTED" ]]; } \
  && ok || no "commits the worktree to $REF and git show reads it back (code=$code resolved=$resolved shown='$shown')"

repo="$work/untouched"
dirty_repo "$repo"
printf 'staged\n' > "$repo/staged.txt"
git_q "$repo" add staged.txt >/dev/null 2>&1
head_before="$(git_q "$repo" rev-parse HEAD 2>&1)"
index_before="$(git_q "$repo" ls-files -s 2>&1)"
log_before="$(git_q "$repo" log --oneline 2>&1)"
preserve "$repo" 409 3 develop-green 1 >/dev/null 2>&1; code=$?
head_after="$(git_q "$repo" rev-parse HEAD 2>&1)"
index_after="$(git_q "$repo" ls-files -s 2>&1)"
log_after="$(git_q "$repo" log --oneline 2>&1)"
{ [[ "$code" == 0 ]] && [[ "$head_after" == "$head_before" ]] \
    && [[ "$index_after" == "$index_before" ]] && [[ "$log_after" == "$log_before" ]]; } \
  && ok || no "leaves HEAD, the index and git log untouched (code=$code head=$head_before/$head_after index_changed=$([[ "$index_after" == "$index_before" ]] && echo no || echo yes) log_changed=$([[ "$log_after" == "$log_before" ]] && echo no || echo yes))"

repo="$work/leafoutput"
make_repo "$repo"
leaf_output "$repo" 'streamed progress' 'final result text'
preserve "$repo" 409 3 develop-green 1 reject >/dev/null 2>&1; code=$?
log_copy="$(copy_path "$repo" 3 reject log)"
out_copy="$(copy_path "$repo" 3 reject out)"
log_text="$(copy_text "$log_copy")"
out_text="$(copy_text "$out_copy")"
{ [[ "$code" == 0 ]] && [[ "$log_text" == "streamed progress" ]] \
    && [[ "$out_text" == "final result text" ]] \
    && [[ -f "$repo/.tdd/develop-green.log" ]] && [[ -f "$repo/.tdd/develop-green.out" ]]; } \
  && ok || no "copies the leaf's log and final output to names carrying step, phase, attempt and mark (code=$code log='$log_text' out='$out_text')"

repo="$work/nooutput"
make_repo "$repo"
leaf_output "$repo" 'streamed progress'
preserve "$repo" 409 3 develop-green 1 stuck >/dev/null 2>&1; code=$?
log_copy="$(copy_path "$repo" 3 stuck log)"
out_copy="$(copy_path "$repo" 3 stuck out)"
log_text="$(copy_text "$log_copy")"
out_there="$([[ -e "$out_copy" ]] && echo yes || echo no)"
{ [[ "$code" == 0 ]] && [[ "$log_text" == "streamed progress" ]] && [[ "$out_there" == no ]]; } \
  && ok || no "preserves the log of a leaf that wrote no final output, with exit 0 (code=$code log='$log_text' out_copy=$out_there)"

repo="$work/nooutputatall"
dirty_repo "$repo"
preserve "$repo" 409 3 develop-green 1 bail >/dev/null 2>&1; code=$?
ref_resolves "$repo"; resolved=$?
copies="$(copies_in "$repo")"
{ [[ "$code" == 0 ]] && [[ "$resolved" == 0 ]] && [[ -z "$copies" ]]; } \
  && ok || no "preserves the tree and exits 0 when the leaf wrote neither log nor output (code=$code resolved=$resolved copies='$copies')"

repo="$work/nomark"
dirty_repo "$repo"
leaf_output "$repo" 'streamed progress' 'final result text'
preserve "$repo" 409 3 develop-green 1 >/dev/null 2>&1; code=$?
ref_resolves "$repo"; resolved=$?
attempts_there="$([[ -e "$(attempts_dir "$repo")" ]] && echo yes || echo no)"
copies="$(copies_in "$repo")"
{ [[ "$code" == 0 ]] && [[ "$resolved" == 0 ]] && [[ "$attempts_there" == no ]] && [[ -z "$copies" ]]; } \
  && ok || no "copies nothing when no mark is given, log present (code=$code resolved=$resolved attempts_dir=$attempts_there copies='$copies')"

repo="$work/blind"
dirty_repo "$repo"
rationale="I used a helper because the verifier rejected the inline version"
leaf_output "$repo" "$rationale" "$rationale"
preserve "$repo" 409 3 develop-green 1 reject >/dev/null 2>&1; code=$?
git_q "$repo" merge-base --is-ancestor "$REF" HEAD >/dev/null 2>&1; reachable=$?
message="$(git_q "$repo" log -1 --format=%B "$REF" 2>&1)"
{ [[ "$code" == 0 ]] && [[ "$reachable" != 0 ]] \
    && [[ "$message" == "attempt: issue 409 step 3 develop-green attempt 1" ]]; } \
  && ok || no "leaves the preserved commit unreachable from HEAD, with a message carrying no rationale (code=$code reachable=$([[ "$reachable" == 0 ]] && echo yes || echo no) message='$message')"

repo="$work/ledgerindex"
dirty_repo "$repo"
prose="A leaf's output is kept under refs/veri, not the branch"
write_ledger "$repo" "The first step, already done" "$prose" "A third step nobody is on"
preserve "$repo" 409 "$prose" develop-green 1 >/dev/null 2>&1; code=$?
indexed="refs/veri/attempts/409/2/develop-green-1"
ref_resolves "$repo" "$indexed"; resolved=$?
refs="$(git_q "$repo" for-each-ref --format='%(refname)' refs/veri/attempts 2>&1 | tr '\n' ' ')"
{ [[ "$code" == 0 ]] && [[ "$resolved" == 0 ]]; } \
  && ok || no "names the ref by the step's ledger index, not its prose (code=$code resolved=$([[ "$resolved" == 0 ]] && echo yes || echo no) refs='$refs')"

repo="$work/prosetitle"
dirty_repo "$repo"
prose="A leaf's tree is kept under refs/veri, not the branch"
preserve "$repo" 409 "$prose" develop-green 1 >/dev/null 2>&1; code=$?
found="$(git_q "$repo" for-each-ref --count=1 --format='%(refname)' refs/veri/attempts/409 2>/dev/null)"
git_q "$repo" check-ref-format "$found" >/dev/null 2>&1; legal=$?
shown="$(git_q "$repo" show "$found:stop-run.sh" 2>&1)"
{ [[ "$code" == 0 ]] && [[ -n "$found" ]] && [[ "$legal" == 0 ]] \
    && [[ "$shown" == "$REJECTED" ]]; } \
  && ok || no "preserves the attempt under a ref git accepts when the step title carries spaces, an apostrophe and a slash (code=$code ref='$found' legal=$([[ "$legal" == 0 ]] && echo yes || echo no) shown='$shown')"

repo="$work/ledgercopies"
make_repo "$repo"
prose="A leaf's output is kept under refs/veri, not the branch"
write_ledger "$repo" "The first step, already done" "$prose"
leaf_output "$repo" 'streamed progress' 'final result text'
preserve "$repo" 409 "$prose" develop-green 1 reject >/dev/null 2>&1; code=$?
log_text="$(copy_text "$(copy_path "$repo" 2 reject log)")"
out_text="$(copy_text "$(copy_path "$repo" 2 reject out)")"
entries="$(copies_in "$repo")"
{ [[ "$code" == 0 ]] && [[ "$log_text" == "streamed progress" ]] \
    && [[ "$out_text" == "final result text" ]] \
    && [[ "$entries" == "2-develop-green-1-reject.log 2-develop-green-1-reject.out " ]]; } \
  && ok || no "names the leaf's copies by the step's ledger index, so a title carrying a slash writes no nested path (code=$code log='$log_text' out='$out_text' entries='$entries')"


repo="$work/otherfailure"
dirty_repo "$repo"
git_q "$repo" update-ref "refs/veri/attempts/409/3" HEAD >/dev/null 2>&1
err="$(preserve "$repo" 409 3 develop-green 1 2>&1 >/dev/null)"; code=$?
said=no
if [[ "$err" == *preserve-attempt.sh* && "$err" == *409* && "$err" == *develop-green* ]]; then said=yes; fi
{ [[ "$code" != 0 ]] && [[ "$said" == yes ]]; } \
  && ok || no "says on stderr that it could not preserve the attempt when the ref write fails for another reason (code=$code said=$said err='$err')"

repo="$work/refusedexact"
dirty_repo "$repo"
git_q "$repo" update-ref "refs/veri/attempts/409/3" HEAD >/dev/null 2>&1
err="$(preserve "$repo" 409 3 develop-green 1 2>&1 >/dev/null)"; code=$?
last="$(printf '%s\n' "$err" | tail -n 1)"
expected="preserve-attempt.sh: could not preserve issue 409 step 3 develop-green attempt 1 to $REF"
{ [[ "$code" == 1 ]] && [[ "$last" == "$expected" ]]; } \
  && ok || no "exits exactly 1 with the could-not-preserve line last on stderr when an existing refs/veri/attempts/409/3 refuses the ref write (code=$code last='$last')"

repo="$work/unborn"
unborn_repo "$repo"
printf '%s\n' "$REJECTED" > "$repo/stop-run.sh"
preserve "$repo" 409 3 develop-green 1 >/dev/null 2>&1; code=$?
[[ "$code" == 2 ]] \
  && ok || no "ends with exit 2 when it fails inside its own EXIT trap's lifetime (code=$code)"

repo="$work/threeargs"
dirty_repo "$repo"
out="$(preserve "$repo" 409 3 develop-green 2>"$work/threeargs.err")"; code=$?
err="$(cat "$work/threeargs.err")"
usage="usage: preserve-attempt.sh <issue> <step> <phase> <attempt> [<mark>]"
{ [[ "$code" == 2 ]] && [[ "$err" == "$usage" ]] && [[ -z "$out" ]]; } \
  && ok || no "called with three arguments exits 2 with exactly the usage line on stderr and nothing on stdout (code=$code out='$out' err='$err')"

inplace="$work/inplace"
linked="$work/linked"
for repo in "$inplace" "$linked"; do
  dirty_repo "$repo"
  mkdir -p "$repo/sub"
  printf 'nested\n' > "$repo/sub/nested.txt"
done
ln -s "$(cd "$HERE/../.." && pwd)" "$work/skill-link"
preserve "$inplace" 409 3 develop-green 1 >/dev/null 2>&1; code_inplace=$?
( cd "$linked/sub" && env "${ident[@]}" "$work/skill-link/scripts/preserve-attempt.sh" 409 3 develop-green 1 ) >/dev/null 2>&1; code_linked=$?
tree_inplace="$(git_q "$inplace" rev-parse --verify --quiet "$REF^{tree}" 2>&1)"
tree_linked="$(git_q "$linked" rev-parse --verify --quiet "$REF^{tree}" 2>&1)"
{ [[ "$code_linked" == "$code_inplace" ]] && [[ "$code_inplace" == 0 ]] \
    && [[ -n "$tree_inplace" ]] && [[ "$tree_linked" == "$tree_inplace" ]]; } \
  && ok || no "run through a symlink to the skill directory from a subdirectory of another repository, preserves that repository's worktree to the same ref, tree and exit code as in place (code=$code_inplace/$code_linked tree='$tree_inplace'/'$tree_linked')"


outside="$work/outside"
mkdir -p "$outside/bin" "$outside/cwd" "$outside/tmp"
real_git="$(command -v git)"
printf '#!/bin/sh\necho "$1" >> "%s"\nexec "%s" "$@"\n' "$outside/git.log" "$real_git" > "$outside/bin/git"
chmod +x "$outside/bin/git"
( cd "$outside/cwd" && env GIT_CEILING_DIRECTORIES="$work" TMPDIR="$outside/tmp" PATH="$outside/bin:$PATH" \
    "$PRESERVE" 409 3 develop-green 1 ) >/dev/null 2>"$outside/err"
err="$(cat "$outside/err")"
verbs="$(tr '\n' ' ' < "$outside/git.log" 2>/dev/null)"
left="$(ls -A "$outside/tmp")"
{ [[ "$(wc -l < "$outside/err" | tr -d ' ')" == 1 ]] && [[ "$err" == preserve-attempt.sh:*"not in a git work tree"* ]] \
    && [[ -z "$left" ]] && [[ "$verbs" != *add* ]]; } \
  && ok || no "outside a git work tree prints exactly one stderr line naming preserve-attempt.sh and saying it is not in a git work tree, makes no scratch directory and runs no git add (#1030) (err='$err' left='$left' verbs='$verbs')"


finish

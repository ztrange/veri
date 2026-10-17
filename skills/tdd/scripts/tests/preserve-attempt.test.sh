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
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"
mkdir -p "$work/skill/scripts"
cp -R "$HERE/../preserve-attempt.sh" "$HERE/../veri" "$work/skill/scripts/"
PRESERVE="$work/skill/scripts/preserve-attempt.sh"

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
ln -s "$work/skill" "$work/skill-link"
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


repo="$work/refformat"
dirty_repo "$repo"
preserve "$repo" 409 "a—b ⟦x⟧/c'd e" develop-green 1 >/dev/null 2>&1; code=$?
made="$(git_q "$repo" for-each-ref --format='%(refname)' refs/veri/attempts/409/ 2>&1)"
git_q "$repo" check-ref-format "$made" >/dev/null 2>&1; accepted=$?
{ [[ "$code" == 0 ]] && [[ "$(printf '%s\n' "$made" | wc -l | tr -d ' ')" == 1 ]] && [[ "$accepted" == 0 ]]; } \
  && ok || no "for a step holding multi-byte characters, '/', an apostrophe and spaces creates one ref git check-ref-format accepts (#1032) (code=$code made='$made' accepted=$accepted)"


repo="$work/trackedignored"
make_repo "$repo"
printf 'committed\n' > "$repo/t.txt"
git_q "$repo" add t.txt >/dev/null 2>&1
git_q "$repo" commit -q -m "track t.txt" >/dev/null 2>&1
printf 't.txt\n' > "$repo/.gitignore"
printf 'edited by the leaf\n' > "$repo/t.txt"
preserve "$repo" 409 3 develop-green 1 >/dev/null 2>&1; code=$?
shown="$(git_q "$repo" show "$REF:t.txt" 2>&1)"
{ [[ "$code" == 0 ]] && [[ "$shown" == "edited by the leaf" ]]; } \
  && ok || no "keeps a file tracked in HEAD and matched by .gitignore in the preserved tree with its worktree content (#1033) (code=$code shown='$shown')"


repo="$work/trackedignoredneighbours"
make_repo "$repo"
printf 'committed\n' > "$repo/t.txt"
printf 'committed\n' > "$repo/gone.txt"
git_q "$repo" add t.txt gone.txt >/dev/null 2>&1
git_q "$repo" commit -q -m "track t.txt and gone.txt" >/dev/null 2>&1
printf 't.txt\nscratch.log\n' > "$repo/.gitignore"
printf 'ignored\n' > "$repo/scratch.log"
printf 'new\n' > "$repo/fresh.txt"
rm "$repo/gone.txt"
preserve "$repo" 409 3 develop-green 1 >/dev/null 2>&1; code=$?
listed="$(git_q "$repo" ls-tree --name-only "$REF" 2>&1 | tr '\n' ' ')"
{ [[ "$code" == 0 ]] && [[ "$listed" == ".gitignore fresh.txt stop-run.sh t.txt " ]]; } \
  && ok || no "beside a tracked ignored file, leaves an untracked ignored file and a deleted tracked file out of the preserved tree and keeps an untracked non-ignored one (#1033) (code=$code listed='$listed')"


repo="$work/trackedignoredcaller"
make_repo "$repo"
printf 'committed\n' > "$repo/t.txt"
git_q "$repo" add t.txt >/dev/null 2>&1
git_q "$repo" commit -q -m "track t.txt" >/dev/null 2>&1
printf 't.txt\n' > "$repo/.gitignore"
printf 'edited by the leaf\n' > "$repo/t.txt"
printf 'staged\n' > "$repo/staged.txt"
git_q "$repo" add staged.txt >/dev/null 2>&1
head_before="$(git_q "$repo" rev-parse HEAD 2>&1)"
branch_before="$(git_q "$repo" symbolic-ref HEAD 2>&1)"
index_before="$(git_q "$repo" ls-files -s 2>&1)"
preserve "$repo" 409 3 develop-green 1 >/dev/null 2>&1; code=$?
head_after="$(git_q "$repo" rev-parse HEAD 2>&1)"
branch_after="$(git_q "$repo" symbolic-ref HEAD 2>&1)"
index_after="$(git_q "$repo" ls-files -s 2>&1)"
{ [[ "$code" == 0 ]] && [[ "$head_after" == "$head_before" ]] && [[ "$branch_after" == "$branch_before" ]] \
    && [[ "$index_after" == "$index_before" ]]; } \
  && ok || no "preserving a worktree holding a tracked file .gitignore matches leaves the caller's index, HEAD and branch untouched (#1033) (code=$code head=$head_before/$head_after branch=$branch_before/$branch_after index_changed=$([[ "$index_after" == "$index_before" ]] && echo no || echo yes))"


repo="$work/pinned-scratch"
dirty_repo "$repo"
leaf_output "$repo" 'scratch progress' 'scratch result'
decoy="$work/decoy"
make_repo "$decoy"
write_ledger "$decoy" "The first step, already done" "A step the decoy is on"
leaf_output "$decoy" 'decoy progress' 'decoy result'
ledger_before="$(cat "$decoy/.tdd/issue-409.md")"
mutant="$decoy/skills/tdd/scripts"
mkdir -p "$mutant"
cp -R "$HERE/../veri" "$mutant/veri"
awk '/^exec python3/ { print "cd \"$(dirname \"$0\")\"" } { print }' "$PRESERVE" > "$mutant/preserve-attempt.sh"
chmod +x "$mutant/preserve-attempt.sh"
( cd "$repo" && env "${ident[@]}" "$mutant/preserve-attempt.sh" 409 3 develop-green 1 reject ) >/dev/null 2>"$work/pinned-scratch.err"; code=$?
problems=""
decoy_refs="$(git_q "$decoy" for-each-ref --format='%(refname)' refs/veri 2>&1)"
[[ -z "$decoy_refs" ]] || problems+="; the decoy repository gained refs: $decoy_refs"
[[ ! -e "$(attempts_dir "$decoy")" ]] || problems+="; $(attempts_dir "$decoy") was written: $(copies_in "$decoy")"
[[ "$(cat "$decoy/.tdd/issue-409.md")" == "$ledger_before" ]] || problems+="; the decoy ledger changed"
[[ "$code" != 0 ]] || problems+="; exit=0, want the case to fail on a subject that resolved the decoy repository"
{ [[ -z "$problems" ]]; } \
  && ok || no "#1158: a preserve-attempt.sh that resolves its toplevel from its own directory, not the suite's scratch repository, writes no .tdd/attempts entry, ref or ledger change outside that repository (${problems#; }; stderr='$(cat "$work/pinned-scratch.err")')"


repo="$work/scratch-copy"
dirty_repo "$repo"
leaf_output "$repo" 'scratch progress' 'scratch result'
scratch="$(cd "$work" && pwd -P)"
subject_dir="$(cd "$(dirname "$PRESERVE")" && pwd -P)"
problems=""
if [[ "$subject_dir/" != "$scratch/"* ]]; then
  problems+="; want the suite to run a copy of preserve-attempt.sh under its scratch directory $scratch, it runs $subject_dir/preserve-attempt.sh"
else
  landing="$(cd "$subject_dir/../.." && pwd -P)"
  if [[ "$landing/" != "$scratch/"* || "$landing/" == "$(cd "$repo" && pwd -P)/"* ]]; then
    problems+="; want the copy's ../.. inside $scratch and outside the scratch repository, it is $landing"
  else
    live="$landing/.tdd/wt/5"
    mkdir -p "$live/.tdd"
    printf '%s\n' "$$" > "$live/.tdd/conductor.pid"
    write_ledger "$live" "The first step, already done" "A step the live run is on" 2>/dev/null
    ledger_before="$(cat "$live/.tdd/issue-409.md")"
    cp "$PRESERVE" "$PRESERVE.orig"
    awk '/^exec python3/ { print "cd \"$(dirname \"$0\")/../..\"" } { print }' "$PRESERVE.orig" > "$PRESERVE"
    chmod +x "$PRESERVE"
    preserve "$repo" 409 3 develop-green 1 reject >/dev/null 2>"$work/scratch-copy.err"
    mv "$PRESERVE.orig" "$PRESERVE"
    landing_refs="$(git -C "$landing" for-each-ref --format='%(refname)' refs/veri/attempts 2>/dev/null)"
    [[ -z "$landing_refs" ]] || problems+="; refs written beside the scratch repository: $landing_refs"
    [[ ! -e "$(attempts_dir "$landing")" ]] || problems+="; $(attempts_dir "$landing") was written: $(copies_in "$landing")"
    [[ ! -e "$(attempts_dir "$live")" ]] || problems+="; $(attempts_dir "$live") was written: $(copies_in "$live")"
    [[ "$(cat "$live/.tdd/issue-409.md")" == "$ledger_before" ]] || problems+="; the live-looking run's ledger changed"
  fi
fi
{ [[ -z "$problems" ]]; } \
  && ok || no "#1158: the suite runs a scratch copy of preserve-attempt.sh, and a cd \"\$(dirname \"\$0\")/../..\" planted into it writes no .tdd/attempts entry, ref or ledger change outside the scratch repository (${problems#; })"


repo="$work/noidentity"
dirty_repo "$repo"
git -C "$repo" config --unset user.name
git -C "$repo" config --unset user.email
printf '[user]\n\tuseConfigOnly = true\n' > "$work/noidentity.gitconfig"
( cd "$repo" && env -u GIT_AUTHOR_NAME -u GIT_AUTHOR_EMAIL -u GIT_COMMITTER_NAME -u GIT_COMMITTER_EMAIL -u EMAIL \
    GIT_CONFIG_GLOBAL="$work/noidentity.gitconfig" GIT_CONFIG_NOSYSTEM=1 \
    "$PRESERVE" 409 3 develop-green 1 ) >/dev/null 2>"$work/noidentity.err"; code=$?
ref_resolves "$repo"; resolved=$?
{ [[ "$code" == 0 ]] && [[ "$resolved" == 0 ]]; } \
  && ok || no "#1438: with no user.name or user.email in any git config, writes $REF and exits 0 (code=$code resolved=$resolved stderr='$(cat "$work/noidentity.err")')"

repo="$work/noidentity-copies"
dirty_repo "$repo"
git -C "$repo" config --unset user.name
git -C "$repo" config --unset user.email
leaf_output "$repo" 'streamed progress' 'final result text'
printf '[user]\n\tuseConfigOnly = true\n' > "$work/noidentity-copies.gitconfig"
( cd "$repo" && env -u GIT_AUTHOR_NAME -u GIT_AUTHOR_EMAIL -u GIT_COMMITTER_NAME -u GIT_COMMITTER_EMAIL -u EMAIL \
    GIT_CONFIG_GLOBAL="$work/noidentity-copies.gitconfig" GIT_CONFIG_NOSYSTEM=1 \
    "$PRESERVE" 409 3 develop-green 1 reject ) >/dev/null 2>"$work/noidentity-copies.err"; code=$?
log_text="$(copy_text "$(copy_path "$repo" 3 reject log)")"
out_text="$(copy_text "$(copy_path "$repo" 3 reject out)")"
{ [[ "$log_text" == "streamed progress" ]] && [[ "$out_text" == "final result text" ]]; } \
  && ok || no "#1438: with no user.name or user.email in any git config, a mark still copies .tdd/develop-green.log and .tdd/develop-green.out under .tdd/attempts/ (code=$code log='$log_text' out='$out_text' stderr='$(cat "$work/noidentity-copies.err")')"

finish

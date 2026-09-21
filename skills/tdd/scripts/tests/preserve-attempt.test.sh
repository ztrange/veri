#!/usr/bin/env bash
# Tests for scripts/preserve-attempt.sh — the side-ref snapshot a troubled step leaves behind,
# so the tree a rejected or stuck leaf produced is still readable after the run (issue #409).
#
# Contract under test:
#   preserve-attempt.sh <issue> <step> <phase> <attempt>   # run from the issue's worktree
#       commits the worktree as it stands to refs/veri/attempts/<issue>/<step>/<phase>-<attempt>
#
# The subject is git's own storage, so this suite is not in the fast tier: the behaviour under
# test IS a real repository's refs, and a fake git could not answer `git show`. Every case runs
# against a throwaway `git init` repo with one commit, and asks git rather than the filesystem —
# a file written under .git by hand would pass a filesystem check and be no commit at all.
#
# Run: scripts/tests/preserve-attempt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PRESERVE="$HERE/../preserve-attempt.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# The identity every commit this suite causes is made under, stated once: the suite must not
# depend on whatever user.name/user.email the machine running it carries (CI carries none).
# In the environment rather than as `git -c` flags because half the commits are git's own,
# made inside the script under test, which takes no flags from here.
ident=(GIT_AUTHOR_NAME=veri GIT_AUTHOR_EMAIL=veri@example.test
       GIT_COMMITTER_NAME=veri GIT_COMMITTER_EMAIL=veri@example.test)

# git_q <repo> <args…> — git run against <repo> under that identity.
git_q() { local repo="$1"; shift; env "${ident[@]}" git -C "$repo" "$@"; }

# Every case calls the script with the same coordinates — issue 409, step 3, develop-green,
# attempt 1 — so the one ref they all expect is spelled out once rather than per case.
REF="refs/veri/attempts/409/3/develop-green-1"

# ref_resolves <repo> — 0 when $REF names a commit in <repo>. Asked of git rather than of the
# filesystem, for the reason in the header: a file written under .git by hand would pass a
# filesystem check and be no commit at all.
ref_resolves() { git_q "$1" rev-parse --verify --quiet "$REF^{commit}" >/dev/null 2>&1; }

# copy_path <repo> <mark> <ext> — where preservation puts the leaf's <ext> file in <repo> for
# those same coordinates under <mark>. The name is the criterion itself — step, phase, attempt
# and the mark that triggered the preservation — so it is built in one place, not per case.
copy_path() { printf '%s/.tdd/attempts/3-develop-green-1-%s.%s' "$1" "$2" "$3"; }

# copy_text <path> — the preserved file's contents, or the literal <missing> when it was never
# written. A failure message that says <missing> distinguishes "preserved the wrong bytes" from
# "preserved nothing", which an empty string would not.
copy_text() { if [[ -f "$1" ]]; then cat "$1"; else echo "<missing>"; fi; }

# new_repo <path> — a throwaway repo at <path>, on `main`, carrying one commit that tracks
# stop-run.sh. -b main names the default branch rather than inheriting init.defaultBranch.
new_repo() {
  mkdir -p "$1"
  git init -q -b main "$1" >/dev/null 2>&1
  printf 'committed\n' > "$1/stop-run.sh"
  git_q "$1" add stop-run.sh >/dev/null 2>&1
  git_q "$1" commit -q -m "initial" >/dev/null 2>&1
}

# preserve <repo> <args…> — call the script from <repo>, under the same identity: the commit
# it makes is git's, and a machine with no configured user (CI) must not decide whether this
# case can run at all.
preserve() {
  local repo="$1"; shift
  ( cd "$repo" && env "${ident[@]}" "$PRESERVE" "$@" )
}

# 1. the worktree as it stands lands on a ref named by issue, step, phase and attempt, and
#    `git show` reads that commit's tree back — the rejected file, which no commit on the
#    branch ever carried
repo="$work/repo"
new_repo "$repo"
printf 'rejected work\n' > "$repo/stop-run.sh"
preserve "$repo" 409 3 develop-green 1 >/dev/null 2>&1; code=$?
ref_resolves "$repo"; resolved=$?
shown="$(git_q "$repo" show "$REF:stop-run.sh" 2>&1)"
{ [[ "$code" == 0 ]] && [[ "$resolved" == 0 ]] && [[ "$shown" == "rejected work" ]]; } \
  && ok || no "commits the worktree to $REF and git show reads it back (code=$code resolved=$resolved shown='$shown')"

# 2. preserving leaves the work branch untouched — HEAD, the index and `git log` read the same
#    after as before, so a rebase-merge of the branch carries none of the preserved commit. The
#    index is made to differ from HEAD first (a staged file), so "unchanged" is a real claim
#    rather than one an empty index would satisfy by accident.
repo="$work/untouched"
new_repo "$repo"
printf 'rejected work\n' > "$repo/stop-run.sh"
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

# 3. the leaf's own output is preserved beside the tree: the progress log and the final-output
#    file are copied to names carrying the step, phase, attempt and the mark that triggered the
#    preservation, so a reader can pair them with the event that made the step interesting. The
#    originals stay where run-leaf.sh left them — this is a copy, not a move, because the leaf
#    that wrote them may still be the one a retry reads back.
repo="$work/leafoutput"
new_repo "$repo"
mkdir -p "$repo/.tdd"
printf 'streamed progress\n' > "$repo/.tdd/develop-green.log"
printf 'final result text\n' > "$repo/.tdd/develop-green.out"
preserve "$repo" 409 3 develop-green 1 reject >/dev/null 2>&1; code=$?
log_copy="$(copy_path "$repo" reject log)"
out_copy="$(copy_path "$repo" reject out)"
log_text="$(copy_text "$log_copy")"
out_text="$(copy_text "$out_copy")"
{ [[ "$code" == 0 ]] && [[ "$log_text" == "streamed progress" ]] \
    && [[ "$out_text" == "final result text" ]] \
    && [[ -f "$repo/.tdd/develop-green.log" ]] && [[ -f "$repo/.tdd/develop-green.out" ]]; } \
  && ok || no "copies the leaf's log and final output to names carrying step, phase, attempt and mark (code=$code log='$log_text' out='$out_text')"

# 4. a leaf killed before it wrote its final-output file still gets its log preserved, and the
#    preservation reports success: a missing .out is the normal shape of a stuck or killed leaf,
#    not a failure of preserving what there was. No .out copy is written, because there was
#    nothing to copy.
repo="$work/nooutput"
new_repo "$repo"
mkdir -p "$repo/.tdd"
printf 'streamed progress\n' > "$repo/.tdd/develop-green.log"
preserve "$repo" 409 3 develop-green 1 stuck >/dev/null 2>&1; code=$?
log_copy="$(copy_path "$repo" stuck log)"
out_copy="$(copy_path "$repo" stuck out)"
log_text="$(copy_text "$log_copy")"
out_there="$([[ -e "$out_copy" ]] && echo yes || echo no)"
{ [[ "$code" == 0 ]] && [[ "$log_text" == "streamed progress" ]] && [[ "$out_there" == no ]]; } \
  && ok || no "preserves the log of a leaf that wrote no final output, with exit 0 (code=$code log='$log_text' out_copy=$out_there)"

# 5. and a leaf that wrote neither file is preserved too: the tree is still on its ref and the
#    preservation still reports success. Nothing is copied, so a reader is never handed an
#    empty file that reads as "the leaf said nothing" when the truth is it never wrote one.
repo="$work/nooutputatall"
new_repo "$repo"
printf 'rejected work\n' > "$repo/stop-run.sh"
preserve "$repo" 409 3 develop-green 1 bail >/dev/null 2>&1; code=$?
ref_resolves "$repo"; resolved=$?
copies="$(ls "$repo/.tdd/attempts" 2>/dev/null | tr '\n' ' ')"
{ [[ "$code" == 0 ]] && [[ "$resolved" == 0 ]] && [[ -z "$copies" ]]; } \
  && ok || no "preserves the tree and exits 0 when the leaf wrote neither log nor output (code=$code resolved=$resolved copies='$copies')"

# 6. and the mark is what turns copying on: the same call without it — four arguments, with a
#    progress log sitting right there in .tdd — preserves the tree and copies nothing. An
#    untroubled step is the common case, and it must cost what it costs today: no .tdd/attempts
#    directory, no copies in it.
repo="$work/nomark"
new_repo "$repo"
printf 'rejected work\n' > "$repo/stop-run.sh"
mkdir -p "$repo/.tdd"
printf 'streamed progress\n' > "$repo/.tdd/develop-green.log"
printf 'final result text\n' > "$repo/.tdd/develop-green.out"
preserve "$repo" 409 3 develop-green 1 >/dev/null 2>&1; code=$?
ref_resolves "$repo"; resolved=$?
attempts_there="$([[ -e "$repo/.tdd/attempts" ]] && echo yes || echo no)"
copies="$(ls "$repo/.tdd/attempts" 2>/dev/null | tr '\n' ' ')"
{ [[ "$code" == 0 ]] && [[ "$resolved" == 0 ]] && [[ "$attempts_there" == no ]] && [[ -z "$copies" ]]; } \
  && ok || no "copies nothing when no mark is given, log present (code=$code resolved=$resolved attempts_dir=$attempts_there copies='$copies')"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
